# REC_DAYROOM build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (room class)
+ `models/mfg/REC_DAYROOM/params.json`.

## Basis

- Envelope 5000 x 4000 x 2400 mm, claimed on the graph (params.size_mm): 20 m2 fitout shell (A-M-419) (X-HAB sec3)
- Material class: aluminium (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [5000.0, 4000.0, 2380.0] sits inside the claimed envelope: True.
3. 1 solid(s), all valid: True.
4. Empty mass 2451.8 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
