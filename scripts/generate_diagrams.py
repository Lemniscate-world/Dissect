#!/usr/bin/env python3
"""
Auto-generate architectural diagrams for Dissect.
Generates Class, Package, and Sequence diagrams using pyreverse and graphviz.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "architecture"
DISSECT_PKG = PROJECT_ROOT / "dissect"

def setup_dirs():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

def generate_class_diagram():
    print("🎨 Generating Class Diagram...")
    try:
        subprocess.run([
            "pyreverse",
            "-o", "png",
            "-p", "dissect",
            str(DISSECT_PKG),
            "-d", str(DOCS_DIR)
        ], check=True)
        print("✅ Class diagram generated in docs/architecture/")
    except FileNotFoundError:
        print("❌ pyreverse not found. Install it with: pip install pylint")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate class diagram: {e}")

def generate_sequence_diagram():
    print("🎬 Generating Sequence Diagram (Conceptual)...")
    # Dissect uses Mermaid for its own viz, let's use it for documentation too.
    mermaid_content = """
sequenceDiagram
    participant User
    participant CLI
    participant Parser
    participant Graph
    participant Exporter
    
    User->>CLI: dissect trace file.json
    CLI->>Parser: parse_trace_file(path)
    Parser->>Parser: Auto-detect format
    Parser->>Graph: Create Nodes & Edges
    Graph-->>CLI: OrchestrationGraph
    CLI->>Exporter: export(graph, format='html')
    Exporter-->>User: workflow.html
    """
    
    diagram_path = DOCS_DIR / "sequence_diagram.mmd"
    with open(diagram_path, "w") as f:
        f.write(mermaid_content)
    print(f"✅ Sequence diagram source saved to {diagram_path}")

def update_readme():
    print("📝 Updating README with diagrams...")
    # Placeholder for logic to inject diagram links if strictly required
    # For now, just ensuring they exist is enough
    pass

def main():
    setup_dirs()
    generate_class_diagram()
    generate_sequence_diagram()
    update_readme()

if __name__ == "__main__":
    main()
