# Build log - HDR_CO2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HDR_CO2.md`; envelope per `models/mfg/HDR_CO2/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HDR_CO2/hdr_co2.py`

## Checks

- Build bbox 2000 x 33.7 x 33.7 mm against the 2000 x 33.7 x 33.7 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HDR_CO2/export/hdr_co2.step`; export STL closed and manifold, 1 solid(s); `cad/stl/HDR_CO2.stl` replaced from the build (ASCII, metres)
- Nozzles: all 9 rows of `docs-authority/nozzles/HDR_CO2.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 7 rows (manifold spool + 6 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table), bore 26.9 mm inside the 17 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized
- Schedule datums clamped into the 50 mm cross-section: inlets 10 to 11.3 mm, outlet datums 600 down to 38.6 mm (holds, W12); N3/N4 carry services with no present edge and are drawn verbatim
- BOM `models/mfg/HDR_CO2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HDR_CO2/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HDR_CO2/hdr_co2.py`
- `models/mfg/HDR_CO2/draw_hdr_co2.py`
- `models/mfg/HDR_CO2/bom.csv`
- `models/mfg/HDR_CO2/fasteners.csv`
- `models/mfg/HDR_CO2/line_list.csv`
- `models/mfg/HDR_CO2/check.json`
- `models/mfg/HDR_CO2/WORK_ORDER.md`
- `build export `models/mfg/HDR_CO2/export/hdr_co2.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
