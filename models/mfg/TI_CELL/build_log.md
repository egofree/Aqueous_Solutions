TI_CELL build log - FOUNDRY-TI_CELL-10 / FOUNDRY-TI_CELL-11 acceptance

Date: 2026-10-26. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/TI_CELL/ti_cell.py` + `params.json`; drawing set `models/mfg/TI_CELL/drawings/`;
build script chain run headless:

    $CADQUERY_PYTHON ti_cell.py         # build + checks + bom.csv + fasteners.csv + WORK_ORDER + STEP/STL
    $CADQUERY_PYTHON draw_ti_cell.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    $CADQUERY_PYTHON draw_ti_cell.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL solid check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step; check.json written by the build.
2. The in-envelope build solid spans the full 800 x 800 x 1600 frame (skid base, posts,
   retort lift beam) and the export STL is watertight - the M2 multi-body compound is
   superseded. The X-PAR-04 gate (flow_graph/param/test_envelopes.py) passes.
3. All parts valid; the vessels fuse through the skid frame and the interconnects.
4. Drawings name graph revision AC; 8 sheets stamped by AQS-DWG-002, SVG + PDF.

## Deviations from the M2 export

- The M2 kroll_train geometry (foundry.py) is superseded: the M3 build regenerates
  bom.csv and fasteners.csv from the model and replaces export/ti_cell.step/.stl.
- The schedule hardware attaches to the vessels and stays in envelope (the M2 export
  was a disjoint compound; nothing resized, all nozzles per the task-04 schedule).
- The skid frame is new design content: base plate, four posts, the retort lift beam
  for the batch change-out, and vessel pedestals at the interconnect heights.
