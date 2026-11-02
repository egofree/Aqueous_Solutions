# Build log - WS_HF_ED

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_HF_ED.md`; envelope per `models/mfg/WS_HF_ED/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_HF_ED/ws_hf_ed.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_HF_ED/export/ws_hf_ed.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_HF_ED.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/WS_HF_ED.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)
- Tank: node design_storage D 300 x H 300, wall 4.75 (AQS-DUTY-064); the 0.02 m3 nominal volume is reported for the record, no residence claim (W12)
- PVDF wetted per duty section 3 (X-MAT-09 85 C basis, not CPVC); the design_storage material row (PE) superseded by duty section 3 (holds, W12)
- BOM `models/mfg/WS_HF_ED/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_HF_ED/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_HF_ED/ws_hf_ed.py`
- `models/mfg/WS_HF_ED/draw_ws_hf_ed.py`
- `models/mfg/WS_HF_ED/bom.csv`
- `models/mfg/WS_HF_ED/fasteners.csv`
- `models/mfg/WS_HF_ED/check.json`
- `models/mfg/WS_HF_ED/WORK_ORDER.md`
- `build export `models/mfg/WS_HF_ED/export/ws_hf_ed.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
