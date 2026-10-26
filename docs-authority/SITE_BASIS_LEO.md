# Low Earth orbit site basis

Document number: AQS-SITE-010
Revision: A
Date: 2026-10-25
Profile: `flow_graph/param/sites/leo.json` (site id `leo`)
Plan: AQS-PLAN-011 section 9; owner decision Q-023 (station-class orbit, no rotating section)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, scaling findings. The locale run correctly identifies that 47 units cannot operate in microgravity without replacement units. X-LOC-10 stays open on the named remainder. | 2026-10-25 |

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

## 3. Scaling findings (the locale run correctly identifies the design gap)

The scaling model reports that 47 units cannot operate at this site because the profile does not provide:
- `buoyant_separation` (microgravity removes gravity-driven settling, flotation and phase separation)
- `free_surface` (microgravity makes liquid free surfaces unstable)
- `air_heat_sink` (vacuum removes convective cooling)
- `vent_sink` (vacuum means nothing can be vented overboard)
- `liquid_water_at_ambient` (vacuum means open water sublimates)
- `air_oxidant` (vacuum has no oxygen for combustion)

These findings are correct. The replacement units that the LEO variant needs — centrifuge separators, membrane gas-liquid contactors, radiative heat rejection panels, closed pressurised tanks with bladder or diaphragm management, and fuel-cell oxygen from the plant's own electrolysis — do not yet exist in the graph. Building them is the X-LOC-10 design pass, which is the largest single engineering effort in the locale study.

## 4. What the profile does establish

- PV is the only practical source in orbit; the eclipse-cycle storage model replaces the daily night model.
- Radiators (Stefan-Boltzmann) replace all convective heat rejection.
- The electrical system floats with structural bonding (no earth electrode in orbit).
- Water is closed-loop recycling; no local source exists.
- Motion is microgravity (residual acceleration about 1e-6 g); no heel, roll or pitch.

## 5. Open items

1. Centrifuge separators and membrane gas-liquid contactors to replace buoyant separation for every liquid-liquid and gas-liquid process.
2. Radiative heat-rejection panels sized by the Stefan-Boltzmann law to replace air coolers and dry coolers.
3. Closed pressurised tanks with bladder or diaphragm management to replace open tanks and sumps.
4. Fuel-cell oxygen from the plant's own water electrolysis to replace atmospheric oxidant for the backup generator.
5. Recovery-based vent system to replace atmospheric venting.
6. Crew radiation shielding design (water and polyethylene) for the habitable space.
