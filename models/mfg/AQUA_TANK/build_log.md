# AQUA_TANK build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (tank class)
+ `models/mfg/AQUA_TANK/params.json`.

## Basis

- Envelope 2100 x 1100 x 1100 mm, claimed on the graph (params.size_mm): 2.0 m3 working volume at the 60 kg stock / 30 kg-per-m3 class (TECHTREE tilapia glossary; A-M-415): 2000 x 1000 x 1000 ID + 50 walls, EPDM-lined HDPE (X-FARM sec3)
- Material class: HDPE (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [2100.0, 1100.0, 1100.0] sits inside the claimed envelope: True.
3. 1 solid(s), all valid: True.
4. Empty mass 2394.2 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
