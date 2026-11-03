# Build log - GLASS_DIGEST

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GLASS_DIGEST.md`; envelope per `models/mfg/GLASS_DIGEST/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GLASS_DIGEST/glass_digest.py`

## Checks

- Build bbox 700 x 700 x 900 mm against the 700 x 700 x 900 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GLASS_DIGEST/export/glass_digest.step`; export STL closed and manifold, 13 solid(s); `cad/stl/GLASS_DIGEST.stl` replaced from the build (ASCII, metres)
- Nozzles: all 12 rows of `docs-authority/nozzles/GLASS_DIGEST.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- M2 close-out per the HX8 close pattern: the Oct-31-era reactors.py study build verified through the current shared lib (unit-dir builder, 12-row issued schedule, tracker W2, section 5 artifacts completed); the stale envelope-era drawing set and GA.md superseded
- A-VES: model shell volume 48.3 L against the node design V_L 49.9724 L (V_work 37.4793 L, tau 22.5014 h at 85 C); reported, no residence claim added
- Schedule N4 row repaired to the schedule quoting (unquoted comma in 'digest NaOH, 20 wt%' shifted face and height); change record in notes/glass_oilgas_m3_2026-11-02.md
- BOM `models/mfg/GLASS_DIGEST/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GLASS_DIGEST/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GLASS_DIGEST/glass_digest.py`
- `models/mfg/GLASS_DIGEST/draw_glass_digest.py`
- `models/mfg/GLASS_DIGEST/bom.csv`
- `models/mfg/GLASS_DIGEST/fasteners.csv`
- `models/mfg/GLASS_DIGEST/check.json`
- `models/mfg/GLASS_DIGEST/WORK_ORDER.md`
- `build export `models/mfg/GLASS_DIGEST/export/glass_digest.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
