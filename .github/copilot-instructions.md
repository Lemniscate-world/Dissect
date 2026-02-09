# Dissect Project Instructions (GitHub Copilot)

You are an AI programming assistant working on **Dissect**, an open-source AI orchestration visualization engine.

## 🧠 Core Philosophy
1.  **Switzerland Positioning**: DO NOT prefer one framework (LangChain/CrewAI/AutoGen) over others. Keep core logic (`graph.py`) pure and independent.
2.  **Beauty is a Feature**: Visualizations MUST be stunning (dark mode, animations). If it looks like a debugger, it's wrong.
3.  **Zero-Config**: Users should just run `dissect trace file.json`. Auto-detection is mandatory.

## 🏗️ Architecture Constraints
- **Graph Source of Truth**: Data flow: `JSON Trace` -> `Framework Parser` -> `OrchestrationGraph` -> `Exporter`. NEVER skip the graph.
- **No Heavy Deps**: Do not import `langchain`, `crewai`, or `autogen` packages in `dissect/` core.
- **Self-Contained HTML**: Generated HTML files must work offline. Embed all CSS/JS.

## 📐 Design Principles
- **SRP (Single Responsibility Principle)**: Each class/module does ONE thing. `TraceParser` parses, `Graph` stores, `Exporter` renders. No "God Objects".
- **DRY (Don't Repeat Yourself)**: Extract common logic into utilities.
- **KISS (Keep It Simple, Stupid)**: Prefer simple implementations over complex abstractions. If a `dict` works, don't make a `class`.
- **YAGNI (You Ain't Gonna Need It)**: Do not build features "for the future". Implementation matches current requirements only.
- **SOLID**: Adhere to Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.
- **Duck Typing**: Pythonic approach. If it walks like a `dict` and quacks like a `dict`, treat it as one. Don't force strict `isinstance` checks unless necessary.
- **Clean Code**: readable names > comments. Small functions.
- **Agile**: Iterate fast. Ship code that works, then refactor. Don't spend days on "perfect" architecture before seeing pixels.

## 🛠️ Tooling & Hooks
- **Pre-Commit**: MANDATORY. Must run `ruff`, `mypy`, `pylint` before every commit.
- **Diagrams**: All commits MUST auto-generate architectural diagrams (Class, Sequence, Component) and embed them in `README.md`.
- **Linters**:
    - `ruff`: Fast linting & formatting.
    - `mypy`: Strict static type checking.
    - `pylint`: Deep code analysis.
    - `CodeQL`: Security vulnerability scanning.

## 📝 Coding Standards
- **Python**: Add type hints to ALL function signatures.
- **Testing**: MANDATORY after each code add.
    - **Coverage**: Minimum 60% required. Fail build if lower.
    - **Automated Tests**: CI/CD ready.
    - **Unit Tests**: Isolated function logic.
    - **Integration Tests**: End-to-end trace parsing.
    - **Logic Tests**: Graph constraints and critical path correctness.
    - **Fuzzy Tests**: Resilience against malformed inputs.
    - **Module Coverage**: Ensure EACH part, EACH module is tested. No exceptions.
- **Protocol**:
    - **Step-by-Step**: Follow the plan. Do not jump ahead.
    - **Phase Verification**: Verify ALL tasks of Phase N are complete before starting Phase N+1.
- **Naming**: Use `OrchestrationGraph`, `Node`, `Edge`. Avoid framework-specific jargon in core models.

## 🚫 Forbidden
- Hardcoding user paths.
- Leaving `print()` statements (use logging).
- Creating files outside `dissect/`, `examples/`, or `tests/`.

## 🔄 Common Workflows
- **New Parser**: Subclass `TraceParser` in `trace_receiver.py`. Add detection in `parse_trace_file`.
- **Update Viz**: Edit `HTML_TEMPLATE` in `html.py`. Run `cli.py visualize` to regenerate examples.
