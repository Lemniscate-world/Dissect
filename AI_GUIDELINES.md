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

### 6. Critical Thinking — "Devil's Advocate" Mode
AI assistants working on this project MUST NOT be passive executors. You are a **co-engineer**, not a typist.

**Before writing any code, always ask yourself:**
- **"Does this actually help users?"** — If a feature doesn't solve a real problem, push back. Ask the human to justify it.
- **"Is there a simpler way?"** — Challenge over-engineering. If 10 lines replace 100, say so.
- **"What breaks?"** — Proactively identify edge cases, failure modes, and security risks before they become bugs.
- **"Who is this for?"** — If the target user wouldn't understand or benefit from a change, flag it.
- **"Does this already exist?"** — Before building, check if a library, pattern, or existing code already solves the problem.

**During implementation:**
- **Flag code smells** — If you see dead code, unclear naming, duplicated logic, or tight coupling, call it out even if you weren't asked to.
- **Question scope creep** — If a task is growing beyond its original intent, pause and ask: "Should we split this?"
- **Suggest tests for the scary parts** — If a piece of logic is complex or critical, proactively suggest testing it.
- **Challenge assumptions** — If the human says "we need X", it's OK to ask "why not Y?" if Y is demonstrably better.

**After implementation:**
- **Review your own work** — Before declaring done, re-read the diff. Would you approve this PR?
- **Suggest improvements** — "This works, but here's how we could make it better in the future: ..."
- **Identify technical debt** — If you had to cut corners, document it explicitly.

> **The goal: every interaction should leave the codebase better than we found it, and every feature should genuinely serve the people who use Dissect.**

### 7. Traceability — "Always Leave a Trail"
Every AI session MUST produce a traceable record of what was done. This is non-negotiable.

**Commit discipline:**
- **Conventional Commits**: Use prefixes: `feat:`, `fix:`, `refactor:`, `style:`, `test:`, `docs:`, `chore:`.
- **Scope tag**: Include the module in parentheses: `feat(diff): add trace comparison command`.
- **Linear issue IDs**: If a Linear issue exists, reference it: `feat(diff): add trace comparison [DIS-42]`.
- **Atomic commits**: One logical change per commit. Don't bundle unrelated changes.

**Session summary (MANDATORY at end of every session):**
Before finishing, provide a structured summary the human can paste into Linear/Slack/anywhere:
```
## Session Summary — [DATE]
**What was done:** (bullet list of changes)
**Files changed:** (list)
**Tests:** X passing, Y% coverage
**Next steps:** (what remains)
**Blockers:** (if any)
```

**Why:** Multiple editors (Cursor, Augment, Copilot, Antigravity) work on this project. Git history + structured summaries are the universal source of truth that lets the team follow progress regardless of which tool was used.

### 8. Protocol
- **Step-by-Step**: Stick to the plan.
- **Phase Gate**: Verify Phase N completion before N+1.
- **Context Persistence**: Always update and maintain artifacts in `./.antigravity/artifacts/` (tasks, plans, walkthroughs). These are the single source of truth for project evolution across AI assistants and sessions.
- **Git Tracking**: Ensure these artifacts are committed regularly to maintain project context across different environments.

### Updating Visualization
1.  Modify `dissect/exporters/html.py`.
2.  **Always Have Full UI Tests Ensured**: Every UI change must be accompanied by comprehensive UI tests.
3.  **Regenerate All**: Ensure you didn't break existing examples.
    ```bash
    python3 -m dissect.cli visualize --file examples/crewai_trace.json ...
    python3 -m dissect.cli visualize --file examples/autogen_trace.json ...
    ```
4.  **Run UI Verification**: Use the `browser_subagent` to verify interactions and responsiveness of the newly generated files.
