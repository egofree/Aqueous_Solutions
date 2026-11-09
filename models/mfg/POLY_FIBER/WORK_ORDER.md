# POLY_FIBER work order (M3 roster acceptance)

1. W1 Source. `poly_fiber.py` (CadQuery) reads the plant graph through the shared reader (`models/mfg/lib/graph_node.py`) and rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`), the AQUA_TANK pattern: the envelope, graph revision and nozzle schedule come from the node and the unit CSV; the form class, wall and material class are builder-owned params. Cut and join the cabinet shell per `models/mfg/POLY_FIBER/params.json` (size_mm 3100 x 1300 x 1900).
2. bench-scale melt-spin line: extruder + spinnerette + quench + winder at the 0.09 kg/d draw (A-M-429) (X-POLY sec3) (sheet-metal cabinet class, 5 mm)
3. Fit the sec3 material class (SS304); liner per params where specified.
4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass per `check.json` `part_mass_kg` - 1147.0 kg at the 2026-11-09 close-out rebuild).
