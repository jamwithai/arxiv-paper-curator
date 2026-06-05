---
name: offline-eval
description: Evaluate a retrieval experiment offline — run a query set through the API for control vs variant, compute overlap/rank metrics, optionally LLM-as-judge via Ollama — and emit a comparison table.
---

# Offline Eval

Compare control vs variant on real queries before anything ships. Requires services
up (`make health` first).

## Steps

1. **Query set**: use `docs/eval-queries.md` if present, else generate 10-15 diverse
   questions from indexed papers (factual, comparative, methodological) and save them
   there for reuse.
2. **Run both arms** against `POST /api/v1/ask` (or `POST /api/v1/search` for
   retrieval-only evals):
   ```bash
   curl -s localhost:8000/api/v1/ask -H 'content-type: application/json' \
     -d '{"query": "<q>", "top_k": 5, "use_hybrid": true}'
   ```
   Control = current defaults; variant = the env overrides printed by
   `/setup-experiment` (restart the API with them: `make restart`).
3. **Retrieval metrics** per query, from the `sources`/chunks returned:
   - **hit overlap** (Jaccard of retrieved chunk ids)
   - **rank shifts** of shared hits
   - score deltas where available
4. **LLM-as-judge (optional)**: for answer-level evals, ask the local model to grade
   both answers blind (A/B order randomized) on relevance + groundedness, 1-5:
   `OllamaClient.generate()` (`src/services/ollama/client.py`) or a direct
   `curl localhost:11434/api/generate`. Judge model ≠ generation model where possible.
5. **Report**: per-query table + aggregate (mean overlap, judge win-rate), a 3-line
   interpretation, and a recommendation: *ship variant / keep control / needs more
   queries*. Update the experiment's row in `docs/experiments.md`.

## Extend this by…

nDCG against a labeled relevance set, statistical significance on win-rates, or
batch-running the query set through the Airflow DAG.
