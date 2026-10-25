# 2026-10-25 — documentation rewrite to AQS-DOC-002

This record covers the rewrite of pages under `docs-authority/` to the documentation style guide (AQS-DOC-002). The progress of the rewrite, page by page, is tracked in `docs-authority/REWRITE_TODO.md` (AQS-DOC-003). No graph, driver, rate or topology change is made by this work.

## Batch 1

- `DOC_REGISTER.md` (AQS-REG-001) Rev C: purpose and scope added and the rules rewritten, in the generator `docs-authority/_doc_register.py`. The generator now cuts a part qualifier at the end of its first sentence, so that entries such as `AQS-INV-005 sheet MF-01` no longer show part of the following sentence.
- `PROJECT_PLAN.md` (AQS-PLAN-005) Rev C: rewritten in full. The phases, limits and values are unchanged. The hard-coded count of duty pages was removed.
- `TASK_PLAN.md` (AQS-PLAN-007) Rev C: sections 1 to 6 rewritten in `docs-authority/_task_plan_gen.py`. The list of next tasks is now generated from the triage tags of the open cross-cutting tasks. The hand-kept list and the progress record that had accumulated in that section are kept, as written, in Appendix A.
- `OPEN_QUESTIONS.md` (AQS-OQ-001) Rev B: purpose and scope added. The question rows are unchanged.
- `REWRITE_TODO.md` (AQS-DOC-003): new page, number from `_doc_register.py --next AQS-DOC`.
- `GLOSSARY.md`: BLD added.
- `README.md` (documentation map): the row for `DOCUMENTATION_STYLE.md`, which was merged into `DOC_STYLE.md` on 2026-10-24 and no longer exists, was removed.

## Batch 2

- `SECTOR_DEFINITIONS.md` (AQS-SEC-001) Rev I: generator text in `docs-authority/_sector_definitions.py` rewritten, the catalogue split into a data table, a table of system tree descriptions and a table of graph notes, and the alias names set in code format. The notes in the graph and the descriptions in the system tree are unchanged.
- `SURPLUS_PASS_THRESHOLDS.md` (AQS-SUR-001) Rev D: rewritten in full. Thresholds, inputs and sources unchanged. The stale pointer to a canonical copy outside this repository was removed.
- `GLOSSARY.md`: FRM and HP added.

## Batch 3

- `SELF_COPY_BOM.md` (AQS-BOM-SC-001) Rev H: rewritten in full. Every row, rate and identifier is kept. Section 4 stated `reprap_bom_complete` as true (the revision F value); the graph and the seed model hold false since revision G, and the table now says so. The pointer to a canonical copy outside this repository was removed. The generated reconciliation, now section 8, is rewritten in `docs-authority/_sc_reconcile.py`, which also labels a gap with no stated reason instead of leaving the cell blank.
- `docs-authority/_polymers_sizing.py` and `sizing/POLYMERS_LINE.md`: citation of the reconciliation section updated to section 8 of Rev H.
- `GLOSSARY.md`: EDC and VCM added.

## Batch 4: removed pages

- `docs-authority/DUTY_CALC.md` (AQS-DUTY-081) deleted. It was a snapshot of a retired duty calculation at an earlier graph revision, stated a unit count that no longer holds, was written by no generator and was cited by no document. The unit duty sheets in `docs-authority/duties/` replace it.
- `docs-authority/ISOMETRIC.md` (AQS-ISO-003) deleted; the path is retired. It listed close-pipe isometrics for IA-CLOSE edges, most of which are no longer in the graph, and was written by no generator. The per-line isometric set AQS-ISO-002 (`ISO_SHEETS.md`) replaces it.
- `docs-authority/_doc_register.py`: a page that is deleted now has its number withdrawn. The register lists withdrawn numbers in a new section 6, `--next` never issues them again, and `--check` fails if a page claims one.
- `docs-authority/retired_names.json`: the two deleted paths added with their successors, so that the citation check rejects them in live text.
- Documentation map: rows for the two pages removed.

## Batch 5

- `HEAT_LADDER.md` (AQS-HEAT-LADDER-001) Rev A: rewritten in full and given a revision letter and a record of revisions for the first time. Every edge, temperature, rating, elevation and envelope is kept. The page was not on the pending list of the style check.

## Batch 6

- `FEED_ASSAY.md` (AQS-ASSAY-001) Rev F: rewritten. The record of revisions listed B, D, C and omitted E, which was recorded only in section 8; it now lists B to F in order. The page stated Revision C although revisions D and E had been issued. Section numbers are kept because other pages and `flow_graph/param/drivers.json` cite them. No value changed.
- Review of four pages cited by no other page (`FARM_WASTE.md`, `NUTRIENT_BALANCE.md`, `NUTRIENT_GAPS.md`, `HAB_FIXTURES.md`); findings recorded in `REWRITE_TODO.md` section 6 for a decision. Nothing deleted.

## Batch 7

- `CRYO_ASU.md` (AQS-DUTY-018) Rev C, `RELIEF.md` (AQS-REL-001) Rev B and `RED_AUDIT.md` (AQS-RED-001) Rev C rewritten. No value changed. The redundancy audit no longer records who set the redundancy rule; it cites `AGENTS.md`.
- `GLOSSARY.md`: DM and SPOF added.
- Further pages reviewed and recorded in `REWRITE_TODO.md` section 6: `FURNACE.md`, `SIDE_FARM.md`, `FARM.md`, `SOLVENT_ROUTE.md`.

## Batch 8

- `LIFTING.md` (AQS-BLD-015), `WPS_REGISTER.md` (AQS-WLD-002) and `HAZ_AREA.md` (AQS-ELEC-009) rewritten to Rev B through their generators (`_lifting.py`, `_wps.py`, `_haz_area.py`). No value changed. The lifting page no longer states that level L-2 has no lifted equipment, which contradicted its own table.
- `GLOSSARY.md`: CMAA, QF, QW, IIA and IIC added.
