# Site profile, baseline profile and loader

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev C, AQS-PLAN-007 (task X-LOC-02).

## Change

- `flow_graph/schema/site_profile.schema.json` lists the profile groups and, under `x-groups`, the entries each group must carry and whether the group must carry entries at every site.
- `flow_graph/param/sites/baseline.json` holds the study site values with their present references and register ids. Entries that supply a driver name it in `binds`.
- `flow_graph/param/site.py` loads and validates the profile chosen by `AQS_SITE` (the baseline when unset). A missing group, a missing required entry, an entry without units or a basis, an unknown reference key, or a group with no entries and no reason or task id is an error. An unknown site id is an error.
- `drivers.load()` applies the bound entries. The units must match the driver.
- `water_tower.py`, `_water_tower.py`, `_relief_register.py`, `_model_workbook.py`, `models/freecad/params.py`, `models/freecad/cryo.py` and the design tool's driver listing now read the drivers through the loader.
- The power sizing cache key includes the site profiles, the schema and the selected site.
- `python3 -m flow_graph.param.regen` refuses a site other than the baseline until the output namespaces exist (X-LOC-04).

## Baseline

With the baseline profile the resolved drivers equal `drivers.json` entry for entry (`flow_graph/param/test_site_profile.py`). A full regeneration changed no generated output except the module list in the design check register, which gained `flow_graph/param/site.py`.

## Check

`scripts/check_all.sh --full` passes.
