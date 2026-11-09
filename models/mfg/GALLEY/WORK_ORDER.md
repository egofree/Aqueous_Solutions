# GALLEY work order (M3 roster acceptance)

1. Source: `galley.py` (CadQuery) reads the plant graph through the shared reader (`models/mfg/lib/graph_node.py`) and rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`), the AQUA_TANK pattern; the envelope (size_mm 4000 x 3000 x 2400), graph revision and nozzle schedule come from the node and the unit CSV. Run: `python3 models/mfg/GALLEY/galley.py`.
2. 12 m2 fitout shell at the A-M-419 room basis, 2400 ceiling (AQS-HAB-001) (X-HAB sec3)
3. Fit the sec3 material class (aluminium); liner per params where specified.
4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass 1959.4 kg; all 8 schedule rows of `docs-authority/nozzles/GALLEY.csv` drawn).

Holds. (1) The drawing set in `drawings/` predates this build; it regenerates with the unit drawing round (`draw_galley.py` is the drawing-set driver, not the model). (2) `docs-authority/duties/GALLEY.md` section 7 still names `draw_galley.py` as the manufacturing model; the model is `galley.py` (the duty page updates outside this folder). (3) The counter run, appliance envelope and nozzle elevations are study proportions (W12 class): the schedule z 800 vent datum predates the 2400 box and is drawn flush at the envelope top; the appliance is a purchased envelope, maker prints govern at order.
