# X-END-02 — end-of-life material return, Rev C duty-sheet sweep (AQS-END-002)

Date: 2026-10-21. Item: X-END-02 (still PARTIAL, residual narrowed). Depends: X-BAS-01, X-PRO-01
(done). Triage: desk P2.

## What was delivered

`docs-authority/EOL_RETURN.md` / `inventory/EOL_RETURN.csv` regenerated at **Rev C** by
`docs-authority/_eol.py` after the 2026-10-19/20 duty-sheet issue wave landed:

- The 44 units that waited on a duty sheet at Rev B were swept: section-3 material text now
  exists and the keyword classing picked it up where it names a classable material.
- **Unassigned: 89 → 73 lines**; classed 931 → **947 of 1020** (organic 401, metal_plateable 440,
  metal_reactive 76, silicate_oxide 30, unassigned 73).
- Every residual line carries a named hold (Rev B's zero-silent-line rule kept):
  - **70 lines**: the unit duty sheet section 3 explicitly says *material selection pending at
    unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases* — 35 units ×
    (envelope body + process nozzle), including the pot cells (AL_POT, MG_POT, TI_CELL, CR_CELL,
    CA_POT, MO_CELL) and the metallurgy line (CAST_LINE, CONT_CAST, SINTER, SI_REDUCE, IND_MELT,
    FORGE, ROLL, DRAW, EXTRUDE, and companions). No feeding class is invented: classing an
    as-yet-unselected material would contradict the duty sheet that says "not chosen on this
    page".
  - **2 lines**: HCL_BURNER has no duty sheet file yet (its unit task 01).
  - **1 pointer row** (OF-13): the AQS-INV-004 fabricated-part roll-up pointer to per-unit BOM
    classing, unchanged.
- **Held total 159** (fluoropolymer 57, Ti-as-blanks 23, Nd/Dy-in-cake 5, Pt-Rh gauze 1,
  duty-sheet-pending 72, pointer 1) — the fluoropolymer HF-scrubber constraint, the Ti acid-
  strength boundary and the NdFeB/Pt-Rh holds are unchanged in substance.

## Why the box stays open (honest)

The Done-when is "each unit material assigned to a plant feed class under AQS-ASSAY-001". For the
73 residual lines there is no material to class yet — the selection is itself the pending unit
task 09 work (`AQS-STD-002` palette across the bounding cases). The Rev C sweep exhausted
everything the present artifacts can class without inventing; the residual is now exactly the
unit task 09 sweep plus one duty sheet. Board status stays `PARTIAL` with the narrowed numbers.

## Board mechanics

`EVIDENCE_PASS['X-END-02']` partial note updated to Rev C numbers; DOC_REGISTER bumped B → C;
dated Rev C row in the doc. Desk P2 open count stays 1 (X-END-02).

## Verification

- pytest 62 passed; `regen --check` 920 files 0 stale; contract check and gasket census green;
  X-GOV-20 scan clean on the touched files.
- After unit task 09 selections land, one `_eol.py` run classes the 70; the HCL_BURNER lines
  follow its duty sheet; the pointer row is a declared roll-up artifact, not a material.
