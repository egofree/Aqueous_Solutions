# Unit ↔ FreeCAD name map — coverage

| Field | Value |
|---|---|
| Doc | **AQS-UNIT-FREECAD-MAP-001** Rev F |
| Date | 2026-11-01 (America/Chicago) |
| Licence | CERN-OHL-S-2.0 |
| Map | `models/freecad/unit_freecad_map.json` at Rev F (150 entries; 137 at Rev D, 93 at Rev C) |
| Evidence | `plant.FCStd` inventory via `/usr/bin/freecadcmd` (1181 objects, 1097 Part::Feature, 66 Mesh::Feature); CadQuery unit builders under `models/mfg/` |
| Plan | AQS-PLAN-3D-001 — CAD-M1 massing done 2026-10-01; foundry/polymers builders 2026-10-19; census re-stamp 2026-11-01 |

## Rev F (2026-11-01) — census re-stamp against graph Rev AC

The plant was rebuilt from the current builders and the census was recounted
from the new `plant.FCStd` inventory (`models/REBUILD.sh`: OpenSCAD detail
STLs recompiled with `build_stls.sh`, then `build_plant.py`; clash checks
clean). The map's `graph_revision` stamp moves B → AC. No row changed: every
`mapped` and `massing_only` row's Feature is present in the inventory, and
every `cadquery_export` row has its STEP/STL under `models/mfg/<UNIT>/export/`
or `cad/stl/`. Object totals match the previous build; the geometry under
them is refreshed from the current builders.

## Summary counts (Rev F census)

| Status | Count |
|---|---|
| `mapped` | 60 |
| `massing_only` | 41 |
| `cadquery_export` | 36 |
| `placeholder_skip` | 7 |
| `unmapped` | 6 |
| **Total rows** | **150** |

- Rows classified: **100%** (150/150)
- Graph nodes: **218** — 200 present, 16 placeholder, 2 retired
  (`flow_graph/plant_flow_graph.json` Rev AC)
- Rowed present units covered (`mapped`, `massing_only` or `cadquery_export`):
  **135/146 (92.5 percent)**
- Present graph nodes without a map row: **54** — 13 of them carry their own
  `unit_id` as a `plant.FCStd` Part::Feature (see below); 41 have no Feature
- Present units with CAD by any route: **148/200 (74.0 percent)**
- Placeholder nodes: **16** on the graph (skip or massing_only — no
  placeholder solids)

## Present graph nodes without a map row (69)

The 150 rows cover 149 of the 218 graph nodes; the row for `TERRACE_IRRIG`
names a unit the graph retired. The 69 unrowed nodes split:

- **54 present.** 13 have a `plant.FCStd` Feature named exactly `unit_id`
  (the standing convention: units authored from issued or study envelopes on
  the placed copy carry their own name and take no row):

| unit_id | Present as plant.FCStd Feature |
|---|---|
| `BIOFILTER` | yes (`farm.py`) |
| `EW_3` … `EW_8` | yes, one each (`leach_cstr.py`) |
| `GALLEY` | yes (`fitout.py`) |
| `PROD_C5_C10`, `PROD_C11_C18`, `PROD_C19_C28`, `PROD_C29` | yes, one each (`wet_products.py`) |
| `ZNBR2_BR2_REGEN` | yes (`electrical_yard.py`) |

  The other 41 present unrowed units have no Feature in `plant.FCStd`
  (ladder heat batteries `Q1_A`–`Q4_B`, headers, litho line, grease kettles,
  habitation rooms and similar). Adding rows for them is open; the census
  counts them so the coverage figure stays honest.
- **15 placeholder** — no CAD expected under the placeholder policy.

## Unmapped present (no Feature by design or still open)

| unit_id | Graph presence | Notes |
|---|---|---|
| `BOUNDARY_EXPORT` | present | logical DOCK boundary node |
| `LOAD_AGG` | present | electrical aggregation logical node |
| `PROD_MEOH` | present | Rev D: AQS-DUTY-064 storage row added (A-M-278): sized D850 x H1150 mm welded-steel tank + |
| `PROD_O2` | present | Rev D: AQS-DUTY-064 storage row added (A-M-278): surplus-O2 cylinder-bank equivalent volum |
| `Q4_BUS` | present | thermal collector bus logical |
| `TERRACE_IRRIG` | NOT_ON_GRAPH | unit retired 2026-10-18 with terrace irrigation |

## Placeholder policy

| unit_id | status | Graph presence | freecad_names |
|---|---|---|---|
| `BLOW_MOLD` | `placeholder_skip` | present | — |
| `CONTINUOUS_RECYCLE` | `placeholder_skip` | present | — |
| `DUCKWEED` | `massing_only` | present | — |
| `ELECTRODE_COAT` | `placeholder_skip` | present | — |
| `GEO_ORC` | `massing_only` | placeholder | GEO_ORC |
| `LITHO_STUB` | `placeholder_skip` | retired | — |
| `REMIN` | `placeholder_skip` | present | — |
| `SOLAR_PV_CELL` | `placeholder_skip` | present | — |
| `VCD_TRAIN` | `placeholder_skip` | present | — |

`DUCKWEED` is graph-present with no solid: the raceway is scale-guarded and
the builder emits it only at a scale that fits the plate. `GEO_ORC` is
graph-placeholder but keeps its `electrical_yard.py` Feature.
`S13_CLASS_TREAT` is retired on the graph while `d1b_massing.py` still draws
it (open item).

## Alias rows (unit_id ≠ Feature Name)

| unit_id | FreeCAD Name(s) | Builder |
|---|---|---|
| `AFTERBURNER_FLUE` | `HX7_FLUE_JACKET` | gas_handling.py |
| `BMED_ACID` | `BMED_REGEN` | wet_products.py |
| `BMED_BASE` | `BMED_REGEN` | wet_products.py |
| `CRYO_AHU_COND_CONDENSABLE` | `CRYO_AHU_COND` | cryo.py |
| `FLOAT_SINK` | `FLOAT_DEWATER`, `SINK_DEWATER` | leach_cstr.py |
| `FLUE_KO` | `FLUE_CAP` | cryo.py |
| `GEO_GHEX` | `KO_GEO_GHEX` | electrical_yard.py |
| `GLASS_BURNOUT` | `BURNOUT_ROTARY` | glass_line.py |
| `GLASS_DIGEST` | `NaOH_DIGEST` | glass_line.py |
| `GLASS_MILL` | `MILL` | glass_line.py |
| `GLASS_RINSE` | `RINSE_DEWATER` | glass_line.py |
| `HDR_O2` | `HDR_O2_N`, `HDR_O2_S`, `HDR_O2_E`, `HDR_O2_W` | pipe_services.py |
| `HDR_UPW` | `HDR_UPW_N`, `HDR_UPW_S`, `HDR_UPW_E`, `HDR_UPW_W` | pipe_services.py |
| `HOPPER` | `HOPPER_SHREDDER` | leach_cstr.py |
| `NORTH_DOCK` | `DOCK`, `DOCK_APRON_N`, `DOCK_DOOR_N` | building_stack.py |
| `OIL_DRYER` | `DRYER` | oil_line.py |
| `OIL_FRAC` | `FRACTIONATOR` | oil_line.py |
| `OIL_PYRO` | `INDUCTION_PYROLYZER` | oil_line.py |
| `POLISH_BANK` | `PK_1`, `PK_2`, `PK_3`, `PK_6`, `PK_7`, `PK_8`, `PK_9` | wet_products.py |
| `RELIEF_CRYO` | `CRYO_VENT_STACK` | cryo.py |
| `RELIEF_H2` | `H2_STACK` | gas_handling.py |
| `TERRACE_IRRIG` | `TERRACE_IRRIG_HDR_S` | building_stack.py |

## Full table (Rev F census — regenerates with the map and the plant inventory)

| unit_id | status | freecad_names | builder | group_path |
|---|---|---|---|---|
| `ACID_POLISH_SCRUB` | `mapped` | ACID_POLISH_SCRUB | gas_handling.py | Plant/Process/Gas |
| `AFTERBURNER` | `mapped` | AFTERBURNER | oil_line.py | Plant/Process/Oil_Glass |
| `AFTERBURNER_FLUE` | `mapped` | HX7_FLUE_JACKET | gas_handling.py | Plant/Process/Gas |
| `AIR_RECEIVER` | `massing_only` | AIR_RECEIVER | d1b_massing.py | — |
| `ALK_SCRUBBER` | `mapped` | ALK_SCRUBBER | gas_handling.py | Plant/Process/Gas |
| `AL_POT` | `cadquery_export` | — | mfg/foundry.py | — |
| `AQUA_UV` | `massing_only` | AQUA_UV | farm.py | Plant/Life/Farm |
| `BACKUP_GEN` | `mapped` | BACKUP_GEN | electrical_yard.py | Plant/Electrical |
| `BAGHOUSE` | `mapped` | BAGHOUSE | gas_handling.py | Plant/Process/Gas |
| `BEE_HIVE` | `massing_only` | BEE_HIVE | farm.py | Plant/Life/Farm |
| `BLACK_DIGEST` | `massing_only` | BLACK_DIGEST | d1b_massing.py | Plant/Life/Habitation |
| `BLOW_MOLD` | `placeholder_skip` | — | — | — |
| `BMED_ACID` | `massing_only` | BMED_REGEN | wet_products.py | Plant/Process/Wet |
| `BMED_BASE` | `massing_only` | BMED_REGEN | wet_products.py | Plant/Process/Wet |
| `BMED_UPW_POLISH` | `massing_only` | BMED_UPW_POLISH | d1b_massing.py | Plant/Process/Wet |
| `BOUNDARY_EXPORT` | `unmapped` | — | — | — |
| `BSFL_BIN` | `massing_only` | BSFL_BIN | farm.py | Plant/Life/Farm |
| `C29_RECYCLE` | `massing_only` | C29_RECYCLE | oil_line.py | Plant/Process/Oil_Glass |
| `CAST_LINE` | `cadquery_export` | — | mfg/foundry.py | — |
| `CATCH_TANK` | `mapped` | CATCH_TANK | building_stack.py | Plant/Building/Cores_Shafts |
| `CA_POT` | `cadquery_export` | — | mfg/foundry.py | — |
| `CHICKEN_COOP` | `massing_only` | CHICKEN_COOP | farm.py | Plant/Life/Farm |
| `COLD_MILL` | `mapped` | COLD_MILL | mfg_shop.py | Plant/Process/Wet |
| `COMB_HEAT` | `cadquery_export` | — | mfg/foundry.py | — |
| `CONTINUOUS_RECYCLE` | `placeholder_skip` | — | — | — |
| `CONT_CAST` | `cadquery_export` | — | mfg/foundry.py | — |
| `CRU` | `mapped` | CRU | wet_products.py | Plant/Process/Wet |
| `CRYO_AHU` | `mapped` | CRYO_AHU | cryo.py | Plant/Process/Cryo |
| `CRYO_AHU_COND_CONDENSABLE` | `mapped` | CRYO_AHU_COND | cryo.py | Plant/Process/Cryo |
| `CRYO_ASU` | `mapped` | CRYO_ASU | cryo.py | Plant/Process/Cryo |
| `CRYO_CO2` | `mapped` | CRYO_CO2 | cryo.py | Plant/Process/Cryo |
| `CRYO_DED_COOL` | `mapped` | CRYO_DED_COOL | cryo.py | Plant/Process/Cryo |
| `CRYO_H2` | `mapped` | CRYO_H2 | cryo.py | Plant/Process/Cryo |
| `CRYO_HX_Q4` | `mapped` | CRYO_HX_Q4 | cryo.py | Plant/Process/Cryo |
| `CRYO_N2` | `mapped` | CRYO_N2 | cryo.py | Plant/Process/Cryo |
| `CRYO_O2` | `mapped` | CRYO_O2 | cryo.py | Plant/Process/Cryo |
| `CR_CELL` | `cadquery_export` | — | mfg/foundry.py | — |
| `DRAW` | `cadquery_export` | — | mfg/foundry.py | — |
| `DUCKWEED` | `massing_only` | — | farm.py | Plant/Life/Farm |
| `DUCK_PEN` | `massing_only` | DUCK_PEN | farm.py | Plant/Life/Farm |
| `ELECTRODE_COAT` | `placeholder_skip` | — | — | — |
| `EW_1` | `mapped` | EW_1 | leach_cstr.py | Plant/Process/Wet |
| `EW_2` | `mapped` | EW_2 | leach_cstr.py | Plant/Process/Wet |
| `EW_9` | `mapped` | EW_9 | leach_cstr.py | Plant/Process/Wet |
| `EXTRUDE` | `cadquery_export` | — | mfg/foundry.py | — |
| `FAB_UPW_TANK` | `massing_only` | FAB_UPW_TANK | d1b_massing.py | Plant/Process/Wet |
| `FEED_PREP` | `massing_only` | FEED_PREP | farm.py | Plant/Life/Farm |
| `FILM_CAST` | `cadquery_export` | — | mfg/polymers.py | — |
| `FLOAT_SINK` | `mapped` | FLOAT_DEWATER, SINK_DEWATER | leach_cstr.py | Plant/Process/Wet |
| `FLUE_KO` | `mapped` | FLUE_CAP | cryo.py | Plant/Process/Cryo |
| `FLUX_PREP` | `cadquery_export` | — | mfg/foundry.py | — |
| `FOOD_STORE` | `massing_only` | FOOD_STORE | d1b_massing.py | — |
| `FORGE` | `cadquery_export` | — | mfg/foundry.py | — |
| `FUEL_CELL` | `mapped` | FUEL_CELL | electrical_yard.py | Plant/Electrical |
| `GAS_ATOMIZER` | `mapped` | GAS_ATOMIZER | mfg_shop.py | Plant/Process/Wet |
| `GEO_GHEX` | `mapped` | KO_GEO_GHEX | electrical_yard.py | Plant/Electrical |
| `GEO_HP` | `mapped` | GEO_HP | electrical_yard.py | Plant/Electrical |
| `GEO_HP_CLOSED_LOOP` | `massing_only` | GEO_HP_CLOSED_LOOP | d1b_massing.py | Plant/Electrical |
| `GEO_ORC` | `massing_only` | GEO_ORC | electrical_yard.py | Plant/Electrical |
| `GLASS_BURNOUT` | `massing_only` | BURNOUT_ROTARY | glass_line.py | Plant/Process/Oil_Glass |
| `GLASS_DIGEST` | `mapped` | NaOH_DIGEST | glass_line.py | Plant/Process/Oil_Glass |
| `GLASS_MILL` | `massing_only` | MILL | glass_line.py | Plant/Process/Oil_Glass |
| `GLASS_RINSE` | `massing_only` | RINSE_DEWATER | glass_line.py | Plant/Process/Oil_Glass |
| `GREY_TREAT` | `massing_only` | GREY_TREAT | d1b_massing.py | Plant/Life/Habitation |
| `GROW_BED` | `mapped` | GROW_BED | farm.py | Plant/Life/Farm |
| `GW_INTAKE` | `massing_only` | GW_INTAKE | d1b_massing.py | Plant/Electrical |
| `H2O_ELYZ` | `mapped` | H2O_ELYZ | cryo.py | — |
| `H2_DRYER` | `mapped` | H2_DRYER | gas_handling.py | Plant/Process/Gas |
| `HABITATION` | `mapped` | HABITATION | habitation.py | Plant/Life/Habitation |
| `HDR_H2` | `mapped` | HDR_H2 | build_wet.py | Plant/Process/Wet |
| `HDR_O2` | `mapped` | HDR_O2_N, HDR_O2_S, HDR_O2_E, HDR_O2_W | pipe_services.py | Plant/Life/Habitation |
| `HDR_UPW` | `mapped` | HDR_UPW_N, HDR_UPW_S, HDR_UPW_E, HDR_UPW_W | pipe_services.py | Plant/Life/Habitation |
| `HF_GEN` | `cadquery_export` | — | mfg/polymers.py | — |
| `HOPPER` | `mapped` | HOPPER_SHREDDER | leach_cstr.py | Plant/Process/Wet |
| `HYDRO_SET` | `mapped` | HYDRO_SET | building_stack.py | Plant/Building/Cores_Shafts |
| `IND_MELT` | `cadquery_export` | — | mfg/foundry.py | — |
| `INV_CAST` | `cadquery_export` | — | mfg/foundry.py | — |
| `LEACH_CSTR_1` | `mapped` | LEACH_CSTR_1 | leach_cstr.py | Plant/Process/Wet |
| `LITHO_STUB` | `placeholder_skip` | — | — | — |
| `LOAD_AGG` | `unmapped` | — | — | — |
| `MEOH_FC` | `massing_only` | MEOH_FC | d1b_massing.py | Plant/Electrical |
| `MEOH_FERM` | `massing_only` | MEOH_FERM | d1b_massing.py | Plant/Electrical |
| `MEOH_SYNTH` | `massing_only` | MEOH_SYNTH | d1b_massing.py | Plant/Electrical |
| `MEOH_TANK` | `massing_only` | MEOH_TANK | d1b_massing.py | Plant/Electrical |
| `METAL_STORE` | `massing_only` | METAL_STORE | d1b_massing.py | — |
| `MET_AHU` | `mapped` | MET_AHU | mfg_shop.py | Plant/Process/Wet |
| `MET_HX_Q4` | `mapped` | MET_HX_Q4 | mfg_shop.py | Plant/Process/Wet |
| `MET_MELT` | `mapped` | MET_MELT | mfg_shop.py | Plant/Process/Wet |
| `MET_SCRUB` | `mapped` | MET_SCRUB | mfg_shop.py | Plant/Process/Wet |
| `MET_SYN` | `massing_only` | MET_SYN | d1b_massing.py | Plant/Electrical |
| `MFG_SHOP` | `mapped` | MFG_SHOP | mfg_shop.py | Plant/Process/Wet |
| `MG_POT` | `cadquery_export` | — | mfg/foundry.py | — |
| `MO_CELL` | `cadquery_export` | — | mfg/foundry.py | — |
| `NORTH_DOCK` | `mapped` | DOCK, DOCK_APRON_N, DOCK_DOOR_N | building_stack.py | Plant/Building/Cores_Shafts |
| `NUTRIENT_DOSE` | `mapped` | NUTRIENT_DOSE | farm.py | Plant/Life/Farm |
| `OIL_DRYER` | `mapped` | DRYER | oil_line.py | Plant/Process/Oil_Glass |
| `OIL_FRAC` | `mapped` | FRACTIONATOR | oil_line.py | Plant/Process/Oil_Glass |
| `OIL_PYRO` | `mapped` | INDUCTION_PYROLYZER | oil_line.py | Plant/Process/Oil_Glass |
| `PELLET` | `cadquery_export` | — | mfg/polymers.py | — |
| `POLISH_BANK` | `mapped` | PK_1, PK_2, PK_3, PK_6, PK_7, PK_8, PK_9 | wet_products.py | Plant/Process/Wet |
| `POLY_COND` | `cadquery_export` | — | mfg/polymers.py | — |
| `POLY_F` | `cadquery_export` | — | mfg/polymers.py | — |
| `POLY_FIBER` | `massing_only` | POLY_FIBER | mfg_shop.py | Plant/Process/Wet |
| `POLY_OLEFIN` | `cadquery_export` | — | mfg/polymers.py | — |
| `POLY_STOCK` | `cadquery_export` | — | mfg/polymers.py | — |
| `POWDER_RESIN` | `cadquery_export` | — | mfg/polymers.py | — |
| `PROD_MEOH` | `unmapped` | — | — | — |
| `PROD_O2` | `unmapped` | — | — | — |
| `PV_ARRAY` | `mapped` | PV_ARRAY | electrical_yard.py | Plant/Electrical |
| `Q4_BUS` | `unmapped` | — | — | — |
| `QUAIL_CAGE` | `massing_only` | QUAIL_CAGE | farm.py | Plant/Life/Farm |
| `RABBIT_HUTCH` | `massing_only` | RABBIT_HUTCH | farm.py | Plant/Life/Farm |
| `RECTIFIER` | `mapped` | RECTIFIER | electrical_yard.py | Plant/Electrical |
| `RELIEF_CRYO` | `mapped` | CRYO_VENT_STACK | cryo.py | Plant/Process/Cryo |
| `RELIEF_H2` | `mapped` | H2_STACK | gas_handling.py | Plant/Process/Gas |
| `REMIN` | `placeholder_skip` | — | — | — |
| `RES_HEAT` | `cadquery_export` | — | mfg/foundry.py | — |
| `RF_HEAT` | `cadquery_export` | — | mfg/foundry.py | — |
| `ROLL` | `cadquery_export` | — | mfg/foundry.py | — |
| `ROOF_TANK` | `mapped` | ROOF_TANK | building_stack.py | Plant/Building/Cores_Shafts |
| `S13_CLASS_TREAT` | `massing_only` | S13_CLASS_TREAT | d1b_massing.py | Plant/Process/Wet |
| `SALT_FEED` | `mapped` | SALT_FEED | wet_products.py | Plant/Process/Wet |
| `SHELL_BREAK` | `cadquery_export` | — | mfg/foundry.py | — |
| `SHELL_BUILD` | `cadquery_export` | — | mfg/foundry.py | — |
| `SHELL_BURNOUT` | `cadquery_export` | — | mfg/foundry.py | — |
| `SINTER` | `cadquery_export` | — | mfg/foundry.py | — |
| `SOLAR_PV_CELL` | `placeholder_skip` | — | — | — |
| `SOL_ARK_60K` | `mapped` | SOL_ARK_60K | electrical_yard.py | Plant/Electrical |
| `STOCK_OUT` | `cadquery_export` | — | mfg/foundry.py | — |
| `TERRACE_IRRIG` | `unmapped` | TERRACE_IRRIG_HDR_S | building_stack.py | Plant/Building/Terraces |
| `TFE_SYN` | `cadquery_export` | — | mfg/polymers.py | — |
| `TI_CELL` | `cadquery_export` | — | mfg/foundry.py | — |
| `VAC_CAST` | `cadquery_export` | — | mfg/foundry.py | — |
| `VAC_IND` | `cadquery_export` | — | mfg/foundry.py | — |
| `VCD_TRAIN` | `placeholder_skip` | — | — | — |
| `VDF_SYN` | `cadquery_export` | — | mfg/polymers.py | — |
| `VERMI_BIN` | `massing_only` | VERMI_BIN | farm.py | Plant/Life/Farm |
| `WAFER_FAB` | `mapped` | WAFER_FAB | wafer_fab.py | Plant/Process/Wet |
| `WAX_PATTERN` | `cadquery_export` | — | mfg/foundry.py | — |
| `WET_BENCH` | `mapped` | WET_BENCH | wafer_fab.py | Plant/Process/Wet |
| `WIRE_DRAW` | `mapped` | WIRE_DRAW | mfg_shop.py | Plant/Process/Wet |
| `WS_AMMONIA` | `massing_only` | WS_AMMONIA | d1b_massing.py | Plant/Process/Wet |
| `WS_DOPE` | `massing_only` | WS_DOPE | d1b_massing.py | Plant/Process/Wet |
| `WS_HF_ED` | `massing_only` | WS_HF_ED | d1b_massing.py | Plant/Process/Wet |
| `WS_KOH` | `massing_only` | WS_KOH | d1b_massing.py | Plant/Process/Wet |
| `WS_NITRIC` | `massing_only` | WS_NITRIC | d1b_massing.py | Plant/Process/Wet |
| `WS_PEROX` | `massing_only` | WS_PEROX | d1b_massing.py | Plant/Process/Wet |
| `WS_SLURRY` | `massing_only` | WS_SLURRY | d1b_massing.py | Plant/Process/Wet |
| `WS_SOLV` | `massing_only` | WS_SOLV | d1b_massing.py | Plant/Process/Wet |
| `ZNBR2` | `mapped` | ZNBR2 | electrical_yard.py | Plant/Electrical |

## Rev D (2026-10-19) — foundry/polymers CadQuery rows (historical)

The map gained 44 rows at Rev D (93 → 137 entries).

- **36 `cadquery_export` rows** from the FOUNDRY/POLYMERS builders: 26 in
  `models/mfg/foundry.py` and 10 in `models/mfg/polymers.py`. Each is a
  parametric CadQuery model reading `params.design`/`params.envelope` from
  `flow_graph/param/foundry_poly.py` (AQS-DUTY-072/073) and exporting
  STEP/STL/BOM under `models/mfg/<UNIT>/export/`; live trains and standby
  placeholders both carry rows (standby rows note their basis).
- **8 restored-unit/store rows**: AIR_RECEIVER, FOOD_STORE, METAL_STORE
  (D-DOCK buffer stores, `d1b_massing.py`), CRYO_ASU, H2O_ELYZ, RELIEF_CRYO
  (`cryo.py`), PROD_MEOH, PROD_O2 — the first six carry Features; PROD_MEOH
  and PROD_O2 remain `unmapped` until a CAD lane stages their tanks at the
  D-DOCK (`cad/stl/` carries their study envelopes).

## CAD-M1 massing — **done** 2026-10-01 (America/Chicago) (historical)

| Field | Value |
|---|---|
| Id | **CAD-M1** (plan id WP-D1b) |
| Builder | `d1b_massing.py` (hooked from `build_plant.py`) |
| Dims | `D1B_TBD_*` aliases of existing STUB/TOTE/DIGEST/P_TANK/BMED params — **not** PE nameplates / rates |
| Features added (18) | Names = `unit_id` Part::Feature |
| Remain unmapped / logical (3) | `BOUNDARY_EXPORT`, `LOAD_AGG`, `Q4_BUS` |

The d1b pass now attaches 23 TBD Part::Feature units at SCALE_M = 1.0 (the
X-FARM / X-POLY / X-UI-002 build-out units joined at map Rev E).

## Presence filter (done 2026-10-01 America/Chicago)

| Field | Value |
|---|---|
| Policy | `skip_disabled_and_placeholder_unless_mapped_massing` |
| Bridge | `graph_geometry_bridge.py` — `presence_filter` / `--presence-report` / `--apply-presence` / `--self-test` |
| Baseline (gold Rev B) | omit Feature set **empty** → object count **1114** unchanged (parts **1030**) |
| T6 (`LEACH_CSTR_1` `enabled=false`) | objects **1114→1113**, Part::Feature **1030→1029**, removed `LEACH_CSTR_1` |
| Logical unmapped | stay **skip** (`BOUNDARY_EXPORT`, `LOAD_AGG`, `Q4_BUS`) — no solids |
| Placeholders | skip unless map `status=massing_only` opt-in |

Envelope / structural Features not listed on skipped process units are left
in place.
