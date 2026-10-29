# Commit identity and the mail map

Date: 2026-10-29. Files: `.mailmap`, `scripts/check_all.sh`, `AGENTS.md`, `CONTRIBUTING.md`.

## Finding

Commits from 2026-10-01 onward, and every commit on `main` from 2026-10-25 09:34 (UTC-5) to the head of 2026-10-26, carry the author and committer `Buddy Dev <buddy@example.com>`. That identity is the `[user]` entry in the machine-wide Git configuration (`~/.gitconfig`) of the owner's workstation. Clones on that workstation without their own `user.email` setting inherited it. Clones that set the owner's identity in `.git/config` committed correctly. The commits were therefore made from the owner's clones and belong to the owner.

## Decision

The history is not rewritten. A rewrite would change every commit hash from the first affected commit, would need a forced push of `main`, and would break every existing clone, fork and cited commit hash. `.mailmap` maps the placeholder identity to the owner instead; `git log`, `git shortlog` and `git blame` show the owner's name, and the commit objects are unchanged.

## Prevention

`scripts/check_all.sh` now fails when `git config user.email` is unset or is a placeholder address. `AGENTS.md` and `CONTRIBUTING.md` state the identity to commit under.
