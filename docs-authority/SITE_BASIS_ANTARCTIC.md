# Antarctic site basis

Document number: AQS-SITE-008
Revision: A
Date: 2026-10-25
Profile: `flow_graph/param/sites/antarctic.json` (site id `antarctic`)
Plan: AQS-PLAN-011 section 7; owner decisions Q-021 (coastal McMurdo class) and Q-025 (waste processing under the treaty)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, scaling actions, design consequences, closure status | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page records the Antarctic variant: a coastal platform of the McMurdo class, with sea access and seawater. The profile carries the bounding cold-climate environment, the Madrid Protocol constraints, and the scaling actions that replace the ground loop and pumped hydro. The plant is land-based (not a hull) but the frozen permafrost ground changes the structural, earthing and ground-loop assumptions fundamentally.

## 2. Environment

| Quantity | Value | Source |
|---|---|---|
| Station | McMurdo class, 77.85 S, 166.67 E, 10 m elevation (coastal) | NOAA_MCMURDO |
| Mean annual temperature | -18 C | NOAA_MCMURDO |
| Summer / winter extremes | 8 C / -50 C | NOAA_MCMURDO |
| Mean wind / gusts | 6.2 m/s / above 51 m/s | NOAA_MCMURDO |
| Seawater temperature | -2 C (requires waste-heat warming before RO) | NSIDC_SEAICE |
| Mineral resources | prohibited (Article 7) | ANTARCTIC_TREATY |
| Thermal design (interim, A-M-392) | cooling 8 C, heating -50 C, insulation ambient -18 C | metocean record replaces these |
| Ground / wind / snow (interim, A-M-393) | bearing 144 kPa, resistivity 5000 ohm m, ghex 0 W/m, frost 0.5 m, wind 51 m/s, drift 0.5 kPa | geotechnical and metocean survey replaces these |

## 3. Scaling actions as applied

- HYDRO_SET eliminated: pumped-hydro reservoirs would need heating and enclosure at this site. Replacement: CRYO_H2 (the seasonal hydrogen store with the fuel cell).
- GEO_GHEX eliminated: frozen permafrost has very high resistivity and the ground-loop heat exchange is not viable. Replacement: DRY_COOLER as a heat-recovery coil (rejected heat is a resource, not a waste).
- DRY_COOLER duplicated: the heat-recovery pair also serves the seawater-intake warming duty.
- Wind is the primary source (share 1.0, capacity factor 0.35 study); PV is an option (zero through the dark season).

## 4. Design consequences

- Power: wind is the primary source; the hydrogen bank and fuel cell are the seasonal store for the austral polar night (about 120 days). PV is a summer option. The oversize rule applies to the wind capacity factor rather than the PV yield.
- Heat: heating dominates. The dry cooler becomes a heat-recovery coil. All water lines need freeze protection.
- Materials: the minimum design temperature (-50 C) triggers the ASME B31.3 paragraph 323.2.2 impact-test requirements. Thermoplastics outside heated space are excluded.
- Water: seawater RO is the default (waste-heat warmed, the McMurdo practice); snow melt is the diverse second source.
- Feedstock: Article 7 prohibits mineral resource activity. Local feed is limited to station waste and returned cargo.
- Codes: the Antarctic Treaty family (class rules, SOLAS, MARPOL, the Madrid Protocol) added on top of the operating state's law.
- Earthing: frozen permafrost has very high resistivity (5000 ohm m interim); the grounding study reruns.

## 5. Closure status

The profile is committed and validates. The locale run is blocked on the wind-primary power sizing integration into `flow_graph/param/write_graph.py`: the `write_graph power` stage accesses PV-specific output keys (`pv_kWp`, `store_kW`, `inverters`, `export_peak_kW`) that a wind-primary portfolio does not produce. The power-sizing calculation itself has been extended to handle wind-primary portfolios (nameplate = demand / capacity factor). The remaining work is the write-stage restructure.

Open items, in order:

1. Wind-primary write-stage integration: `flow_graph/param/write_graph.py` power() must handle non-PV primary sources. This is the X-LOC-08 design pass.
2. ASHRAE climatic design conditions for McMurdo replace the interim design temperatures (A-M-392).
3. The metocean and geotechnical survey at the chosen coastal parcel replaces the interim wind, snow, soil and seismic values (A-M-393).
4. The mooring site itself (Q-021); every site-bound value is a station-climate interim until it is chosen.
5. Environmental evaluation under Annex I for the waste-processing role (Q-025).
