---
description: Ensure Antigravity artifacts are persistent and accessible across editors
---

This workflow ensures Antigravity's artifacts are tracked in the repository for persistence across different machines and editors.

1. Ensure the artifacts directory exists:
```bash
mkdir -p .antigravity/artifacts
```

2. Copy/Update artifacts from Antigravity's internal storage (Antigravity handles this, but manual sync is possible):
```bash
cp /path/to/internal/brain/*.md .antigravity/artifacts/
```

3. Commit changes to Git:
```bash
git add .antigravity/artifacts/
git commit -m "docs: update antigravity artifacts"
```

4. Verification:
```bash
ls .antigravity/artifacts/
cat .antigravity/artifacts/task.md
```
