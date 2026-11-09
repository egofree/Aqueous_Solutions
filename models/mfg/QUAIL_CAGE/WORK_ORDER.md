# QUAIL_CAGE work order (M3 roster acceptance)

1. Source: `quail_cage.py` (CadQuery, on the shared close-out builder `models/mfg/farm_closeout.py`) reads the plant graph through `models/mfg/lib/graph_node.py` (AQUA_TANK pattern) and rebuilds every solid; the `envelope` and `layout` blocks it writes to `params.json` are builder-owned and pass through tracker regeneration.
2. 20-hen Coturnix battery, 4 tiers x 0.075 m2/cage at the 0.025 kg/d ration class (A-M-422; TECHTREE coturnix.md) (X-FARM sec3)
3. Fit the sec3 material class (HDG_steel); liner per params where specified.
4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass 185.8 kg).
