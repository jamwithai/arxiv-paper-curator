---
name: setup-experiment
description: Scaffold a retrieval experiment — a variant behind a config flag with boilerplate tests — for knobs like RRF rank_constant, chunk_size, or BM25-vs-hybrid. Use when starting an A/B retrieval comparison.
---

# Setup Experiment

Scaffold a control-vs-variant retrieval experiment behind a config flag, so
`/offline-eval` can compare them and `/cleanup-experiment` can retire the loser.

## Real knobs in this repo

| Knob | Where | Default |
|---|---|---|
| RRF `rank_constant` | `src/services/opensearch/index_config_hybrid.py` (`HYBRID_RRF_PIPELINE`) | 60 |
| `chunk_size` / `overlap_size` | `ChunkingSettings` in `src/config.py` (env: `CHUNKING__CHUNK_SIZE`) | 600 / 100 |
| BM25 vs hybrid | `use_hybrid` on `AskRequest` → `OpenSearchClient.search_unified()` | hybrid |
| Retrieval depth | `top_k` on `AskRequest` (1-10) | 3 |

## Steps

1. **Name the experiment**: short slug, e.g. `rrf-k-20`. One hypothesis per
   experiment ("lower rank_constant favors top-ranked lexical hits → better precision").
2. **Wire the variant behind config, not code forks**:
   - Settings-based knobs need no code change — document the env override
     (e.g. `CHUNKING__CHUNK_SIZE=300`).
   - For knobs that are currently constants (e.g. `rank_constant`), lift the constant
     into the relevant settings class in `src/config.py` with the current value as
     default, and thread it through (e.g. into `HYBRID_RRF_PIPELINE` construction).
3. **Add boilerplate tests**: a unit test asserting the default is unchanged, and one
   asserting the override reaches the OpenSearch request body
   (`tests/unit/services/test_opensearch_query_builder.py` shows the idiom).
4. **Record the experiment**: add a row to `docs/experiments.md` (create if missing):
   slug · knob · control · variant · hypothesis · status `active`.
5. **Hand off**: print the exact env overrides for control and variant runs, ready for
   `/offline-eval`.

## Extend this by…

Multi-arm variants, per-request experiment headers, or persisting experiment metadata
in Postgres instead of a markdown table.
