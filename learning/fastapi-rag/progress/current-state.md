# Current Learning State

> 本文件永远只保留一个当前状态。推进课程时替换下列值，不要追加第二组相互冲突的状态。

- Current session: W01D01
- Status: environment-blocked
- Last completed session: none
- Active task: Expose uv in Git Bash, then complete the Day 1 liveness contract
- Hint level used: 0
- Last test result: expected red verified in an isolated temporary uv environment on CPython 3.12.13 — 3 failed with the Day 1 missing-app message
- Blockers: uv is not currently available in Git Bash; the temporary verification environment was removed
- Next action: Install or expose uv, run `uv sync --project learning/fastapi-rag`, then reproduce the expected red Day 1 test result locally

## Status values

Use exactly one of these values:

- `environment-blocked`: required runtime or tool is unavailable;
- `ready`: prerequisites work and the session has not started;
- `in-progress`: the learner is actively attempting the current task;
- `blocked`: learning work started but a concrete issue prevents progress;
- `completed`: every completion-gate item for the current session has evidence.

When the environment is repaired, change `Status` to `ready`, replace `Last test result` with the actual command outcome, clear `Blockers`, and set `Next action` to the Day 1 diagnostic question.
