# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

**moai-zero-to-rag** — The Mother of AI, Phase 1: arXiv Paper Curator. A 7-week,
production-grade RAG curriculum: FastAPI → OpenSearch hybrid search → Ollama RAG →
LangGraph agentic RAG → Telegram bot. Each week's architecture and learning material
lives in `README.md` (weekly table) and `notebooks/week1/` … `notebooks/week7/`.

## Common Commands

All services run via Docker Compose; Python tooling runs through `uv` (never pip).

```bash
make start      # docker compose up --build -d (API, Postgres, OpenSearch, Airflow, Ollama, Redis, Langfuse)
make stop       # docker compose down
make status     # docker compose ps
make logs       # docker compose logs -f
make health     # curl checks: API :8000, OpenSearch :9200, Airflow :8080, Ollama :11434
make setup      # uv sync
make format     # uv run ruff format
make lint       # uv run ruff check --fix && uv run mypy src/
make test       # uv run pytest
make test-cov   # uv run pytest --cov=src --cov-report=html
make clean      # docker compose down -v && docker system prune -f
```

## Architecture Map

Request flow: `src/routers/` → `src/services/` → `src/repositories/` (Postgres) /
OpenSearch.

- **Routers** (`src/routers/`): `ask.py` (`POST /api/v1/ask`, classic RAG),
  `hybrid_search.py` (`POST /api/v1/search`), `agentic_ask.py`
  (`POST /api/v1/ask-agentic`, LangGraph), `ping.py`.
- **OpenSearch** (`src/services/opensearch/`): `client.py` — `search_unified()` routes
  BM25-only vs hybrid via the `use_hybrid` flag; `query_builder.py` builds queries;
  `index_config_hybrid.py` defines the index and the RRF pipeline
  (`HYBRID_RRF_PIPELINE`, `rank_constant=60`).
- **Agentic RAG** (`src/services/agents/`): LangGraph workflow in `agentic_rag.py`,
  nodes under `nodes/`, state in `state.py`, prompts in `prompts.py`.
- **LLM** (`src/services/ollama/`): `client.py` — `generate()`, `generate_stream()`,
  `generate_rag_answer()`. Local models via Ollama (default `llama3.2:1b`).
- **Other services**: `arxiv/` (API client), `pdf_parser/` (Docling), `indexing/`
  (chunking), `embeddings/` (Jina, 1024-dim), `cache/` (Redis), `langfuse/` (tracing),
  `telegram/` (bot), `metadata_fetcher.py` (ingestion orchestrator).
- **Config** (`src/config.py`): nested pydantic-settings; access via `get_settings()`.
  Env vars use `__` nesting (e.g. `OPENSEARCH__HOST`, `CHUNKING__CHUNK_SIZE`,
  `ARXIV__MAX_RESULTS`).
- **Pipelines**: Airflow DAGs in `airflow/dags/`.
- **Schemas** (`src/schemas/`): Pydantic models; API request/response under
  `schemas/api/` (e.g. `AskRequest` with `top_k`, `use_hybrid`, `model`).

Services are constructed through `make_*()` factory functions (`factory.py` in each
service package) — use these, don't instantiate clients directly.

## Conventions

- **Python 3.12**, dependencies managed by `uv` (`pyproject.toml` + `uv.lock`).
- **Ruff**: import sorting only (`lint.select = ["I"]`) + formatting, line length 130.
  Don't introduce other lint rules in code changes.
- **Mypy**: configured lenient (`ignore_errors = true`); still keep annotations on new
  public functions.
- **Pytest**: `asyncio_mode = "auto"` (async tests need no marker), env from
  `.env.test`. Tests are class-based (`class TestX:`), fixtures inline with
  `@pytest.fixture`, mocking via `MagicMock`/`AsyncMock` + `pytest-mock`.
- **Test layout**: `tests/unit/` (hermetic, mocked deps — this is what CI runs),
  `tests/api/` (FastAPI via `LifespanManager` + `AsyncClient`, fixtures in
  `tests/api/conftest.py`; the lifespan connects to real Redis/OpenSearch, so these
  **need `make start`**), `tests/integration/` (hits real services). `/local-ci` runs
  the service-dependent suites in pre-merge mode.
- **Docstrings**: prose-first and minimal — one sentence, present tense, period.
  Add a short WHY paragraph only when non-obvious. No section-header docstring styles.

## Quality Gates

- A PostToolUse hook runs `pre-commit` (ruff import-sort, ruff-format, mypy) on every
  file you edit — treat any failure as a blocker before continuing.
- `/local-ci` is the pre-merge gate: it replicates `.github/workflows/ci.yml` locally
  and adds integration tests on feature branches. Run it before any merge.
- Run a code review pass (e.g. `/code-review`) before opening a PR.

## Workflow Policy

- **PRD as hub**: substantial features start with `/write-a-prd` — a PRD GitHub issue
  with a dependency graph, per-issue test plans, and a Linked-work table that tracks
  child issues/PRs through their lifecycle. Implementation happens via `/work-issue`.
- **One PR per issue** by default; bundling needs explicit agreement, documented in the PRD.
- **Worktrees**: do feature work in `git worktree` checkouts under `.claude/worktrees/`,
  never on the primary checkout. The primary working directory stays on `main` with a
  clean tree so concurrent sessions don't collide.
- **Test-first**: write the regression test in the same commit as the change. No test
  plan on the issue → don't start coding.
- **PR size limits**: ≤500 changed lines and ≤10 files for auto-merge eligibility.
  Larger PRs need human review.
- **Risky paths** (never auto-merge, flag for human review): `compose.yml`,
  `Dockerfile`, `.github/`, `.env*`, `airflow/`.
- **Merging**: squash-merge with `gh pr merge <num> --squash --delete-branch`, run from
  outside the worktree. **Never** use `gh pr merge --auto`.
- **Branch naming**: `feat/<desc>`, `fix/<desc>`, `chore/<desc>`, `docs/<desc>`.
- Leave unrelated uncommitted changes in the working tree untouched; stage specific
  files (`git add <paths>`), never `git add -A`.

## Experiments

Retrieval experiments toggle real knobs behind config/env flags (see
`/setup-experiment`): RRF `rank_constant` (`index_config_hybrid.py`), `chunk_size`
(`ChunkingSettings`), BM25-vs-hybrid (`use_hybrid` through `search_unified()`).
Evaluate variants with `/offline-eval` (control vs variant through `POST /api/v1/ask`,
optional LLM-as-judge via Ollama); retire finished ones with `/cleanup-experiment`;
inventory with `/list-experiments`.
