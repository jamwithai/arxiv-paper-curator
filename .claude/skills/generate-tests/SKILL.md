---
name: generate-tests
description: Generate pytest tests for a target file following this repo's conventions (class-based, asyncio auto mode, AsyncMock, factory patching). Use with a path, e.g. /generate-tests src/services/ollama/client.py.
---

# Generate Tests

Write tests that look like they were always here.

## Steps

1. **Read the target** (`$ARGUMENTS`) and its existing tests, if any. Find the
   mirroring test path: `src/services/x/y.py` → `tests/unit/services/x/test_y.py`;
   router behavior → `tests/api/routers/test_<router>.py`.
2. **Study a neighbor test file first** (e.g. `tests/unit/services/test_arxiv_client.py`,
   `tests/api/routers/test_agentic_ask.py`) and copy its idioms.
3. **Repo conventions** (non-negotiable):
   - Class-based: `class TestSearchUnified:` grouping related cases.
   - `asyncio_mode = "auto"` — async tests are plain `async def test_*`, no marker.
   - Inline `@pytest.fixture` in the test file; shared API fixtures come from
     `tests/api/conftest.py` (`LifespanManager` + `AsyncClient`).
   - Mock with `MagicMock`/`AsyncMock`; patch service construction at the factory
     (`src.services.<pkg>.factory.make_*`), not deep internals.
   - Cover: happy path, one edge case per branch, error propagation.
4. **Run them**: `uv run pytest <new test file> -q`, then `make test` for the suite.
   Don't hand over red tests.

## Extend this by…

Generating property-based tests (hypothesis), coverage-gap targeting from
`make test-cov` output, or parametrized fixtures for the OpenSearch query matrix.
