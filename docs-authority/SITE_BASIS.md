# Site basis

Document number: AQS-SITE-002  
Revision: C  
Date: 2026-10-29

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue; study site set by owner decision; soil bearing corrected from 2000 to 1500 psf (X-BLD-03, 2026-10-16) | 2026-10-15 |
| B | Rewritten to DOC_STYLE (AQS-DOC-002): purpose, terms and caption; values unchanged | 2026-10-24 |
| C | Re-framed as the location-neutral bounding basis (owner decision, 2026-10-29): the baseline is not tied to a location, and every site value is the strictest value across the localization set. The former DFW study-site values are superseded as the basis; location enters as an input of the site design tool. | 2026-10-29 |

## 1. Purpose and scope

The plant is a system of engineering: an engineer can build it, whole or in part, at a location of their choice. The baseline design therefore carries no location. Each site value in the baseline is a **bounding value**: the strictest value across the localization set (`flow_graph/param/sites/`, AQS-PLAN-011), carried from the governing site with its published source. A real site design takes its location as an input of the site design tool, replaces every bounding value with the location's published value, and the model re-solves. Because the baseline bounds the set, a site design reduces demand.

Seismic spectral values are the one exception: they are a per-site input, because the spectral shape changes the foundation method (presumptive bearing versus an engineered foundation), not a scalar size. The baseline carries its study-site value; a site design replaces it and the foundation re-solves.

## 2. Terms

Design dry bulb: the outdoor air temperature exceeded for only the stated share of hours in a year. The 0.4 % cooling value is exceeded for 0.4 % of the hours; the 99.6 % heating value is exceeded (colder) for 0.4 % of the hours.

Bounding value: the strictest value of a kind across the localization set. It is a default, not a forecast: it keeps the baseline conservative for any location the set spans, and a site design always replaces it.

Risk Category II: the ordinary building category of ASCE 7-22, which sets the return period of the design wind.

Ss and S1: mapped spectral accelerations at 0.2 s and 1 s periods (ASCE 7-22), which set the seismic load. SDS and SD1 are the design spectral accelerations derived from them.

Site class: soil category for seismic amplification (IBC 1613.2.2).

## 3. Baseline bounding values

Table 3.1 lists the bounding values and their governing sites. The profile entries are bound to the drivers (`flow_graph/param/drivers.json`), so the values here, in the drivers and in the baseline profile (`flow_graph/param/sites/baseline.json`) are one set.

Table 3.1. Location-neutral bounding values

| Item | Value | Governing site | Source |
| --- | --- | --- | --- |
| Cooling design, 0.4 % dry bulb | 47.4 °C | death_valley | NOAA normals, Furnace Creek (Q-033) |
| Heating design, 99.6 % dry bulb | −9.4 °C | death_valley | NOAA normals, Furnace Creek (Q-033) |
| Insolation, annual mean PV yield | 5.41 kWh/kWp d | baseline run | NREL PVWatts v8 |
| Night hours for the storage model | 14 h | death_valley | NOAA normals |
| Basic wind speed (Risk II) | 70 m/s | floating_island | Saffir-Simpson category 5 |
| Flat-roof snow | 0.24 kPa | baseline run | A-M-105 (the set's strictest) |
| Seismic SDS / SD1 | 0.107 g / 0.08 g (study value; per-site input) | baseline run | ASCE 7-22; replaced at each site |
| Soil, allowable bearing | 72 kPa (1500 psf) presumptive clay | location-neutral | IBC Table 1806.2; a geotechnical report replaces it |
| Soil, resistivity (grounding) | 50 Ω·m class | location-neutral | GROUNDING study value; a Wenner test replaces it |

## 4. How the values are used

Outdoor equipment and cooling loops are rated at the bounding 0.4 % cooling dry bulb (47.4 °C). The structural frame and foundations take the bounding wind (70 m/s) and the study seismic; the foundation check at the bounding seismic of any higher-spectral site re-solves with that site's values and may require an engineered foundation. PV is sized at `pv_oversize_factor` times the nameplate that closes the daily balance at the bounding yield.

## 5. Values still to be sourced

- The annual-mean envelope coefficients (heating and cooling season mean temperature differences and the IECC climate-zone envelope values) still carry the former DFW-derived study values; their bounding needs the published station normals of the governing sites. Tracked under X-BAS-03.
- The polar-night power architecture for the antarctic site is a different technology class question: Q-034.
- Per-parcel values (ASCE Hazard Tool, geotechnical report, Wenner test) belong to each site design, not to the baseline.

## 6. References

- AQS-PLAN-011, the localization plan, and the site profiles in `flow_graph/param/sites/`.
- ASCE/SEI 7-22, Minimum Design Loads (wind, snow, seismic).
- IBC 1806.2, presumptive allowable bearing pressures.
- NREL PVWatts Calculator v8, the baseline site run.
- NOAA NCEI climate normals for the governing sites (Furnace Creek; McMurdo).
- The former DFW study-site values (ASHRAE Dallas Love Field design conditions; NREL PVWatts Dallas) remain in the assumptions history and in the git record of this page.
