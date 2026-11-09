# Build log - GALLEY

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GALLEY.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 4000 x 3000 x 2380 mm: inside the envelope with margin (envelope 4000 x 3000 x 2400 mm)
- Solid source: build export `models/mfg/GALLEY/export/galley.step`
- BOM `models/mfg/GALLEY/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GALLEY/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/GALLEY/galley.py` (build model; `draw_galley.py` drives the drawing set)
- `models/mfg/GALLEY/export/galley.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.

## Rebuild

- 2026-11-09: rebuilt through `galley.py` (the shared close-out builder
  `models/mfg/farm_closeout.py`, the AQUA_TANK pattern; the envelope, graph revision
  and nozzle schedule read from the node and `docs-authority/nozzles/GALLEY.csv`
  through `models/mfg/lib/graph_node.py`). export/, check.json, bom.csv,
  fasteners.csv and the params.json envelope/layout blocks regenerated from the
  build. bbox 4000 x 3000 x 2400 mm (vent flush at the box top; walls to z 2380),
  one fused solid, all 8 schedule rows drawn, empty mass 1959.4 kg (was 1744.6 kg:
  the SS304 counter run, the purchased appliance envelope, the PP boards and the
  nozzle set added). `cad/stl/GALLEY.stl` replaced from the build solid (X-PAR-04
  envelope registry, metres). The 2026-10-31 record above keeps the former
  shell-only build; the drawing set predates this rebuild.
