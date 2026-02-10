"""
Tests for DOT Exporter
"""

import os
import tempfile
import unittest

from dissect.exporters.dot import export_dot, save_dot
from dissect.graph import Edge, Node, NodeType, OrchestrationGraph


class TestDotExporter(unittest.TestCase):
    def setUp(self):
        self.graph = OrchestrationGraph(name="Test Graph")
        self.graph.add_node(Node("1", "Agent A", NodeType.AGENT))
        self.graph.add_node(Node("2", "Tool B", NodeType.TOOL))
        self.graph.add_edge(Edge("1", "2"))

    def test_export_dot_basic_structure(self):
        """Test DOT output has correct digraph structure."""
        dot = export_dot(self.graph)
        self.assertIn('digraph "Test Graph"', dot)
        self.assertIn("rankdir=TB", dot)
        self.assertTrue(dot.strip().endswith("}"))

    def test_export_dot_nodes(self):
        """Test all nodes appear in DOT output."""
        dot = export_dot(self.graph)
        self.assertIn('"1"', dot)
        self.assertIn('"2"', dot)
        self.assertIn("Agent A", dot)
        self.assertIn("Tool B", dot)

    def test_export_dot_edges(self):
        """Test edges appear in DOT output."""
        dot = export_dot(self.graph)
        self.assertIn('"1" -> "2"', dot)

    def test_export_dot_node_colors(self):
        """Test each node type gets the correct fill color."""
        graph = OrchestrationGraph(name="Color Test")
        graph.add_node(Node("a", "Agent", NodeType.AGENT))
        graph.add_node(Node("t", "Tool", NodeType.TOOL))
        graph.add_node(Node("l", "LLM", NodeType.LLM_CALL))
        graph.add_node(Node("i", "Input", NodeType.USER_INPUT))
        graph.add_node(Node("o", "Output", NodeType.OUTPUT))
        graph.add_node(Node("u", "Unknown", NodeType.UNKNOWN))

        dot = export_dot(graph)
        self.assertIn('#E3F2FD', dot)  # AGENT
        self.assertIn('#FFF3E0', dot)  # TOOL
        self.assertIn('#F3E5F5', dot)  # LLM_CALL
        self.assertIn('#E8F5E9', dot)  # USER_INPUT
        self.assertIn('#FFEBEE', dot)  # OUTPUT
        self.assertIn('#F5F5F5', dot)  # UNKNOWN

    def test_export_dot_with_duration(self):
        """Test nodes with durations include duration in label."""
        graph = OrchestrationGraph(name="Duration Test")
        graph.add_node(Node("1", "Slow Agent", NodeType.AGENT, start_time=0, end_time=0.5))
        dot = export_dot(graph)
        self.assertIn("500ms", dot)

    def test_export_dot_without_duration(self):
        """Test nodes without durations don't show duration."""
        graph = OrchestrationGraph(name="No Duration")
        graph.add_node(Node("1", "Fast Agent", NodeType.AGENT))
        dot = export_dot(graph)
        self.assertIn("Fast Agent", dot)
        self.assertNotIn("ms", dot)

    def test_export_dot_edge_with_label(self):
        """Test edges with labels render correctly."""
        graph = OrchestrationGraph(name="Label Test")
        graph.add_node(Node("a", "A", NodeType.AGENT))
        graph.add_node(Node("b", "B", NodeType.TOOL))
        graph.add_edge(Edge("a", "b", label="calls"))
        dot = export_dot(graph)
        self.assertIn('[label="calls"]', dot)

    def test_export_dot_edge_without_label(self):
        """Test edges without labels render as plain arrows."""
        dot = export_dot(self.graph)
        self.assertIn('"1" -> "2";', dot)
        # Should NOT have a label attribute on this edge
        lines = dot.split("\n")
        edge_lines = [l for l in lines if '"1" -> "2"' in l]
        self.assertEqual(len(edge_lines), 1)
        self.assertNotIn("label", edge_lines[0])

    def test_save_dot(self):
        """Test save_dot writes file correctly."""
        with tempfile.NamedTemporaryFile(suffix=".dot", delete=False) as f:
            output_path = f.name

        try:
            save_dot(self.graph, output_path)
            with open(output_path, "r") as f:
                content = f.read()
            self.assertIn('digraph "Test Graph"', content)
            self.assertIn("Agent A", content)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_export_dot_empty_graph(self):
        """Test DOT export with empty graph."""
        graph = OrchestrationGraph(name="Empty")
        dot = export_dot(graph)
        self.assertIn('digraph "Empty"', dot)
        self.assertTrue(dot.strip().endswith("}"))


if __name__ == "__main__":
    unittest.main()

