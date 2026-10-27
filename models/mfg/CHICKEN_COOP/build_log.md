# CHICKEN_COOP build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (frame class)
+ `models/mfg/CHICKEN_COOP/params.json`.

## Basis

- Envelope 2500 x 1300 x 1900 mm, claimed on the graph (params.size_mm): 12 birds x 0.2 m2 floor + nest row + perch at the 0.12 kg/d ration house class (A-M-417; TECHTREE chickens.md) (X-FARM sec3)
- Material class: HDG_steel (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [2500.0, 1300.0, 1900.0] sits inside the claimed envelope: True.
3. 3 solid(s), all valid: True.
4. Empty mass 1050.0 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
