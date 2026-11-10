# Open findings

Source of truth for unresolved audit findings in this repository. Audits append
rows; fixing sessions mark `fixed` with a commit hash; Quality Control marks
`closed` after verification.

| id | severity | file | description | status |
| --- | --- | --- | --- | --- |
| F-20261109-03 | medium | docs-authority/INTERNALS.md | CRYO_H2 basis hard-codes "32 tubes DN114 / 1.14 m3" (also MFG_MODEL_PLAN.md, _internals.py, INTERNALS.json). | closed (verified 64e032401) |
| F-20261109-04 | medium | models/mfg/CRYO_O2, CRYO_CO2 | Saddle mass/cost double count (~1040.9 kg, ~$7,911) held since Nov 5; re-verify at HEAD with sister nozzle sheets (Rev AC). | closed (verified 2026-11-09: double count absent at 5ee8dd369, bom rows 2/3 frame-only + one saddle line, builders separate parts); nozzle-sheet part carried as F-20261109-06 |
| F-20261109-05 | low | PLAN_ROUNDS_2026-11-09.md (Aqueous planning reviews, outside this repository) | Manifests and end equality omit refs/review-backup/* and refs/stash; use full for-each-ref. | closed (verified 2026-11-09: CRYO round captured full for-each-ref (25 refs) and stash list with IDs before/after; equal, and equal to live repo at QC) |
| F-20261109-06 | medium | docs-authority/nozzles/CRYO_O2.csv, CRYO_CO2.csv | CRYO round's reconciled heights still fall outside the builders' rail bands, so the CAD lane still clamps them: O2 N2 575 (DN25 fits 488.85-551.15 in band H-130..H-30), O2 N5/N6/N8 at 600 left as is and also clamped; CO2 N4-N7 425 (band H-120..H-20: DN15 fits 342.65-417.35, DN25 350.85-411.15). | closed (verified 64e032401) |
| F-20261109-07 | medium | docs-authority/_internals.py:129-130 | CRYO_O2 and CRYO_CO2 basis text has the same hard-coded tube and volume pattern as F-03, and it is stale: O2 says 0.47 m3, node 0.5; CO2 says 0.0953 m3, node 0.0974; both say "DN114". | closed (verified 64e032401) |
| F-20261109-08 | low | docs-authority/_internals.py (CRYO round delta) | The CRYO_H2 f-string hard-codes the class text "DN100 Sch 160"; the handoff says it is read from the node material. tracker_after.txt was captured at 18:24 CT, before the 18:27 CSV redo (QC re-run: 200/200). | closed (verified 64e032401) |
| F-20261109-09 | low | ROUND_CRYO_FIX_QC_2026-11-09.md (Aqueous planning reviews, outside this repository) | Handoff base table misquotes origin/main as 65c2d11f...ce54a1a5...; actual and evidence are ...ce54b1a5... | open |
| F-20261109-10 | low | docs-authority/nozzles/CRYO_O2.csv, CRYO_CO2.csv | Datums 520/380 are hand-computed band centres stored as fixed numbers; no gate re-runs the builder land_z test, so a rack-height change would silently re-clamp. CRYO_O2/CO2 check.json, WORK_ORDER W12, drawings and STEP keep the old clamp records until the cad lane runs, and the top-vent note still says "clamped" by template. | open |
