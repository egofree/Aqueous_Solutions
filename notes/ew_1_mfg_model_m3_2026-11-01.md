# EW_1 manufacturing model accepted M3 — 2026-11-01

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) section 2 work order and section 5
acceptance, A-core + A-CELL. Graph Rev AC. Pattern-setter for EW_2 to EW_9.

## What changed

- `models/mfg/EW_1/ew_1.py`: new parametric source (W1). Reads `params.json`, builds the CPVC
  tank (wall 10 mm, AQS-DUTY-051 section 1 zone stack), the 25/26 electrode bank at 100 mm pitch,
  the AQS-BUS-001 EW-1 bus pair, and all 12 schedule nozzles flush at the envelope faces; writes
  the exports, the BOM, `fasteners.csv` and `check.json`.
- `models/mfg/EW_1/draw_ew_1.py` + `drawings/`: W7 set (GA front/side, nozzle orientation, three
  part sheets, iso), stamped by `docs-authority/_drawings.py`. The old envelope-pointer `GA.md`
  and the three unstamped sheets drawn from the superseded style-builder export are removed; the
  new sheets carry their content.
- `models/mfg/EW_1/WORK_ORDER.md`: W10/W11/W12 route, self-copy (none) and the named holds, plus
  the per-unit recipe for EW_2 to EW_9.
- `cad/stl/EW_1.stl`: replaced from the build (ASCII, metres, X-PAR-04 envelope registry).
- `models/mfg/tracker.py`: EW_1 joins ACCEPTED (M3 evidence verified on the files); `--check`
  gains the documented optional unit filter; the generated board sentence names the new M3 unit.
- `models/mfg/lib/nozzles.py`: `place_on_face` side faces now offset by the rotated extent, so
  the documented flush-at-the-face default really ends flush (the pre-rotation bbox carried the
  stub diameter, not its length; the T0 self-test covered only `outside=True` and top/bottom and
  still passes).
- Generated in the same commit: duty `docs-authority/duties/EW_1.md` section 7 model pointer
  (`docs-authority/_duty_basis.py`), plan section 7 row and counts (`models/mfg/tracker.py`),
  `params.json` W2 refresh, `docs-authority/DRAWING_REGISTER.md`.

## Acceptance evidence

`python3 models/mfg/tracker.py --check EW_1` green; A-CELL: 25 cathodes / 26 anodes at 100 mm
pitch, plates 600 × 420 immersed (0.504 m² both faces, 12.6 m² bank), bus pack 2 × 110 × 6.3 mm
Cu per the published EW-1 row. Holds are named in `models/mfg/EW_1/WORK_ORDER.md` W12, led by the
bus current basis (published pack at 2105 A vs the duty section 9 bounding 2476 A) and the
working-level reading (fill 1.243 m³ to z 680 vs the 487 mm overflow notch).
