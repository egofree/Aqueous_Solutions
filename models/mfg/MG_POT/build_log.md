MG_POT build log - FOUNDRY-MG_POT-10 / FOUNDRY-MG_POT-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/MG_POT/mg_pot.py` + `params.json`; drawing set `models/mfg/MG_POT/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON mg_pot.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_mg_pot.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_mg_pot.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The build solid sits inside the 800 x 800 x 1600 envelope; the N1/N3/N4/N5 schedule
   hardware overhangs at most 45.1 mm against the 50 mm allowance.
3. All parts valid; the cad/stl registry copy is the in-envelope build in metres and the
   X-PAR-04 gate (flow_graph/param/test_envelopes.py) passes.
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.
5. Electrode duty drawn at the design point: 54.89 A over 4 anodes at the D50 x 300 mm
   immersion, j 0.028 A/cm2 (A-M-282 class); the Cl2 off-take is the DN80 class for
   1.4813 kg/d (N2 return, N6 chlorinator feed per the A-M-280 ruling).

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv and
  fasteners.csv from the model and replaces export/mg_pot.step/.stl.
- The N8 vent is a horizontal DN15 stub on the riser at z 800 (the M2 roof-penetrating
  stub overhung the envelope; nothing resized, the schedule names the vent at the top).
