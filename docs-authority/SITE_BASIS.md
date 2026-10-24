# Site basis

Document number: AQS-SITE-002  
Revision: B  
Date: 2026-10-24

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue; study site set by owner decision; soil bearing corrected from 2000 to 1500 psf (X-BLD-03, 2026-10-16) | 2026-10-15 |
| B | Rewritten to DOC_STYLE (AQS-DOC-002): purpose, terms and caption; values unchanged | 2026-10-24 |

## 1. Purpose and scope

The design needs a site to fix its climate and structural loads. No parcel has been chosen. By owner decision, the study site is at 33.0° N, a Dallas–Fort Worth class location. This page lists the climate, wind, seismic, snow and soil values used for that study site and says which are published and which are assumptions.

Assumed values are also recorded in the assumptions register (AQS-REG-002). They will be replaced when a parcel is fixed.

## 2. Terms

Design dry bulb: the outdoor air temperature exceeded for only the stated share of hours in a year. The 0.4 % cooling value is exceeded for 0.4 % of the hours; the 99.6 % heating value is exceeded (colder) for 0.4 % of the hours.

MCWB: mean coincident wet bulb, the average wet-bulb temperature at the cooling design dry bulb.

Risk Category II: the ordinary building category of ASCE 7-22, which sets the return period of the design wind.

Ss and S1: mapped spectral accelerations at 0.2 s and 1 s periods (ASCE 7-22), which set the seismic load.

Site class: soil category for seismic amplification (IBC 1613.2.2).

## 3. Site values

Table 3.1 lists the values and their status.

Table 3.1. Study site values

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
| Soil | expansive clay, allowable bearing 1500 psf (72 kPa) | assumption | IBC Table 1806.2 presumptive value for clay and silt (Unified Soil Classification System groups CL, ML, MH, CH; ASTM D2487); corrected from 2000 psf, which is the sand value (X-BLD-03, 2026-10-16); geotechnical report replaces it |
| Frost depth | 6 in (150 mm) | assumption | Local practice; replaced by the building official's value |

## 4. How the values are used

Outdoor equipment and cooling loops are rated at the 0.4 % cooling dry bulb (37.8 °C) and the 99.6 % heating dry bulb (−7.2 °C). Duties for the Q4 loop and air-cooled equipment that used a different ambient temperature are checked under the X-BAS-03 follow-up items in the task plan.

## 5. Values still to be sourced

The seismic, snow and wind values need the ASCE Hazard Tool run for a fixed parcel, and the soil values need a geotechnical report. Task X-BAS-03 stays open until these are sourced.

## 6. References

- B1. ASHRAE Handbook—Fundamentals 2017, climatic design conditions, Dallas Love Field (station 722583).
- B2. ASHRAE design temperature table, Texas, Dallas/Fort Worth (hvaclogic.org).
- B3. NREL PVWatts Calculator v8, Dallas, Texas, fixed latitude tilt.
- B4. ASCE/SEI 7-22 Fig. 26.5-1B, Risk Category II; Dallas band 105–115 mph (windload.solutions summary).
- B5. ASCE Hazard Tool, https://ascehazardtool.org (not yet run for a parcel).
