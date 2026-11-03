# Build log - BLOW_MOLD

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BLOW_MOLD.md`; envelope per `models/mfg/BLOW_MOLD/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BLOW_MOLD/blow_mold.py`

## Checks

- Build bbox 1200 x 800 x 1600 mm against the 1200 x 800 x 1600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/BLOW_MOLD/export/blow_mold.step`; export STL closed and manifold, 6 solid(s); `cad/stl/BLOW_MOLD.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/BLOW_MOLD.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Continuous-extrusion blow molder per the node design block (Precious Plastic class; AQS-EQP-MFG-001; A-M-285): 316L melt path per duty section 3 (barrel, head, downward die), the three drive groups as purchased envelopes per plan rule 6 with the node ratings (2.2 / 0.75 / 0.75 kW), and the mold tool envelope (BLOW-MOLD-TOOL-01)
- The article geometry is not named on the node: the mold set is an envelope and the mold detail is a named hold (W12)
- Guard frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/BLOW_MOLD/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BLOW_MOLD/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/BLOW_MOLD/blow_mold.py`
- `models/mfg/BLOW_MOLD/draw_blow_mold.py`
- `models/mfg/BLOW_MOLD/bom.csv`
- `models/mfg/BLOW_MOLD/fasteners.csv`
- `models/mfg/BLOW_MOLD/check.json`
- `models/mfg/BLOW_MOLD/WORK_ORDER.md`
- `build export `models/mfg/BLOW_MOLD/export/blow_mold.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-SC (route hold); holds named in WORK_ORDER W12.
