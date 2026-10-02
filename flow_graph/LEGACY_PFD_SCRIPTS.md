# Legacy PFD / SLD scripts vs flow-graph renders

Document: **AQS-FLOW-GRAPH-001** annex  
Licence: **CERN-OHL-S-2.0**  
Date: 2026-10-01

## Authority

| Artefact | Role |
|---|---|
| `plant_flow_graph.json` | **Sole typed topology** |
| `views/{pfd,mfd,efd-*}.{json,dot,svg}` | Layer renders regenerated from graph |
| `pfd_bridge.py` | Thin helper — load/filter edges for matplotlib bridges |
| `pfd_scripts/*.py` + hub `*_pfd.png` / `electrical_sld.png` | Matplotlib sheets — **graph-bridged** where noted below |

Do **not** invent rates/nameplates/stream routes in either path.

## Bridge status

| Path | Status |
|---|---|
| EFD electrical SVG (`views/efd-elec.svg`) | **Graph-driven** — includes **S17** + ESS peer elec edges |
| MFD mass SVG (`views/mfd.svg`) | **Graph-driven** — includes MeOH **S73–S82**, **NORTH_DOCK** / **DOCK_EXPORT_TBD**, campus orphan **HYDRO_SET** |
| EFD ess / thermal SVGs | **Graph-driven** |
| `pfd_scripts/electrical_sld.py` → `electrical_sld.png` | **Graph-bridged** — S17 + ESS peers; layout still drawlib |
| `pfd_scripts/mass_flow_pfd.py` → `mass_flow_pfd.png` | **Graph-bridged** — S01–S72 + MeOH S73–S82 + DOCK_EXPORT_TBD |
| `pfd_scripts/ew_cascade_pfd.py` | **Graph-bridged** — IA-EW-01…04 |
| `pfd_scripts/continuous_recycling_pfd.py` | **Graph-bridged** — IA-REC-* + IA-WET-* |
| `pfd_scripts/glass_ceramic_pfd.py` | **Graph-bridged** — IA-GLASS-* |
| `pfd_scripts/bmed_regen_pfd.py` | **Graph-bridged** — IA-BMED-* |
| `pfd_scripts/polish_bank_pfd.py` | **Graph-bridged** — IA-POL-* |
| `pfd_scripts/hydro_dock_pfd.py` | **Graph-bridged** — HYDRO + DOCK_EXPORT_TBD |
| `pfd_scripts/znbr2_flow_pfd.py` | **Graph-bridged** — IA-ESS-ZNBR2-* |
| `pfd_scripts/meoh_train_pfd.py` | **Graph-bridged** — S73–S82 + IA-ESS-MEOH-* |
| `pfd_scripts/oil_line_pfd.py` | **Graph-bridged** — IA-OIL-* + S67/S11 |
| `pfd_scripts/wet_line_factory_pfd.py` | **Graph-bridged** — IA-WET-* / IA-REC-01 + S09/S10/S31–S35/S38/S65–S66 |
| `pfd_scripts/metal_forming_pfd.py` | **Graph-bridged** — S57–S63 / S71–S72 |
| `pfd_scripts/mfg_shop_pfd.py` | **Graph-bridged** — S08/S16/S58–S61 |
| `pfd_scripts/hab_water_pfd.py` | **Graph-bridged** — S01/S12/S21/S25–S29 |
| `pfd_scripts/habitation_pfd.py` | **Graph-bridged** — S02/S12/S14–S15/S21/S26/S78 |
| `pfd_scripts/fab_upw_pfd.py` | **Graph-bridged** — S01/S09/S27 |
| `pfd_scripts/terrace_irrigation_pfd.py` | **Graph-bridged** — S40–S42 |
| `pfd_scripts/fuel_cell_pfd.py` | **Graph-bridged** — S49–S53 |
| `pfd_scripts/backup_gen_pfd.py` | **Graph-bridged** — S45–S47 |
| `pfd_scripts/geothermal_pfd.py` | **Graph-bridged** — S06/S43–S44/S48 |
| `pfd_scripts/wafer_fab_pfd.py` | **Graph-bridged** — S03/S36–S39 |
| `pfd_scripts/fab_reagent_forks_pfd.py` | **Graph-bridged** — S31–S37 |
| `pfd_scripts/solar_cell_pfd.py` | **Graph-bridged** — S10/S27/S35 peers; **SOLAR_PV_CELL** node has no dedicated edges yet (placeholder) |
| `pfd_scripts/farm_pfd.py` | **Graph-bridged** — S04/S06–S07/S11/S13–S15/S14X/S20 |
| `pfd_scripts/nutrient_pfd.py` | **Graph-bridged** — S07/S12/S30 |
| `pfd_scripts/cryo_pfd.py` | **Graph-bridged** — S02–S05/S18/S54–S56/S64/S67–S68/S70 |
| `pfd_scripts/vent_closure_pfd.py` | **Graph-bridged** — S19/S56/S62/S65–S66/S71 |
| `pfd_scripts/container_layout.py` | **Layout overlay** — container_cross S##/IA; not a process PFD |
| `pfd_scripts/campus_life_hazard_pfds.py` | **Layout overlay** — campus_cross on each sheet |
| `pfd_scripts/building_stack_pfds.py` | **Layout overlay** — building_cross on each sheet |

## Regenerate graph views

```bash
cd Diagrams/aqueous_diagrams/flow_graph
python3 build_seed.py
python3 export_authority_md.py
python3 render_layer_views.py
```

## Regenerate bridged PNGs

```bash
cd Diagrams/aqueous_diagrams
# Prefer system python with matplotlib:
/usr/bin/python3 pfd_scripts/electrical_sld.py
/usr/bin/python3 pfd_scripts/mass_flow_pfd.py
/usr/bin/python3 pfd_scripts/ew_cascade_pfd.py
/usr/bin/python3 pfd_scripts/continuous_recycling_pfd.py
/usr/bin/python3 pfd_scripts/glass_ceramic_pfd.py
/usr/bin/python3 pfd_scripts/bmed_regen_pfd.py
/usr/bin/python3 pfd_scripts/polish_bank_pfd.py
/usr/bin/python3 pfd_scripts/hydro_dock_pfd.py
/usr/bin/python3 pfd_scripts/znbr2_flow_pfd.py
/usr/bin/python3 pfd_scripts/meoh_train_pfd.py
/usr/bin/python3 pfd_scripts/oil_line_pfd.py
/usr/bin/python3 pfd_scripts/wet_line_factory_pfd.py
/usr/bin/python3 pfd_scripts/metal_forming_pfd.py
/usr/bin/python3 pfd_scripts/mfg_shop_pfd.py
/usr/bin/python3 pfd_scripts/hab_water_pfd.py
/usr/bin/python3 pfd_scripts/habitation_pfd.py
/usr/bin/python3 pfd_scripts/fab_upw_pfd.py
/usr/bin/python3 pfd_scripts/terrace_irrigation_pfd.py
/usr/bin/python3 pfd_scripts/fuel_cell_pfd.py
/usr/bin/python3 pfd_scripts/backup_gen_pfd.py
/usr/bin/python3 pfd_scripts/geothermal_pfd.py
/usr/bin/python3 pfd_scripts/wafer_fab_pfd.py
/usr/bin/python3 pfd_scripts/fab_reagent_forks_pfd.py
/usr/bin/python3 pfd_scripts/solar_cell_pfd.py
/usr/bin/python3 pfd_scripts/farm_pfd.py
/usr/bin/python3 pfd_scripts/nutrient_pfd.py
/usr/bin/python3 pfd_scripts/cryo_pfd.py
/usr/bin/python3 pfd_scripts/vent_closure_pfd.py
/usr/bin/python3 pfd_scripts/container_layout.py
/usr/bin/python3 pfd_scripts/campus_life_hazard_pfds.py
/usr/bin/python3 pfd_scripts/building_stack_pfds.py
# or: python3 rebuild.py --all-pfds
#     python3 rebuild.py --sync
```

## Remaining legacy (process sheets)

**Empty for process line PFDs** — all emitters under `pfd_scripts/` that draw process topology are graph-bridged (IA/S## overlays + register via `pfd_bridge.sector_edges` / `ia_edges`).

Helpers excluded (not sheets): `drawlib.py`, `params.py`, `sector_style.py`.

### Honest residual (not blockers for bridge tranche)

| Item | Why not “fully closed” |
|---|---|
| **DOCK_EXPORT_TBD** | Namespace TBD — **no fake S##** |
| Null rates | Graph rates stay null until authority fills them |
| **SOLAR_PV_CELL** | Placeholder node; no dedicated edges — sheet uses shared S10/S27/S35 peers |
| Matplotlib full rewrite | Optional — layout still drawlib/sector_style; overlays only |
| Campus / building / container | Non-process **layout** sheets — light graph cross-link overlay (not process PFDs) |
