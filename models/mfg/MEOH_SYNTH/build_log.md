# Build log - MEOH_SYNTH

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_SYNTH.md`; envelope per `models/mfg/MEOH_SYNTH/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MEOH_SYNTH/meoh_synth.py`

## Checks

- Build bbox 414 x 414 x 2585 mm against the 414 x 414 x 2585 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MEOH_SYNTH/export/meoh_synth.step`; export STL closed and manifold, 2 solid(s); `cad/stl/MEOH_SYNTH.stl` replaced from the build (ASCII, metres)
- Nozzles: all 9 rows of `docs-authority/nozzles/MEOH_SYNTH.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Pressure part 316L per duty section 3 (API 941, AQS-REV-H2-001 section 5); the node SA-106 B tube row superseded (hold, W12)
- A-VES: the bed volume (3.213 L model against the node 3.2143 L V_work_L) is reported; no residence time derived (duty section 2 claims no holdup)
- Purchased items as envelopes per plan rule 6: catalyst bed (3.54 kg Cu/ZnO/Al2O3) and feed preheater (0.818 kW)
- Two solids: the vessel chain and the bed-with-grids envelope at running clearance in the bore; both closed and manifold
- BOM `models/mfg/MEOH_SYNTH/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_SYNTH/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MEOH_SYNTH/meoh_synth.py`
- `models/mfg/MEOH_SYNTH/draw_meoh_synth.py`
- `models/mfg/MEOH_SYNTH/bom.csv`
- `models/mfg/MEOH_SYNTH/fasteners.csv`
- `models/mfg/MEOH_SYNTH/check.json`
- `models/mfg/MEOH_SYNTH/WORK_ORDER.md`
- `build export `models/mfg/MEOH_SYNTH/export/meoh_synth.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
