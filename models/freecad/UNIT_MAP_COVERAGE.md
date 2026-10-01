# Unit ↔ FreeCAD name map — coverage

| Field | Value |
|---|---|
| Doc | **AQS-UNIT-FREECAD-MAP-001** Rev B |
| Date | 2026-10-01 (America/Chicago) |
| Licence | CERN-OHL-S-2.0 |
| Graph | AQS-FLOW-GRAPH-001 Rev B (91 nodes) |
| Map | `models/freecad/unit_freecad_map.json` (hub: `cad/freecad/`) |
| Evidence | `plant.FCStd` inventory via `/usr/bin/freecadcmd` (1114 objects, 1030 Part::Feature) |
| Plan | AQS-PLAN-3D-001 — CAD-M1 massing done 2026-10-01 |

## Summary counts

| Status | Count |
|---|---|
| `mapped` | 56 |
| `massing_only` | 25 |
| `placeholder_skip` | 7 |
| `unmapped` | 3 |
| **Total rows** | **91** |

- Rows classified: **100%** (91/91)
- Present units mapped or massing_only: **76/79** (96.2%)
- Placeholder nodes: **12** (skip or massing_only — no placeholder solids)

## CAD-M1 massing — **done** 2026-10-01 (America/Chicago)

| Field | Value |
|---|---|
| Id | **CAD-M1** (plan id WP-D1b) |
| Builder | `d1b_massing.py` (hooked from `build_plant.py`) |
| Dims | `D1B_TBD_*` aliases of existing STUB/TOTE/DIGEST/P_TANK/BMED params — **not** PE nameplates / rates |
| Features added (18) | Names = `unit_id` Part::Feature |
| Remain unmapped / logical (3) | `BOUNDARY_EXPORT`, `LOAD_AGG`, `Q4_BUS` |
| Present coverage | **76/79 (96.2%)** |

### Features added

`MEOH_FC`, `MEOH_FERM`, `MEOH_SYNTH`, `MEOH_TANK`, `BLACK_DIGEST`, `BMED_UPW_POLISH`, `GREY_TREAT`, `S13_CLASS_TREAT`, `FAB_UPW_TANK`, `WS_AMMONIA`, `WS_DOPE`, `WS_HF_ED`, `WS_KOH`, `WS_NITRIC`, `WS_PEROX`, `WS_SLURRY`, `WS_SOLV`, `GEO_HP_CLOSED_LOOP`

## Unmapped present (logical-only remaining)

| unit_id | sector | class | Notes |
|---|---|---|---|
| `BOUNDARY_EXPORT` | DOCK | boundary | logical DOCK boundary node; no solid |
| `LOAD_AGG` | ELEC | load_agg | electrical aggregation logical node; no solid |
| `Q4_BUS` | HAB | header | thermal collector bus logical; related HX Features (CRYO_HX_Q4, MET_HX_Q4, HVAC_Q4, FC_HX_ |

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
| `BLACK_DIGEST` | `massing_only` | `BLACK_DIGEST` | `d1b_massing.py` | Plant/Life/Habitation |
| `BLOW_MOLD` | `placeholder_skip` | — | `—` | — |
| `BMED_ACID` | `massing_only` | `BMED_REGEN` | `wet_products.py` | Plant/Process/Wet |
| `BMED_BASE` | `massing_only` | `BMED_REGEN` | `wet_products.py` | Plant/Process/Wet |
| `BMED_UPW_POLISH` | `massing_only` | `BMED_UPW_POLISH` | `d1b_massing.py` | Plant/Process/Wet |
| `BOUNDARY_EXPORT` | `unmapped` | — | `—` | — |
| `C29_RECYCLE` | `massing_only` | `C29_RECYCLE` | `oil_line.py` | Plant/Process/Oil_Glass |
| `CATCH_TANK` | `mapped` | `CATCH_TANK` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `COLD_MILL` | `mapped` | `COLD_MILL` | `mfg_shop.py` | Plant/Process/Wet |
| `CONTINUOUS_RECYCLE` | `placeholder_skip` | — | `—` | — |
| `CRU` | `mapped` | `CRU` | `wet_products.py` | Plant/Process/Wet |
| `CRYO_AHU` | `mapped` | `CRYO_AHU` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_AHU_COND_CONDENSABLE` | `mapped` | `CRYO_AHU_COND` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_CO2` | `mapped` | `CRYO_CO2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_DED_COOL` | `mapped` | `CRYO_DED_COOL` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_H2` | `mapped` | `CRYO_H2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_HX_Q4` | `mapped` | `CRYO_HX_Q4` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_N2` | `mapped` | `CRYO_N2` | `cryo.py` | Plant/Process/Cryo |
| `CRYO_O2` | `mapped` | `CRYO_O2` | `cryo.py` | Plant/Process/Cryo |
| `ELECTRODE_COAT` | `placeholder_skip` | — | `—` | — |
| `EW_1` | `mapped` | `EW_1` | `leach_cstr.py` | Plant/Process/Wet |
| `EW_2` | `mapped` | `EW_2` | `leach_cstr.py` | Plant/Process/Wet |
| `EW_9` | `mapped` | `EW_9` | `leach_cstr.py` | Plant/Process/Wet |
| `FAB_UPW_TANK` | `massing_only` | `FAB_UPW_TANK` | `d1b_massing.py` | Plant/Process/Wet |
| `FLOAT_SINK` | `mapped` | `FLOAT_DEWATER`, `SINK_DEWATER` | `leach_cstr.py` | Plant/Process/Wet |
| `FUEL_CELL` | `mapped` | `FUEL_CELL` | `electrical_yard.py` | Plant/Electrical |
| `GAS_ATOMIZER` | `mapped` | `GAS_ATOMIZER` | `mfg_shop.py` | Plant/Process/Wet |
| `GEO_GHEX` | `mapped` | `KO_GEO_GHEX` | `electrical_yard.py` | Plant/Electrical |
| `GEO_HP` | `mapped` | `GEO_HP` | `electrical_yard.py` | Plant/Electrical |
| `GEO_HP_CLOSED_LOOP` | `massing_only` | `GEO_HP_CLOSED_LOOP` | `d1b_massing.py` | Plant/Electrical |
| `GEO_ORC` | `massing_only` | `GEO_ORC` | `electrical_yard.py` | Plant/Electrical |
| `GLASS_BURNOUT` | `massing_only` | `BURNOUT_ROTARY` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_DIGEST` | `mapped` | `NaOH_DIGEST` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_MILL` | `massing_only` | `MILL` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GLASS_RINSE` | `massing_only` | `RINSE_DEWATER` | `glass_line.py` | Plant/Process/Oil_Glass |
| `GREY_TREAT` | `massing_only` | `GREY_TREAT` | `d1b_massing.py` | Plant/Life/Habitation |
| `GROW_BED` | `mapped` | `GROW_BED` | `farm.py` | Plant/Life/Farm |
| `H2_DRYER` | `mapped` | `H2_DRYER` | `gas_handling.py` | Plant/Process/Gas |
| `HABITATION` | `mapped` | `HABITATION` | `habitation.py` | Plant/Life/Habitation |
| `HDR_H2` | `mapped` | `HDR_H2` | `build_wet.py` | Plant/Process/Wet |
| `HDR_O2` | `mapped` | `HDR_O2_N`, `HDR_O2_S`, `HDR_O2_E`, `HDR_O2_W` | `pipe_services.py` | Plant/Life/Habitation |
| `HDR_UPW` | `mapped` | `HDR_UPW_N`, `HDR_UPW_S`, `HDR_UPW_E`, `HDR_UPW_W` | `pipe_services.py` | Plant/Life/Habitation |
| `HOPPER` | `mapped` | `HOPPER_SHREDDER` | `leach_cstr.py` | Plant/Process/Wet |
| `HYDRO_SET` | `mapped` | `HYDRO_SET` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `LEACH_CSTR_1` | `mapped` | `LEACH_CSTR_1` | `leach_cstr.py` | Plant/Process/Wet |
| `LITHO_STUB` | `placeholder_skip` | — | `—` | — |
| `LOAD_AGG` | `unmapped` | — | `—` | — |
| `MEOH_FC` | `massing_only` | `MEOH_FC` | `d1b_massing.py` | Plant/Electrical |
| `MEOH_FERM` | `massing_only` | `MEOH_FERM` | `d1b_massing.py` | Plant/Electrical |
| `MEOH_SYNTH` | `massing_only` | `MEOH_SYNTH` | `d1b_massing.py` | Plant/Electrical |
| `MEOH_TANK` | `massing_only` | `MEOH_TANK` | `d1b_massing.py` | Plant/Electrical |
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
| `Q4_BUS` | `unmapped` | — | `—` | — |
| `RECTIFIER` | `mapped` | `RECTIFIER` | `electrical_yard.py` | Plant/Electrical |
| `REMIN` | `placeholder_skip` | — | `—` | — |
| `ROOF_TANK` | `mapped` | `ROOF_TANK` | `building_stack.py` | Plant/Building/Cores_Shafts |
| `S13_CLASS_TREAT` | `massing_only` | `S13_CLASS_TREAT` | `d1b_massing.py` | Plant/Process/Wet |
| `SALT_FEED` | `mapped` | `SALT_FEED` | `wet_products.py` | Plant/Process/Wet |
| `SOLAR_PV_CELL` | `placeholder_skip` | — | `—` | — |
| `SOL_ARK_60K` | `mapped` | `SOL_ARK_60K` | `electrical_yard.py` | Plant/Electrical |
| `TERRACE_IRRIG` | `mapped` | `TERRACE_IRRIG_HDR_S` | `building_stack.py` | Plant/Building/Terraces |
| `VCD_TRAIN` | `placeholder_skip` | — | `—` | — |
| `WAFER_FAB` | `mapped` | `WAFER_FAB` | `wafer_fab.py` | Plant/Process/Wet |
| `WET_BENCH` | `mapped` | `WET_BENCH` | `wafer_fab.py` | Plant/Process/Wet |
| `WIRE_DRAW` | `mapped` | `WIRE_DRAW` | `mfg_shop.py` | Plant/Process/Wet |
| `WS_AMMONIA` | `massing_only` | `WS_AMMONIA` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_DOPE` | `massing_only` | `WS_DOPE` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_HF_ED` | `massing_only` | `WS_HF_ED` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_KOH` | `massing_only` | `WS_KOH` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_NITRIC` | `massing_only` | `WS_NITRIC` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_PEROX` | `massing_only` | `WS_PEROX` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_SLURRY` | `massing_only` | `WS_SLURRY` | `d1b_massing.py` | Plant/Process/Wet |
| `WS_SOLV` | `massing_only` | `WS_SOLV` | `d1b_massing.py` | Plant/Process/Wet |
| `ZNBR2` | `mapped` | `ZNBR2` | `electrical_yard.py` | Plant/Electrical |



## Presence filter (done 2026-10-01 America/Chicago)

| Field | Value |
|---|---|
| Policy | `skip_disabled_and_placeholder_unless_mapped_massing` |
| Bridge | `graph_geometry_bridge.py` — `presence_filter` / `--presence-report` / `--apply-presence` / `--self-test` |
| Baseline (gold Rev B) | omit Feature set **empty** → object count **1114** unchanged (parts **1030**) |
| T6 (`LEACH_CSTR_1` `enabled=false`) | objects **1114→1113**, Part::Feature **1030→1029**, removed `LEACH_CSTR_1` |
| Logical unmapped | stay **skip** (`BOUNDARY_EXPORT`, `LOAD_AGG`, `Q4_BUS`) — no solids |
| Placeholders | skip unless map `status=massing_only` opt-in |

Envelope / structural Features not listed on skipped process units are left in place.
