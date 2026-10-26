CR_CELL build log - FOUNDRY-CR_CELL-10 / FOUNDRY-CR_CELL-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/CR_CELL/cr_cell.py` + `params.json`; drawing set `models/mfg/CR_CELL/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON cr_cell.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_cr_cell.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_cr_cell.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The build solid sits inside the 800 x 800 x 1600 envelope; the schedule hardware
   overhangs within the 50 mm allowance (check.json connection_overhang_mm).
3. All parts valid; the cad/stl registry copy is the in-envelope build in metres and the
   X-PAR-04 gate (flow_graph/param/test_envelopes.py) passes.
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.
5. Electrode duty drawn at the design point per the graph design row (A-M-282 class).

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv and
  fasteners.csv from the model and replaces export/cr_cell.step/.stl.
- The vent is a horizontal DN15 stub on the riser at z 800 (the M2 roof-penetrating
  stub overhung the envelope; nothing resized, the schedule names the vent at the top).
