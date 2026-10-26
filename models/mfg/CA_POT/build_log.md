CA_POT build log - FOUNDRY-CA_POT-10 / FOUNDRY-CA_POT-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/CA_POT/ca_pot.py` + `params.json`; drawing set `models/mfg/CA_POT/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON ca_pot.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_ca_pot.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_ca_pot.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The build solid sits inside the 800 x 800 x 1600 envelope (inside_size_mm_shell true);
   the N1/N2/N3 schedule hardware overhangs at most 44.5 mm against the 50 mm allowance.
3. All parts valid (isValid on every solid); the cad/stl registry copy is the in-envelope
   build in metres and the X-PAR-04 gate (flow_graph/param/test_envelopes.py) passes.
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.
5. Electrode duty drawn at the design point: 3.61 A over 3 anodes at the D50 x 250 mm
   immersion, j 0.0029 A/cm2 (study; the A-M-282 class bounds it far below the AL_POT bank).

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv and
  fasteners.csv from the model and replaces export/ca_pot.step/.stl.
- The N5 vent moves to a horizontal DN15 stub on the riser at z 800 (the M2 roof-penetrating
  stub overhung the envelope; nothing resized, the schedule names the vent at the top).
