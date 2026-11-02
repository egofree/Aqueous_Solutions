# Build log - MEOH_FERM

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_FERM.md`; envelope per `models/mfg/MEOH_FERM/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MEOH_FERM/meoh_ferm.py`

## Checks

- Build bbox 425 x 425 x 600 mm against the 425 x 425 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MEOH_FERM/export/meoh_ferm.step`; export STL closed and manifold, 5 solid(s); `cad/stl/MEOH_FERM.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/MEOH_FERM.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 48 h working volume V = 0.0007 m3 (duty section 2) is an existing holdup basis - the model level (z 305.1) is set by it and reported; no new residence-time claim
- Agitation per the node mixer row: daily recirculation pump (envelope, plan rule 6) with a DN15 loop; no top-entry agitator named - none drawn (W12)
- PVC-U wetted per duty section 3; the node HDPE row superseded for the wetted parts (holds, W12); the 600 datums clamped to 570.7
- The skid chain fuses to one solid; the face stubs stay separate until the connecting lines make their joints (check.solids_note)
- BOM `models/mfg/MEOH_FERM/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_FERM/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MEOH_FERM/meoh_ferm.py`
- `models/mfg/MEOH_FERM/draw_meoh_ferm.py`
- `models/mfg/MEOH_FERM/bom.csv`
- `models/mfg/MEOH_FERM/fasteners.csv`
- `models/mfg/MEOH_FERM/check.json`
- `models/mfg/MEOH_FERM/WORK_ORDER.md`
- `build export `models/mfg/MEOH_FERM/export/meoh_ferm.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
