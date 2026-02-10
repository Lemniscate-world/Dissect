"""
Automated UI Tests for Dissect Next-Gen Visualization
"""

import os
import unittest

from dissect.exporters.html import save_html
from dissect.graph import Edge, Node, NodeType, OrchestrationGraph


class TestUIVisualization(unittest.TestCase):
    def setUp(self):
        self.output_dir = "tests/test_outputs"
        os.makedirs(self.output_dir, exist_ok=True)

        # Create a standard mock graph for testing
        self.graph = OrchestrationGraph(name="UI Test Trace")
        self.graph.add_node(Node("n1", "Researcher", NodeType.AGENT, metadata={"role": "Expert"}))
        self.graph.add_node(Node("n2", "Writer", NodeType.AGENT, metadata={"role": "Editor"}))
        self.graph.add_node(Node("n3", "Researching AI", NodeType.TOOL))
        self.graph.add_edge(Edge("n1", "n3"))
        self.graph.add_edge(Edge("n3", "n2"))

        self.test_html = os.path.abspath(os.path.join(self.output_dir, "ui_verify.html"))

    def test_ui_render_and_placeholders(self):
        """
        Verify that the HTML is generated and DOES NOT contain raw placeholders.
        """
        save_html(self.graph, self.test_html)

        with open(self.test_html, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that placeholders were replaced
        self.assertNotIn("{title}", content)
        self.assertNotIn("{node_count}", content)
        self.assertNotIn("{critical_duration}", content)
        self.assertNotIn("{graph_json}", content)

        # Check that data exists
        self.assertIn("UI Test Trace", content)
        self.assertIn("Researcher", content)
        self.assertIn("Writer", content)

    def verify_with_browser(self):
        """
        This method is intended to be called by the Antigravity agent
        using the 'browser_subagent' tool to perform live verification.
        """
        # The agent should:
        # 1. Open self.test_html
        # 2. Check for "Dissect UI Test Trace" header
        # 3. Check for existence of .node-agent elements
        # 4. Click "Start Trace" and verify progress bar moves
        # 5. Click "Researcher" node and verify sidebar displays "Researcher"
        # TODO: Implement deeper automated browser verification if needed
        return True


if __name__ == "__main__":
    unittest.main()
