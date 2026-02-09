"""
Dissect 2.0 - CLI

Command-line interface for the Orchestration Visualizer.
"""

import argparse
import sys

from .explain import explain_graph
from .exporters.dot import save_dot
from .exporters.html import save_html
from .exporters.mermaid import save_mermaid
from .trace_receiver import parse_trace_file


def explain_command(args):
    """Generate AI summary of the trace."""
    print(f"Parsing trace file: {args.file}")

    try:
        graph = parse_trace_file(args.file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Generating insights using {args.provider}...")
    summary = explain_graph(graph, provider=args.provider, model=args.model)

    print("\n" + "=" * 40)
    print(" DISSECT AI INSIGHTS")
    print("=" * 40 + "\n")
    print(summary)
    print("\n" + "=" * 40)


def trace_command(args):
    """Parse a trace file and display summary."""
    print(f"Parsing trace file: {args.file}")

    try:
        graph = parse_trace_file(args.file)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing trace: {e}")
        sys.exit(1)

    print("\n✓ Parsed successfully!")
    print(f"  Name: {graph.name}")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")

    # Show critical path
    critical_path = graph.get_critical_path()
    if critical_path:
        total_duration = sum(n.duration_ms or 0 for n in critical_path)
        print(f"\n  Critical Path ({total_duration:.0f}ms):")
        for node in critical_path:
            duration = f"({node.duration_ms:.0f}ms)" if node.duration_ms else ""
            print(f"    → {node.name} {duration}")


def visualize_command(args):
    """Generate visualization from trace file."""
    print(f"Parsing trace file: {args.file}")

    try:
        graph = parse_trace_file(args.file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_file = args.output
    format_type = args.format.lower()

    if format_type == "mermaid":
        if not output_file.endswith(".md"):
            output_file = f"{output_file}.md"
        save_mermaid(graph, output_file)
        print(f"✓ Mermaid diagram saved to: {output_file}")

    elif format_type == "dot":
        if not output_file.endswith(".dot"):
            output_file = f"{output_file}.dot"
        save_dot(graph, output_file)
        print(f"✓ DOT diagram saved to: {output_file}")

    elif format_type == "html":
        if not output_file.endswith(".html"):
            output_file = f"{output_file}.html"
        save_html(graph, output_file)
        print(f"✓ Interactive HTML saved to: {output_file}")

    elif format_type == "json":
        if not output_file.endswith(".json"):
            output_file = f"{output_file}.json"
        with open(output_file, "w") as f:
            f.write(graph.to_json())
        print(f"✓ JSON saved to: {output_file}")

    else:
        print(f"Unknown format: {format_type}")
        print("Supported formats: mermaid, dot, html, json")
        sys.exit(1)


def serve_command(args):
    """Start a local server for real-time trace viewing."""
    print("Starting Dissect server...")
    print(f"  Port: {args.port}")
    print(f"  Open: http://localhost:{args.port}")
    print("\nNote: Real-time server not yet implemented.")
    print("Use 'dissect visualize' to generate static visualizations.")


def main():
    parser = argparse.ArgumentParser(
        prog="dissect", description="Dissect 2.0 - Orchestration Visualizer for AI Agent Workflows"
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Trace command
    trace_parser = subparsers.add_parser("trace", help="Parse and inspect a trace file")
    trace_parser.add_argument("--file", "-f", required=True, help="Path to trace file (JSON)")
    trace_parser.set_defaults(func=trace_command)

    # Visualize command
    viz_parser = subparsers.add_parser("visualize", help="Generate visualization from trace")
    viz_parser.add_argument("--file", "-f", required=True, help="Path to trace file (JSON)")
    viz_parser.add_argument(
        "--format",
        "-t",
        default="html",
        choices=["html", "mermaid", "dot", "json"],
        help="Output format (default: html)",
    )
    viz_parser.add_argument(
        "--output", "-o", default="workflow", help="Output file path (default: workflow)"
    )
    viz_parser.set_defaults(func=visualize_command)

    # Serve command (placeholder)
    serve_parser = subparsers.add_parser(
        "serve", help="Start local server for real-time visualization"
    )
    serve_parser.add_argument(
        "--port", "-p", type=int, default=8080, help="Port to listen on (default: 8080)"
    )
    serve_parser.set_defaults(func=serve_command)

    # Explain command
    explain_parser = subparsers.add_parser(
        "explain", help="Generate AI-powered insights from trace"
    )
    explain_parser.add_argument("--file", "-f", required=True, help="Path to trace file (JSON)")
    explain_parser.add_argument(
        "--provider",
        "-p",
        default="openai",
        choices=["openai", "ollama"],
        help="AI provider (default: openai)",
    )
    explain_parser.add_argument("--model", "-m", help="Model name to use")
    explain_parser.set_defaults(func=explain_command)

    # Version
    parser.add_argument("--version", "-v", action="version", version="Dissect 2.0.0")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
