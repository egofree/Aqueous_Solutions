# Build log - LITHO_ALIGN

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LITHO_ALIGN.md`; envelope per `models/mfg/LITHO_ALIGN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/LITHO_ALIGN/litho_align.py`

## Checks

- Build bbox 1200 x 600 x 800 mm against the 1200 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/LITHO_ALIGN/export/litho_align.step`; export STL closed and manifold, 5 solid(s); `cad/stl/LITHO_ALIGN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 2 rows of `docs-authority/nozzles/LITHO_ALIGN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Contact aligner per the node design block and AQS-LITH-001 rev C (named on the node): 6061 frame and base, aluminium stage, 4140 leadscrew (shop lathe), chrome-on-glass mask (shop mill), and the 365 nm LED array envelope (1 W optical) as the purchased item per plan rule 6
- Duty section 2 prose carries the seed figure 500 x 500 x 800; the node 1200 x 600 x 800 governs, the older figure named (hold W12)
- Guard frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/LITHO_ALIGN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LITHO_ALIGN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/LITHO_ALIGN/litho_align.py`
- `models/mfg/LITHO_ALIGN/draw_litho_align.py`
- `models/mfg/LITHO_ALIGN/bom.csv`
- `models/mfg/LITHO_ALIGN/fasteners.csv`
- `models/mfg/LITHO_ALIGN/check.json`
- `models/mfg/LITHO_ALIGN/WORK_ORDER.md`
- `build export `models/mfg/LITHO_ALIGN/export/litho_align.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-SC (route hold); holds named in WORK_ORDER W12.
