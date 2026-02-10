"""
Tests for dissect.diff — trace comparison logic.
"""

import unittest

from dissect.diff import EdgeDiff, NodeDiff, TraceDiff, diff_graphs, format_diff
from dissect.graph import Edge, Node, NodeType, OrchestrationGraph


def _make_graph(name, nodes, edges=None):
    """Helper to build a graph quickly."""
    g = OrchestrationGraph(name=name)
    for n in nodes:
        g.add_node(n)
    for e in edges or []:
        g.add_edge(e)
    return g


def _node(id, name, start=None, end=None, ntype=NodeType.AGENT):
    return Node(id=id, name=name, node_type=ntype, start_time=start, end_time=end)


class TestDiffGraphs(unittest.TestCase):
    def test_identical_graphs(self):
        """Two identical graphs should produce no changes."""
        nodes = [_node("1", "Agent A", 0, 1), _node("2", "Agent B", 1, 2)]
        edges = [Edge(source_id="1", target_id="2")]
        old = _make_graph("Workflow", nodes, edges)
        new = _make_graph("Workflow", nodes, edges)

        result = diff_graphs(old, new)
        self.assertFalse(result.has_changes)
        self.assertEqual(len(result.added_nodes), 0)
        self.assertEqual(len(result.removed_nodes), 0)
        self.assertEqual(len(result.edge_diffs), 0)

    def test_added_node(self):
        """New graph has an extra node."""
        old = _make_graph("W", [_node("1", "Agent A")])
        new = _make_graph("W", [_node("1", "Agent A"), _node("2", "Agent B")])

        result = diff_graphs(old, new)
        self.assertTrue(result.has_changes)
        self.assertEqual(len(result.added_nodes), 1)
        self.assertEqual(result.added_nodes[0].name, "Agent B")

    def test_removed_node(self):
        """New graph is missing a node."""
        old = _make_graph("W", [_node("1", "Agent A"), _node("2", "Agent B")])
        new = _make_graph("W", [_node("1", "Agent A")])

        result = diff_graphs(old, new)
        self.assertTrue(result.has_changes)
        self.assertEqual(len(result.removed_nodes), 1)
        self.assertEqual(result.removed_nodes[0].name, "Agent B")

    def test_duration_regression(self):
        """Node got slower between runs."""
        old = _make_graph("W", [_node("1", "Agent A", 0, 1)])
        new = _make_graph("W", [_node("1", "Agent A", 0, 3)])

        result = diff_graphs(old, new)
        self.assertTrue(result.has_changes)
        regs = result.regressions
        self.assertEqual(len(regs), 1)
        self.assertEqual(regs[0].name, "Agent A")
        assert regs[0].duration_change_ms is not None
        assert regs[0].duration_change_pct is not None
        self.assertAlmostEqual(regs[0].duration_change_ms, 2000.0)
        self.assertAlmostEqual(regs[0].duration_change_pct, 200.0)

    def test_duration_improvement(self):
        """Node got faster between runs."""
        old = _make_graph("W", [_node("1", "Agent A", 0, 4)])
        new = _make_graph("W", [_node("1", "Agent A", 0, 2)])

        result = diff_graphs(old, new)
        imps = result.improvements
        self.assertEqual(len(imps), 1)
        assert imps[0].duration_change_ms is not None
        self.assertTrue(imps[0].duration_change_ms < 0)

    def test_edge_added(self):
        """New graph has an extra edge."""
        n1, n2 = _node("1", "A"), _node("2", "B")
        old = _make_graph("W", [n1, n2], [])
        new = _make_graph("W", [n1, n2], [Edge(source_id="1", target_id="2")])

        result = diff_graphs(old, new)
        self.assertEqual(len(result.added_edges), 1)
        self.assertEqual(result.added_edges[0].source, "A")
        self.assertEqual(result.added_edges[0].target, "B")

    def test_edge_removed(self):
        """New graph is missing an edge."""
        n1, n2 = _node("1", "A"), _node("2", "B")
        old = _make_graph("W", [n1, n2], [Edge(source_id="1", target_id="2")])
        new = _make_graph("W", [n1, n2], [])

        result = diff_graphs(old, new)
        self.assertEqual(len(result.removed_edges), 1)

    def test_unchanged_node_no_duration(self):
        """Nodes without durations should be 'unchanged'."""
        old = _make_graph("W", [_node("1", "Agent A")])
        new = _make_graph("W", [_node("x", "Agent A")])  # different ID, same name

        result = diff_graphs(old, new)
        self.assertFalse(result.has_changes)
        self.assertEqual(len(result.changed_nodes), 0)

    def test_node_matched_by_name_not_id(self):
        """Nodes should be matched by name, not ID."""
        old = _make_graph("W", [_node("old-id", "Agent A", 0, 1)])
        new = _make_graph("W", [_node("new-id", "Agent A", 0, 1)])

        result = diff_graphs(old, new)
        self.assertFalse(result.has_changes)


class TestFormatDiff(unittest.TestCase):
    def test_no_changes(self):
        diff = TraceDiff(old_name="A", new_name="B")
        output = format_diff(diff)
        self.assertIn("No differences found", output)

    def test_regression_output(self):
        diff = TraceDiff(
            old_name="A",
            new_name="B",
            node_diffs=[
                NodeDiff(
                    node_id="1",
                    name="Slow Agent",
                    status="changed",
                    old_duration_ms=1000,
                    new_duration_ms=2000,
                    duration_change_ms=1000,
                    duration_change_pct=100.0,
                ),
            ],
        )
        output = format_diff(diff)
        self.assertIn("Regressions", output)
        self.assertIn("Slow Agent", output)
        self.assertIn("+1000ms", output)

    def test_added_removed_output(self):
        diff = TraceDiff(
            old_name="A",
            new_name="B",
            node_diffs=[
                NodeDiff(node_id="1", name="New Agent", status="added", new_duration_ms=500),
                NodeDiff(node_id="2", name="Old Agent", status="removed", old_duration_ms=300),
            ],
        )
        output = format_diff(diff)
        self.assertIn("Added Nodes", output)
        self.assertIn("Removed Nodes", output)
        self.assertIn("New Agent", output)
        self.assertIn("Old Agent", output)

    def test_edge_changes_output(self):
        diff = TraceDiff(
            old_name="A",
            new_name="B",
            edge_diffs=[
                EdgeDiff(source="X", target="Y", status="added"),
                EdgeDiff(source="Y", target="Z", status="removed"),
            ],
        )
        output = format_diff(diff)
        self.assertIn("Edge Changes", output)
        self.assertIn("+ X", output)
        self.assertIn("- Y", output)


if __name__ == "__main__":
    unittest.main()
