Create a pull request for the current branch. Use "$ARGUMENTS" as the PR title if
provided, otherwise derive one from the commits.

1. `git status` — confirm we're on a feature branch (not main) and review what's staged.
2. Stage only the files belonging to this change (`git add <paths>`, never `-A`),
   commit if needed.
3. `git push -u origin HEAD`
4. `gh pr create --title "<title>" --body` with sections: Summary (bullets from the
   diff) and Test plan (how it was verified). Include `Closes #<issue>` if this
   branch maps to an issue.
5. Print the PR URL.
