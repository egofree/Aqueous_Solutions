# BIOFILTER build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (tank class)
+ `models/mfg/BIOFILTER/params.json`.

## Basis

- Envelope 1100 x 900 x 1000 mm, claimed on the graph (params.size_mm): moving-bed vessel 0.55 m3 at the 0.9 kg/d feed ammonia load, K1 media 0.2 m3 (A-M-415; TECHTREE aquaponics) (X-FARM sec3)
- Material class: HDPE (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [1100.0, 900.0, 1012.1] sits inside the claimed envelope: False.
3. 1 solid(s), all valid: True.
4. Empty mass 84.1 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
