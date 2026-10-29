# Derived file register stable across the commit that carries the outputs

Date: 2026-10-29. Files: `docs-authority/_rev_stamp.py`, `docs-authority/DERIVED_REVISIONS.md` (AQS-GOV-006).

## Finding

`scripts/check_all.sh --full` failed at the idempotency step on `main` (9799dc3b). One cause was the derived file register: `_rev_stamp.py` stamped every uncommitted derived file "working tree" before it looked at whether the regeneration had vouched for the file. A full regeneration run before a commit therefore wrote "working tree" rows, and the same regeneration run after the commit wrote graph commit rows, so the register could never reproduce itself across the commit that carried it. The project worked around this with follow-up commits that only refreshed derived files.

## Change

A file that the regeneration receipt or a generator manifest vouches for at the current graph hash is stamped from the last graph commit whether or not it is committed yet. Only files outside the vouched set fall back to their own commit history. The other cause, derived files committed without a full regeneration, is fixed by the next commit, which carries only regenerated outputs.
