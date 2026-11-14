# Build log - WAX_PATTERN

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WAX_PATTERN.md`; envelope per `models/mfg/WAX_PATTERN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WAX_PATTERN/wax_pattern.py`

## Checks

- Build bbox 800 x 600 x 1200 mm against the 800 x 600 x 1200 mm envelope: filled exactly, inside (tracker check green). The close-out build reads the node box flush - the 5 mm SS304 cabinet carrying the wax melt pot on its steam manifold, the injector and pattern die, the PP-H bin and PE drain pan; the extraction hood of the former bench-frame build is withdrawn (2026-11-09 conversion; the former `bench_prep.py` source is withdrawn with it)
- Route-class hold named: `prep` has no AQS-PLAN-006 section 4 class; the frame-weldment practice (F-MACH row) is the named study route
- Internals: node row `none`; the machine the design block names (wax pattern injection bench, 10 L pot, 0.5 kW injector) is drawn as the unit per the duty sheet
- Nozzles: all 6 rows of `docs-authority/nozzles/WAX_PATTERN.csv` drawn at tag, face and bore as atmospheric open-bore tube stubs flush at the envelope faces (per-tag positions in check.nozzles_drawn); N6 (power terminal) is a cable schedule row, carried verbatim, never drawn; the solids row drawn DN15, bore not calculated per W4
- BOM `models/mfg/WAX_PATTERN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners completed with the hold-down rows beside the slab anchors (8.8 CS / A4-70 per the W5 grade rule); WORK_ORDER kept to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated 2026-11-14 from the accepted build through `draw_wax_pattern.py` (8 sheets: ga_front/ga_side/plan/iso01 + the cabinet, top, manifold and pot part sheets; title blocks per AQS-DWG-002, graph Rev AD). The former routing of the drawing script through `bench_prep.py` re-manifested the withdrawn bench build over the close-out outputs (check.json lost the nozzles_drawn record, tracker --check named it); the drawing script now draws through the shared close-out driver like the other converted units

## Sources

- `models/mfg/WAX_PATTERN/wax_pattern.py`
- `models/mfg/farm_closeout.py`
- `models/mfg/WAX_PATTERN/export/wax_pattern.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; route-class hold named in WORK_ORDER W12.
