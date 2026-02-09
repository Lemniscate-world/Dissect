# Dissect AI Guidelines

This project uses specific rules for AI assistants to ensure quality and consistency.

## For Developers
If you are using an AI coding assistant (Cursor, Windsurf, Copilot, etc.), please ensure it is aware of the context rules:
- **Cursor/Windsurf**: `.cursorrules` (in root)
- **GitHub Copilot**: `.github/copilot-instructions.md`

## core Principles

### 1. Framework Neutrality ("Switzerland")
Dissect is a **Translation Layer**.
- We allow LangChain, CrewAI, and AutoGen to speak to each other visually.
- We do not pick winners.
- We do not depend on their heavy libraries.

### 2. Visualization First
- The HTML output is the **Product**.
- It must be "Boardroom Ready". Use generic tech (Vanilla JS + SVG/Canvas) to ensure portability and style.

### 3. Architecture
- **Input**: Any JSON Trace
- **Core**: `OrchestrationGraph` (Generic)
- **Output**: HTML/Mermaid/DOT

### 4. Design Principles
- **SRP**: Single Responsibility. No "God Classes".
- **DRY**: detailed logic belongs in utilities, not duplicated.
- **KISS**: Simple is better than complex.
- **YAGNI**: Don't overengineer for hypothetical futures.
- **SOLID**: Follow the 5 commandments of OOD.
- **Duck Typing**: Embrace Python's dynamic nature.
- **Clean Code**: Readings names, small functions, no side effects.
- **Agile**: Ship > Argue. Code wins arguments.

### 5. Tooling
- **Pre-commit**: Ruff, Mypy, Pylint.
- **Diagrams**: Auto-generated Class/Sequence diagrams in README.
- **Security**: CodeQL scanning.

## Adding Features

### Adding a Framework Support
1.  **Get a Trace**: You need a raw JSON export from the framework.
2.  **Map to Nodes**: Decide what is an `AGENT` vs `TOOL` vs `LLM_CALL`.
3.  **Implement Parser**: Add class `MyFrameworkParser(TraceParser)`.
4.  **Test**: Write tests covering all layers:
    - **Coverage**: 60% Minimum.
    - **Module Coverage**: Ensure EACH part, EACH module is tested.
    - **Unit**: Individual methods.
    - **Integration**: Full parsing of `examples/`.
    - **Logic**: Graph structure verification.
    - **Fuzzy**: Random input testing.

### 6. Protocol
- **Step-by-Step**: Stick to the plan.
- **Phase Gate**: Verify Phase N completion before N+1.

### Updating Visualization
1.  Modify `dissect/exporters/html.py`.
2.  **Regenerate All**: Ensure you didn't break existing examples.
    ```bash
    python -m dissect.cli visualize --file examples/crewai_trace.json ...
    python -m dissect.cli visualize --file examples/autogen_trace.json ...
    ```
