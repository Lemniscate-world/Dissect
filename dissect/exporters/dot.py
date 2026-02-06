"""
Dissect 2.0 - DOT Exporter

Export OrchestrationGraph to Graphviz DOT format.
"""

from ..graph import OrchestrationGraph, NodeType


def export_dot(graph: OrchestrationGraph) -> str:
    """
    Export graph to Graphviz DOT format.
    
    Returns:
        DOT diagram string.
    """
    lines = [
        f'digraph "{graph.name}" {{',
        '    rankdir=TB;',
        '    node [shape=box, style="rounded,filled", fontname="Arial"];',
        '    edge [fontname="Arial", fontsize=10];',
        '',
    ]
    
    # Color map by node type
    color_map = {
        NodeType.AGENT: "#E3F2FD",
        NodeType.TOOL: "#FFF3E0",
        NodeType.LLM_CALL: "#F3E5F5",
        NodeType.USER_INPUT: "#E8F5E9",
        NodeType.OUTPUT: "#FFEBEE",
        NodeType.UNKNOWN: "#F5F5F5",
    }
    
    # Add nodes
    for node in graph.nodes.values():
        color = color_map.get(node.node_type, "#F5F5F5")
        label = node.name
        if node.duration_ms:
            label = f"{node.name}\\n{node.duration_ms:.0f}ms"
        
        lines.append(f'    "{node.id}" [label="{label}", fillcolor="{color}"];')
    
    lines.append("")
    
    # Add edges
    for edge in graph.edges:
        if edge.label:
            lines.append(f'    "{edge.source_id}" -> "{edge.target_id}" [label="{edge.label}"];')
        else:
            lines.append(f'    "{edge.source_id}" -> "{edge.target_id}";')
    
    lines.append("}")
    
    return "\n".join(lines)


def save_dot(graph: OrchestrationGraph, file_path: str) -> None:
    """Save graph as DOT file."""
    content = export_dot(graph)
    with open(file_path, "w") as f:
        f.write(content)
