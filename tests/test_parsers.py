"""
Tests for Dissect 2.0 - Trace Parsers
"""

import os
import unittest

from dissect.trace_receiver import OrchestrationGraph, parse_trace_file


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


if __name__ == "__main__":
    unittest.main()
