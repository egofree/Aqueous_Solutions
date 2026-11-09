# Build log - WASHROOM

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WASHROOM.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 3000 x 2000 x 2380 mm: inside the envelope with margin (envelope 3000 x 2000 x 2400 mm)
- Solid source: build export `models/mfg/WASHROOM/export/washroom.step`
- BOM `models/mfg/WASHROOM/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WASHROOM/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/WASHROOM/washroom.py` (build model; `draw_washroom.py` drives the drawing set)
- `models/mfg/WASHROOM/export/washroom.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.

## Rebuild

- 2026-11-09: rebuilt through `washroom.py` (the shared close-out builder
  `models/mfg/farm_closeout.py`, the AQUA_TANK pattern; the envelope, graph revision
  and nozzle schedule read from the node and `docs-authority/nozzles/WASHROOM.csv`
  through `models/mfg/lib/graph_node.py`). export/, check.json, bom.csv,
  fasteners.csv and the params.json envelope/layout blocks regenerated from the
  build. bbox 3000 x 2000 x 2400 mm (vent flush at the box top; walls to z 2380),
  one fused solid, all 4 schedule rows drawn, empty mass 842.2 kg (was 745.8 kg:
  the SS304 fixture set and the nozzle set added). `cad/stl/WASHROOM.stl` replaced
  from the build solid (X-PAR-04 envelope registry, metres). The 2026-10-31 record
  above keeps the former shell-only build; the drawing set predates this rebuild.
