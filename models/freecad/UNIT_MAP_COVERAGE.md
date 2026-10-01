# Unit ↔ FreeCAD name map — coverage (WP-D1)

| Field | Value |
|---|---|
| Doc | **AQS-UNIT-FREECAD-MAP-001** Rev A |
| Date | 2026-10-01 (America/Chicago) |
| Licence | CERN-OHL-S-2.0 |
| Graph | AQS-FLOW-GRAPH-001 Rev B (91 nodes) |
| Map | `models/freecad/unit_freecad_map.json` (hub: `cad/freecad/`) |
| Evidence | `plant.FCStd` inventory via `/usr/bin/freecadcmd` (1060 objects, 976 Part::Feature) |
| Plan | AQS-PLAN-3D-001 WP-D1 |

## Summary counts

| Status | Count |
|---|---|
| `mapped` | 56 |
| `massing_only` | 7 |
| `placeholder_skip` | 7 |
| `unmapped` | 21 |
| **Total rows** | **91** |

- Rows classified: **100%** (91/91)
- Present units mapped or massing_only: **58/79** (73.4%)
- Placeholder nodes: **12** (skip or massing_only — no invented boxes)

## Unmapped present (honest gaps)

| unit_id | sector | class | Notes |
|---|---|---|---|
| `BLACK_DIGEST` | WTR | digest | present WTR unit; no Part::Feature in plant.FCStd (NaOH_DIGEST is glass-line, no |
| `BMED_UPW_POLISH` | WTR | skid | present WTR skid; no Feature in plant.FCStd |
| `BOUNDARY_EXPORT` | DOCK | boundary | logical DOCK boundary node; no solid |
| `FAB_UPW_TANK` | FAB | tank | present FAB tank; no Feature (ROOF_TANK/CATCH_TANK are building water, not fab U |
| `GEO_HP_CLOSED_LOOP` | GEO | None | present loop topology node; no dedicated Feature (related GEO_HP / KO_GEO_GHEX / |
| `GREY_TREAT` | WTR | treat | present WTR treat; HDR_GREY_* are headers only, not treatment solids |
| `LOAD_AGG` | ELEC | load_agg | electrical aggregation logical node; no solid |
| `MEOH_FC` | MEOH | iem_fc | present MEOH; no Feature in plant.FCStd |
| `MEOH_FERM` | MEOH | ferment | present MEOH; no Feature |
| `MEOH_SYNTH` | MEOH | reactor | present MEOH; no Feature |
| `MEOH_TANK` | MEOH | tank | present MEOH; no Feature |
| `Q4_BUS` | HAB | header | thermal collector bus logical; related HX Features (CRYO_HX_Q4, MET_HX_Q4, HVAC_ |
| `S13_CLASS_TREAT` | WET | None | present WET treat class node; no Feature |
| `WS_AMMONIA` | FAB | reagent | fab reagent fork; no dedicated Feature (ETCH_RETURN is return header, not reagen |
| `WS_DOPE` | FAB | reagent | fab reagent fork; no Feature |
| `WS_HF_ED` | FAB | reagent | fab reagent fork; no Feature |
| `WS_KOH` | FAB | reagent | fab reagent fork; no Feature |
| `WS_NITRIC` | FAB | reagent | fab reagent fork; no Feature |
| `WS_PEROX` | FAB | reagent | fab reagent fork; no Feature |
| `WS_SLURRY` | FAB | reagent | fab reagent fork; no Feature |
| `WS_SOLV` | FAB | reagent | fab reagent fork; no Feature |

## Placeholder policy

| unit_id | status | freecad_names |
|---|---|---|
| `BLOW_MOLD` | `placeholder_skip` | — |
| `C29_RECYCLE` | `massing_only` | `C29_RECYCLE` |
| `CONTINUOUS_RECYCLE` | `placeholder_skip` | — |
| `ELECTRODE_COAT` | `placeholder_skip` | — |
| `GEO_ORC` | `massing_only` | `GEO_ORC` |
| `GLASS_BURNOUT` | `massing_only` | `BURNOUT_ROTARY` |
| `GLASS_MILL` | `massing_only` | `MILL` |
| `GLASS_RINSE` | `massing_only` | `RINSE_DEWATER` |
| `LITHO_STUB` | `placeholder_skip` | — |
| `REMIN` | `placeholder_skip` | — |
| `SOLAR_PV_CELL` | `placeholder_skip` | — |
| `VCD_TRAIN` | `placeholder_skip` | — |

## Alias rows (unit_id ≠ Feature Name)

| unit_id | FreeCAD Name(s) | Builder |
|---|---|---|
| `AFTERBURNER_FLUE` | `HX7_FLUE_JACKET` | `gas_handling.py` |
| `BMED_ACID` | `BMED_REGEN` | `wet_products.py` |
| `BMED_BASE` | `BMED_REGEN` | `wet_products.py` |
| `CRYO_AHU_COND_CONDENSABLE` | `CRYO_AHU_COND` | `cryo.py` |
| `FLOAT_SINK` | `FLOAT_DEWATER`, `SINK_DEWATER` | `leach_cstr.py` |
| `GEO_GHEX` | `KO_GEO_GHEX` | `electrical_yard.py` |
| `GLASS_BURNOUT` | `BURNOUT_ROTARY` | `glass_line.py` |
| `GLASS_DIGEST` | `NaOH_DIGEST` | `glass_line.py` |
| `GLASS_MILL` | `MILL` | `glass_line.py` |
| `GLASS_RINSE` | `RINSE_DEWATER` | `glass_line.py` |
| `HDR_O2` | `HDR_O2_N`, `HDR_O2_S`, `HDR_O2_E`, `HDR_O2_W` | `pipe_services.py` |
| `HDR_UPW` | `HDR_UPW_N`, `HDR_UPW_S`, `HDR_UPW_E`, `HDR_UPW_W` | `pipe_services.py` |
| `HOPPER` | `HOPPER_SHREDDER` | `leach_cstr.py` |
| `NORTH_DOCK` | `DOCK`, `DOCK_APRON_N`, `DOCK_DOOR_N` | `building_stack.py` |
| `OIL_DRYER` | `DRYER` | `oil_line.py` |
| `OIL_FRAC` | `FRACTIONATOR` | `oil_line.py` |
| `OIL_PYRO` | `INDUCTION_PYROLYZER` | `oil_line.py` |
| `POLISH_BANK` | `PK_1`, `PK_2`, `PK_3`, `PK_6`, `PK_7`, `PK_8`, `PK_9` | `wet_products.py` |
| `TERRACE_IRRIG` | `TERRACE_IRRIG_HDR_S` | `building_stack.py` |

## Full table

| unit_id | status | freecad_names | builder | group_path |
|---|---|---|---|---|
| `ACID_POLISH_SCRUB` | `mapped` | `ACID_POLISH_SCRUB` | `gas_handling.py` | Plant/Process/Gas |
| `AFTERBURNER` | `mapped` | `AFTERBURNER` | `oil_line.py` | Plant/Process/Oil_Glass |
| `AFTERBURNER_FLUE` | `mapped` | `HX7_FLUE_JACKET` | `gas_handling.py` | Plant/Process/Gas |
| `ALK_SCRUBBER` | `mapped` | `ALK_SCRUBBER` | `gas_handling.py` | Plant/Process/Gas |
| `BACKUP_GEN` | `mapped` | `BACKUP_GEN` | `electrical_yard.py` | Plant/Electrical |
| `BAGHOUSE` | `mapped` | `BAGHOUSE` | `gas_handling.py` | Plant/Process/Gas |
| `BLACK_DIGEST` | `unmapped` | — | — | — |
| `BLOW_MOLD` | `placeholder_skip` | — | — | — |
| `BMED_ACID` | `massing_only` | `BMED_REGEN` | `wet_products.py` | Plant/Process/Wet |
| `BMED_BASE` | `massing_only` | `BMED_REGEN` | `wet_products.py` | Plant/Process/Wet |
| `BMED_UPW_POLISH` | `unmapped` | — | — | — |
| `BOUNDARY_EXPORT` | `unmapped` | — | — | — |
| `C29_RECYCLE` | `massing_only` | `C29_RECYCLE` | `oil_line.py` | Plant/Process/Oil_Glass |
| `CATCH_TANK` | `mapped` | `CATCH_TANK` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `COLD_MILL` | `mapped` | `COLD_MILL` | `mfg_shop.py` | Plant/Process/Wet |
| `CONTINUOUS_RECYCLE` | `placeholder_skip` | — | — | — |
| `CRU` | `mapped` | `CRU` | `wet_products.py` | Plant/Process/Wet |
| `CRYO_AHU` | `mapped` | `CRYO_AHU` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_AHU_COND_CONDENSABLE` | `mapped` | `CRYO_AHU_COND` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_CO2` | `mapped` | `CRYO_CO2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_DED_COOL` | `mapped` | `CRYO_DED_COOL` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_H2` | `mapped` | `CRYO_H2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_HX_Q4` | `mapped` | `CRYO_HX_Q4` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_N2` | `mapped` | `CRYO_N2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_O2` | `mapped` | `CRYO_O2` | `cryo.py` | Plant/Process/Cryo |
| `ELECTRODE_COAT` | `placeholder_skip` | — | — | — |
| `EW_1` | `mapped` | `EW_1` | `leach_cstr.py` | Plant/Process/Wet |
| `EW_2` | `mapped` | `EW_2` | `leach_cstr.py` | Plant/Process/Wet |
| `EW_9` | `mapped` | `EW_9` | `leach_cstr.py` | Plant/Process/Wet |
| `FAB_UPW_TANK` | `unmapped` | — | — | — |
| `FLOAT_SINK` | `mapped` | `FLOAT_DEWATER`, `SINK_DEWATER` | `leach_cstr.py` | Plant/Process/Wet |
| `FUEL_CELL` | `mapped` | `FUEL_CELL` | `electrical_yard.py` | Plant/Electrical |
| `GAS_ATOMIZER` | `mapped` | `GAS_ATOMIZER` | `mfg_shop.py` | Plant/Process/Wet |
| `GEO_GHEX` | `mapped` | `KO_GEO_GHEX` | `electrical_yard.py` | Plant/Electrical |
| `GEO_HP` | `mapped` | `GEO_HP` | `electrical_yard.py` | Plant/Electrical |
| `GEO_HP_CLOSED_LOOP` | `unmapped` | — | — | — |
| `GEO_ORC` | `massing_only` | `GEO_ORC` | `electrical_yard.py` | Plant/Electrical |
| `GLASS_BURNOUT` | `massing_only` | `BURNOUT_ROTARY` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_DIGEST` | `mapped` | `NaOH_DIGEST` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_MILL` | `massing_only` | `MILL` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_RINSE` | `massing_only` | `RINSE_DEWATER` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GREY_TREAT` | `unmapped` | — | — | — |
| `GROW_BED` | `mapped` | `GROW_BED` | `farm.py` | Plant/Life/Farm |
| `H2_DRYER` | `mapped` | `H2_DRYER` | `gas_handling.py` | Plant/Process/Gas |
| `HABITATION` | `mapped` | `HABITATION` | `habitation.py` | Plant/Life/Habitation |
| `HDR_H2` | `mapped` | `HDR_H2` | `build_wet.py` | Plant/Process/Wet |
| `HDR_O2` | `mapped` | `HDR_O2_N`, `HDR_O2_S`, `HDR_O2_E`, `HDR_O2_W` | `pipe_services.py` | Plant/Life/Habitation |
| `HDR_UPW` | `mapped` | `HDR_UPW_N`, `HDR_UPW_S`, `HDR_UPW_E`, `HDR_UPW_W` | `pipe_services.py` | Plant/Life/Habitation |
| `HOPPER` | `mapped` | `HOPPER_SHREDDER` | `leach_cstr.py` | Plant/Process/Wet |
| `HYDRO_SET` | `mapped` | `HYDRO_SET` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `LEACH_CSTR_1` | `mapped` | `LEACH_CSTR_1` | `leach_cstr.py` | Plant/Process/Wet |
| `LITHO_STUB` | `placeholder_skip` | — | — | — |
| `LOAD_AGG` | `unmapped` | — | — | — |
| `MEOH_FC` | `unmapped` | — | — | — |
| `MEOH_FERM` | `unmapped` | — | — | — |
| `MEOH_SYNTH` | `unmapped` | — | — | — |
| `MEOH_TANK` | `unmapped` | — | — | — |
| `MET_AHU` | `mapped` | `MET_AHU` | `mfg_shop.py` | Plant/Process/Wet |
| `MET_HX_Q4` | `mapped` | `MET_HX_Q4` | `mfg_shop.py` | Plant/Process/Wet |
| `MET_MELT` | `mapped` | `MET_MELT` | `mfg_shop.py` | Plant/Process/Wet |
| `MET_SCRUB` | `mapped` | `MET_SCRUB` | `mfg_shop.py` | Plant/Process/Wet |
| `MFG_SHOP` | `mapped` | `MFG_SHOP` | `mfg_shop.py` | Plant/Process/Wet |
| `NORTH_DOCK` | `mapped` | `DOCK`, `DOCK_APRON_N`, `DOCK_DOOR_N` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `NUTRIENT_DOSE` | `mapped` | `NUTRIENT_DOSE` | `farm.py` | Plant/Life/Farm |
| `OIL_DRYER` | `mapped` | `DRYER` | `oil_line.py` | Plant/Process/Oil_Glass |
| `OIL_FRAC` | `mapped` | `FRACTIONATOR` | `oil_line.py` | Plant/Process/Oil_Glass |
| `OIL_PYRO` | `mapped` | `INDUCTION_PYROLYZER` | `oil_line.py` | Plant/Process/Oil_Glass |
| `POLISH_BANK` | `mapped` | `PK_1`, `PK_2`, `PK_3`, `PK_6`, `PK_7`, `PK_8`, `PK_9` | `wet_products.py` | Plant/Process/Wet |
| `PV_ARRAY` | `mapped` | `PV_ARRAY` | `electrical_yard.py` | Plant/Electrical |
| `Q4_BUS` | `unmapped` | — | — | — |
| `RECTIFIER` | `mapped` | `RECTIFIER` | `electrical_yard.py` | Plant/Electrical |
| `REMIN` | `placeholder_skip` | — | — | — |
| `ROOF_TANK` | `mapped` | `ROOF_TANK` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `S13_CLASS_TREAT` | `unmapped` | — | — | — |
| `SALT_FEED` | `mapped` | `SALT_FEED` | `wet_products.py` | Plant/Process/Wet |
| `SOLAR_PV_CELL` | `placeholder_skip` | — | — | — |
| `SOL_ARK_60K` | `mapped` | `SOL_ARK_60K` | `electrical_yard.py` | Plant/Electrical |
| `TERRACE_IRRIG` | `mapped` | `TERRACE_IRRIG_HDR_S` | `building_stack.py` | Plant/Building/Terraces |
| `VCD_TRAIN` | `placeholder_skip` | — | — | — |
| `WAFER_FAB` | `mapped` | `WAFER_FAB` | `wafer_fab.py` | Plant/Process/Wet |
| `WET_BENCH` | `mapped` | `WET_BENCH` | `wafer_fab.py` | Plant/Process/Wet |
| `WIRE_DRAW` | `mapped` | `WIRE_DRAW` | `mfg_shop.py` | Plant/Process/Wet |
| `WS_AMMONIA` | `unmapped` | — | — | — |
| `WS_DOPE` | `unmapped` | — | — | — |
| `WS_HF_ED` | `unmapped` | — | — | — |
| `WS_KOH` | `unmapped` | — | — | — |
| `WS_NITRIC` | `unmapped` | — | — | — |
| `WS_PEROX` | `unmapped` | — | — | — |
| `WS_SLURRY` | `unmapped` | — | — | — |
| `WS_SOLV` | `unmapped` | — | — | — |
| `ZNBR2` | `mapped` | `ZNBR2` | `electrical_yard.py` | Plant/Electrical |

## Method

1. Open hub `cad/freecad/plant.FCStd` with freecadcmd; list Name, Label, TypeId.
2. Cross-check `add(doc, "NAME", …)` in sector builders (`build_plant.py` attach chain).
3. Classify every graph `unit_id` — **no invented geometry**; honest `unmapped` / `placeholder_skip`.
4. Bridge loads map and reports coverage % (see `graph_geometry_bridge.py`).

---

CERN-OHL-S-2.0. Planning-local coverage; map JSON also in share `models/freecad/`.
