# Dissect

> **Visualize AI Agent Workflows** | LangChain • CrewAI • AutoGen • OpenTelemetry

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![Coverage](https://img.shields.io/badge/coverage-66%25-brightgreen.svg)](tests/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com/Lemniscate-world/Dissect)

Dissect helps you understand what's happening inside your AI agent systems. Parse traces, visualize workflows, and identify bottlenecks.

![Dissect Visualization](/home/kuro/.gemini/antigravity/brain/aa252a15-bec2-4bd2-a6ff-37bd01849699/dissect_v2_demo_1770657475382.png)

## Features

- 🔌 **Multi-Framework Support** – Works with LangChain, CrewAI, AutoGen, and any OpenTelemetry-compatible system
- 📊 **Beautiful Visualizations** – Interactive HTML, Mermaid diagrams, Graphviz DOT
- ⏱️ **Critical Path Analysis** – Identify the slowest paths in your workflows
- 🚀 **Zero Config** – Auto-detects trace formats

## Quick Start

```bash
# Install
pip install dissect

# Parse a trace file
dissect trace --file trace.json

# Generate interactive HTML visualization
dissect visualize --file trace.json --format html --output workflow.html

# Generate Mermaid diagram
dissect visualize --file trace.json --format mermaid --output workflow.md
```

## Example Output

```
✓ Parsed successfully!
  Name: Trace
  Nodes: 7
  Edges: 6

  Critical Path (750ms):
    → User Query (50ms)
    → Writer Agent (400ms)
    → Claude Call (300ms)
```

## Supported Trace Formats

| Format | Auto-Detected By |
|--------|------------------|
| OpenTelemetry | `spans` or `resourceSpans` field |
| LangChain | `runs` or `run_type` field |
| CrewAI | `crew_name`, `agents` + `tasks` |
| AutoGen | `agents` + `messages` |

## Visualization Formats

| Format | Command | Use Case |
|--------|---------|----------|
| HTML | `--format html` | Interactive exploration |
| Mermaid | `--format mermaid` | Documentation, GitHub |
| DOT | `--format dot` | Graphviz rendering |
| JSON | `--format json` | Programmatic access |

## Development

```bash
# Clone
git clone https://github.com/Lemniscate-world/Dissect.git
cd Dissect

# Install in dev mode
pip install -e .

# Run tests
python -m pytest
```

## Roadmap

- [x] Multi-framework trace parsing
- [x] HTML/Mermaid/DOT export
- [x] Critical path analysis
- [x] 🌡️ Latency Heatmaps (Bottleneck detection)
- [x] `dissect explain` (AI-powered insights)
- [ ] `dissect watch` (Live trace streaming)
- [ ] VS Code extension
- [ ] Dissect Cloud (hosted dashboard)

## Architecture

### Class Diagram
![Class Diagram](docs/architecture/classes.png)

### Sequence Diagram
```mermaid
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
```

## License

Apache 2.0 – see [LICENSE](LICENSE)

---

Built with ❤️ by [Lemniscate World](https://github.com/Lemniscate-world)
