Diagnose and fix the failing CI run for the current branch (workflow:
`.github/workflows/ci.yml`). Optional run id: "$ARGUMENTS".

1. `gh run list --branch $(git branch --show-current) --limit 5` — find the failing run
   (or use the provided id).
2. `gh run view <id> --log-failed` — pull only the failing step logs.
3. Reproduce locally with the matching command (`uv run ruff check`,
   `uv run ruff format --check`, `uv run mypy src/`,
   `uv run pytest --ignore=tests/integration`).
4. Fix the root cause, not the symptom. Re-run the local command until green, then
   push and confirm the new run passes.
