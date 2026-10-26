IND_MELT build log - FOUNDRY-IND_MELT-10 / FOUNDRY-IND_MELT-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/IND_MELT/ind_melt.py` + `params.json`; drawing set `models/mfg/IND_MELT/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON ind_melt.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_ind_melt.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_ind_melt.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The in-envelope build solid spans the full 1000 x 1000 x 1500 envelope; the melt stubs,
   tilt hardware and charge chute overhang within the 50 mm allowance.
3. All parts valid; the export STL is watertight (15 closed bodies - a multi-item skid:
   furnace shell chain, coil turns, crucible group, hardware groups).
4. The cad/stl registry copy is the in-envelope build in metres and the X-PAR-04 gate
   (flow_graph/param/test_envelopes.py) passes.
5. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.

## Deviations from the M2 export

- The M2 foundry.py export stays superseded: the M3 build regenerates bom.csv and
  fasteners.csv from the model and replaces export/ind_melt.step/.stl.
- The ten charge rows land on the common charge chute at -X z 160 (registered layout
  choice, params.json layout_note); each row keeps its task-04 schedule entry.
