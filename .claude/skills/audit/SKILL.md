---
name: audit
description: Run a versioned quality audit — deterministic scanners plus AI review passes over this repo's risk surfaces — and write docs/quality-audit-vN.md with a delta against the previous audit.
---

# Quality Audit

Produce a versioned, comparable snapshot of code health. Each run writes
`docs/quality-audit-vN.md` (N = previous + 1) and diffs against v(N-1).

## 1. Deterministic scanners

```bash
uv run ruff check
uv run mypy src/
uvx pip-audit                     # dependency CVEs
uv run pytest --co -q | tail -1   # test count
```

Record counts, not walls of output.

## 2. AI review passes (this repo's risk surfaces)

- **Search injection** — `src/services/opensearch/query_builder.py`: is user input
  ever interpolated into query strings or index names without going through the
  structured query DSL?
- **Prompt injection** — agentic surface: `src/services/agents/nodes/`,
  `src/services/agents/prompts.py`, and the Telegram entry point
  (`src/services/telegram/`). Can retrieved chunk content or user messages steer the
  agent off its prompts? Are tool outputs treated as data?
- **Secrets & config** — `src/config.py`, `.env*`, `compose.yml`: defaults that leak
  into production, credentials in compose, settings echoed into logs.

One subagent per pass; findings need `file:line` evidence and a severity
(critical/high/medium/low).

## 3. Report — `docs/quality-audit-vN.md`

Sections: Summary grades (A-F per area) · Findings table (id, severity, file:line,
description) · Risk register · Delta vs v(N-1) (fixed / still open / new / regressed)
· Recommendations (top 3, sized).

## Extend this by…

Adding OWASP LLM Top-10 checklist coverage, dependency-license checks, or wiring the
audit into a scheduled run.
