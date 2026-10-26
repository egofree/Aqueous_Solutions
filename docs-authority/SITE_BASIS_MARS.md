# Mars site basis

Document number: AQS-SITE-009
Revision: A
Date: 2026-10-25
Profile: `flow_graph/param/sites/mars.json` (site id `mars`)
Plan: AQS-PLAN-011 section 8; owner decision Q-022 (mid-latitude, Arcadia Planitia)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, scaling actions, design consequences | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the Mars variant: a mid-latitude site with shallow ground ice of the Arcadia Planitia class. The mean surface pressure is close to the triple point of water, so the plant operates inside pressurised shells. Carbon dioxide feeds methanol synthesis and a future methanation unit. Ground ice is the water source. Partial gravity (3.71 m/s2) means settling and flotation work but more slowly.

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
| Surface radiation | 0.64 mSv/d dose equivalent at Gale crater | NASA_MARS_RAD |
| Perchlorate in soil | 0.4 to 0.6 percent by mass | NASA_MARS_PERCHLORATE |
| Ground ice | excess ice within metres of the surface | NASA_MARS_ICE |
| Thermal design (interim, A-M-395) | cooling -31 C, heating -89 C, insulation ambient -63 C | in-situ record replaces these |

## 3. Scaling actions as applied

- PUMPED_HYDRO eliminated: the roof and catch tanks are replaced or eliminated at this site. Replacement: ZNBR2.
- GEO_HP and GEO_GHEX eliminated: GEO becomes regolith heat exchange. Replacement: DRY_COOLER.
- No other scaling: the profile bindings drive the sizes.

## 4. Design consequences

- Pressurised shells: the mean surface pressure is close to the triple point of water, so open liquid water cannot be kept. Habitat and process halls are pressurised shells governed by internal pressure, not gravity. Regolith cover gives shielding and part of the load.
- Atmosphere as a resource: CO2 feeds methanol synthesis and a future methanation unit. N2 and Ar for buffer gas come from CRYO. Solid oxide electrolysis (MOXIE) is the diverse second oxygen source behind water electrolysis.
- Heat rejection: the thin atmosphere gives weak convection; radiators and regolith heat exchange replace air coolers.
- Water: ground-ice extraction and perchlorate removal is a new unit. Recycling closure matters more than on Earth.
- Heat rejection: the low air density gives weak convective cooling. Radiators and regolith heat exchange replace air coolers.
- Combustion: the atmosphere has no usable oxygen. AFTERBURNER and BACKUP_GEN run on plant oxygen or are replaced.
- Partial gravity: settling, flotation and packed columns work but more slowly.
- Earthing: dry regolith gives no earth electrode; the electrical system floats with insulation monitoring.
- Codes: the Outer Space Treaty, the COSPAR planetary-protection policy and NASA-STD-3001 apply.

## 5. Open items

1. The locale run is not yet executed (the profile is committed; the next step is the first locale regeneration).
2. Atmosphere intake, ice extraction and methanation units join the graph in their own tasks.
3. Perchlorate removal and the regolith feed case need assay mapping in AQS-ASSAY-001.
4. The landing site itself (Q-022); every site-bound value is a model-based interim until it is chosen.
