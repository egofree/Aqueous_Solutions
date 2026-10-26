# Mars site basis

Document number: AQS-SITE-009
Revision: B
Date: 2026-10-26
Profile: `flow_graph/param/sites/mars.json` (site id `mars`)
Plan: AQS-PLAN-011 section 8; owner decision Q-022 (mid-latitude, Arcadia Planitia)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, scaling findings. | 2026-10-26 |
| B | X-LOC-09 design pass: the locale-replacement units enter the graph and the scaling actions resolve; the ground loop stays. | 2026-10-26 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the Mars variant: a mid-latitude site with shallow ground ice of the Arcadia Planitia class. The mean surface pressure (0.636 kPa) is close to the triple point of water, so the plant operates inside pressurised shells. The thin CO2 atmosphere provides no convective cooling, no oxidant for combustion, and no vent sink. Partial gravity (3.71 m/s2) means settling and flotation work but more slowly.

## 2. Environment

| Quantity | Value | Source |
|---|---|---|
| Surface gravity | 3.71 m/s2 | NASA_MARS_FACT |
| Solar day (sol) | 24.66 h | NASA_MARS_FACT |
| Synodic period | 779.94 d | NASA_MARS_FACT |
| Solar irradiance | 586.2 W/m2 mean | NASA_MARS_FACT |
| Surface pressure | 0.636 kPa | NASA_MARS_FACT |
| Atmospheric composition | CO2 0.951, N2 0.0259, Ar 0.0194, O2 0.00161 | NASA_MARS_ATMOS |
| Temperature | 210 K mean; 184 to 242 K diurnal | NASA_MARS_FACT |
| Surface radiation | 0.64 mSv/d at Gale crater | NASA_MARS_RAD |
| Perchlorate in soil | 0.4 to 0.6 percent by mass | NASA_MARS_PERCHLORATE |
| Ground ice | excess ice within metres of the surface | NASA_MARS_ICE |
| Thermal design (interim, A-M-395) | cooling -31 C, heating -89 C, insulation ambient -63 C | in-situ record replaces these |

## 3. What the site carries and what it replaces

The site capabilities follow from the environment: buoyant separation and free surfaces hold at 3.71 m/s2; regolith is ground contact; the thin atmosphere gives no air heat sink, no oxidant and no vent sink; the surface pressure sits at the triple point of water, so ambient-pressure liquid water cannot be kept.

Two systems need no replacement and stay:

- **The ground loop stays.** Regolith is ground contact: GEO_GHEX rejects through the regolith (ground.ghex_capacity_W_m) and GEO_HP lifts on it. The locale keeps both units.
- **The flow battery stays.** At partial gravity the zinc-bromine electrolyte management works; the bromine-regeneration loop is closed hardware with no atmospheric discharge, so it runs unchanged.

Seventeen units cannot operate as designed at this site. Each scaling action eliminates one with a replacement of a different technology that the X-LOC-09 design pass adds to the graph (placeholder at the Earth reference plant, where the need does not arise):

| Replaced function | Mars unit | Design basis |
|---|---|---|
| Convective heat rejection | RAD_PANEL (space radiator, 12 kW duty context) | rejects radiatively to the sky at 180 K sink, emissivity 0.90 (A-M-396, A-M-397); area follows the Stefan-Boltzmann law |
| Open water storage | TANK_BLD (closed bladder tank) | 200 kPa design pressure inside the shell (A-M-400); replaces CATCH_TANK and ROOF_TANK |
| Atmospheric relief and vents | REC_HDR (closed recovery header) | every relief and offgas returns to a hold-and-reprocess skid; nothing discharges (A-M-398); replaces both relief valves, four vent scrubbers and the flue junction |
| Air-fired waste oxidation | CAT_OX (catalytic oxidiser) | plant-oxygen bleed at 450 C bed, far below the 850 C thermal chamber (A-M-399) |
| Fuel-fired trim heat | E_HEAT (resistance heater) | the N+1 melt heat runs on the grid at the A-M-283 30 kW connected duty |
| Combustion genset | FUEL_CELL | the diverse second power source (AQS-FC-001) |
| Pumped hydro | ZNBR2 | no open water body; the flow battery carries storage |
| Scrubbed UPW and methanol storage | imported closed pressurised tanks | process units imported as closed hardware |

The full action list with per-action registers is in the profile (`scaling.actions`) and renders into the site scaling document.

## 4. What the profile establishes

- PV is the primary source (2.5 kWh/kWp/d before dust losses, A-M-109 oversize); the worst stretch is the sol night plus a dust storm, carried by ZNBR2 storage with the fuel cell behind it.
- Heat rejects through two modes: the radiator to the sky and the ground loop to the regolith.
- Ground ice is the water source; perchlorate removal is required before use (0.4 to 0.6 percent by mass).
- The atmosphere is the carbon source for methanol synthesis.
- Regolith gives radiation shielding and part of the shell load.
- The electrical system floats with insulation monitoring (dry regolith gives no earth electrode).
- Codes: Outer Space Treaty, COSPAR planetary protection, NASA-STD-3001.

## 5. Open items

1. The locale regeneration runs after this page; its outputs land under `sites/mars/` and the site tests prove them.
2. Ground-ice extraction, perchlorate removal and solid-oxide CO2 electrolysis (the diverse oxygen source) are follow-on design units; nothing in the scaling resolution blocks on them.
3. The landing site itself (Q-022); every site-bound value is a model-based interim until it is chosen.
4. Feed cases for regolith, perchlorate and imported hardware need mapping in AQS-ASSAY-001.
