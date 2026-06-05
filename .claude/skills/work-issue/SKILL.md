---
name: work-issue
description: Ship a GitHub issue end-to-end — worktree, test-first implementation, review, PR, local CI, merge, PRD update. Use with an issue number, e.g. /work-issue 42.
---

# Work an Issue

Take a GitHub issue from open to merged without touching the primary checkout.

## Steps

1. **Read the issue**: `gh issue view $1 --comments`. Require ≥2 acceptance-criteria
   bullets and a test plan — stop and ask if missing. Note the parent PRD number
   ("Part of #N") if present. Block on open upstream dependencies.
2. **Sync + worktree** (mandatory — the primary checkout stays on `main`):
   ```bash
   git fetch origin main
   git worktree add .claude/worktrees/issue-$1 origin/main
   cd .claude/worktrees/issue-$1
   git checkout -b feat/$1-<slug>     # or fix/ chore/ docs/
   ```
3. **Implement test-first**: regression test in the same commit as the change. The
   PostToolUse hook runs pre-commit on every edit — treat failures as blockers.
   Follow `CLAUDE.md` conventions (factories, class-based tests, `AsyncMock`).
4. **Review**: run `/code-review` on the diff. Apply in-scope fixes only; defer
   out-of-scope refactors to new issues.
5. **Size check**: if the diff exceeds **500 lines or 10 files**, or touches risky
   paths (`compose.yml`, `Dockerfile`, `.github/`, `.env*`, `airflow/`), label the PR
   `needs-human-review` and do not auto-merge.
6. **Open the PR**: stage specific files (`git add <paths>`, never `-A`), push, then:
   ```bash
   gh pr create --title "<title>" --body "Closes #$1

   ## Summary
   - <bullets>

   ## Test plan
   - [ ] <from the issue>"
   ```
   `Closes #$1` is mandatory so the issue auto-closes on merge.
7. **Update the parent PRD** (if any): comment the PR URL and set the Linked-work
   table row to "Open" (`gh issue edit <prd> --body-file -`).
8. **Run `/local-ci`** — the pre-merge gate. FAIL → fix and re-run; do not merge red.
9. **Merge if safe** (within size limits, no risky paths, local-ci green), from
   outside the worktree:
   ```bash
   cd /tmp && gh pr merge <num> --squash --delete-branch
   ```
   Never `gh pr merge --auto`. Large/risky PRs: print the URL and stop for a human.
10. **Close the loop**: set the PRD row to "Merged"; if this PR fixed something a
    previous PR missed, append 2-4 lines to the PRD's "Post-merge findings".
    Remove the worktree (`git worktree remove .claude/worktrees/issue-$1`) and verify
    the primary checkout is still clean on `main`.

## Extend this by…

Auto-assigning reviewers, posting a summary to the team channel, or chaining the next
issue from the PRD's parallel-safe set.
