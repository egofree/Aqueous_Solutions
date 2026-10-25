# Death Valley site basis

Document number: AQS-SITE-006
Revision: A
Date: 2026-10-25
Profile: `flow_graph/param/sites/death_valley.json` (site id `death_valley`)
Plan: AQS-PLAN-011 section 6; open question Q-033 (the parcel)

| Rev | Description | Date |
|---|---|---|
| A | First issue with the first locale run: profile, environment, design consequences and closure result | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the Death Valley variant: the bounding hot-desert environment the profile states, the design consequences the model applies, and the result of the first locale run. Death Valley is a national park, so a plant would sit outside it; the profile uses the climate record of the Furnace Creek station (USC00042319) and the parcel remains owner question Q-033. The reference plant stays the baseline profile; this variant writes only its differences under `sites/death_valley/`.

## 2. Environment

| Quantity | Value | Source |
|---|---|---|
| Station | Death Valley NP, USC00042319, 36.46 N, 116.87 W, elevation -59 m | NOAA_NORMALS_DV |
| July mean daily maximum / minimum, 1991-2020 | 47.4 C / 32.8 C | NOAA_NORMALS_DV |
| Highest recorded air temperature | 56.7 C (1913-07-10) | NCEI_DV_EXTREMES |
| Lowest recorded air temperature | about -9.4 C | NCEI_DV_EXTREMES |
| Mean annual precipitation, 1991-2020 | 56 mm | NOAA_NORMALS_DV |
| Cooling design dry bulb (interim, A-M-385) | 47.4 C | NOAA_NORMALS_DV; the ASHRAE 0.4 % value for the nearest listed station is higher and replaces it |
| Groundwater | wells on the alluvial fan, about 30 C, moderately mineralised, high silica, fluoride and arsenic | USGS_DV_GW |
| Snow | negligible | NOAA_NORMALS_DV |
| Seismic, wind, soil | interim bounding values (A-M-386, A-M-387) | ASCE7_22; hazard lookups and the geotechnical report at the parcel replace them |

## 3. Design consequences as built

- Heat rejection: the low-grade water loop rejects evaporatively through DRY_COOLER (mode `evaporative`, charged against the water balance), because outside air sits above the low-grade return for much of the summer; the ground loop keeps GEO_GHEX in ground mode. Night rejection into the thermal stores and a heat-pump lift remain design options on this profile and are not drawn by the run.
- Water: rain is negligible, so the make-up source is groundwater with sand separation and reverse osmosis for silica, fluoride and arsenic; the reject is a plant stream with a defined outlet. The intake unit GW_INTAKE is in the graph and in the site run; its rate solves to 0 kg/d because the condensate harvest is indoor-air recovery and the evaporative rejection charge is not yet booked (Section 5, open item 1, task X-LOC-13).
- PV: the resource is higher than the baseline (6.3 against 5.41 kWh/kWp/d before losses, NREL_PVWATTS class basis), with cell-temperature and soiling losses to be applied by the parcel-hourly run. The sizing rule is unchanged: PV is sized at the oversize factor times the nameplate that closes the daily balance.
- Storage and coverage: the worst stretch stays the night. The first locale run reports a plant demand of 165.87 kW, 2322.2 kWh drawn over the stretch and a coverage of 1.09 (AQS-SITE-005, the site copy under `sites/death_valley/`).
- Crew and ventilation: outdoor work follows the state heat illness rules (CA_TITLE8_3395). Cooling dominates the ventilation load at the interim design dry bulb.
- Scaling: no unit is eliminated and no manual factor is applied; the profile bindings drive the sizing. The water-intake unit joins the graph in its own task.
- Codes: the United States building family applies (AQS-STD-007), with the state and county codes of the parcel.

## 4. What the run produced

The first locale run regenerated 269 outputs that differ from the baseline into `sites/death_valley/`, including the site copies of the power and scaling pages, the design check, the load list, the wire inventory and the self-copy bill of materials. The baseline tree is unchanged by a locale run.

## 5. Closure result and open items

The mass balance closes at the site. The site design check passes: the former QC-09 finding is resolved by making the check read the graph's sized hydrogen store (17 kg, AQS-ELEC-007 / X-PAR-12) instead of a frozen 19 kg constant that the store basis had superseded; the rack holds the store within the band at both sites.

Open items, in order:

1. Evaporative rejection water charge. The condensate harvest is indoor-air recovery (greenhouse and habitation vapour condensed on the coils), so it does not depend on outdoor humidity and does not fall at a dry site; the intake therefore solves to 0 kg/d in the present run. The site water charge that does belong to this profile is the spray the evaporative rejection consumes: rejected duty divided by the latent heat of water. Booking it against the roof-tank balance is a design pass of its own - it must state the ordering between the heat solve and the mass closure - and is recorded as task X-LOC-13. Until it is built the intake stays at zero and the page does not claim a site water deficit.
2. ASHRAE climatic design conditions for the nearest listed station replace the interim design temperatures (A-M-385).
3. The ASCE Hazard Tool lookups (wind, seismic, snow) and the geotechnical report at the parcel replace the interim bounding values (A-M-386, A-M-387).
4. The parcel itself (Q-033); every parcel-bound value in this page is a station-climate interim until it is chosen.
