"""
Tests for Mermaid Exporter
"""

import os
import tempfile
import unittest

from dissect.exporters.mermaid import export_mermaid, save_mermaid
from dissect.graph import Edge, Node, NodeType, OrchestrationGraph


class TestMermaidExporter(unittest.TestCase):
    def setUp(self):
        self.graph = OrchestrationGraph(name="Test Graph")
        self.graph.add_node(Node("1", "Agent A", NodeType.AGENT))
        self.graph.add_node(Node("2", "Tool B", NodeType.TOOL))
        self.graph.add_edge(Edge("1", "2"))

    def test_export_mermaid_strings(self):
        """Test that Mermaid export generates correct syntax."""
        mermaid_code = export_mermaid(self.graph)

        self.assertIn("flowchart TD", mermaid_code)
        self.assertIn('1["Agent A"]', mermaid_code)
        self.assertIn('2["Tool B"]', mermaid_code)
        self.assertIn("1 --> 2", mermaid_code)
        self.assertIn("classDef agent", mermaid_code)  # Styling check

    def test_export_mermaid_with_duration(self):
        """Test that nodes with durations include duration in label."""
        graph = OrchestrationGraph(name="Duration Test")
        graph.add_node(Node("1", "Slow Agent", NodeType.AGENT, start_time=0, end_time=0.5))
        mermaid_code = export_mermaid(graph)
        self.assertIn("500ms", mermaid_code)

    def test_export_mermaid_with_edge_label(self):
        """Test that edges with labels render correctly."""
        graph = OrchestrationGraph(name="Label Test")
        graph.add_node(Node("a", "A", NodeType.AGENT))
        graph.add_node(Node("b", "B", NodeType.TOOL))
        graph.add_edge(Edge("a", "b", label="calls"))
        mermaid_code = export_mermaid(graph)
        self.assertIn("a -->|calls| b", mermaid_code)

    def test_save_mermaid(self):
        """Test save_mermaid writes file correctly."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = f.name

        try:
            save_mermaid(self.graph, output_path)
            with open(output_path, "r") as f:
                content = f.read()
            self.assertIn("flowchart TD", content)
            self.assertIn("Agent A", content)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


if __name__ == "__main__":
    unittest.main()
