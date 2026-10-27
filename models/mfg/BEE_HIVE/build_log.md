# BEE_HIVE build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (hive class)
+ `models/mfg/BEE_HIVE/params.json`.

## Basis

- Envelope 600 x 500 x 1100 mm, claimed on the graph (params.size_mm): 10-frame deep + medium + stand (A-M-424; TECHTREE beekeeping) (X-FARM sec3)
- Material class: pine (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [650.0, 550.0, 1150.0] sits inside the claimed envelope: False.
3. 3 solid(s), all valid: True.
4. Empty mass 176.1 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
