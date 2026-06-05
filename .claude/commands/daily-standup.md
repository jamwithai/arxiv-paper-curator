Summarize my recent work for standup. Period: "$ARGUMENTS" (default: yesterday).

1. `git log --since="<period>" --author="$(git config user.email)" --oneline --all`
2. `gh pr list --author @me --state all --limit 10`
3. Output three short sections: **Done** / **In progress** / **Blockers** (infer
   blockers from failing CI or PRs awaiting review). Keep it under 10 lines.
