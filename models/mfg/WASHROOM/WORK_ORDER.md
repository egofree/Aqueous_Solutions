# WASHROOM work order (M3 roster acceptance)

1. Source: `washroom.py` (CadQuery) reads the plant graph through the shared reader (`models/mfg/lib/graph_node.py`) and rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`), the AQUA_TANK pattern; the envelope (size_mm 3000 x 2000 x 2400), graph revision and nozzle schedule come from the node and the unit CSV. Run: `python3 models/mfg/WASHROOM/washroom.py`.
2. 8 m2 fitout shell (A-M-419; AQS-HAB-001) (X-HAB sec3)
3. Fit the sec3 material class (FRP); liner per params where specified.
4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass 842.2 kg; all 4 schedule rows of `docs-authority/nozzles/WASHROOM.csv` drawn).

Holds. (1) The drawing set in `drawings/` predates this build; it regenerates with the unit drawing round (`draw_washroom.py` is the drawing-set driver, not the model). (2) `docs-authority/duties/WASHROOM.md` section 7 still names `draw_washroom.py` as the manufacturing model; the model is `washroom.py` (the duty page updates outside this folder). (3) The fixture set and the nozzle elevations are study proportions (W12 class): the schedule z 800 vent datum predates the 2400 box and is drawn flush at the envelope top; the fixture envelopes are study sheet proportions, maker prints govern at order.
