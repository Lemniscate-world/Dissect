"""
Tests for Dissect 2.0 - Trace Parsers
"""

import json
import os
import tempfile
import unittest

from dissect.graph import NodeType, OrchestrationGraph
from dissect.trace_receiver import (
    AutoGenParser,
    CrewAIParser,
    LangChainParser,
    OpenTelemetryParser,
    parse_trace_file,
)


class TestTraceParsers(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.join(os.path.dirname(__file__), "../examples")

    def test_opentelemetry_parser(self):
        trace_path = os.path.join(self.examples_dir, "sample_trace.json")
        if not os.path.exists(trace_path):
            self.skipTest("Sample trace not found")

        graph = parse_trace_file(trace_path)
        self.assertIsInstance(graph, OrchestrationGraph)
        self.assertGreater(len(graph.nodes), 0)

    def test_crewai_parser(self):
        trace_path = os.path.join(self.examples_dir, "crewai_trace.json")
        if not os.path.exists(trace_path):
            self.skipTest("CrewAI trace not found")

        graph = parse_trace_file(trace_path)
        self.assertIsInstance(graph, OrchestrationGraph)
        self.assertEqual(graph.name, "Research & Writing Crew")
        self.assertGreater(len(graph.nodes), 0)

    def test_autogen_parser(self):
        trace_path = os.path.join(self.examples_dir, "autogen_trace.json")
        if not os.path.exists(trace_path):
            self.skipTest("AutoGen trace not found")

        graph = parse_trace_file(trace_path)
        self.assertIsInstance(graph, OrchestrationGraph)
        self.assertGreater(len(graph.nodes), 0)


class TestOpenTelemetryParserUnit(unittest.TestCase):
    """Unit tests for OpenTelemetryParser without file dependencies."""

    def test_parse_simple_spans(self):
        data = {
            "spans": [
                {
                    "spanId": "s1",
                    "name": "langchain.agent",
                    "startTimeUnixNano": "1000000000",
                    "endTimeUnixNano": "2000000000",
                    "attributes": [],
                },
                {
                    "spanId": "s2",
                    "name": "tool_call",
                    "parentSpanId": "s1",
                    "attributes": [],
                },
            ]
        }
        parser = OpenTelemetryParser()
        graph = parser.parse(data)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
        self.assertAlmostEqual(graph.nodes["s1"].start_time, 1.0)
        self.assertAlmostEqual(graph.nodes["s1"].end_time, 2.0)

    def test_parse_otlp_full_structure(self):
        data = {
            "resourceSpans": [
                {
                    "scopeSpans": [
                        {
                            "spans": [
                                {"spanId": "a", "name": "root", "attributes": []},
                            ]
                        }
                    ]
                }
            ]
        }
        parser = OpenTelemetryParser()
        graph = parser.parse(data)
        self.assertEqual(len(graph.nodes), 1)

    def test_parse_attributes(self):
        data = {
            "spans": [
                {
                    "spanId": "s1",
                    "name": "test",
                    "attributes": [
                        {"key": "str_key", "value": {"stringValue": "hello"}},
                        {"key": "int_key", "value": {"intValue": "42"}},
                        {"key": "dbl_key", "value": {"doubleValue": 3.14}},
                        {"key": "bool_key", "value": {"boolValue": True}},
                        {"key": "other_key", "value": {"arrayValue": [1, 2]}},
                    ],
                }
            ]
        }
        parser = OpenTelemetryParser()
        graph = parser.parse(data)
        meta = graph.nodes["s1"].metadata
        self.assertEqual(meta["str_key"], "hello")
        self.assertEqual(meta["int_key"], 42)
        self.assertAlmostEqual(meta["dbl_key"], 3.14)
        self.assertTrue(meta["bool_key"])

    def test_node_type_detection(self):
        data = {
            "spans": [
                {"spanId": "s1", "name": "langchain.agent.run", "attributes": []},
                {"spanId": "s2", "name": "openai.chat.completion", "attributes": []},
            ]
        }
        parser = OpenTelemetryParser()
        graph = parser.parse(data)
        self.assertEqual(graph.nodes["s1"].node_type, NodeType.AGENT)
        self.assertEqual(graph.nodes["s2"].node_type, NodeType.LLM_CALL)


class TestLangChainParserUnit(unittest.TestCase):
    def test_parse_with_child_runs(self):
        data = {
            "name": "LC Trace",
            "runs": [
                {
                    "id": "r1",
                    "name": "AgentExecutor",
                    "run_type": "agent",
                    "start_time": 1000000000.0,
                    "end_time": 1000001000.0,
                    "child_runs": [
                        {
                            "id": "r2",
                            "name": "search_tool",
                            "run_type": "tool",
                            "child_runs": [],
                        }
                    ],
                }
            ],
        }
        parser = LangChainParser()
        graph = parser.parse(data)
        self.assertEqual(graph.name, "LC Trace")
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(graph.nodes["r1"].node_type, NodeType.AGENT)
        self.assertEqual(graph.nodes["r2"].node_type, NodeType.TOOL)
        self.assertEqual(len(graph.edges), 1)

    def test_parse_timestamp_iso(self):
        parser = LangChainParser()
        ts = parser._parse_timestamp("2025-01-15T10:30:00Z")
        self.assertIsNotNone(ts)
        self.assertIsInstance(ts, float)

    def test_parse_timestamp_milliseconds(self):
        parser = LangChainParser()
        ts = parser._parse_timestamp(1705312200000)  # ms
        self.assertAlmostEqual(ts, 1705312200.0)

    def test_parse_timestamp_seconds(self):
        parser = LangChainParser()
        ts = parser._parse_timestamp(1705312200.0)
        self.assertAlmostEqual(ts, 1705312200.0)

    def test_parse_timestamp_invalid(self):
        parser = LangChainParser()
        self.assertIsNone(parser._parse_timestamp("not-a-date"))
        self.assertIsNone(parser._parse_timestamp(None))
        self.assertIsNone(parser._parse_timestamp([1, 2, 3]))


class TestCrewAIParserUnit(unittest.TestCase):
    def test_parse_with_execution_trace(self):
        data = {
            "crew_name": "Test Crew",
            "crew_id": "crew-1",
            "agents": [],
            "tasks": [],
            "execution_trace": [
                {
                    "step_id": "step-1",
                    "type": "agent_execution",
                    "name": "Research Step",
                    "start_time": 1000.0,
                    "end_time": 1005.0,
                },
                {
                    "step_id": "step-2",
                    "type": "tool_call",
                    "name": "Web Search",
                },
            ],
        }
        parser = CrewAIParser()
        graph = parser.parse(data)
        self.assertEqual(graph.name, "Test Crew")
        # crew root + 2 steps
        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(graph.nodes["step-1"].node_type, NodeType.AGENT)
        self.assertEqual(graph.nodes["step-2"].node_type, NodeType.TOOL)

    def test_parse_with_agent_tool_calls(self):
        data = {
            "crew_name": "Tool Crew",
            "crew_id": "crew-2",
            "agents": [
                {
                    "agent_id": "a1",
                    "role": "Researcher",
                    "tool_calls": [
                        {"tool_id": "t1", "tool_name": "web_search"},
                        {"tool_id": "t2", "tool_name": "calculator"},
                    ],
                }
            ],
            "tasks": [],
        }
        parser = CrewAIParser()
        graph = parser.parse(data)
        # crew root + agent + 2 tools
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(graph.nodes["t1"].node_type, NodeType.TOOL)
        self.assertEqual(graph.nodes["t1"].name, "web_search")

    def test_parse_with_tasks(self):
        data = {
            "crew_name": "Task Crew",
            "crew_id": "crew-3",
            "agents": [],
            "tasks": [
                {"task_id": "task-1", "description": "Research AI trends"},
                {"task_id": "task-2", "description": "Write summary report"},
            ],
        }
        parser = CrewAIParser()
        graph = parser.parse(data)
        # crew root + 2 tasks
        self.assertEqual(len(graph.nodes), 3)


class TestAutoGenParserUnit(unittest.TestCase):
    def test_parse_conversation(self):
        data = {
            "name": "AG Chat",
            "agents": [
                {"name": "UserProxy", "type": "user_proxy"},
                {"name": "Assistant", "type": "assistant"},
            ],
            "messages": [
                {"message_id": "m1", "sender": "UserProxy", "content": "Hello", "role": "user"},
                {
                    "message_id": "m2",
                    "sender": "Assistant",
                    "content": "Hi there",
                    "role": "assistant",
                },
            ],
        }
        parser = AutoGenParser()
        graph = parser.parse(data)
        self.assertEqual(graph.name, "AG Chat")
        # 2 agents + 2 messages
        self.assertEqual(len(graph.nodes), 4)
        # m1 connects to UserProxy agent, m2 connects to m1
        self.assertEqual(len(graph.edges), 2)

    def test_parse_with_function_calls(self):
        data = {
            "name": "FC Chat",
            "agents": [],
            "messages": [
                {
                    "message_id": "m1",
                    "sender": "Agent",
                    "content": "Calling tool",
                    "function_calls": [
                        {"id": "fc1", "name": "search", "arguments": '{"q": "test"}'},
                    ],
                }
            ],
        }
        parser = AutoGenParser()
        graph = parser.parse(data)
        # 1 message + 1 function call
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(graph.nodes["fc1"].node_type, NodeType.TOOL)
        self.assertEqual(graph.nodes["fc1"].name, "search")

    def test_parse_with_tool_calls_key(self):
        """Test AutoGen messages using 'tool_calls' instead of 'function_calls'."""
        data = {
            "name": "TC Chat",
            "agents": [],
            "messages": [
                {
                    "message_id": "m1",
                    "sender": "Agent",
                    "content": "Using tool",
                    "tool_calls": [
                        {"id": "tc1", "function": {"name": "calc", "arguments": "{}"}},
                    ],
                }
            ],
        }
        parser = AutoGenParser()
        graph = parser.parse(data)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(graph.nodes["tc1"].name, "calc")

    def test_parse_timestamp_variants(self):
        parser = AutoGenParser()
        self.assertIsNone(parser._parse_timestamp(None))
        self.assertAlmostEqual(parser._parse_timestamp(1705312200.0), 1705312200.0)
        self.assertAlmostEqual(parser._parse_timestamp(1705312200000), 1705312200.0)
        self.assertIsNone(parser._parse_timestamp("bad-date"))


class TestAutoDetection(unittest.TestCase):
    """Test parse_trace_file auto-detection logic."""

    def _write_temp_json(self, data):
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        json.dump(data, f)
        f.close()
        return f.name

    def test_detect_opentelemetry(self):
        path = self._write_temp_json({"spans": [{"spanId": "s1", "name": "test", "attributes": []}]})
        try:
            graph = parse_trace_file(path)
            self.assertIsInstance(graph, OrchestrationGraph)
        finally:
            os.remove(path)

    def test_detect_langchain(self):
        path = self._write_temp_json({"runs": [{"id": "r1", "name": "chain", "run_type": "chain", "child_runs": []}]})
        try:
            graph = parse_trace_file(path)
            self.assertIsInstance(graph, OrchestrationGraph)
        finally:
            os.remove(path)

    def test_detect_crewai(self):
        path = self._write_temp_json({"crew_name": "Test", "agents": [], "tasks": []})
        try:
            graph = parse_trace_file(path)
            self.assertEqual(graph.name, "Test")
        finally:
            os.remove(path)

    def test_detect_autogen(self):
        path = self._write_temp_json({"messages": [{"message_id": "m1", "sender": "A", "content": "hi"}]})
        try:
            graph = parse_trace_file(path)
            self.assertIsInstance(graph, OrchestrationGraph)
        finally:
            os.remove(path)

    def test_detect_fallback_to_otel(self):
        path = self._write_temp_json({"unknown_format": True})
        try:
            graph = parse_trace_file(path)
            self.assertIsInstance(graph, OrchestrationGraph)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
