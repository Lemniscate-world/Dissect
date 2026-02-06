
# Dissect 2.0 - Orchestration Visualizer

> **"Visualize how AI agent systems process requests."**

## Mission
Dissect is no longer an algorithm detector. It is now an **Orchestration Visualizer** for AI agent workflows built with LangChain, CrewAI, AutoGen, and similar frameworks.

**Algorithm detection has been spun off into a separate project: Algoritmi (AI8).**

---

## Objectives

| Objective | Success Metric | Timeline |
|---|---|---|
| Trace Ingestion | Support OpenTelemetry + native SDK hooks | v2.0 |
| Agent Workflow Maps | Visualize LangChain/CrewAI/AutoGen graphs | v2.0 |
| Latency Heatmaps | Identify slow steps in orchestrations | v2.1 |
| Decision Path Traces | "Agent A → Tool B → Agent C" explanations | v2.2 |

---

## Core Features

### 1. Agent Workflow Maps
- Visualize multi-agent topologies (who talks to whom).
- Framework support: LangChain, CrewAI, AutoGen.
- Export: Mermaid, DOT, interactive HTML.

### 2. Data Flow Diagrams
- Trace how user input flows through the system.
- Highlight data transformations at each step.

### 3. Latency Heatmaps
- Color-code nodes by execution time.
- Identify bottlenecks in real-time.

### 4. Decision Path Traces
- "This output happened because: Agent A called Tool B, which triggered Agent C."
- Useful for debugging and auditing.

---

## Tech Stack
- **Trace Ingestion**: OpenTelemetry SDK / Custom hooks
- **Backend**: Python (FastAPI)
- **Visualization**: D3.js / Cytoscape.js
- **Storage**: SQLite (local) / ClickHouse (scale)

---

## Competitive Landscape

| Tool | Strength | Weakness | Dissect Opportunity |
|---|---|---|---|
| **LangSmith** | Deep LangChain integration | Proprietary, expensive | Open-source alternative |
| **Langfuse** | Open-source, self-hostable | LLM-focused, not agent-focused | Agent workflow focus |
| **Arize Phoenix** | Great for ML observability | Not agent-specific | Agent-first design |
| **CrewAI Visualizer** | Native CrewAI support | CrewAI-only | Multi-framework support |
| **AutoGen Studio** | Native AutoGen support | AutoGen-only | Multi-framework support |

**Dissect's Differentiator**: A **unified, open-source** orchestration visualizer that works across LangChain, CrewAI, AutoGen, and custom agents.

---

## Roadmap

### Phase 1: Foundation (Month 1)
- [ ] Archive algorithm detection code
- [ ] Set up OpenTelemetry trace receiver
- [ ] Basic trace parsing for LangChain

### Phase 2: Visualization (Month 2-3)
- [ ] D3.js workflow graph renderer
- [ ] Latency heatmap overlay
- [ ] Decision path trace viewer

### Phase 3: Multi-Framework (Month 4+)
- [ ] CrewAI integration
- [ ] AutoGen integration
- [ ] Real-time streaming dashboard