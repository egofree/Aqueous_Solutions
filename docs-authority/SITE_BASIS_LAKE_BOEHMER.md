# Lake Boehmer site basis and mobile solar electrodialysis design

Document number: AQS-SITE-015
Revision: A
Date: 2026-11-01
Profile: `flow_graph/param/sites/lake_boehmer.json` (site id `lake_boehmer`, site code LB)
Plan: AQS-PLAN-011 sections 4-6; open questions Q-034, Q-036 and Q-037
Locale design pass: `flow_graph/param/lake_boehmer.py` (stamps `params.lb_design` on the LB_* units and LIO_BAT)

| Rev | Description | Date |
|---|---|---|
| A | First issue: profile, environment, feed basis and its gaps, the ED train design and sizing, power and storage, the container concept, and the safety and honesty statements | 2026-11-01 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

Lake Boehmer is a salt lake in Pecos County, west Texas, fed by the artesian discharge of the abandoned Sloan Blair No. 1 oil well. This page records the locale: a mobile, solar-powered, unmanned electrodialysis plant that draws lake brine, strips the hydrogen sulfide, softens it, desalts it in two electrodialysis stages, and returns the product and the concentrate to the lake. The service is lake restoration. The reference plant stays the baseline profile; this variant writes only its differences. The sizing values on this page are what the drivers produce (drivers `WTR.lake-boehmer.*` through `flow_graph/param/lake_boehmer.py`); they re-derive when a driver changes.

## 2. Site and environment

The site sits near Imperial, Pecos County, Texas, at the climate-grid point 31.22 N, 102.73 W; the parcel is not chosen yet and replaces the grid point at the next site design. Table 2.1 lists the environment with its sources and verification state.

Table 2.1. Environment basis

| Quantity | Value | Source | Verification |
|---|---|---|---|
| Design temperature range | -18 C to 43 C | NWS Fort Stockton-Pecos County Airport records (Winter Storm Uri low, 2021-02; 114 F high, June 2023) | ASHRAE station values replace the station records at the parcel |
| PV yield, design | 5.8 kWh/kWp/d before losses | NREL/GSA Pecos County class 5.8-6.1; the ERA5 grid point (2020-2024) reads 5.62 | PVWatts hourly run at the parcel |
| PV yield, winter trough | 3.5 kWh/kWp/d | SOLAR_RESOURCE_PECOS | same hourly run |
| Night served from storage | 13.5 h | NWS Fort Stockton December | hourly load and irradiance run |
| Gross lake evaporation | 5.0-7.5 ft/yr (about 1.5-2.3 m/yr) | TWDB Technical Note 21-01 | site note only; the return boundary makes it a lake property |
| Basic wind speed | 49 m/s class | ASCE7_22 | hazard-tool run at the parcel |
| Snow, seismic, ground values | coarse class values, each flagged | ASCE7_22, IBC2027_1806 | hazard tool and geotechnical report at the parcel |

The grid point, not a parcel, fixes the climate inputs; the jurisdiction is United States, Texas, with TCEQ water-quality authority, RRC over the well source, and Pecos County codes at the parcel.

## 3. Feed, product, and the honest salt balance

The feed is artesian brine from the abandoned well, not irrigation drainage. Table 3.1 carries the feed basis with its verification state; every derived value waits on the sealed MPGCD laboratory report for the wellhead brine.

Table 3.1. Feed basis

| Parameter | Value | Source | Verification |
|---|---|---|---|
| Total dissolved solids | about 105 g/L (three times seawater) | Texas Monthly (Gold, 2021-12-08), derived | A-M-434; sealed MPGCD report |
| Sulfate | about 7,500 mg/L (about 25 x the SMCL of 300 mg/L) | RRC sampling reported by CBS7/KOSA (2022-10-03) | A-M-435; sealed MPGCD report |
| Hydrogen sulfide | 110 ppm at the wellhead (design value, worst reported case) | RRC news release 2022-04-08 with Etech | A-M-436; the MPGCD laboratory read far higher |
| Calcium | unmeasured | gap | A-M-447; the assay sets the softening chemistry and confirms the recovery |
| Radioactivity, arsenic | reported slight, unquantified | gap | assay and radiological screen at the design pass |

The product target is the TCEQ segment 2311 annual-average class: TDS 15,000 mg/L, chloride 7,000 mg/L, sulfate 3,500 mg/L (A-M-448). Recovery is 0.5 of the feed as product (A-M-437), set by the concentrate gypsum limit: calcium sulfate saturation at most 2 x Ksp with prior lime/soda softening.

The salt balance closes by construction: feed salt = product salt + concentrate salt. The honesty statement the owner decision requires (Q-037) follows: **both the product and the concentrate return to the lake, so the net lake salt removal is about zero.** Only the scrubbed sulfide and the softening sludge leave the lake system. The service the plant sells is degas plus in-lake dilution, not salt export. The export alternative - product sent to segment 2311 waters - would make the net removal equal the product flow times the product TDS (about 15 kg/m3, about 7.5 t/d at the design flow); it is recorded as the alternative, not the design.

## 4. Process train

The train is LB_INTAKE (floating screened shallow-lake intake) to LB_DEGAS (packed air stripper sized from the Henry coefficients of H2S and CO2, A-M-450) to LB_DEGAS_SCRUB (caustic-polish scrubber on the stripper off-gas) to LB_SOFTEN (lime/soda-ash reactor with clarifier) to LB_ED1 (primary stage, 105 to 45 g/L) to LB_ED2 (polishing stage, 45 to 15 g/L) to LB_PROD_TANK, and out through LB_PROD_OUTLET, the accounting boundary of the return diffuser. LB_BRINE_RETURN carries the concentrate from both stages plus the softening sludge to the same diffuser. LB_CHEM_STORE holds lime, soda ash, scrubber caustic and clean-in-place acid. Heat rejects to air through DRY_COOLER; the ground loop is eliminated. The units are placeholders in the reference graph under `WTR.lake-boehmer-train` and size at this pass.

## 5. Sizing (what the drivers produce)

Table 5.1 lists the electrodialysis sizing from the transfer function in the module docstring of `flow_graph/param/lake_boehmer.py` (F from CODATA2018; cell-pair voltage A-M-438; current efficiency and density A-M-439/440; membrane area A-M-441). The specific-energy rule: per cubic metre of dilute, the charge that transports the salt at the current efficiency, at the cell-pair voltage, over the Faraday constant.

Table 5.1. Electrodialysis sizing at the design drivers

| Quantity | Value | Basis |
|---|---|---|
| Dilute (product) flow | 500 m3/d | recovery driver A-M-437 |
| Stage 1 duty | about 1,027,000 eq/d, 77.7 kWh/m3, about 38,847 kWh/d | 105 to 45 g/L, A-M-449 split |
| Stage 2 duty | about 513,000 eq/d, 38.8 kWh/m3, about 19,424 kWh/d | 45 to 15 g/L |
| Modules (duty / installed) | stage 1: 14 / 15; stage 2: 7 / 8 | R = j A CE / F per module; N+1 spare per stage (A-M-451) |
| Rectifier capacity, installed | 1,800 + 960 kW | the ceil margin; normal operation runs the duty point |
| Auxiliaries | 4.0 kWh/m3 of feed, about 4,000 kWh/d | A-M-442 |
| Site demand | about 2,595 kW average | the sum above over 24 h |

Power follows the repo D-PV rule: the balancing array at the site yield and derate, times the oversize factor (2.0), on a redeployable ground-mount ballast-rack field - the PV array is **not** containerized. The battery usable store carries the night energy plus the contingency days (A-M-443); the charged store divides by the round trip. LIO_BAT replaces the flow battery, pumped hydro, genset, fuel cell and methanol storage functions at this locale (Q-034, Q-036). Table 5.2 lists the result; the numbers re-derive from the drivers, and the generator output is the authority for the current values.

Table 5.2. Power and storage at the lake_boehmer locale drivers

| Quantity | Value |
|---|---|
| PV balancing nameplate | about 16,656 kWp |
| PV nameplate installed | about 33,312 kWp |
| Battery usable store | about 97,299 kWh (night plus one contingency day) |
| Battery charged store | about 139,000 kWh |
| Battery containers | about 35 ISO 1CC |
| Total container count | ED 12 + utility 14 + battery 35 (parametric; A-M-444/445/446) |

## 6. Container layout concept

Every process module is an ISO 1CC 20-ft container (6058 x 2438 x 2591 mm external, A-M-444) set on the pad by crane and haulable on a standard semitrailer. Two ED modules share a container with their rectifiers and the clean-in-place manifold. The softening duty takes three containers (reactor, clarifier, sludge set); power conversion takes three (PV inverters, ED rectifier rooms, battery converters). The chemical store, product buffer, controls and the brine-return set take one or two each. The counts are parametric from the module and utility counts and re-derive with them.

## 7. Safety

Hydrogen sulfide makes the pad a lethal site. Fixed H2S monitors stand at the degasser, the scrubber and the vent, with the OSHA ceiling of 10 ppm as the never-exceed value, wind socks, and a two-person rule outside the control container. The 110 ppm wellhead reading is the site-safety design value; the scrubber design load waits on the dissolved-sulfide assay (A-M-436). If the packed tower cannot meet the vent target on the assayed sulfide, caustic chemical stripping is the fallback (A-M-450).

## 8. Gaps

The open site-design items, each flagged in the profile or the drivers with needs_verification:

- Bathymetry (intake siting and diffuser design).
- The full ionic assay, including calcium, magnesium and silica, from the sealed MPGCD laboratory report.
- Radioactivity and arsenic quantification (reported slight, unmeasured).
- The parcel boundary, haul route and pad survey (climate, wind, snow, seismic and ground values are grid-point and class placeholders until then).
- The packed-tower transfer-units design and the pH-dependent sulfide speciation.
- The recovery confirmation against the assayed gypsum saturation.
