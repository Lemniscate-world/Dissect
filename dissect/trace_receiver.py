"""
Dissect 2.0 - Trace Receiver

Parses OpenTelemetry traces and framework-specific trace formats
into OrchestrationGraph structures.
"""

from typing import Dict, List, Any, Optional
from .graph import OrchestrationGraph, Node, Edge, NodeType
import json


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
                    source_id=parent_id,
                    target_id=span["spanId"],
                    label=span.get("name", "")
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
            metadata=attributes
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
    
    def _process_run(self, run: Dict[str, Any], graph: OrchestrationGraph, parent_id: Optional[str]):
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
                "error": run.get("error")
            }
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
            except:
                return None
        return None


def parse_trace_file(file_path: str) -> OrchestrationGraph:
    """
    Parse a trace file and auto-detect the format.
    
    Args:
        file_path: Path to a JSON trace file.
    
    Returns:
        OrchestrationGraph representation of the trace.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    
    # Auto-detect format
    if "resourceSpans" in data or "spans" in data:
        parser = OpenTelemetryParser()
    elif "runs" in data or "run_type" in data:
        parser = LangChainParser()
    else:
        # Default to OpenTelemetry
        parser = OpenTelemetryParser()
    
    return parser.parse(data)
