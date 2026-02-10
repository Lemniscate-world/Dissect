"""
Tests for CLI
"""

import argparse
import unittest
from unittest.mock import MagicMock, patch

from dissect.cli import diff_command, main, trace_command, visualize_command


class TestCLI(unittest.TestCase):
    @patch("argparse.ArgumentParser.parse_args")
    @patch("dissect.cli.trace_command")
    def test_main_trace(self, mock_trace, mock_args):
        """Test that trace command is routed correctly."""
        mock_args.return_value = argparse.Namespace(
            func=mock_trace, command="trace", file="trace.json"
        )
        main()
        mock_trace.assert_called_once()

    @patch("dissect.cli.parse_trace_file")
    @patch("builtins.print")
    def test_trace_command(self, mock_print, mock_parse):
        """Test trace command execution."""
        mock_graph = MagicMock()
        mock_graph.name = "Test Graph"
        mock_graph.nodes = [1, 2]
        mock_graph.edges = [1]
        mock_graph.get_critical_path.return_value = []
        mock_parse.return_value = mock_graph

        args = argparse.Namespace(file="trace.json")
        trace_command(args)

        mock_parse.assert_called_with("trace.json")
        # Check that we printed something
        self.assertTrue(mock_print.call_count > 0)

    @patch("dissect.cli.parse_trace_file")
    @patch("dissect.cli.save_html")
    @patch("builtins.print")
    def test_visualize_command_html(self, mock_print, mock_save_html, mock_parse):
        """Test visualize command for HTML output."""
        mock_graph = MagicMock()
        mock_parse.return_value = mock_graph

        args = argparse.Namespace(file="trace.json", format="html", output="out")
        visualize_command(args)

        mock_save_html.assert_called_with(mock_graph, "out.html")

    @patch("dissect.cli.explain_graph")
    @patch("dissect.cli.parse_trace_file")
    def test_explain_command(self, mock_parse, mock_explain):
        from dissect.cli import explain_command

        mock_explain.return_value = "AI Insight"
        args = MagicMock()
        args.file = "test.json"
        args.provider = "openai"
        args.model = None

        with patch("builtins.print"):
            explain_command(args)

        mock_parse.assert_called_once_with("test.json")
        mock_explain.assert_called_once()


    @patch("dissect.cli.format_diff")
    @patch("dissect.cli.diff_graphs")
    @patch("dissect.cli.parse_trace_file")
    @patch("builtins.print")
    def test_diff_command(self, mock_print, mock_parse, mock_diff, mock_format):
        """Test diff command execution."""
        mock_old = MagicMock()
        mock_new = MagicMock()
        mock_parse.side_effect = [mock_old, mock_new]
        mock_diff.return_value = MagicMock()
        mock_format.return_value = "No differences"

        args = argparse.Namespace(old="old.json", new="new.json")
        diff_command(args)

        self.assertEqual(mock_parse.call_count, 2)
        mock_diff.assert_called_once_with(mock_old, mock_new)
        mock_format.assert_called_once()


if __name__ == "__main__":
    unittest.main()
