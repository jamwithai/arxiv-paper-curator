# Claude Code Workshop — 2 Hours, Basic → Advanced

**Audience:** mid-to-senior agentic ML engineers.
**Format:** live demo on this repo. Attendees watch, ask, and leave with a repo they
can clone — every artifact demoed is committed here.
**Thesis:** Claude Code isn't a chat box, it's a programmable engineering harness.
This repo's `.claude/` directory is the syllabus.

---

## Prep checklist (do this the day before AND 30 min before)

- [ ] `make start` then `make health` — API :8000, OpenSearch :9200, Airflow :8080,
      Ollama :11434 all green. A few papers ingested and indexed (Week 2 DAG run).
- [ ] `gh auth status` green; push access to the repo.
- [ ] `uv run pre-commit run --all-files` passes (so the hook demo fails only when
      you *want* it to).
- [ ] Pre-stage a small demo issue (used in the centerpiece): e.g. "Add a `sources`
      count field to AskResponse" with acceptance criteria + test plan.
- [ ] Terminal font ≥16pt; `claude` starts clean in the repo root.
- [ ] Fallback (see bottom) rehearsed once end-to-end this week.

---

## Run of show

### 0:00–0:15 — Foundations: the harness, not the chat box

| Show | How |
|---|---|
| CLAUDE.md anatomy | Open `CLAUDE.md`; explain it loads every session: commands, architecture map, conventions, policy. Contrast with prompting from scratch. |
| `/init` story | Mention: this file was *generated then curated* — `/init` bootstraps it on any repo. |
| Context economics | `/context` (what's loaded, token costs), `/compact` (summarize to keep going). |
| Permission modes | `/permissions`; default vs `acceptEdits` vs plan mode. Plan mode live: ask for a refactor, show it explores read-only and proposes before touching anything. |
| Memory | Ask Claude to remember a preference; show it persists across sessions. |

**Beat to land:** "Everything else in the next 105 minutes is configuration *of this harness*, checked into git like any other code."

### 0:15–0:35 — Skills vs commands: teach the distinction with files

| Show | How |
|---|---|
| Legacy command | Open `.claude/commands/create-pr.md` — a prompt in a file, `$ARGUMENTS` substitution, user-invoked only. Run `/daily-standup` live (30s payoff). |
| Skill | Open `.claude/skills/generate-tests/SKILL.md` — frontmatter (`name`, `description`), the description is what lets Claude *auto-invoke* it when relevant. |
| The contrast | Commands = user-triggered prompt expansion. Skills = model-discoverable capabilities with structure, supporting files, invocation control. |
| Live run | `/generate-tests src/services/ollama/client.py` — watch it study neighbor tests first (that instruction is *in the skill*), then write conventional tests. |
| Anatomy tour | `ls -R .claude/` — settings, skills, commands, worktrees convention. 60 seconds, just the shape. |

### 0:35–0:55 — Hooks, settings, permissions: determinism around the model

| Show | How |
|---|---|
| The hook | Open `.claude/settings.json` → PostToolUse runs pre-commit on every edited file. |
| Fire it live | Ask Claude to add an import in the wrong order somewhere; the hook auto-fixes/flags **immediately** — no "please run the linter" prompting. |
| Why it matters | Hooks are *enforced by the harness*, not the model's goodwill. CLAUDE.md is advice; hooks are law. |
| Permissions | Walk the allowlist in `settings.json`: pre-approved `make`/`uv`/`gh` reads vs everything else prompting. `settings.local.json` for personal overrides (gitignored). |
| Mention | Sandboxed bash, PreToolUse blocking hooks (exit 2), managed org settings — pointers for the security-minded. |

### 0:55–1:20 — Centerpiece: the engineering workflow

The full loop, live, on the pre-staged demo issue:

1. `/write-a-prd` (abbreviated — show the PRD issue structure it produces: dependency
   graph, per-issue test plans, **Linked-work table**, Post-merge findings).
2. `/work-issue <N>` — narrate as it goes:
   - worktree under `.claude/worktrees/issue-N` (primary checkout never leaves main —
     this is how you run 3 sessions in parallel without collisions)
   - test-first edit; hook fires on every write
   - `/code-review` pass before the PR
   - PR opens with `Closes #N`; PRD table flips to "Open"
3. `/local-ci` — the pre-merge gate; jobs mirror `.github/workflows/ci.yml` exactly,
   plus integration tests because we're on a feature branch.
4. Squash-merge from outside the worktree; PRD table flips to "Merged"; worktree removed.

**Beat to land:** the PRD is a *living hub* — six weeks later you can read it and know
what shipped, what broke, and what the team learned (Post-merge findings).

### 1:20–1:40 — Agentic ML workflows: experiments as a first-class loop

1. `/setup-experiment` — scaffold `rrf-k-20`: lift `rank_constant` (see
   `src/services/opensearch/index_config_hybrid.py`) into config, variant behind an
   env override, boilerplate tests, logged in `docs/experiments.md`.
2. `/offline-eval` — control vs variant through `POST /api/v1/ask`; hit-overlap +
   rank-shift table; **LLM-as-judge with local Ollama** (blind A/B, randomized order).
3. `/cleanup-experiment` + `/list-experiments` — experiments get *retired*, not
   abandoned; stale-flag detection.
4. While the eval runs: **subagents** — fire two parallel Explore agents ("map the
   chunking pipeline" / "map the agent graph") and show both come back while the main
   context stays clean. Mention background tasks (`/tasks`).

**Beat to land:** the same skill pattern that automates PRs automates *your ML
iteration loop* — eval harnesses, judge prompts, experiment hygiene.

### 1:40–1:55 — Advanced & scale (concepts + pointers, no deep demo)

- **Plugins & marketplaces**: bundle skills+hooks+MCP into installable packages;
  official + community marketplaces; this repo's `.claude/` could ship as one.
- **MCP**: connect external systems (GitHub, observability, DBs) as tools; `.mcp.json`.
- **Claude in CI**: the Claude Code GitHub Action — automated PR review/fix loops in
  Actions (concept; we deliberately ship plain `ci.yml` here).
- **Agent SDK**: the same loop, headless, in Python/TypeScript — build your own
  agents on the harness that just ran your PR.
- **Agent Teams** (experimental): multiple coordinated sessions with a shared task
  list — the worktree convention you saw is what makes this safe.
- **Checkpoints & rewind**: `/rewind` after a bad path; resume sessions.

### 1:55–2:00 — Q&A + adoption checklist

What to copy into your repo **tomorrow**, in order of ROI:
1. `CLAUDE.md` (run `/init`, then curate to ~150 lines)
2. The PostToolUse lint/type hook (10 lines of JSON, immediate payoff)
3. A `/local-ci` skill mirroring your CI
4. One workflow skill you repeat weekly (PR creation, test generation)
5. The PRD/work-issue loop once the team trusts 1–4

---

## Fallback plan

If the live GitHub flow stalls (network, gh auth, Actions queue):
- A throwaway branch with the completed centerpiece artifacts (PRD issue screenshot,
  merged PR) prepared the day before — narrate from those.
- Every skill also runs read-only: `/local-ci --only lint,types` and
  `/list-experiments` need no network.
- Worst case: open the SKILL.md files and teach from the artifacts — they're written
  to be read.

---

## Appendix: Claude Code feature inventory (cheat sheet)

| Feature | What it is | Level |
|---|---|---|
| CLAUDE.md | Per-repo instructions loaded every session | Basic |
| Memory | Persistent cross-session facts Claude maintains | Basic |
| Slash commands (built-in) | `/init`, `/context`, `/compact`, `/permissions`, `/rewind`, `/agents`, … | Basic |
| Custom commands | Prompt-in-a-file, `$ARGUMENTS` (`.claude/commands/`) | Basic |
| Skills | Model-discoverable capabilities with frontmatter (`.claude/skills/*/SKILL.md`) | Intermediate |
| Settings & permissions | allow/ask/deny rules, permission modes, `settings.local.json` | Intermediate |
| Hooks | Deterministic shell hooks at lifecycle events (PostToolUse, PreToolUse, …) | Intermediate |
| Plan mode | Read-only explore → approved plan → execute | Intermediate |
| Subagents | Parallel workers with isolated context | Intermediate |
| Worktrees | Parallel sessions without checkout collisions | Intermediate |
| Background tasks | Long-running work that doesn't block the session | Intermediate |
| MCP | External tools/services via Model Context Protocol | Intermediate |
| Plugins & marketplaces | Distributable bundles of skills/hooks/MCP | Advanced |
| GitHub Action | Claude review/fix loops inside CI | Advanced |
| Agent SDK | Headless harness in Python/TS for custom agents | Advanced |
| Agent Teams | Coordinated multi-session swarms (experimental) | Advanced |
| Sandboxing & managed settings | OS-level bash isolation; org-enforced policy | Advanced |
