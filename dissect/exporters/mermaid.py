"""
Dissect 2.0 - Mermaid Exporter

Export OrchestrationGraph to Mermaid diagram format.
"""

from ..graph import OrchestrationGraph, NodeType


def export_mermaid(graph: OrchestrationGraph) -> str:
    """
    Export graph to Mermaid flowchart format.
    
    Returns:
        Mermaid diagram string.
    """
    lines = ["flowchart TD"]
    
    # Node styling by type
    style_map = {
        NodeType.AGENT: ":::agent",
        NodeType.TOOL: ":::tool",
        NodeType.LLM_CALL: ":::llm",
        NodeType.USER_INPUT: ":::input",
        NodeType.OUTPUT: ":::output",
        NodeType.UNKNOWN: "",
    }
    
    # Add nodes
    for node in graph.nodes.values():
        # Escape special characters in name
        safe_name = node.name.replace('"', "'").replace("[", "(").replace("]", ")")
        style = style_map.get(node.node_type, "")
        
        # Format with duration if available
        label = safe_name
        if node.duration_ms:
            label = f"{safe_name}<br/>{node.duration_ms:.0f}ms"
        
        lines.append(f'    {node.id}["{label}"]{style}')
    
    # Add edges
    for edge in graph.edges:
        if edge.label:
            lines.append(f"    {edge.source_id} -->|{edge.label}| {edge.target_id}")
        else:
            lines.append(f"    {edge.source_id} --> {edge.target_id}")
    
    # Add styling
    lines.extend([
        "",
        "    classDef agent fill:#E3F2FD,stroke:#1976D2",
        "    classDef tool fill:#FFF3E0,stroke:#F57C00",
        "    classDef llm fill:#F3E5F5,stroke:#7B1FA2",
        "    classDef input fill:#E8F5E9,stroke:#388E3C",
        "    classDef output fill:#FFEBEE,stroke:#D32F2F",
    ])
    
    return "\n".join(lines)


def save_mermaid(graph: OrchestrationGraph, file_path: str) -> None:
    """Save graph as Mermaid diagram file."""
    content = export_mermaid(graph)
    with open(file_path, "w") as f:
        f.write(content)
