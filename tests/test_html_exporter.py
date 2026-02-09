"""
Tests for HTML Exporter
"""

import unittest
import os
import tempfile
from dissect.graph import OrchestrationGraph, Node, NodeType, Edge
from dissect.exporters.html import save_html


class TestHTMLExporter(unittest.TestCase):
    
    def setUp(self):
        self.graph = OrchestrationGraph(name="Test Graph")
        self.graph.add_node(Node("1", "Agent A", NodeType.AGENT))
        self.graph.add_node(Node("2", "Tool B", NodeType.TOOL))
        self.graph.add_edge(Edge("1", "2"))
        
    def test_save_html_content(self):
        """Test that HTML export contains critical data."""
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name
            
        try:
            save_html(self.graph, output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                
            # Verify core components exist
            self.assertIn("Test Graph", content)
            self.assertIn("Agent A", content)
            self.assertIn("Tool B", content)
            self.assertIn("Dissect", content)
            self.assertIn("graphData", content)
            
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
