"""
Tests for Dissect 2.0 - Orchestration Graph
"""

import unittest
from dissect.graph import OrchestrationGraph, Node, Edge, NodeType


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
        nodes = {n['id']: n for n in data['nodes']}
        
        self.assertAlmostEqual(nodes['A']['heat_score'], 0.0)
        self.assertAlmostEqual(nodes['B']['heat_score'], 0.5)
        self.assertAlmostEqual(nodes['C']['heat_score'], 1.0)

if __name__ == '__main__':
    unittest.main()
