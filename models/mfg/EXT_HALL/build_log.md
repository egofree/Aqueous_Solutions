# Build log - EXT_HALL

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EXT_HALL.md`; envelope per `models/mfg/EXT_HALL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/EXT_HALL/ext_hall.py`

## Checks

- Build bbox 186000 x 174000 x 6000 mm against the 186000 x 174000 x 6000 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/EXT_HALL/export/ext_hall.step`; export STL closed and manifold, 1 solid(s); `cad/stl/EXT_HALL.stl` replaced from the build (ASCII, metres)
- Nozzles: none - the duty section 4 states None (electrical feed SF-EXT_HALL, air-source heat pumps D77, GEO_GHEX not coupled); no nozzle schedule is issued and no nozzle hardware is drawn (hold, WORK_ORDER W12)
- Building massing per the node size_note and the placement_seed blocks (the authority): 162 x 174 m + 24 x 156 m L-shape, 6 m eave; slab 150 mm, wall panels 300 mm, roof deck 100 mm, portal-frame column grid at every 6 m grid point inside the L (803 columns, 31 x 29 bays)
- No process internals: the fitout programme stays the duty-sheet open item; the roof PV interface is the PV_ARRAY model's scope - nothing doubled
- Route hold carried by name (building class); column/wall/roof sections are massing values - the structural design is the X-BLD lane's (holds, WORK_ORDER W12)
- BOM `models/mfg/EXT_HALL/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EXT_HALL/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/EXT_HALL/ext_hall.py`
- `models/mfg/EXT_HALL/draw_ext_hall.py`
- `models/mfg/EXT_HALL/bom.csv`
- `models/mfg/EXT_HALL/fasteners.csv`
- `models/mfg/EXT_HALL/check.json`
- `models/mfg/EXT_HALL/WORK_ORDER.md`
- `build export `models/mfg/EXT_HALL/export/ext_hall.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
