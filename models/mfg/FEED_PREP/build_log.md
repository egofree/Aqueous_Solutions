# FEED_PREP build log - X-FARM M3 roster acceptance

Date: 2026-10-27. Authority: AQS-PLAN-006 section 5 (the FLUX_PREP-class build+check acceptance;
the 8-sheet drawing set follows as its own pass). Model source: `models/mfg/farm_hab.py` (cabinet class)
+ `models/mfg/FEED_PREP/params.json`.

## Basis

- Envelope 1300 x 900 x 1700 mm, claimed on the graph (params.size_mm): mixer + grinder + HP drier cabinet at the 0.6 kW duty (A-M-426) (X-FARM sec3) (sheet-metal cabinet class, 5 mm)
- Material class: SS304 (the unit's issued sec3 selection).

## Evidence (check.json is the machine-checked copy)

1. Builds headless from params.json; STEP + STL in `export/`.
2. Bounding box [1300.0, 900.0, 1700.0] sits inside the claimed envelope: True.
3. 3 solid(s), all valid: True.
4. Empty mass 491.3 kg (wall volume x the class density; sheet-gauge panels, hollow housings).

## Follow-on

- 8-sheet drawing set + DRAWING_REGISTER rows: own pass (the FLUX_PREP/WAX_PATTERN precedent).
- Locale note: the unit carries per the LOCALIZATION_PLAN section 5.6 scaling rules.
