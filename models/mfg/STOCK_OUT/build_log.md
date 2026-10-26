STOCK_OUT build log - FOUNDRY-STOCK_OUT-10 / FOUNDRY-STOCK_OUT-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/STOCK_OUT/stock_out.py` + `params.json`; drawing set `models/mfg/STOCK_OUT/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON stock_out.py         # build + checks + bom.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_stock_out.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_stock_out.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The in-envelope build solid spans the full 1200 x 800 x 1500 rack datum; nothing
   overhangs the envelope faces.
3. All parts valid; the export STL is watertight (3 closed bodies); the cad/stl registry
   copy passes the X-PAR-04 gate (flow_graph/param/test_envelopes.py).
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv from the
  model and replaces export/stock_out.step/.stl.
- The ten schedule rows are nominal staging positions: the seven inlets land on the tier
  decks at the z 160 datum and the issue sill carries N8 (registered layout choice).
