# Build log - AFTERBURNER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-HX; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AFTERBURNER.md`; envelope per `models/mfg/AFTERBURNER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/AFTERBURNER/afterburner.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/AFTERBURNER/export/afterburner.step`; export STL closed and manifold, 12 solid(s); `cad/stl/AFTERBURNER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 12 rows of `docs-authority/nozzles/AFTERBURNER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Machine: combustion chamber ID 200 x 600 per duty section 8 (AQS-DUTY-063 Rev B section 6, X-SAN-01), >= 850 C for >= 2 s (EU IED Art. 50); steel wall 6 and refractory 50 are study values (holds, W12)
- A-HX: chamber volume 0.01885 m3; residence at the AFTERBURNER_FLUE node design flow 0.0018 m3/s is 10.5 s against the >= 2 s requirement - reported, not called a calculated design (the duty claims no heat rate)
- Purchased envelopes per plan rule 6 from the node equipment list: burner + ignition + BMS 0.05 kW, flue ID fan 0.1332 kW, dampers + flame monitor 0.01 kW; burner detail open on the duty (hold, W12)
- Schedule N4/N5 rows repaired to the schedule quoting (unquoted comma in 'Q1 flue, not Q4' shifted face and height); change record in notes/glass_oilgas_m3_2026-11-02.md
- BOM `models/mfg/AFTERBURNER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/AFTERBURNER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/AFTERBURNER/afterburner.py`
- `models/mfg/AFTERBURNER/draw_afterburner.py`
- `models/mfg/AFTERBURNER/bom.csv`
- `models/mfg/AFTERBURNER/fasteners.csv`
- `models/mfg/AFTERBURNER/check.json`
- `models/mfg/AFTERBURNER/WORK_ORDER.md`
- `build export `models/mfg/AFTERBURNER/export/afterburner.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-HX; holds named in WORK_ORDER W12.
