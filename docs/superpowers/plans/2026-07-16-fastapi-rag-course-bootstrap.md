# FastAPI RAG Course Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the approved first delivery of a ten-week FastAPI and RAG learning course: the complete course framework, Day 1 lesson, progressive hints, intentionally failing Day 1 contract tests, and progress-tracking templates.

**Architecture:** The course lives in an isolated Python subproject at `learning/fastapi-rag/` and does not modify the existing production example under `src/`. Day 1 exposes only the behavioral contract and test harness; the learner must create `app/main.py`, so the initial test run is intentionally red. Later lessons and reference implementations are not generated in this delivery.

**Tech Stack:** Python 3.12, uv, FastAPI, HTTPX, pytest, AnyIO, Ruff, MyPy, Markdown

## Global Constraints

- Use Chinese for teaching text and English for code, identifiers, API fields, and Git examples.
- Keep all learning-project files under `learning/fastapi-rag/`; do not modify the existing `src/`, `tests/`, notebooks, or root Python project.
- Create only the ten-week framework and Day 1 executable materials; do not generate later lesson answers or a reference implementation.
- Day 1 must fit a 60–90 minute session and teach HTTP request/response basics, a FastAPI application object, one liveness route, status codes, JSON, OpenAPI, and a first red-green TDD loop.
- The learner writes all core implementation code. Course files may define behavior, tests, and three levels of hints but must not contain a copy-paste implementation.
- Day 1's baseline test run must fail loudly because `app/main.py` is absent, with an actionable assertion message rather than a skipped test.
- The ten-week roadmap must preserve the confirmed order: FastAPI/HTTP, async database/Alembic, JWT isolation, PDF/background tasks, Docling/BM25, embeddings/vector/hybrid retrieval, RAG/SSE, caching/observability/evaluation, production hardening, independent assessment.
- The final course contract must retain the confirmed local stack and boundaries: PostgreSQL, OpenSearch, Ollama, Redis, Langfuse, Docling, local Docker Compose, single API worker while using `BackgroundTasks`, stateless RAG, no frontend, and Agentic RAG as an extension.
- Do not commit automatically; the learner uses stage-level commits.

---

## File Map

- `learning/fastapi-rag/README.md`: Entry point, learning contract, workflow, commands, and first-session instructions.
- `learning/fastapi-rag/CURRICULUM.md`: Ten-week, six-session-per-week roadmap with outcomes and gates but no solutions.
- `learning/fastapi-rag/pyproject.toml`: Isolated Python 3.12 uv project and Day 1 tooling configuration.
- `learning/fastapi-rag/app/__init__.py`: Empty package marker only; `app/main.py` intentionally remains absent.
- `learning/fastapi-rag/lessons/day-01.md`: Day 1 Socratic lesson, requirements, timebox, and completion gate.
- `learning/fastapi-rag/hints/day-01/level-1.md`: Concept-only hint.
- `learning/fastapi-rag/hints/day-01/level-2.md`: Interface and file-contract hint.
- `learning/fastapi-rag/hints/day-01/level-3.md`: Language-neutral pseudocode hint, not valid Python.
- `learning/fastapi-rag/tests/day01/test_liveness.py`: Intentionally red behavioral contract tests.
- `learning/fastapi-rag/progress/current-state.md`: Machine- and human-readable resume point for “继续学习”.
- `learning/fastapi-rag/progress/learning-log.md`: Per-session evidence log.
- `learning/fastapi-rag/progress/weekly-review.md`: Weekly mastery review template.
- `docs/superpowers/plans/2026-07-16-fastapi-rag-course-bootstrap.md`: This implementation plan.

---

### Task 1: Course Contract and Ten-Week Framework

**Files:**
- Create: `learning/fastapi-rag/README.md`
- Create: `learning/fastapi-rag/CURRICULUM.md`

**Interfaces:**
- Consumes: The approved learning scope in this plan's Global Constraints.
- Produces: Stable course rules and week/session identifiers used by lesson and progress files (`W01D01` through `W10D06`).

- [ ] **Step 1: Write the course entry point**

Create `README.md` with these exact sections and responsibilities:

```markdown
# FastAPI RAG Learning Lab

## 你的目标
State the ten-week independent-project outcome and three-hour final assessment.

## 学习规则
State learner-owned implementation, Socratic questioning, three hint levels,
red-green-refactor, evidence-based completion, and stage-level learner commits.

## 技术边界
List the fixed local stack, core API scope, non-goals, and extension topics.

## 如何继续学习
Define the “继续学习” resume protocol using progress/current-state.md,
progress/learning-log.md, and the current tests.

## 第一次学习
Provide only setup, baseline-red-test, and Day 1 lesson links.

## 常用命令
Give uv sync, Day 1 pytest, Ruff, and MyPy commands scoped to this subproject.
```

- [ ] **Step 2: Write the ten-week roadmap**

Create `CURRICULUM.md` with six sessions per week. Every week must include:

```markdown
## Week N — Topic
**周目标:** observable outcome
**周验收:** behavior or explanation the learner must demonstrate

| Session | Focus | Evidence |
|---|---|---|
| WNN D01 | one bounded topic | test/output/explanation |
...
| WNN D06 | weekly integration and review | weekly gate |
```

Use these fixed weekly topics:

```text
W01 HTTP, FastAPI, Pydantic, in-memory CRUD
W02 async SQLAlchemy, PostgreSQL, repositories, Alembic
W03 password hashing, access JWT, dependencies, ownership isolation
W04 knowledge bases, secure PDF upload, cursor pagination, BackgroundTasks
W05 Docling, structure-aware chunking, OpenSearch mapping, BM25
W06 Ollama embeddings, vector retrieval, hybrid retrieval with RRF
W07 grounded prompting, structured citations, JSON RAG, standard SSE
W08 versioned Redis cache, structured logging, Langfuse, bilingual Recall@5
W09 Problem Details, resource limits, integration tests, Docker Compose
W10 quality gate, explanation review, three-hour independent assessment
```

- [ ] **Step 3: Check roadmap scope**

Run:

```bash
rg -n "Week [0-9]+|W[0-9]{2}D[0-9]{2}|参考实现|Agentic" learning/fastapi-rag/README.md learning/fastapi-rag/CURRICULUM.md
```

Expected: ten week headings, session identifiers through `W10D06`, no reference implementation, and Agentic RAG described only as an extension.

- [ ] **Step 4: Record checkpoint**

Run:

```bash
git diff -- learning/fastapi-rag/README.md learning/fastapi-rag/CURRICULUM.md
```

Expected: only the two new course-framework files.

### Task 2: Isolated Day 1 Learning Project

**Files:**
- Create: `learning/fastapi-rag/pyproject.toml`
- Create: `learning/fastapi-rag/app/__init__.py`
- Create: `learning/fastapi-rag/lessons/day-01.md`
- Create: `learning/fastapi-rag/hints/day-01/level-1.md`
- Create: `learning/fastapi-rag/hints/day-01/level-2.md`
- Create: `learning/fastapi-rag/hints/day-01/level-3.md`

**Interfaces:**
- Consumes: Session `W01D01` and course rules from Task 1.
- Produces: A Python project named `fastapi-rag-learning`, an empty `app` package, and the learner-facing Day 1 contract. The learner later produces `app.main:app`.

- [ ] **Step 1: Define the isolated Python project**

Create `pyproject.toml` with:

```toml
[project]
name = "fastapi-rag-learning"
version = "0.1.0"
description = "A test-driven FastAPI and RAG learning lab"
requires-python = ">=3.12,<3.13"
dependencies = [
    "fastapi>=0.115.12",
    "uvicorn>=0.34.0",
]

[dependency-groups]
dev = [
    "anyio>=4.9.0",
    "httpx>=0.28.1",
    "mypy>=1.15.0",
    "pytest>=8.3.5",
    "ruff>=0.11.5",
]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
src = ["app", "tests"]

[tool.mypy]
python_version = "3.12"
strict = true
packages = ["app"]
```

- [ ] **Step 2: Create only the package marker**

Create an empty `app/__init__.py`. Do not create `app/main.py`; its absence is the Day 1 red state.

- [ ] **Step 3: Write the Socratic Day 1 lesson**

The lesson must contain:

```markdown
# Day 1 — 你的第一个可验证 FastAPI 契约

## 今日产出
`GET /api/v1/health/live` returns HTTP 200 and `{"status": "alive"}`.

## 时间预算
10 min diagnosis, 15 min concepts, 10 min red test, 25 min implementation,
15 min explanation and log, 5 min buffer.

## 开场诊断题
One question comparing a Python function return value with an HTTP response.

## 任务约束
Create only app/main.py; export FastAPI as app; set title/version; declare one GET
operation with summary; do not add database, service layer, custom errors, or RAG.

## TDD workflow
Run the red test, inspect the failure, implement the minimum, rerun, then run lint/type checks.

## 必须回答的复盘题
Questions covering status code, JSON serialization, path operation, async necessity,
and OpenAPI metadata.

## 完成门槛
Tests pass, checks pass, learner explains concepts without notes, and updates progress files.
```

Do not include valid Python implementing the route.

- [ ] **Step 4: Write progressive hints**

Create three files with strictly increasing detail:

```text
Level 1: identify the application object, path operation, and serializable return value.
Level 2: reveal app/main.py, exported name app, exact title/version/path/method/summary/payload.
Level 3: pseudocode using non-Python verbs such as CREATE, REGISTER, RETURN; no import or decorator syntax.
```

Each hint must begin with a warning to open it only after recording the previous attempt.

- [ ] **Step 5: Lock dependencies**

Run:

```bash
uv lock --project learning/fastapi-rag
```

Expected: `learning/fastapi-rag/uv.lock` is created without resolving the root project.

### Task 3: Intentionally Red Day 1 Contract Tests

**Files:**
- Create: `learning/fastapi-rag/tests/day01/test_liveness.py`

**Interfaces:**
- Consumes: Future learner module `app.main` exporting `app: fastapi.FastAPI`.
- Produces: Three behavioral tests for the liveness response, default 404 behavior, and OpenAPI contract.

- [ ] **Step 1: Write the test-side loader**

Use `importlib.util.find_spec` and `importlib.import_module` so every test fails with this explicit message while `app/main.py` is absent:

```text
Day 1 starts red: create app/main.py and export a FastAPI instance named 'app'.
```

After import, assert that the exported object is a `FastAPI` instance.

- [ ] **Step 2: Write the liveness behavior test**

Use `httpx.AsyncClient` with `ASGITransport` and assert:

```text
GET /api/v1/health/live
status_code == 200
response.json() == {"status": "alive"}
content-type starts with application/json
```

- [ ] **Step 3: Write the framework behavior test**

Request an unknown path and assert `404`. This verifies the learner is using the ASGI app rather than calling a Python function directly.

- [ ] **Step 4: Write the OpenAPI contract test**

Assert:

```text
info.title == "FastAPI RAG Learning API"
info.version == "0.1.0"
paths contains /api/v1/health/live
GET operation summary == "Check liveness"
200 response is documented
```

- [ ] **Step 5: Verify the intended red state**

Run:

```bash
uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q
```

Expected: exactly three failed tests, each failing because `app/main.py` is absent. No test may be skipped or connect to an external service.

- [ ] **Step 6: Verify test-source quality**

Run:

```bash
uv run --project learning/fastapi-rag ruff check learning/fastapi-rag/tests learning/fastapi-rag/app
```

Expected: `All checks passed!`

### Task 4: Resume State and Learning Evidence

**Files:**
- Create: `learning/fastapi-rag/progress/current-state.md`
- Create: `learning/fastapi-rag/progress/learning-log.md`
- Create: `learning/fastapi-rag/progress/weekly-review.md`

**Interfaces:**
- Consumes: Session identifiers and gates from Tasks 1–3.
- Produces: A stable resume protocol for future “继续学习” sessions.

- [ ] **Step 1: Create the current-state record**

Initialize it with:

```markdown
# Current Learning State

- Current session: W01D01
- Status: ready
- Last completed session: none
- Active task: Complete the Day 1 liveness contract
- Hint level used: 0
- Last test result: expected red — app/main.py is intentionally absent
- Blockers: none
- Next action: Read lessons/day-01.md and answer its diagnostic question
```

Add a rule that future updates replace values rather than append competing states.

- [ ] **Step 2: Create the per-session log template**

Include fields for date, session, duration, diagnostic answer, test command/result, implemented behavior, explanation in the learner's own words, hint level, mistakes, remaining questions, and next retrieval-practice date.

- [ ] **Step 3: Create the weekly review template**

Include evidence-based ratings for independent implementation, conceptual explanation, tests, error diagnosis, and retention; include exact weekly gate result and next-week adjustment.

- [ ] **Step 4: Verify internal links and state**

Run:

```bash
rg -n "current-state|learning-log|weekly-review|W01D01|expected red" learning/fastapi-rag
```

Expected: the entry point, Day 1 lesson, and progress files point to a single active session and explicitly identify the expected red state.

### Task 5: Final Review and Verification

**Files:**
- Review: all files under `learning/fastapi-rag/`

**Interfaces:**
- Consumes: All prior task outputs.
- Produces: A reviewed, reproducible first course delivery with no answer leakage.

- [ ] **Step 1: Inspect the structural diff**

Run:

```bash
git status --short
git diff --stat
```

Expected: only this plan and the new `learning/fastapi-rag/` subtree are changed.

- [ ] **Step 2: Scan for answer leakage and placeholders**

Run:

```bash
rg -n "from fastapi import|@app\.|TODO|TBD|参考实现" learning/fastapi-rag --glob '!uv.lock'
```

Expected: no valid route implementation, no TODO/TBD placeholders, and any occurrence of “参考实现” only states that it is intentionally unavailable.

- [ ] **Step 3: Run deterministic checks**

Run:

```bash
uv run --project learning/fastapi-rag ruff check learning/fastapi-rag/app learning/fastapi-rag/tests
uv run --project learning/fastapi-rag mypy learning/fastapi-rag/app
uv run --project learning/fastapi-rag pytest learning/fastapi-rag/tests/day01 -q
```

Expected: Ruff and MyPy pass. Pytest reports exactly three expected failures with the Day 1 red-state message.

- [ ] **Step 4: Review course quality**

Verify manually:

```text
- Every confirmed week appears once and in the approved order.
- Every week has six bounded sessions and one evidence-based gate.
- Day 1 is achievable in 60–90 minutes.
- Day 1 tests check response values, headers, status, default routing, and OpenAPI.
- Hints increase progressively and contain no executable solution.
- Progress files support a future state-driven resume.
- No existing production code is modified.
```

- [ ] **Step 5: Report the intentional red baseline accurately**

The final report must say that the course scaffold and static checks pass, while Day 1 tests intentionally fail until the learner creates `app/main.py`. Do not describe the suite as fully passing.

---

## Self-Review

- **Spec coverage:** The plan covers the ten-week framework, Day 1 lesson, progressive hints, isolated test tooling, expected-red contract tests, and progress templates. Later lessons, core implementation, and reference answers are explicitly excluded.
- **Placeholder scan:** The plan contains no implementation placeholders. Pedagogical future work is expressed as locked scope, not `TODO` or `TBD` markers in deliverables.
- **Type consistency:** All tests consume one stable interface: `app.main` exports `app: FastAPI`. The required route and OpenAPI metadata use the same names in the lesson, hints, and tests.
