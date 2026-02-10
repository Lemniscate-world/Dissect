"""
Dissect 2.0 - Trace Diff

Compare two OrchestrationGraphs and report differences:
- Added/removed nodes
- Duration regressions/improvements
- Structural changes (edge differences)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .graph import Node, OrchestrationGraph


@dataclass
class NodeDiff:
    """Difference for a single node between two traces."""

    node_id: str
    name: str
    status: str  # "added", "removed", "changed", "unchanged"
    old_duration_ms: Optional[float] = None
    new_duration_ms: Optional[float] = None
    duration_change_ms: Optional[float] = None
    duration_change_pct: Optional[float] = None

    @property
    def is_regression(self) -> bool:
        """True if duration increased (got slower)."""
        return self.duration_change_ms is not None and self.duration_change_ms > 0

    @property
    def is_improvement(self) -> bool:
        """True if duration decreased (got faster)."""
        return self.duration_change_ms is not None and self.duration_change_ms < 0


@dataclass
class EdgeDiff:
    """Difference for edges between two traces."""

    source: str
    target: str
    status: str  # "added", "removed"
    label: Optional[str] = None


@dataclass
class TraceDiff:
    """Complete diff between two traces."""

    old_name: str
    new_name: str
    node_diffs: List[NodeDiff] = field(default_factory=list)
    edge_diffs: List[EdgeDiff] = field(default_factory=list)

    @property
    def added_nodes(self) -> List[NodeDiff]:
        return [d for d in self.node_diffs if d.status == "added"]

    @property
    def removed_nodes(self) -> List[NodeDiff]:
        return [d for d in self.node_diffs if d.status == "removed"]

    @property
    def changed_nodes(self) -> List[NodeDiff]:
        return [d for d in self.node_diffs if d.status == "changed"]

    @property
    def regressions(self) -> List[NodeDiff]:
        return [d for d in self.node_diffs if d.is_regression]

    @property
    def improvements(self) -> List[NodeDiff]:
        return [d for d in self.node_diffs if d.is_improvement]

    @property
    def added_edges(self) -> List[EdgeDiff]:
        return [d for d in self.edge_diffs if d.status == "added"]

    @property
    def removed_edges(self) -> List[EdgeDiff]:
        return [d for d in self.edge_diffs if d.status == "removed"]

    @property
    def has_changes(self) -> bool:
        return len(self.added_nodes) > 0 or len(self.removed_nodes) > 0 or \
               len(self.changed_nodes) > 0 or len(self.edge_diffs) > 0


def diff_graphs(old: OrchestrationGraph, new: OrchestrationGraph) -> TraceDiff:
    """
    Compare two OrchestrationGraphs and return their differences.

    Nodes are matched by name (not ID, since IDs may differ between runs).
    """
    result = TraceDiff(old_name=old.name, new_name=new.name)

    # Build name-to-node maps
    old_by_name: Dict[str, Node] = {n.name: n for n in old.nodes.values()}
    new_by_name: Dict[str, Node] = {n.name: n for n in new.nodes.values()}

    all_names = set(old_by_name.keys()) | set(new_by_name.keys())

    for name in sorted(all_names):
        old_node = old_by_name.get(name)
        new_node = new_by_name.get(name)

        if old_node and not new_node:
            result.node_diffs.append(NodeDiff(
                node_id=old_node.id, name=name, status="removed",
                old_duration_ms=old_node.duration_ms,
            ))
        elif new_node and not old_node:
            result.node_diffs.append(NodeDiff(
                node_id=new_node.id, name=name, status="added",
                new_duration_ms=new_node.duration_ms,
            ))
        else:
            # Both exist — compare durations
            old_dur = old_node.duration_ms
            new_dur = new_node.duration_ms
            change_ms = None
            change_pct = None

            if old_dur is not None and new_dur is not None:
                change_ms = new_dur - old_dur
                if old_dur > 0:
                    change_pct = (change_ms / old_dur) * 100

            status = "changed" if change_ms and abs(change_ms) > 0.01 else "unchanged"
            result.node_diffs.append(NodeDiff(
                node_id=new_node.id, name=name, status=status,
                old_duration_ms=old_dur, new_duration_ms=new_dur,
                duration_change_ms=change_ms, duration_change_pct=change_pct,
            ))

    # Compare edges by (source_name, target_name) pairs
    def edge_key(graph: OrchestrationGraph, edge) -> Optional[Tuple[str, str]]:
        src = graph.nodes.get(edge.source_id)
        tgt = graph.nodes.get(edge.target_id)
        if src and tgt:
            return (src.name, tgt.name)
        return None

    old_edges = {edge_key(old, e) for e in old.edges if edge_key(old, e)}
    new_edges = {edge_key(new, e) for e in new.edges if edge_key(new, e)}

    for src, tgt in sorted(new_edges - old_edges):
        result.edge_diffs.append(EdgeDiff(source=src, target=tgt, status="added"))
    for src, tgt in sorted(old_edges - new_edges):
        result.edge_diffs.append(EdgeDiff(source=src, target=tgt, status="removed"))

    return result


def format_diff(diff: TraceDiff) -> str:
    """Format a TraceDiff as a human-readable string."""
    lines = []
    lines.append(f"Comparing: {diff.old_name} → {diff.new_name}")
    lines.append("")

    if not diff.has_changes:
        lines.append("✓ No differences found.")
        return "\n".join(lines)

    # Summary
    lines.append(f"  Nodes: +{len(diff.added_nodes)} added, "
                 f"-{len(diff.removed_nodes)} removed, "
                 f"~{len(diff.changed_nodes)} changed")
    lines.append(f"  Edges: +{len(diff.added_edges)} added, "
                 f"-{len(diff.removed_edges)} removed")
    lines.append("")

    # Regressions (most important)
    if diff.regressions:
        lines.append("⚠ Duration Regressions:")
        for d in diff.regressions:
            pct = f" ({d.duration_change_pct:+.1f}%)" if d.duration_change_pct else ""
            lines.append(f"  ↑ {d.name}: {d.old_duration_ms:.0f}ms → "
                         f"{d.new_duration_ms:.0f}ms ({d.duration_change_ms:+.0f}ms{pct})")
        lines.append("")

    # Improvements
    if diff.improvements:
        lines.append("✓ Duration Improvements:")
        for d in diff.improvements:
            pct = f" ({d.duration_change_pct:+.1f}%)" if d.duration_change_pct else ""
            lines.append(f"  ↓ {d.name}: {d.old_duration_ms:.0f}ms → "
                         f"{d.new_duration_ms:.0f}ms ({d.duration_change_ms:+.0f}ms{pct})")
        lines.append("")

    # Added nodes
    if diff.added_nodes:
        lines.append("+ Added Nodes:")
        for d in diff.added_nodes:
            dur = f" ({d.new_duration_ms:.0f}ms)" if d.new_duration_ms else ""
            lines.append(f"  + {d.name}{dur}")
        lines.append("")

    # Removed nodes
    if diff.removed_nodes:
        lines.append("- Removed Nodes:")
        for d in diff.removed_nodes:
            dur = f" ({d.old_duration_ms:.0f}ms)" if d.old_duration_ms else ""
            lines.append(f"  - {d.name}{dur}")
        lines.append("")

    # Edge changes
    if diff.edge_diffs:
        lines.append("Edge Changes:")
        for e in diff.edge_diffs:
            symbol = "+" if e.status == "added" else "-"
            lines.append(f"  {symbol} {e.source} → {e.target}")

    return "\n".join(lines)

