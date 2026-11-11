# Build log - GROW_BED

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GROW_BED.md`; envelope per `models/mfg/GROW_BED/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GROW_BED/grow_bed.py`

## Checks

- Build bbox 7310 x 4030 x 910.6 mm against the 7310 x 4030 x 911 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GROW_BED/export/grow_bed.step`; export STL closed and manifold, 4 solid(s); `cad/stl/GROW_BED.stl` replaced from the build (ASCII, metres)
- Nozzles: all 22 rows of `docs-authority/nozzles/GROW_BED.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Crop grow bed per the node area_basis (A-M-229): HDPE basin + EPDM liner, interior 7280 x 4000 mm = 29.12 m2, LECA media envelope at a 250 mm study depth, drain sump at the bay corner (A-FARM: liner and drain drawn), LED canopy at the node 2.0463 kW stamp (A-M-144)
- A-FARM: bed area matches the node, NOT shrunk to fit the study box - the full bed is the export/ build; the registry carries the 2000 x 1000 x 400 bay module (the CRYO_ASU X-PAR-04 treatment) and the export bbox misfit is section-7-reported, nothing resized (plan rule 3)
- 22 schedule rows verbatim; the z 600 canopy rows drawn at the envelope top (stale datum, hold W12); media depth/sump/canopy height study values (holds, WORK_ORDER W12)
- BOM `models/mfg/GROW_BED/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GROW_BED/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GROW_BED/grow_bed.py`
- `models/mfg/GROW_BED/draw_grow_bed.py`
- `models/mfg/GROW_BED/bom.csv`
- `models/mfg/GROW_BED/fasteners.csv`
- `models/mfg/GROW_BED/check.json`
- `models/mfg/GROW_BED/WORK_ORDER.md`
- `build export `models/mfg/GROW_BED/export/grow_bed.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; holds named in WORK_ORDER W12.
