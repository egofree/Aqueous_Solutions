SHELL_BURNOUT build log - FOUNDRY-SHELL_BURNOUT-10 / FOUNDRY-SHELL_BURNOUT-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/SHELL_BURNOUT/shell_burnout.py` + `params.json`; drawing set
`models/mfg/SHELL_BURNOUT/drawings/`; build script chain run headless:

    $CADQUERY_PYTHON shell_burnout.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_shell_burnout.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py       # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_shell_burnout.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The in-envelope build solid spans the full 1000 x 1000 x 1500 casing; the N1..N5
   schedule hardware overhangs at most 34 mm against the 50 mm allowance.
3. All parts valid; the export STL is watertight (4 closed bodies); the cad/stl registry
   copy passes the X-PAR-04 gate (flow_graph/param/test_envelopes.py).
4. Overhang metrics computed from the tessellated compound (the OCC compound bbox
   inflates around the cylindrical pass cuts).

## Deviations from the M2 export

- The M2 legacy multi-body compound is superseded (one of the five legacy non-watertight
  models): the M3 build regenerates bom.csv and fasteners.csv from the model and replaces
  export/shell_burnout.step/.stl.
- The N2 fired-shell outlet moves to the +X casing wall at z 600 (schedule datum); N3/N4
  remain on the +Y face.
