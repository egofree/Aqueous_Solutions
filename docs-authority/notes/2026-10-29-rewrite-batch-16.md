# Rewrite batch 16: two stale paths

Date: 2026-10-29

- `docs-authority/AUTHORITY.md` (Rev Z): the row for the cryogenic vacuum-jacketed line envelopes cited `freecad/cryo.py`, which is no longer in the repository. The tags `VJ_001` to `VJ_005` are defined in `models/freecad/cryo.py`, and the row now cites that file.
- `docs-authority/internal/REMAINING_BLD.md` (Rev Z): this page is history, superseded by the task plan AQS-PLAN-007, and is kept as it is. It cited the same old script path and a `pfd/images/` folder that is outside the repository. The first now cites `models/freecad/cryo.py` and the second names the diagrams hub outside the repository. The other file names on the page are records of what was produced at the time and are left unchanged.
