# Developer Handoff

This is the default English handoff document. The Chinese counterpart is [HANDOFF.zh-CN.md](HANDOFF.zh-CN.md); both documents must contain the same information in different languages.

## Quick Start for a New Developer

1. Read `PROJECT_SPEC.md`, `docs/DEVELOPMENT_LOG.md`, `docs/TEST_LOG.md`, and `docs/TEST_REPORT.md`.
2. Confirm the worktree is clean, then run `scripts/run-quality-gate.ps1`.
3. Double-click `Start-ResumeGrowthCoach.cmd` for local use; it checks Ollama and `qwen2.5:3b`. Use `Stop-ResumeGrowthCoach.cmd` when finished; it only stops the verified local server process started from this checkout.
4. After changing scoring, parsing, recommendations, persistence, or an API contract, update tests and both language versions of the relevant logs.

## Major-Change Log Template

Append to `docs/DEVELOPMENT_LOG.md` and mirror the entry in `docs/DEVELOPMENT_LOG.zh-CN.md`:

```markdown
## YYYY-MM-DD: short change title

### Changes
- ...

### Verification
- command: ...
- result: ...

### Remaining Problems
- ...

### Future Work
- **P0**: ...
- **P1**: ...
- **P2**: ...
```

Append to `docs/TEST_LOG.md` and mirror the entry in `docs/TEST_LOG.zh-CN.md`:

```markdown
## YYYY-MM-DD Test Round

### Checked
- ...

### Suspicious Findings and Handling
- ...

### Not Checked
- ...

### User Experience and Edge Cases
- ...
```

## Completion Requirements

- User-facing analysis, roadmap, recommendations, and bullet drafts remain English-only.
- The deterministic layer runs before Ollama; model failure must not break the API.
- Direct and recommended roles use the same scoring function; recommendations exclude the current role.
- A new bug must first become a reproducible automated test, then be fixed with the regression test retained.
- Before pushing, pass pytest, the quality gate, and `git diff --check`; confirm no real personal data is tracked.
- Any log or handoff document must have an English primary file and a semantically identical `.zh-CN.md` counterpart.
