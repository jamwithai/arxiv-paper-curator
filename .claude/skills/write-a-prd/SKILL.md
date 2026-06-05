---
name: write-a-prd
description: Create a PRD as a living GitHub issue — dependency graph, per-issue test plans, Linked-work table — then create the child implementation issues. Use when starting any substantial feature.
---

# Write a PRD

Create a PRD that lives as a GitHub issue and acts as the hub for all implementation
work. Child issues are the spokes; the Linked-work table tracks them to merge.

## Steps

1. **Sync first**: `git fetch origin main`. PRDs written against stale code create
   collisions later.
2. **Interview the user**: problem statement, current behavior (with `file:line`
   references you have verified), user-facing impact. Don't accept vague assertions —
   open the files and confirm.
3. **Explore the repo**: find existing patterns to reuse (service factories `make_*()`,
   router/service/repository layering, schema conventions in `src/schemas/`). The PRD
   should name modules, not invent new architecture where one exists.
4. **Build the dependency graph**: list implementation issues, draw the tree, and
   identify the **parallel-safe set** (issues with no shared files that can be worked
   concurrently in separate worktrees).
5. **Write a test plan per issue** — specific assertions, not "add tests".
   Example: "ask endpoint with `use_hybrid=false` → `search_unified()` called with
   BM25-only path → response `sources` non-empty".
6. **Default: one PR per issue.** If the user wants to bundle, document the override
   in "Further notes".
7. **Create the PRD issue**:
   ```bash
   gh issue create --title "PRD: <feature>" --body-file <prd.md>
   ```
   Mandatory sections: Problem Statement · Solution · Implementation Decisions
   (module names, no file paths) · Dependency graph + parallel-safe set ·
   Implementation issues (title, depends-on, test plan, files touched) ·
   Out of Scope · **Linked work** table (empty at creation) ·
   **Post-merge findings** (empty at creation).
8. **Create child issues**, one per implementation item, each with body
   "Part of #<PRD-number>" plus its test plan.
9. **Update the PRD**: fill the Linked-work table with the child issue numbers,
   status "Not started". Print the PRD URL.

## Linked-work table format

| Issue | PR | Status |
|---|---|---|
| #N | — | Not started / Open / Merged |

`/work-issue` updates this table as PRs open and merge, and appends to Post-merge
findings when follow-up fixes reveal process gaps.

## Extend this by…

Adding effort estimates per issue, a rollback plan section, or auto-labeling child
issues (`gh issue edit --add-label`).
