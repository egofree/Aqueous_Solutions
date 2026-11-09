# RABBIT_HUTCH work order (M3 roster acceptance)

1. Source: `rabbit_hutch.py` (CadQuery, on the shared close-out builder `models/mfg/farm_closeout.py`) reads the plant graph through `models/mfg/lib/graph_node.py` (AQUA_TANK pattern) and rebuilds every solid; the `envelope` and `layout` blocks it writes to `params.json` are builder-owned and pass through tracker regeneration.
2. 3 rabbitry positions x 0.5 m2 with rest mats (A-M-423; TECHTREE rabbits.md) (X-FARM sec3)
3. Fit the sec3 material class (HDG_steel); liner per params where specified.
4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass 224.4 kg).
