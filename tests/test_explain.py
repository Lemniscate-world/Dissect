import unittest
from unittest.mock import patch, MagicMock
from dissect.graph import OrchestrationGraph, Node, NodeType
from dissect.explain import ExplainEngine, explain_graph

class TestExplainEngine(unittest.TestCase):
    def setUp(self):
        self.graph = OrchestrationGraph("Test Trace")
        # 100ms duration
        self.graph.add_node(Node("1", "Agent A", NodeType.AGENT, start_time=0, end_time=0.1))
        # 500ms duration
        self.graph.add_node(Node("2", "Tool B", NodeType.TOOL, start_time=0.2, end_time=0.7))
        
    @patch('requests.post')
    def test_explain_openai(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test Insight"}}]
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            engine = ExplainEngine(provider="openai")
            result = engine.explain(self.graph)
            
            self.assertEqual(result, "Test Insight")
            mock_post.assert_called_once()
            
    @patch('requests.post')
    def test_explain_ollama(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Ollama Insight"}
        }
        mock_post.return_value = mock_response
        
        engine = ExplainEngine(provider="ollama")
        result = engine.explain(self.graph)
        
        self.assertEqual(result, "Ollama Insight")
        
    def test_unsupported_provider(self):
        with self.assertRaises(ValueError):
            ExplainEngine(provider="unsupported")

    def test_missing_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            engine = ExplainEngine(provider="openai")
            result = engine.explain(self.graph)
            self.assertIn("OPENAI_API_KEY not found", result)

    @patch('requests.post')
    def test_api_error(self, mock_post):
        mock_post.side_effect = Exception("Connection Refused")
        engine = ExplainEngine(provider="ollama")
        result = engine.explain(self.graph)
        self.assertIn("Error connecting", result)

if __name__ == "__main__":
    unittest.main()
