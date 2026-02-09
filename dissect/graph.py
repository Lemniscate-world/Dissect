"""
Dissect 2.0 - Orchestration Graph

Internal representation of AI agent workflows.
Nodes represent agents, tools, and LLM calls.
Edges represent data flow and control flow.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    AGENT = "agent"
    TOOL = "tool"
    LLM_CALL = "llm_call"
    USER_INPUT = "user_input"
    OUTPUT = "output"
    UNKNOWN = "unknown"


@dataclass
class Node:
    """A node in the orchestration graph."""

    id: str
    name: str
    node_type: NodeType
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.start_time is not None and self.end_time is not None:
            return (self.end_time - self.start_time) * 1000
        return None


@dataclass
class Edge:
    """An edge connecting two nodes."""

    source_id: str
    target_id: str
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestrationGraph:
    """
    Graph representation of an AI agent orchestration workflow.

    This is the core data structure that Dissect 2.0 operates on.
    Traces from LangChain, CrewAI, AutoGen, etc. are parsed into this format.
    """

    def __init__(self, name: str = "Workflow"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.metadata: Dict[str, Any] = {}

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, node_id: str) -> List[Node]:
        """Get all nodes that this node connects to."""
        child_ids = [e.target_id for e in self.edges if e.source_id == node_id]
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]

    def get_parents(self, node_id: str) -> List[Node]:
        """Get all nodes that connect to this node."""
        parent_ids = [e.source_id for e in self.edges if e.target_id == node_id]
        return [self.nodes[pid] for pid in parent_ids if pid in self.nodes]

    def get_root_nodes(self) -> List[Node]:
        """Get nodes with no incoming edges (entry points)."""
        target_ids = {e.target_id for e in self.edges}
        return [n for n in self.nodes.values() if n.id not in target_ids]

    def get_leaf_nodes(self) -> List[Node]:
        """Get nodes with no outgoing edges (exit points)."""
        source_ids = {e.source_id for e in self.edges}
        return [n for n in self.nodes.values() if n.id not in source_ids]

    def get_critical_path(self) -> List[Node]:
        """
        Get the path with the longest total duration.
        Useful for identifying bottlenecks.
        """

        # Simple DFS to find longest path by duration
        def dfs(node_id: str, visited: set) -> tuple:
            if node_id in visited:
                return (0, [])
            visited.add(node_id)

            node = self.nodes.get(node_id)
            if not node:
                return (0, [])

            node_duration = node.duration_ms or 0
            children = self.get_children(node_id)

            if not children:
                return (node_duration, [node])

            max_child_duration = 0
            max_child_path = []
            for child in children:
                child_duration, child_path = dfs(child.id, visited.copy())
                if child_duration > max_child_duration:
                    max_child_duration = child_duration
                    max_child_path = child_path

            return (node_duration + max_child_duration, [node] + max_child_path)

        roots = self.get_root_nodes()
        if not roots:
            return []

        max_duration = 0
        critical_path = []
        for root in roots:
            duration, path = dfs(root.id, set())
            if duration > max_duration:
                max_duration = duration
                critical_path = path

        return critical_path

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        # Calculate heat scores (0.0 - 1.0) based on duration
        durations = [n.duration_ms for n in self.nodes.values() if n.duration_ms is not None]
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        duration_range = max_duration - min_duration

        nodes_list = []
        for n in self.nodes.values():
            heat_score = 0.0
            if n.duration_ms is not None and duration_range > 0:
                heat_score = (n.duration_ms - min_duration) / duration_range
            elif n.duration_ms is not None and max_duration > 0:
                # If all durations are equal and > 0, treat as max heat? Or min?
                # Usually 0 or 0.5. Let's say 0.
                heat_score = 0.0

            node_dict = {
                "id": n.id,
                "name": n.name,
                "type": n.node_type.value,
                "start_time": n.start_time,
                "end_time": n.end_time,
                "duration_ms": n.duration_ms,
                "heat_score": heat_score,
                "metadata": n.metadata,
            }
            nodes_list.append(node_dict)

        return {
            "name": self.name,
            "nodes": nodes_list,
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "label": e.label,
                    "metadata": e.metadata,
                }
                for e in self.edges
            ],
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize graph to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestrationGraph":
        """Deserialize graph from dictionary."""
        graph = cls(name=data.get("name", "Workflow"))
        graph.metadata = data.get("metadata", {})

        for node_data in data.get("nodes", []):
            node = Node(
                id=node_data["id"],
                name=node_data["name"],
                node_type=NodeType(node_data.get("type", "unknown")),
                start_time=node_data.get("start_time"),
                end_time=node_data.get("end_time"),
                metadata=node_data.get("metadata", {}),
            )
            graph.add_node(node)

        for edge_data in data.get("edges", []):
            edge = Edge(
                source_id=edge_data["source"],
                target_id=edge_data["target"],
                label=edge_data.get("label"),
                metadata=edge_data.get("metadata", {}),
            )
            graph.add_edge(edge)

        return graph
