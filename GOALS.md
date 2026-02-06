
Objective  Success Metrics  Timeline

Accurate Detection	<5% false positive/negative rate	MVP
Multi-Language Support	Python, JavaScript, Java	v1.2
Algorithmic Map & Ecosystem	Repo-wide topology & CI/CD Gates	v2.0

Features
1. **Algorithmic Map (The "Atlas")**:
   - Visual topology of the codebase based on algorithmic complexity.
   - Heatmap visualization (Hot = High Complexity/$O(n^2)$).
   - "Google Maps" for code: Zoom from Folder -> File -> Function.

2. **CI/CD Quality Gates ("The Guard")**:
   - Automated checks in GitHub Actions.
   - Blocks PRs introducing unapproved high-complexity algorithms ($O(n!)$, $O(2^n)$).
   - "Vibecoding" Audit: Flag AI-generated inefficiencies.

3. **Core Detection**:
   - Continue improving ML/AST detection for standard algorithms.

Roadmap & Milestones
Phase 1: Core Detection & Foundation (Current)
- [x] Quicksort detection basics
- [ ] BFS/DFS detection
- [ ] Basic Complexity Analysis ($O(n)$ vs $O(n^2)$)

Phase 2: The Map (Next 3 months)
- [ ] `dissect map` CLI command
- [ ] JSON/HTML output generation
- [ ] Frontend visualization (D3.js/Netron-style)

Phase 3: The Gate (3-6 months)
- [ ] GitHub Action integration
- [ ] Differential analysis (PR vs Main)
- [ ] "Algorithm Inventory" Report

Visualization Strategy
- **Heatmap**: Color-code modules by "Algorithmic Density" and "Risk".
- **Topological**: Show dependency chains between algorithmic components.
- **Interactive**: Click node -> See code + Big-O analysis.

Tech Stack
- Core: Python (AST analysis)
- Viz: D3.js or Cytoscape.js (embedded in single-file HTML report)
- CI: GitHub Actions / Pre-commit hooks