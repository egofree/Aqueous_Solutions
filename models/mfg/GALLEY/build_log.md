# GALLEY build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (room class)
+ `models/mfg/GALLEY/params.json`.

## Basis

- Envelope 4000 x 3000 x 2400 mm, claimed on the graph (params.size_mm): 12 m2 fitout shell at the A-M-419 room basis, 2400 ceiling (AQS-HAB-001) (X-HAB sec3)
- Material class: aluminium (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [4000.0, 3000.0, 2380.0] sits inside the claimed envelope: True.
3. 1 solid(s), all valid: True.
4. Empty mass 1744.6 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
