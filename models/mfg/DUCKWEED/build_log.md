# DUCKWEED build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (tray class)
+ `models/mfg/DUCKWEED/params.json`.

## Basis

- Envelope 30100 x 10100 x 700 mm, claimed on the graph (params.size_mm): 300 m2 raceway at the A-M-420 revision, 400 mm water + 100 freeboard + 200 berm: a lined civil basin, HDPE/EPDM (X-FARM sec3)
- Material class: HDPE (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [30100.0, 10100.0, 700.0] sits inside the claimed envelope: True.
3. 1 solid(s), all valid: True.
4. Empty mass 4855.1 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
