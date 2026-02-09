"""
Dissect 2.0 - AI Insights Engine

Analyzes orchestration graphs using LLMs to provide execution summaries,
bottleneck detection, and architectural insights.
"""

import os
from typing import Any, Dict, Optional

import requests

from .graph import OrchestrationGraph


class ExplainEngine:
    """Engine for generating AI-powered insights from orchestration graphs."""

    SYSTEM_PROMPT = """
You are Dissect, an expert AI Agent Architect.
Your task is to analyze an agent orchestration trace and provide a concise, professional summary.

Focus on:
1. Execution Flow: What was the high-level sequence?
2. Bottlenecks: Which nodes had high latency (heat_score > 0.7)?
3. Logical Loops: Did agents get stuck in repetitive cycles?
4. Optimization: How can this workflow be improved?

Respond in clean Markdown. Use bold for node names.
"""

    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider.lower()
        if self.provider == "openai":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.model = model or "gpt-4o"
            self.url = "https://api.openai.com/v1/chat/completions"
        elif self.provider == "ollama":
            self.model = model or "llama3"
            self.url = "http://localhost:11434/api/chat"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _prepare_prompt(self, graph: OrchestrationGraph) -> str:
        """Convert graph to text representation for LLM."""
        data = graph.to_dict()
        summary = [f"Workflow: {graph.name}"]
        summary.append(f"Total Nodes: {len(graph.nodes)}")

        # Nodes summary
        summary.append("\nNodes:")
        for node in data["nodes"]:
            heat = f"(Heat: {node['heat_score']:.2f})" if "heat_score" in node else ""
            duration = f"{node['duration_ms']:.0f}ms" if node.get("duration_ms") else "unknown"
            summary.append(f"- {node['name']} [{node['type']}] - Duration: {duration} {heat}")

        # Edges summary
        summary.append("\nConnections:")
        for edge in data["edges"]:
            label = f" ({edge['label']})" if edge.get("label") else ""
            summary.append(f"- {edge['source']} -> {edge['target']}{label}")

        return "\n".join(summary)

    def explain(self, graph: OrchestrationGraph) -> str:
        """Get LLM explanation for the graph."""
        prompt = self._prepare_prompt(graph)
        payload: Dict[str, Any]

        if self.provider == "openai":
            if not self.api_key:
                return "Error: OPENAI_API_KEY not found in environment."

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
        else:  # ollama
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
            }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if self.provider == "openai":
                return result["choices"][0]["message"]["content"]

            return result["message"]["content"]

        except Exception as e:
            return f"Error connecting to AI provider ({self.provider}): {e}"


def explain_graph(
    graph: OrchestrationGraph, provider: str = "openai", model: Optional[str] = None
) -> str:
    """Helper function to explain a graph."""
    engine = ExplainEngine(provider, model)
    return engine.explain(graph)
