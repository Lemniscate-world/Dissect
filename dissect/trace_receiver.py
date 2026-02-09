"""
Dissect 2.0 - Trace Receiver

Parses OpenTelemetry traces and framework-specific trace formats
into OrchestrationGraph structures.
"""

import json
from typing import Any, Dict, List, Optional

from .graph import Edge, Node, NodeType, OrchestrationGraph


class TraceParser:
    """
    Base class for trace parsers.
    Subclasses implement framework-specific parsing logic.
    """

    def parse(self, trace_data: Dict[str, Any]) -> OrchestrationGraph:
        raise NotImplementedError


class OpenTelemetryParser(TraceParser):
    """
    Parse OpenTelemetry trace format into OrchestrationGraph.

    Expected format: OTLP JSON export
    https://opentelemetry.io/docs/specs/otlp/
    """

    # Mapping of span attributes to node types
    NODE_TYPE_HINTS = {
        "langchain.agent": NodeType.AGENT,
        "langchain.tool": NodeType.TOOL,
        "langchain.llm": NodeType.LLM_CALL,
        "crewai.agent": NodeType.AGENT,
        "crewai.task": NodeType.AGENT,
        "crewai.tool": NodeType.TOOL,
        "autogen.agent": NodeType.AGENT,
        "autogen.function": NodeType.TOOL,
        "openai.chat": NodeType.LLM_CALL,
        "anthropic.messages": NodeType.LLM_CALL,
    }

    def parse(self, trace_data: Dict[str, Any]) -> OrchestrationGraph:
        """Parse OTLP JSON trace into graph."""
        graph = OrchestrationGraph(name="Trace")

        # OTLP structure: resourceSpans -> scopeSpans -> spans
        spans = self._extract_spans(trace_data)

        # Create nodes from spans
        for span in spans:
            node = self._span_to_node(span)
            graph.add_node(node)

        # Create edges from parent-child relationships
        for span in spans:
            parent_id = span.get("parentSpanId")
            if parent_id and parent_id in graph.nodes:
                edge = Edge(
                    source_id=parent_id, target_id=span["spanId"], label=span.get("name", "")
                )
                graph.add_edge(edge)

        return graph

    def _extract_spans(self, trace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract flat list of spans from OTLP structure."""
        spans = []

        # Handle direct spans array (simplified format)
        if "spans" in trace_data:
            return trace_data["spans"]

        # Handle full OTLP structure
        for resource_span in trace_data.get("resourceSpans", []):
            for scope_span in resource_span.get("scopeSpans", []):
                spans.extend(scope_span.get("spans", []))

        return spans

    def _span_to_node(self, span: Dict[str, Any]) -> Node:
        """Convert an OTLP span to a Node."""
        span_id = span.get("spanId", span.get("span_id", ""))
        name = span.get("name", "Unknown")

        # Determine node type from attributes
        node_type = NodeType.UNKNOWN
        attributes = self._parse_attributes(span.get("attributes", []))

        for attr_key, hint_type in self.NODE_TYPE_HINTS.items():
            if attr_key in attributes or attr_key in name.lower():
                node_type = hint_type
                break

        # Parse timestamps (nanoseconds to seconds)
        start_time = None
        end_time = None
        if "startTimeUnixNano" in span:
            start_time = int(span["startTimeUnixNano"]) / 1e9
        if "endTimeUnixNano" in span:
            end_time = int(span["endTimeUnixNano"]) / 1e9

        return Node(
            id=span_id,
            name=name,
            node_type=node_type,
            start_time=start_time,
            end_time=end_time,
            metadata=attributes,
        )

    def _parse_attributes(self, attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OTLP attributes array into dictionary."""
        result = {}
        for attr in attributes:
            key = attr.get("key", "")
            value = attr.get("value", {})
            # OTLP values are typed (stringValue, intValue, etc.)
            if "stringValue" in value:
                result[key] = value["stringValue"]
            elif "intValue" in value:
                result[key] = int(value["intValue"])
            elif "doubleValue" in value:
                result[key] = float(value["doubleValue"])
            elif "boolValue" in value:
                result[key] = value["boolValue"]
            else:
                result[key] = value
        return result


class LangChainParser(TraceParser):
    """
    Parse LangChain-specific trace format (e.g., LangSmith exports).
    """

    def parse(self, trace_data: Dict[str, Any]) -> OrchestrationGraph:
        """Parse LangChain trace into graph."""
        graph = OrchestrationGraph(name=trace_data.get("name", "LangChain Trace"))

        # LangChain traces typically have a "runs" array
        runs = trace_data.get("runs", [trace_data])

        for run in runs:
            self._process_run(run, graph, parent_id=None)

        return graph

    def _process_run(
        self, run: Dict[str, Any], graph: OrchestrationGraph, parent_id: Optional[str]
    ):
        """Recursively process a LangChain run and its children."""
        run_id = run.get("id", run.get("run_id", ""))
        run_type = run.get("run_type", "unknown")
        name = run.get("name", run_type)

        # Map run_type to NodeType
        type_mapping = {
            "chain": NodeType.AGENT,
            "agent": NodeType.AGENT,
            "tool": NodeType.TOOL,
            "llm": NodeType.LLM_CALL,
            "chat_model": NodeType.LLM_CALL,
            "prompt": NodeType.UNKNOWN,
        }
        node_type = type_mapping.get(run_type, NodeType.UNKNOWN)

        # Parse timestamps
        start_time = None
        end_time = None
        if "start_time" in run:
            # Assume ISO format or Unix timestamp
            start_time = self._parse_timestamp(run["start_time"])
        if "end_time" in run:
            end_time = self._parse_timestamp(run["end_time"])

        # Create node
        node = Node(
            id=run_id,
            name=name,
            node_type=node_type,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "inputs": run.get("inputs"),
                "outputs": run.get("outputs"),
                "error": run.get("error"),
            },
        )
        graph.add_node(node)

        # Create edge from parent
        if parent_id:
            edge = Edge(source_id=parent_id, target_id=run_id)
            graph.add_edge(edge)

        # Process children
        for child in run.get("child_runs", []):
            self._process_run(child, graph, parent_id=run_id)

    def _parse_timestamp(self, ts: Any) -> Optional[float]:
        """Parse timestamp to Unix seconds."""
        if isinstance(ts, (int, float)):
            # Assume Unix timestamp
            if ts > 1e10:  # Likely milliseconds
                return ts / 1000
            return ts
        if isinstance(ts, str):
            # Try ISO format
            from datetime import datetime

            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.timestamp()
            except Exception:
                return None
        return None


class CrewAIParser(TraceParser):
    """
    Parse CrewAI-specific trace format.

    CrewAI traces typically contain crew, agents, and tasks.
    """

    def parse(self, trace_data: Dict[str, Any]) -> OrchestrationGraph:
        """Parse CrewAI trace into graph."""
        crew_name = trace_data.get("crew_name", trace_data.get("name", "CrewAI Workflow"))
        graph = OrchestrationGraph(name=crew_name)

        # CrewAI structure: crew -> agents -> tasks
        crew_id = trace_data.get("crew_id", "crew-root")

        # Add crew as root node
        crew_node = Node(
            id=crew_id,
            name=crew_name,
            node_type=NodeType.AGENT,
            start_time=self._parse_timestamp(trace_data.get("start_time")),
            end_time=self._parse_timestamp(trace_data.get("end_time")),
            metadata={"type": "crew"},
        )
        graph.add_node(crew_node)

        # Process agents
        for agent in trace_data.get("agents", []):
            self._process_agent(agent, graph, parent_id=crew_id)

        # Process tasks (connected to crew)
        for task in trace_data.get("tasks", []):
            self._process_task(task, graph, parent_id=crew_id)

        # Process execution trace if available
        for step in trace_data.get("execution_trace", []):
            self._process_step(step, graph, parent_id=crew_id)

        return graph

    def _process_agent(self, agent: Dict[str, Any], graph: OrchestrationGraph, parent_id: str):
        """Process a CrewAI agent."""
        agent_id = agent.get("agent_id", agent.get("id", f"agent-{len(graph.nodes)}"))

        node = Node(
            id=agent_id,
            name=agent.get("role", agent.get("name", "Agent")),
            node_type=NodeType.AGENT,
            start_time=self._parse_timestamp(agent.get("start_time")),
            end_time=self._parse_timestamp(agent.get("end_time")),
            metadata={
                "goal": agent.get("goal"),
                "backstory": agent.get("backstory"),
                "tools": agent.get("tools", []),
            },
        )
        graph.add_node(node)
        graph.add_edge(Edge(source_id=parent_id, target_id=agent_id))

        # Process tool calls within agent
        for tool_call in agent.get("tool_calls", []):
            self._process_tool_call(tool_call, graph, parent_id=agent_id)

    def _process_task(self, task: Dict[str, Any], graph: OrchestrationGraph, parent_id: str):
        """Process a CrewAI task."""
        task_id = task.get("task_id", task.get("id", f"task-{len(graph.nodes)}"))

        node = Node(
            id=task_id,
            name=task.get("description", task.get("name", "Task"))[:50],
            node_type=NodeType.AGENT,
            start_time=self._parse_timestamp(task.get("start_time")),
            end_time=self._parse_timestamp(task.get("end_time")),
            metadata={
                "description": task.get("description"),
                "expected_output": task.get("expected_output"),
                "agent": task.get("agent"),
                "output": task.get("output"),
            },
        )
        graph.add_node(node)
        graph.add_edge(Edge(source_id=parent_id, target_id=task_id))

    def _process_step(self, step: Dict[str, Any], graph: OrchestrationGraph, parent_id: str):
        """Process an execution step."""
        step_id = step.get("step_id", step.get("id", f"step-{len(graph.nodes)}"))
        step_type = step.get("type", "unknown")

        type_mapping = {
            "agent_execution": NodeType.AGENT,
            "tool_call": NodeType.TOOL,
            "llm_call": NodeType.LLM_CALL,
        }

        node = Node(
            id=step_id,
            name=step.get("name", step_type),
            node_type=type_mapping.get(step_type, NodeType.UNKNOWN),
            start_time=self._parse_timestamp(step.get("start_time")),
            end_time=self._parse_timestamp(step.get("end_time")),
            metadata=step.get("metadata", {}),
        )
        graph.add_node(node)

        # Connect to previous step or parent
        prev_id = step.get("parent_id", parent_id)
        graph.add_edge(Edge(source_id=prev_id, target_id=step_id))

    def _process_tool_call(self, tool: Dict[str, Any], graph: OrchestrationGraph, parent_id: str):
        """Process a tool call."""
        tool_id = tool.get("tool_id", tool.get("id", f"tool-{len(graph.nodes)}"))

        node = Node(
            id=tool_id,
            name=tool.get("tool_name", tool.get("name", "Tool")),
            node_type=NodeType.TOOL,
            start_time=self._parse_timestamp(tool.get("start_time")),
            end_time=self._parse_timestamp(tool.get("end_time")),
            metadata={"input": tool.get("input"), "output": tool.get("output")},
        )
        graph.add_node(node)
        graph.add_edge(Edge(source_id=parent_id, target_id=tool_id))

    def _parse_timestamp(self, ts: Any) -> Optional[float]:
        """Parse timestamp to Unix seconds."""
        if ts is None:
            return None
        if isinstance(ts, (int, float)):
            if ts > 1e10:
                return ts / 1000
            return ts
        if isinstance(ts, str):
            from datetime import datetime

            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.timestamp()
            except Exception:
                return None
        return None


class AutoGenParser(TraceParser):
    """
    Parse AutoGen-specific trace format.

    AutoGen traces contain conversations between agents.
    """

    def parse(self, trace_data: Dict[str, Any]) -> OrchestrationGraph:
        """Parse AutoGen trace into graph."""
        graph = OrchestrationGraph(name=trace_data.get("name", "AutoGen Conversation"))

        # AutoGen structure: agents + messages/conversation
        # First, add all agents as nodes
        agent_ids = {}
        for i, agent in enumerate(trace_data.get("agents", [])):
            agent_id = agent.get("agent_id", agent.get("name", f"agent-{i}"))
            agent_ids[agent.get("name", agent_id)] = agent_id

            node = Node(
                id=agent_id,
                name=agent.get("name", "Agent"),
                node_type=NodeType.AGENT,
                metadata={
                    "type": agent.get("type", "agent"),
                    "system_message": agent.get("system_message"),
                },
            )
            graph.add_node(node)

        # Process conversation/messages as edges between agents
        prev_node_id = None
        for i, msg in enumerate(trace_data.get("messages", trace_data.get("conversation", []))):
            msg_id = msg.get("message_id", f"msg-{i}")
            sender = msg.get("sender", msg.get("name", "unknown"))

            # Determine node type based on content
            node_type = NodeType.AGENT
            if msg.get("function_call") or msg.get("tool_calls"):
                node_type = NodeType.TOOL
            elif msg.get("role") == "assistant" and "content" in msg:
                node_type = NodeType.LLM_CALL

            node = Node(
                id=msg_id,
                name=f"{sender}: {str(msg.get('content', ''))[:30]}...",
                node_type=node_type,
                start_time=self._parse_timestamp(msg.get("timestamp")),
                metadata={"sender": sender, "content": msg.get("content"), "role": msg.get("role")},
            )
            graph.add_node(node)

            # Connect to previous message or sender agent
            if prev_node_id:
                graph.add_edge(Edge(source_id=prev_node_id, target_id=msg_id))
            elif sender in agent_ids:
                graph.add_edge(Edge(source_id=agent_ids[sender], target_id=msg_id))

            prev_node_id = msg_id

            # Process function calls
            for fc in msg.get("function_calls", msg.get("tool_calls", [])):
                self._process_function_call(fc, graph, parent_id=msg_id)

        return graph

    def _process_function_call(self, fc: Dict[str, Any], graph: OrchestrationGraph, parent_id: str):
        """Process an AutoGen function call."""
        fc_id = fc.get("id", f"fc-{len(graph.nodes)}")

        node = Node(
            id=fc_id,
            name=fc.get("name", fc.get("function", {}).get("name", "function")),
            node_type=NodeType.TOOL,
            start_time=self._parse_timestamp(fc.get("start_time")),
            end_time=self._parse_timestamp(fc.get("end_time")),
            metadata={
                "arguments": fc.get("arguments", fc.get("function", {}).get("arguments")),
                "result": fc.get("result"),
            },
        )
        graph.add_node(node)
        graph.add_edge(Edge(source_id=parent_id, target_id=fc_id))

    def _parse_timestamp(self, ts: Any) -> Optional[float]:
        """Parse timestamp to Unix seconds."""
        if ts is None:
            return None
        if isinstance(ts, (int, float)):
            if ts > 1e10:
                return ts / 1000
            return ts
        if isinstance(ts, str):
            from datetime import datetime

            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.timestamp()
            except Exception:
                return None
        return None


def parse_trace_file(file_path: str) -> OrchestrationGraph:
    """
    Parse a trace file and auto-detect the format.

    Supported formats:
    - OpenTelemetry (OTLP JSON)
    - LangChain (LangSmith exports)
    - CrewAI (crew execution traces)
    - AutoGen (conversation traces)

    Args:
        file_path: Path to a JSON trace file.

    Returns:
        OrchestrationGraph representation of the trace.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Auto-detect format
    parser: TraceParser
    if "resourceSpans" in data or "spans" in data:
        parser = OpenTelemetryParser()
    elif "runs" in data or "run_type" in data:
        parser = LangChainParser()
    elif "crew_name" in data or "crew_id" in data or ("agents" in data and "tasks" in data):
        parser = CrewAIParser()
    elif "messages" in data or "conversation" in data or ("agents" in data and "messages" in data):
        parser = AutoGenParser()
    else:
        # Default to OpenTelemetry
        parser = OpenTelemetryParser()

    return parser.parse(data)
