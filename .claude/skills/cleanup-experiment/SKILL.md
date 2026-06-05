---
name: cleanup-experiment
description: Retire a finished retrieval experiment — promote the winner to the default, remove variant flags/conditionals/tests, update the experiment log. Use with a slug, e.g. /cleanup-experiment rrf-k-20.
---

# Cleanup Experiment

Experiments that linger become dead code. Retire them deliberately.

## Steps

1. **Confirm the verdict**: check the experiment's row and eval results in
   `docs/experiments.md`. No recorded result → stop and run `/offline-eval` first.
2. **Promote or revert**:
   - **Variant won**: make the variant value the default (settings class in
     `src/config.py`, or the constant in
     `src/services/opensearch/index_config_hybrid.py`), and remove the override
     plumbing if it was experiment-only.
   - **Control won**: delete the variant plumbing entirely.
3. **Sweep the residue**: grep the slug and the flag name across `src/`, `tests/`,
   `.env*`, `compose.yml`. Remove experiment-only tests; keep (and rename) any test
   that now guards the promoted default.
4. **Update the log**: set status in `docs/experiments.md` to
   `concluded — <winner> shipped`, with one line of evidence.
5. **Ship it**: this is normal code change — go through `/work-issue` (or at minimum
   a reviewed PR), not a direct push.

## Extend this by…

Auto-detecting stale experiments (active > 30 days) or batching multiple retirements
into a single sweep PR.
