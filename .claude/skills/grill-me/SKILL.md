---
name: grill-me
description: Relentlessly interrogate a plan, design, or PRD — walk every branch of the decision tree until nothing is hand-waved. Use before committing to a design you can't cheaply undo.
---

# Grill Me

The user presents a plan; you find every unanswered question in it. You're done when
neither side can produce a question the design doesn't already answer.

## Rules

1. **One question at a time.** Wait for the answer before the next.
2. **Walk the tree**: every decision implies sub-decisions. "Cache the embeddings" →
   where? invalidated when? what's the failure mode when Redis is down? what does the
   cold path cost?
3. **Attack the seams**: error paths, concurrency (two sessions, two worktrees),
   migrations/rollbacks, the empty state, the 10x-scale state.
4. **No vibes**: when an answer is "probably fine", make it concrete — which file,
   which test would prove it, what's the number.
5. **Track the ledger**: keep a running list of *resolved* vs *open* points; show it
   on request. Finish by dumping the resolved decisions as bullet points the user can
   paste into the spec or PRD.

## Extend this by…

Domain question-packs (one for retrieval changes, one for agent-graph changes, one for
infra) seeded from past post-merge findings.
