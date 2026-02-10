"""
Dissect 2.0 - Trace Diff

Compare two OrchestrationGraphs and report differences:
- Added/removed nodes
- Duration regressions/improvements
- Structural changes (edge differences)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

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
        return (
            len(self.added_nodes) > 0
            or len(self.removed_nodes) > 0
            or len(self.changed_nodes) > 0
            or len(self.edge_diffs) > 0
        )


def _collect_edge_keys(graph: OrchestrationGraph) -> Set[Tuple[str, str]]:
    """Collect (source_name, target_name) pairs for all edges in a graph."""
    keys: Set[Tuple[str, str]] = set()
    for edge in graph.edges:
        src = graph.nodes.get(edge.source_id)
        tgt = graph.nodes.get(edge.target_id)
        if src and tgt:
            keys.add((src.name, tgt.name))
    return keys


def _compare_node_durations(name: str, old_node: Node, new_node: Node) -> NodeDiff:
    """Compare durations of two nodes that exist in both traces."""
    old_dur = old_node.duration_ms
    new_dur = new_node.duration_ms
    change_ms = None
    change_pct = None

    if old_dur is not None and new_dur is not None:
        change_ms = new_dur - old_dur
        if old_dur > 0:
            change_pct = (change_ms / old_dur) * 100

    status = "changed" if change_ms and abs(change_ms) > 0.01 else "unchanged"
    return NodeDiff(
        node_id=new_node.id,
        name=name,
        status=status,
        old_duration_ms=old_dur,
        new_duration_ms=new_dur,
        duration_change_ms=change_ms,
        duration_change_pct=change_pct,
    )


def diff_graphs(old: OrchestrationGraph, new: OrchestrationGraph) -> TraceDiff:
    """
    Compare two OrchestrationGraphs and return their differences.

    Nodes are matched by name (not ID, since IDs may differ between runs).
    """
    result = TraceDiff(old_name=old.name, new_name=new.name)

    old_by_name: Dict[str, Node] = {n.name: n for n in old.nodes.values()}
    new_by_name: Dict[str, Node] = {n.name: n for n in new.nodes.values()}

    for name in sorted(set(old_by_name) | set(new_by_name)):
        old_node = old_by_name.get(name)
        new_node = new_by_name.get(name)

        if old_node and not new_node:
            result.node_diffs.append(
                NodeDiff(
                    node_id=old_node.id,
                    name=name,
                    status="removed",
                    old_duration_ms=old_node.duration_ms,
                )
            )
        elif new_node and not old_node:
            result.node_diffs.append(
                NodeDiff(
                    node_id=new_node.id,
                    name=name,
                    status="added",
                    new_duration_ms=new_node.duration_ms,
                )
            )
        else:
            assert old_node is not None
            assert new_node is not None
            result.node_diffs.append(_compare_node_durations(name, old_node, new_node))

    old_edges = _collect_edge_keys(old)
    new_edges = _collect_edge_keys(new)

    for src, tgt in sorted(new_edges - old_edges):
        result.edge_diffs.append(EdgeDiff(source=src, target=tgt, status="added"))
    for src, tgt in sorted(old_edges - new_edges):
        result.edge_diffs.append(EdgeDiff(source=src, target=tgt, status="removed"))

    return result


def _format_duration_section(title: str, nodes: List[NodeDiff], arrow: str) -> List[str]:
    """Format a duration regressions or improvements section."""
    lines = [title]
    for d in nodes:
        pct = f" ({d.duration_change_pct:+.1f}%)" if d.duration_change_pct else ""
        lines.append(
            f"  {arrow} {d.name}: {d.old_duration_ms:.0f}ms → "
            f"{d.new_duration_ms:.0f}ms ({d.duration_change_ms:+.0f}ms{pct})"
        )
    lines.append("")
    return lines


def _format_node_list(
    title: str, nodes: List[NodeDiff], symbol: str, duration_attr: str
) -> List[str]:
    """Format a list of added or removed nodes."""
    lines = [title]
    for d in nodes:
        dur_val = getattr(d, duration_attr)
        dur = f" ({dur_val:.0f}ms)" if dur_val else ""
        lines.append(f"  {symbol} {d.name}{dur}")
    lines.append("")
    return lines


def format_diff(diff: TraceDiff) -> str:
    """Format a TraceDiff as a human-readable string."""
    lines = [f"Comparing: {diff.old_name} → {diff.new_name}", ""]

    if not diff.has_changes:
        lines.append("✓ No differences found.")
        return "\n".join(lines)

    # Summary
    lines.append(
        f"  Nodes: +{len(diff.added_nodes)} added, "
        f"-{len(diff.removed_nodes)} removed, "
        f"~{len(diff.changed_nodes)} changed"
    )
    lines.append(f"  Edges: +{len(diff.added_edges)} added, " f"-{len(diff.removed_edges)} removed")
    lines.append("")

    if diff.regressions:
        lines.extend(_format_duration_section("⚠ Duration Regressions:", diff.regressions, "↑"))

    if diff.improvements:
        lines.extend(_format_duration_section("✓ Duration Improvements:", diff.improvements, "↓"))

    if diff.added_nodes:
        lines.extend(_format_node_list("+ Added Nodes:", diff.added_nodes, "+", "new_duration_ms"))

    if diff.removed_nodes:
        lines.extend(
            _format_node_list("- Removed Nodes:", diff.removed_nodes, "-", "old_duration_ms")
        )

    if diff.edge_diffs:
        lines.append("Edge Changes:")
        for e in diff.edge_diffs:
            symbol = "+" if e.status == "added" else "-"
            lines.append(f"  {symbol} {e.source} → {e.target}")

    return "\n".join(lines)
