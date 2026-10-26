# Low Earth orbit site basis

Document number: AQS-SITE-010
Revision: B
Date: 2026-10-26
Profile: `flow_graph/param/sites/leo.json` (site id `leo`)
Plan: AQS-PLAN-011 section 9; owner decision Q-023 (station-class orbit, no rotating section)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, scaling findings. The locale run correctly identifies that 47 units cannot operate in microgravity without replacement units. X-LOC-10 stays open on the named remainder. | 2026-10-25 |
| B | X-LOC-10 design pass: the microgravity replacements enter the graph (LIO_BAT, WET_OX, HYDRO_GROW, MEM_DIST, beside the X-LOC-09 set) and every scaling action resolves. Locale regeneration complete: 305 outputs under sites/leo/. The station interior is the process space (A-M-401). | 2026-10-26 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the low Earth orbit variant: the environment the profile claims, the scaling findings that the locale run correctly identifies, and the named design gap. LEO is the hardest locale in the study: microgravity removes buoyant separation, free-surface stabilisation and convective heat transfer simultaneously, which invalidates the operating principle of most process equipment.

## 2. Environment

| Quantity | Value | Source |
|---|---|---|
| Orbit | 400 km altitude, 51.6 degrees inclination, eclipse every 92-minute orbit | AQS-PLAN-011 section 9 |
| Gravity | 8.66 m/s2 gravitational; apparent gravity is microgravity (free fall) | NASA_MARS_FACT |
| Atmosphere | vacuum (0 Pa) | AQS-SITE-010 |
| Radiation | 2.0 mSv/d (van Allen belt and galactic cosmic rays) | NASA_MARS_RAD |
| Solar | 5.8 kWh/kWp/d; eclipse every 92-min orbit; storage cycles per orbit, not daily | NREL_PVWATTS |
| Thermal | radiative only: no convection; Stefan-Boltzmann governs | AQS-PLAN-011 section 9 |

## 3. What the site cannot carry, and what replaces it

The scaling model reports that 53 units cannot operate at this site because the profile does not provide:
- `buoyant_separation` (microgravity removes gravity-driven settling, flotation and phase separation)
- `free_surface` (microgravity makes liquid free surfaces unstable)
- `air_heat_sink` (vacuum removes convective cooling)
- `vent_sink` (vacuum means nothing can be vented overboard)
- `liquid_water_at_ambient` (vacuum means open water sublimates)
- `air_oxidant` (vacuum has no oxygen for combustion)

Each of those units now carries a scaling action with a designed different-technology replacement or a named import path:

| Replaced function | LEO unit | Design basis |
|---|---|---|
| Flow-battery and pumped-hydro storage | LIO_BAT (sealed lithium-ion) | sealed cells need no buoyant electrolyte management (A-M-402) |
| Anaerobic sanitation | WET_OX (wet oxidation) | oxidation above the water critical point replaces settling (A-M-403) |
| Soil grow bed (food and CO2 removal) | HYDRO_GROW (soilless chamber) | capillary nutrient delivery replaces gravity drainage (A-M-404) |
| VCD water recovery | MEM_DIST (membrane distillation) | no boiling pool and no film flow (A-M-405) |
| Convective heat rejection and the ground loop | RAD_PANEL (space radiator) | Stefan-Boltzmann to the sky view (A-M-396, A-M-397) |
| Open water storage | TANK_BLD (closed bladder tank) | no free surface (A-M-400) |
| Vents, relief and scrubber discharge | REC_HDR (closed recovery header) | nothing vents to vacuum (A-M-398) |
| Air-fired waste oxidation | CAT_OX | plant-oxygen bleed (A-M-399) |
| Fuel-fired trim heat | E_HEAT | electric resistance (A-M-283 duty) |
| Gravity-settled separation, cells and evaporators | imported capillary-gap and pumped-loop modules | named import paths per unit in the profile (AQS-SITE-010 section 3) |

The full action list with per-action registers is in the profile (`scaling.actions`) and renders into the site scaling document.

## 4. What the profile does establish

- PV is the only practical source in orbit; the eclipse-cycle storage model replaces the daily night model.
- Radiators (Stefan-Boltzmann) replace all convective heat rejection.
- The electrical system floats with structural bonding (no earth electrode in orbit).
- Water is closed-loop recycling; no local source exists.
- Motion is microgravity (residual acceleration about 1e-6 g); no heel, roll or pitch.

## 5. Open items

1. The locale regeneration is complete: 305 outputs differ from the baseline under `sites/leo/`, and the scaling, portfolio and heat-rejection checks pass at every committed profile.
2. The imported modules (capillary-gap electrolysis cells, centrifuges, pumped-loop reactors) enter as named import paths; designing them in-house is the manufacturing-desk follow-on, task by task.
3. The orbit parameters (Q-023) are a model-based interim; the eclipse energy re-sizes the storage (A-M-402) when they are chosen.
5. Recovery-based vent system to replace atmospheric venting.
6. Crew radiation shielding design (water and polyethylene) for the habitable space.
