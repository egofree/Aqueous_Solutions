# X-MFG-31 — in-house mfg models and production routes for the feed-blocked reaction chambers

Date: 2026-10-21. Item: X-MFG-31 (closed). Depends: X-MFG-30 (done). Triage: desk P2.

## Provenance

X-MFG-31 was closed 2026-10-15 in batches (AQS-DUTY-062 sections 1-7: reactors, sanitation, evap,
scrubber, expander, leach; 20 in-house reactor models) and reopened 2026-10-19 listing six units
without "mfg model or route": HF_GEN, VDF_SYN, TFE_SYN, POLY_F, POLY_OLEFIN, POLY_COND.

The reopen was half-stale:
- The **mfg models already exist** for all six — models/mfg/<U>/ with parametric CadQuery sources
  (models/mfg/polymers.py, reactors.py; HF kiln, VDF train, TFE train, F-kettle, oligomerization
  reactor, condensation kettle), STEP/STL exports, bom.csv, fasteners.csv and WORK_ORDER.md.
- The **production routes were missing** — no docs-authority/fab/<U>.md for any of the six.

## Done-when element check

"Every reactor, digester and CSTR designed in-house with full mfg model and production route in
MFG/FAB":

1. **Models**: all six have full work-order sets (verified on disk; see the per-unit tables in the
   AQS-DUTY-073 design-case section for the sizes and rates).
2. **Routes**: this lane issues docs-authority/fab/{HF_GEN,VDF_SYN,TFE_SYN,POLY_F,POLY_OLEFIN,
   POLY_COND}.md in the house route format (EVAP_ACID_VS pattern), each grounded in its duty sheet
   sections 2/3, the graph design rows and the work order. The unit task 13 rows for the six
   auto-tick from the board generator once the route files exist.
3. **Rates**: production stays 0.0 (A-M-267 — feed-blocked trains; per-kg design-case tables sit in
   AQS-DUTY-072/073 so the day a feed lands the rate derives). The fab docs carry the design-case
   duty; nothing invented.

## Finding fixed on the way (code-intent gap)

The A-M-283 poly design wave (2026-10-18) books POLY_OLEFIN design pressure in
`params.design.P_MPa` (5.0 MPa) — invisible to `docs-authority/_asme_class.py`, which read only
`params.design_kPa`, so AQS-ASME-002 carried POLY_OLEFIN as "not a vessel (no design pressure on
the graph)". The generator was extended (design_kPa first, then design.P_MPa) and AQS-ASME-002 goes
to **Rev C**: POLY_OLEFIN reclassifies to **B31.3 piping component** (ID 142 mm ≤ 152 mm,
U-1(c)(2)(j); UG-27 3.8 mm wall already checked in AQS-DUTY-073). Class counts now 170 not-a-vessel
/ 3 atmospheric / 4 B31.3 components / 1 Section VIII-1 awaiting size (EXPANDER).

## Board mechanics

`EVIDENCE_PASS['X-MFG-31']` flipped from `'REOPEN'` to `docs-authority/fab/VDF_SYN.md` (the route
set representative; all six routes + models are the full evidence). `REOPEN_WHY['X-MFG-31']`
removed. Desk P2 open count 7 → 6.

## Explicitly open

- The plants themselves remain rated 0.0 per A-M-267 (owner R12); a feed decision (Q-013 fluorine
  source; IA-C5-POLY collection; digester organic assay AQS-DES-POLY) is what converts the design
  cases to live rates — owner/assay gates, not this desk line.

## Verification

- `pytest -q` includes the AQS-ASME-002 content test where applicable; `regen --check` 920 files
  0 stale (ASME_CODE_INTENT.md is outside the gated manifest — same accepted-lag class as ISO_SHEETS.md —
  and is refreshed in this lane's commit).
- Unit task 13 ticks for the six units verified on the regenerated board.
