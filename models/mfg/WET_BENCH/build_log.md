# Build log - WET_BENCH

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WET_BENCH.md`; envelope per `models/mfg/WET_BENCH/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WET_BENCH/wet_bench.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WET_BENCH/export/wet_bench.step`; export STL closed and manifold, 12 solid(s); `cad/stl/WET_BENCH.stl` replaced from the build (ASCII, metres)
- Nozzles: all 13 rows of `docs-authority/nozzles/WET_BENCH.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Bench per the node equipment list: SC1/SC2 baths 10 L at 80 C with immersion heater envelopes (2.479 kWh/d each), DHF etch bath at ambient, DIW rinse bay; bath arrangement and the unstated bath sizes are the layout choice (W12)
- Wetted material per duty section 3: PVC-U per AQS-STD-002 M1/M2, no metal wetted part; the 80 C baths are CPVC per the duty 60 C rule (the node equipment rows give the temperatures); the node rows name PP tanks, the duty selection governs (plan rule 5; hold W12)
- A-MACH guard: the four-post hold-down frame pins the registry box so the build fills the envelope (X-PAR-04); 8 slab anchors in fasteners.csv
- BOM `models/mfg/WET_BENCH/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WET_BENCH/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WET_BENCH/wet_bench.py`
- `models/mfg/WET_BENCH/draw_wet_bench.py`
- `models/mfg/WET_BENCH/bom.csv`
- `models/mfg/WET_BENCH/fasteners.csv`
- `models/mfg/WET_BENCH/check.json`
- `models/mfg/WET_BENCH/WORK_ORDER.md`
- `build export `models/mfg/WET_BENCH/export/wet_bench.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
