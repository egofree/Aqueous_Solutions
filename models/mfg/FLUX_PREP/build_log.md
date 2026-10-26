FLUX_PREP build log - FOUNDRY-FLUX_PREP-10 / FOUNDRY-FLUX_PREP-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/bench_prep.py` (build_and_export) + `models/mfg/FLUX_PREP/params.json`;
drawing set `models/mfg/FLUX_PREP/drawings/`; chain run headless:

    $CADQUERY_PYTHON bench_prep.py FLUX_PREP        # build + checks + bom.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The bench build solid sits inside the 800 x 600 x 1200 envelope; nothing overhangs the faces.
3. All parts valid; the export STL is watertight (4 closed bodies); the cad/stl registry copy
   passes the X-PAR-04 gate (flow_graph/param/test_envelopes.py).
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv from the
  model and replaces export/.step/.stl.
- The bench shell and hardware are shared-frame design content (bench_prep.py); the two
  benches differ in their task-04 hardware only.
