# Build log - EVAP_BASE

Date: 2026-11-04. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EVAP_BASE.md`; envelope per `models/mfg/EVAP_BASE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/EVAP_BASE/evap_base.py`

## Checks

- Build bbox 1250 x 800 x 3101 mm against the 1250 x 800 x 3100 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/EVAP_BASE/export/evap_base.step`; export STL closed and manifold, 33 solid(s); `cad/stl/EVAP_BASE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/EVAP_BASE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-HX: bundle 20 tubes, 2.356 m2 drawn against the booked 2.33 m2 (latent / (U 1500 x 6 K) on the node 20.95 kW duty; AQS-DUTY-060 section 1)
- The X-MFG-30 MVR idiom in nickel for the NaOH service: DN350 body, separator with mesh pad, blower and interchanger envelopes (plan rule 6)
- Unit-owned builder: the unit folder script replaces the evap_mvr.py EVAP_BASE expansion, so the style pass never clobbers the build
- Route-class hold named: evaporator carries no section 4 class (W12(1)); pilot U and bench leach stay the open duty items (W12(6))
- BOM `models/mfg/EVAP_BASE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EVAP_BASE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/EVAP_BASE/evap_base.py`
- `models/mfg/EVAP_BASE/draw_evap_base.py`
- `models/mfg/EVAP_BASE/bom.csv`
- `models/mfg/EVAP_BASE/fasteners.csv`
- `models/mfg/EVAP_BASE/check.json`
- `models/mfg/EVAP_BASE/WORK_ORDER.md`
- `build export `models/mfg/EVAP_BASE/export/evap_base.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
