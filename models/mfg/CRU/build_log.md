# Build log - CRU

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRU.md`; envelope per `models/mfg/CRU/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CRU/cru.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/CRU/export/cru.step`; export STL closed and manifold, 12 solid(s); `cad/stl/CRU.stl` replaced from the build (ASCII, metres)
- Nozzles: all 13 rows of `docs-authority/nozzles/CRU.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Vessel: vertical PVC-U shell OD 520, wall 10 (study - the duty states no diameter and no wall: drawn to the envelope, holds W12), welded top and bottom, on a seat over a 20 mm plinth inside a four-post hold-down frame
- A-VES: the vessel holds 104.1 L to 100 mm below the top weld; the duty states no holdup basis for this class, so no residence time is derived
- Material per duty section 3: PVC-U wetted (AQS-STD-002 rules M1 and M2; no metal wetted part); the temperature watch is carried as a named hold (above 60 C the thermoplastic is CPVC, never metal; the graph gives no temperature for this unit)
- BOM `models/mfg/CRU/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRU/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/CRU/cru.py`
- `models/mfg/CRU/draw_cru.py`
- `models/mfg/CRU/bom.csv`
- `models/mfg/CRU/fasteners.csv`
- `models/mfg/CRU/check.json`
- `models/mfg/CRU/WORK_ORDER.md`
- `build export `models/mfg/CRU/export/cru.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
