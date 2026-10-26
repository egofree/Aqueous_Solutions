ROLL build log - FOUNDRY-ROLL-10 / FOUNDRY-ROLL-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/ROLL/roll.py` + `params.json`; drawing set `models/mfg/ROLL/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON roll.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_roll.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py   # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_roll.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The in-envelope build solid spans the full 1500 x 800 x 1500 frame (screw-down jack
   reaches the frame datum); the guides and chocks overhang nothing outside the envelope.
3. All parts valid; the export is one fused body whose non_manifold_edges_ascii field
   records one tessellation-seam edge on the stand side faces (check.json note).
4. The cad/stl registry copy passes the X-PAR-04 gate (flow_graph/param/test_envelopes.py).
5. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv and
  fasteners.csv from the model and replaces export/roll.step/.stl.
- The roller tables stand on pedestals tied to the base and the stand; the roll window
  is a full-width slot (nothing resized).
