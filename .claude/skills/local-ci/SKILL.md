---
name: local-ci
description: Run all CI checks locally and report pass/fail — the pre-merge gate. Mirrors .github/workflows/ci.yml, plus integration tests on feature branches. Read-only; never fixes or merges.
---

# Local CI

Replicate the CI pipeline locally so nothing merges red. **Read-only**: report
results, never modify code or merge.

## Mode detection

```bash
branch=$(git rev-parse --abbrev-ref HEAD)
ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
# PRE_MERGE mode when on a feature branch ahead of origin/main
```

## Jobs (always — mirrors .github/workflows/ci.yml)

1. **lint** — `uv run ruff check`
2. **format** — `uv run ruff format --check`
3. **types** — `uv run mypy src/`
4. **unit tests (hermetic)** — `uv run pytest tests/unit --ignore=tests/unit/services/agents --cov=src`
   (the agents exclusion matches ci.yml while Week 7 stabilizes; drop it when CI does)
5. **compose config** — `docker compose config -q`

## Pre-merge jobs (feature branches only — these need live services)

6. **services up?** — `make health`; if any service is down, report and skip jobs 7-8
   with a warning (do not start services yourself).
7. **api tests** — `uv run pytest tests/api/` (FastAPI lifespan connects to real
   Redis/OpenSearch)
8. **integration tests** — `uv run pytest tests/integration/`

## Flags

- `--skip <job>` — skip named job(s)
- `--only <job>` — run only named job(s)
- `--no-pre-merge` / `--force-pre-merge` — override mode detection

## Output format

One line per job (✅/❌/⏭ + duration), then a summary block:

```
Local CI: PASS (5 passed, 0 failed, 2 skipped)
```

On FAIL: list the failing jobs with the last ~15 lines of each failure. Stop there —
fixing is the caller's job.

## Extend this by…

Adding a coverage threshold gate, a Trivy image scan, or caching the last green commit
to skip unchanged jobs.
