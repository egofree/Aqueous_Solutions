# X-CTL-05 — assay, digester, farm study loops issued (AQS-INST-001 Rev C)

Date: 2026-10-21. Item: X-CTL-05 (closed). Depends: X-BAS-01 (done). Triage: desk P2.

## What was delivered

AQS-INST-001 (`docs-authority/INSTRUMENT_LOOPS.md`) goes Rev B → **Rev C**: the three study-loop
pages — assay (§3, the lot station against the seven-class AQS-ASSAY-001 schema), digester (§4,
GLASS_DIGEST temperature/pressure/level/acidity/redox/H2S/volatile-solids), farm (§5, the
eight-step living-water loop) — stand as issued, and the "partial" status is retired.

## Why the partial existed and what resolved it

The 2026-10-20 evidence audit recorded the residual: the Done-when predates the plant-wide index,
loop **membership** had migrated to AQS-CTL-001, and "per-unit setpoint lists remain open with
X-CTL-05". Both halves are now registered:

1. **Membership** — AQS-CTL-001 carries 722 tags (per-unit extension complete 2026-10-20); no unit
   is left without a loop in its sector index (the audit's residual 62 units were authored then).
2. **Set-points** — the AQS-CTL-004 program blocks (X-CTL-04, same day) carry a set-point literal
   per loop from the graph basis column of the index: the A-M-188 +10/-10 % margin class for
   CONTROL loops, the registered 90 % -of-span LSH convention for INDICATION, expected-zero
   set-points alarm on any positive PV.

## Cross-references verified (doc §7 lists them)

- `GLASS_DIGEST-TE-01/-PT-01/-LT-01` sit on PLC-GLASS in the index and as monitor blocks in
  `PLC-GLASS.st`; the digester liquid high-level trip is **SIF-124** in AQS-CTL-003; the paper
  spots (pigment, iodine, lead acetate) are consumables with no recorded channel.
- The FARM sector carries 20 index loops on PLC-FARM; the hourly RTD and toroid readings are the
  recorded channels, the daily paper spots are not.
- The assay lot station's electrical points remain shop equipment beside the index; the classes
  they fill are paper records against AQS-ASSAY-001, not continuous signals on the graph.

## Board mechanics

`DONE_X` + the tuple evidence path (already `docs-authority/INSTRUMENT_LOOPS.md`); criterion text
updated to the Rev C wording (the Done-when's "(partial)" phrasing predates the audit). Dated
closure comment. DOC_REGISTER bumped B → C (2026-10-21, canonical lane). Desk P2 open count
5 → 4.

## Explicitly open

- Nothing instrument-hardware: the dry reader is a build-and-commission item like the rest of
  the shop line; its loops intentionally record no continuous channel beyond the two named ones.
- The digester organic assay gap (AQS-DES-POLY) that gates POLY_COND's live rate is unchanged
  (A-M-267) — this lane does not create the assay, only the reading method was already issued.

## Verification

- pytest 49 passed (incl. the X-CTL-04 gate); `regen --check` 920 files 0 stale; contract check,
  gasket census green; X-GOV-20 scan clean on the touched files.
- Desk P2 remaining: X-PRO-02, X-ASM-01, X-ASM-02, X-END-02.
