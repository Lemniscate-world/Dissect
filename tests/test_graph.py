"""
Tests for Dissect 2.0 - Orchestration Graph
"""

import unittest

from dissect.graph import Edge, Node, NodeType, OrchestrationGraph


class TestOrchestrationGraph(unittest.TestCase):
    def test_add_node(self):
        graph = OrchestrationGraph()
        node = Node(id="1", name="Test Agent", node_type=NodeType.AGENT)
        graph.add_node(node)

        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.nodes["1"].name, "Test Agent")

    def test_add_edge(self):
        graph = OrchestrationGraph()
        node1 = Node(id="1", name="Agent A", node_type=NodeType.AGENT)
        node2 = Node(id="2", name="Agent B", node_type=NodeType.AGENT)
        graph.add_node(node1)
        graph.add_node(node2)

        edge = Edge(source_id="1", target_id="2", label="handoff")
        graph.add_edge(edge)

        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.edges[0].label, "handoff")

    def test_critical_path(self):
        graph = OrchestrationGraph()
        # A -> B -> C (10ms + 20ms + 30ms = 60ms)
        # A -> D (10ms + 5ms = 15ms)

        node_a = Node(id="A", name="A", node_type=NodeType.AGENT, start_time=0, end_time=0.01)
        node_b = Node(id="B", name="B", node_type=NodeType.AGENT, start_time=0.01, end_time=0.03)
        node_c = Node(id="C", name="C", node_type=NodeType.AGENT, start_time=0.03, end_time=0.06)
        node_d = Node(id="D", name="D", node_type=NodeType.AGENT, start_time=0.01, end_time=0.015)

        for n in [node_a, node_b, node_c, node_d]:
            graph.add_node(n)

        graph.add_edge(Edge("A", "B"))
        graph.add_edge(Edge("B", "C"))
        graph.add_edge(Edge("A", "D"))

        critical_path = graph.get_critical_path()
        self.assertEqual(len(critical_path), 3)
        self.assertEqual([n.id for n in critical_path], ["A", "B", "C"])

    def test_heat_score_calculation(self):
        graph = OrchestrationGraph()
        # Node A: 10ms (Min) -> 0.0
        # Node B: 50ms (Mid) -> 0.5
        # Node C: 90ms (Max) -> 1.0

        node_a = Node(id="A", name="A", node_type=NodeType.AGENT, start_time=0, end_time=0.01)
        node_b = Node(id="B", name="B", node_type=NodeType.AGENT, start_time=0, end_time=0.05)
        node_c = Node(id="C", name="C", node_type=NodeType.AGENT, start_time=0, end_time=0.09)

        for n in [node_a, node_b, node_c]:
            graph.add_node(n)

        data = graph.to_dict()
        nodes = {n["id"]: n for n in data["nodes"]}

        self.assertAlmostEqual(nodes["A"]["heat_score"], 0.0)
        self.assertAlmostEqual(nodes["B"]["heat_score"], 0.5)
        self.assertAlmostEqual(nodes["C"]["heat_score"], 1.0)

    def test_get_node(self):
        """Test get_node returns correct node or None."""
        graph = OrchestrationGraph()
        node = Node(id="1", name="Agent", node_type=NodeType.AGENT)
        graph.add_node(node)

        self.assertEqual(graph.get_node("1"), node)
        self.assertIsNone(graph.get_node("nonexistent"))

    def test_get_children(self):
        """Test get_children returns correct child nodes."""
        graph = OrchestrationGraph()
        parent = Node(id="p", name="Parent", node_type=NodeType.AGENT)
        child1 = Node(id="c1", name="Child 1", node_type=NodeType.TOOL)
        child2 = Node(id="c2", name="Child 2", node_type=NodeType.TOOL)
        for n in [parent, child1, child2]:
            graph.add_node(n)
        graph.add_edge(Edge("p", "c1"))
        graph.add_edge(Edge("p", "c2"))

        children = graph.get_children("p")
        self.assertEqual(len(children), 2)
        self.assertEqual({c.id for c in children}, {"c1", "c2"})

    def test_get_parents(self):
        """Test get_parents returns correct parent nodes."""
        graph = OrchestrationGraph()
        p1 = Node(id="p1", name="Parent 1", node_type=NodeType.AGENT)
        p2 = Node(id="p2", name="Parent 2", node_type=NodeType.AGENT)
        child = Node(id="c", name="Child", node_type=NodeType.TOOL)
        for n in [p1, p2, child]:
            graph.add_node(n)
        graph.add_edge(Edge("p1", "c"))
        graph.add_edge(Edge("p2", "c"))

        parents = graph.get_parents("c")
        self.assertEqual(len(parents), 2)
        self.assertEqual({p.id for p in parents}, {"p1", "p2"})

    def test_get_root_nodes(self):
        """Test get_root_nodes returns nodes with no incoming edges."""
        graph = OrchestrationGraph()
        root = Node(id="r", name="Root", node_type=NodeType.AGENT)
        child = Node(id="c", name="Child", node_type=NodeType.TOOL)
        graph.add_node(root)
        graph.add_node(child)
        graph.add_edge(Edge("r", "c"))

        roots = graph.get_root_nodes()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].id, "r")

    def test_get_leaf_nodes(self):
        """Test get_leaf_nodes returns nodes with no outgoing edges."""
        graph = OrchestrationGraph()
        root = Node(id="r", name="Root", node_type=NodeType.AGENT)
        leaf = Node(id="l", name="Leaf", node_type=NodeType.OUTPUT)
        graph.add_node(root)
        graph.add_node(leaf)
        graph.add_edge(Edge("r", "l"))

        leaves = graph.get_leaf_nodes()
        self.assertEqual(len(leaves), 1)
        self.assertEqual(leaves[0].id, "l")

    def test_critical_path_empty_graph(self):
        """Test critical path on empty graph returns empty list."""
        graph = OrchestrationGraph()
        self.assertEqual(graph.get_critical_path(), [])

    def test_critical_path_single_node(self):
        """Test critical path with single node."""
        graph = OrchestrationGraph()
        node = Node(id="1", name="Solo", node_type=NodeType.AGENT, start_time=0, end_time=0.1)
        graph.add_node(node)

        path = graph.get_critical_path()
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0].id, "1")

    def test_to_dict_and_from_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        graph = OrchestrationGraph(name="Roundtrip Test")
        graph.add_node(Node("a", "Agent A", NodeType.AGENT, start_time=0, end_time=0.1))
        graph.add_node(Node("b", "Tool B", NodeType.TOOL, start_time=0.1, end_time=0.3))
        graph.add_edge(Edge("a", "b", label="calls"))
        graph.metadata = {"version": "2.0"}

        data = graph.to_dict()
        restored = OrchestrationGraph.from_dict(data)

        self.assertEqual(restored.name, "Roundtrip Test")
        self.assertEqual(len(restored.nodes), 2)
        self.assertEqual(len(restored.edges), 1)
        self.assertEqual(restored.nodes["a"].name, "Agent A")
        self.assertEqual(restored.nodes["b"].node_type, NodeType.TOOL)
        self.assertEqual(restored.edges[0].label, "calls")
        self.assertEqual(restored.metadata, {"version": "2.0"})

    def test_to_json(self):
        """Test JSON serialization."""
        graph = OrchestrationGraph(name="JSON Test")
        graph.add_node(Node("1", "Agent", NodeType.AGENT))

        json_str = graph.to_json()
        self.assertIn('"JSON Test"', json_str)
        self.assertIn('"Agent"', json_str)

    def test_node_duration_ms(self):
        """Test Node.duration_ms property."""
        node_with = Node("1", "A", NodeType.AGENT, start_time=1.0, end_time=1.5)
        assert node_with.duration_ms is not None
        self.assertAlmostEqual(node_with.duration_ms, 500.0)

        node_without = Node("2", "B", NodeType.AGENT)
        self.assertIsNone(node_without.duration_ms)

        node_partial = Node("3", "C", NodeType.AGENT, start_time=1.0)
        self.assertIsNone(node_partial.duration_ms)

    def test_heat_score_no_durations(self):
        """Test heat score when no nodes have durations."""
        graph = OrchestrationGraph()
        graph.add_node(Node("1", "A", NodeType.AGENT))
        graph.add_node(Node("2", "B", NodeType.AGENT))

        data = graph.to_dict()
        for n in data["nodes"]:
            self.assertEqual(n["heat_score"], 0.0)

    def test_heat_score_equal_durations(self):
        """Test heat score when all durations are equal."""
        graph = OrchestrationGraph()
        graph.add_node(Node("1", "A", NodeType.AGENT, start_time=0, end_time=0.1))
        graph.add_node(Node("2", "B", NodeType.AGENT, start_time=0, end_time=0.1))

        data = graph.to_dict()
        for n in data["nodes"]:
            self.assertEqual(n["heat_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
