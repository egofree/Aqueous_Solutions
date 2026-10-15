# Site basis — AQS-SITE-002 Rev A

Date 2026-10-15. Owner decision: study site at 33.0° N, Dallas–Fort Worth class. No parcel is chosen. Values marked assumption are in AQS-REG-002 and are replaced when a parcel is fixed.

| Item | Value | Status | Source |
| --- | --- | --- | --- |
| Latitude | 33.0° N | owner decision | — |
| Elevation | 607 ft (185 m) | published | ASHRAE 2017 design conditions, Dallas Love Field [B1] |
| Climate zone | 3A | published | ASHRAE 90.1 / IECC, Dallas County [B2] |
| Heating design, 99.6 % | 19 °F (−7.2 °C) | published | [B1][B2] |
| Heating design, 99 % | 24 °F (−4.4 °C) | published | [B1][B2] |
| Cooling design, 0.4 % dry bulb / MCWB | 100 °F / 75 °F (37.8 / 23.9 °C) | published | [B1][B2] |
| Cooling design, 1 % dry bulb | 101 °F class, about 38 °C | published, rounded | [B2] |
| Insolation, latitude tilt | 5.41 kWh/m²/d annual mean | published | NREL PVWatts v8, Dallas [B3] |
| Wind, Risk II, 3 s gust | 105–115 mph band; 115 mph used | band published, value assumption | ASCE 7-22 map band for Dallas [B4] |
| Seismic Ss / S1 | 0.10 g / 0.05 g | assumption | Pending ASCE Hazard Tool lookup at the parcel [B5] |
| Site class | D (default) | assumption | IBC 1613.2.2 default where soil is unknown |
| Seismic design category | A expected | assumption | Follows from the assumed Ss/S1 at class D; confirm with [B5] |
| Ground snow | 5 psf (0.24 kPa) | assumption | Pending [B5] |
| Soil | expansive clay, allowable bearing 2000 psf (96 kPa) | assumption | IBC Table 1806.2 presumptive value for clay; geotechnical report replaces it |
| Frost depth | 6 in (150 mm) | assumption | Local practice; replaced by the building official's value |

Use. Outdoor equipment and cooling loops are rated at the 0.4 % cooling dry bulb (37.8 °C) and the 99.6 % heating dry bulb (−7.2 °C). Q4 and air-cooled duties that used another ambient are checked under X-BAS-03 follow-up items in TASK_PLAN.

Held. Seismic, snow and wind values need the ASCE Hazard Tool at a fixed parcel; soil needs a geotechnical report. X-BAS-03 stays open until these are sourced.

## Sources

- B1. ASHRAE Handbook—Fundamentals 2017, climatic design conditions, Dallas Love Field (station 722583).
- B2. ASHRAE design temperature table, Texas, Dallas/Fort Worth (hvaclogic.org).
- B3. NREL PVWatts Calculator v8, Dallas TX, fixed latitude tilt.
- B4. ASCE/SEI 7-22 Fig. 26.5-1B, Risk Category II; Dallas band 105–115 mph (windload.solutions summary).
- B5. ASCE Hazard Tool, https://ascehazardtool.org (not yet run for a parcel).
