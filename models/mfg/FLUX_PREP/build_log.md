# Build log - FLUX_PREP

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FLUX_PREP.md`; envelope per `models/mfg/FLUX_PREP/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/bench_prep.py FLUX_PREP`

## Checks

- Build bbox 800 x 600 x 1200 mm against the 800 x 600 x 1200 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild (shared with the WAX_PATTERN close-out of the same builder) moves the N2/N3 inlet chutes (-X) to the envelope face, so the A-core 2 overshoot the §7 row carried (830.0 x 600.0 x 1200.0) is cleared, not resized; `cad/stl/FLUX_PREP.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- Route-class hold named: `prep` has no AQS-PLAN-006 section 4 class; the frame-weldment practice (F-MACH row) is the named study route
- Internals: node row `none`; the machine the design block names (salt flux cover preparation bench, 20 L hopper, 0.1 kW mixer) is drawn as the unit per the duty sheet - bench frame, work top, extraction hood, flux hopper cone with mixer rod and stage
- Nozzles: all 5 rows of `docs-authority/nozzles/FLUX_PREP.csv` present at tag, face, height and bore, flush at the envelope faces; solids rows (N1/N2/N3) drawn as chutes, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/FLUX_PREP/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners completed with the hood-bolt row beside the slab anchors (8.8 CS per the W5 grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; the shared builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/FLUX_PREP/draw_flux_prep.py`
- `models/mfg/bench_prep.py`
- `models/mfg/FLUX_PREP/export/flux_prep.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; route-class hold named in WORK_ORDER W12.
