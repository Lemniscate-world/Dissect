from graphviz import Digraph

from .analyzer.complexity import estimate_complexity


class FlowVisualizer:
    def __init__(self):
        self.dot = Digraph("Algorithm Flow", format="png")
        self.dot.attr(rankdir="LR", bgcolor="#F5F5F5")
        self.algorithms = {}

    def add_algorithm(self, name, confidence, category):
        complexity = estimate_complexity(name)
        color = {"sorting": "#FFEBEE", "graph": "#E3F2FD", "search": "#F3E5F5"}.get(
            category, "#FFFFFF"
        )

        self.algorithms[name] = confidence
        self.dot.node(
            name,
            f"<<B>{name}</B>\nConfidence: {confidence:.0%} \nComplexity: {complexity}>",
            shape="Mrecord",
            style="filled",
            fillcolor=color,
            fontcolor="#2E3440",
        )

    def add_dependency(self, source, target):
        self.dot.edge(source, target, color="#4C566A", penwidth="1.5")

    def render(self, filename):
        if not self.algorithms:
            self.dot.node("Empty", "No algorithms detected", shape="note")

        self.dot.render(filename, cleanup=True)
        print(f"Saved visualization to {filename}.png")
