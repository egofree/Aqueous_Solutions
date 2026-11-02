# Build log - GLASS_BURNOUT

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GLASS_BURNOUT.md`; envelope per `models/mfg/GLASS_BURNOUT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GLASS_BURNOUT/glass_burnout.py`

## Checks

- Build bbox 800 x 600 x 1200 mm against the 800 x 600 x 1200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GLASS_BURNOUT/export/glass_burnout.step`; export STL closed and manifold, 4 solid(s); `cad/stl/GLASS_BURNOUT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/GLASS_BURNOUT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 4 rows, tag/from/to/DN/class/service/rating; the HL-GLASS_BURNOUT-Q2-A/B rows ride study edges and carry the study note; edge coverage complete, no new edge
- Machine: burnout rotary drum OD 560 x 700, wall 12 (study), on trunnion stands; drum-full 0.1579 m3 against the 0.2100 m3 duty section 2 seven-day charge - reported, nothing resized (plan rule 3)
- Schedule N3/N4 rows repaired to the schedule quoting (service text carried an unquoted comma that shifted face and height); the change record is in notes/glass_oilgas_m3_2026-11-02.md
- BOM `models/mfg/GLASS_BURNOUT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GLASS_BURNOUT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GLASS_BURNOUT/glass_burnout.py`
- `models/mfg/GLASS_BURNOUT/draw_glass_burnout.py`
- `models/mfg/GLASS_BURNOUT/bom.csv`
- `models/mfg/GLASS_BURNOUT/fasteners.csv`
- `models/mfg/GLASS_BURNOUT/line_list.csv`
- `models/mfg/GLASS_BURNOUT/check.json`
- `models/mfg/GLASS_BURNOUT/WORK_ORDER.md`
- `build export `models/mfg/GLASS_BURNOUT/export/glass_burnout.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
