---
name: brainstorming
description: Design-first gate before any creative or structural work — explore context, clarify, propose 2-3 approaches, converge on a written spec. Use before building anything that doesn't have an obvious single implementation.
---

# Brainstorming

No code until the design is agreed. This skill is a gate, not a detour.

## Steps

1. **Explore first**: read the relevant modules (`src/routers/`, `src/services/`,
   schemas) before forming opinions. Cite `file:line` for every claim about current
   behavior.
2. **Clarify**: ask the questions whose answers change the design. Don't ask what you
   can verify in the code.
3. **Propose 2-3 approaches**, each with: sketch, trade-offs, blast radius (files
   touched), and a recommendation. Lead with the recommended one.
4. **Converge section-by-section**: present the design in pieces and get explicit
   agreement on each — data model, API surface, failure modes, test strategy.
5. **Write the spec**: a short markdown doc (problem, chosen design, rejected
   alternatives + why, test plan). For substantial work, feed it straight into
   `/write-a-prd`.
6. **Review loop**: have a fresh subagent attack the spec ("what breaks? what's
   missing?") before declaring it done. `/grill-me` is the heavier version.

## Extend this by…

Keeping reusable design templates per change-type (new endpoint, new service, new
agent node) and starting step 3 from the matching template.
