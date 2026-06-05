---
name: list-experiments
description: Inventory retrieval experiments — active, concluded, and stale — by reading the experiment log and grepping the codebase for experiment flags.
---

# List Experiments

One table: what's running, what's done, what's rotting.

## Steps

1. **Read the log**: `docs/experiments.md` (slug, knob, status, dates). Missing file
   → report "no experiments recorded" and check step 2 anyway.
2. **Cross-check the code**: grep `src/` and `.env*` for experiment slugs and
   override env vars (`CHUNKING__`, `OPENSEARCH__`, experiment-named settings).
   Flags in code but not in the log → **untracked**; log says active but no code
   references → **ghost**.
3. **Staleness**: anything `active` for >30 days gets flagged stale with a pointer to
   `/cleanup-experiment`.
4. **Report**:

   | Slug | Knob | Status | Age | Action |
   |---|---|---|---|---|
   | rrf-k-20 | rank_constant 60→20 | active | 12d | awaiting eval |

## Extend this by…

Linking each row to its eval report and PRD, or failing `/local-ci` when untracked
experiment flags are detected.
