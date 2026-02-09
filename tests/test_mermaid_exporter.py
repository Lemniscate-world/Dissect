"""
Tests for Mermaid Exporter
"""

import unittest

from dissect.exporters.mermaid import export_mermaid
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


if __name__ == "__main__":
    unittest.main()
