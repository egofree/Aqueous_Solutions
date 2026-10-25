# Localization plan: site profiles and locale variants

Document number: AQS-PLAN-011
Revision: A
Date: 2026-10-25

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-25 |

## 1. Purpose and scope

The plant is meant to work wherever it can be built. This plan sets out how the parametric model will take the site as an input, so that one design produces a variant for each locale and the differences between locales are a generated result. It covers the first locales to be studied: Death Valley (hot desert), Antarctica (polar), Mars (planetary surface) and low Earth orbit.

This page is the investigation and the plan. It does not change the plant graph, the drivers or any generated output. It records:

- how the model represents the site today, and where conditions on the surface of the Earth are fixed in code (section 3);
- the site profile, one data file per locale that carries every environmental input (section 4);
- how a unit states what it needs from its surroundings, and how a locale keeps, replaces or retires it (section 5);
- the environmental values and the design consequences for each locale (sections 6 to 9);
- the gaps in the current architecture and how to close them parametrically (section 10);
- the build order (section 11), the acceptance checks (section 12) and the decisions the owner must take (section 13).

Every value in sections 6 to 9 cites a published source. A value enters the model only through a site profile entry that carries that source, or through an entry in the assumptions register (AQS-REG-002) with the test that will confirm it.

## 2. Summary

- The site is not yet an input. The study site values are in AQS-SITE-002 (`docs-authority/SITE_BASIS.md`) and in `flow_graph/param/drivers.json`, mixed with process drivers. Several facts about the surface of the Earth are constants in code: standard gravity, standard atmospheric pressure, the composition and density of air, and the use of outside air as a heat sink, an oxidant and a vent destination.
- A site profile per locale, `flow_graph/param/sites/<site_id>.json` (to be created), will hold every environmental input in the same form as a driver (value, units, reference or register id, verification test). The driver loader applies the selected profile. The baseline profile carries the present values, so the baseline output does not change.
- Each unit will state its environmental needs, such as a minimum gravity for buoyant separation, outside air for heat rejection, or ground contact. A check compares those needs with the selected profile and requires a recorded decision for every unit whose needs are not met: keep, use an alternate unit, or retire with a stated replacement. The table of these decisions is the answer to the question of what the plant must change to work in each place.
- Death Valley keeps the architecture and stresses heat rejection, water supply and material temperatures. Antarctica stresses a dark season, freezing, and a treaty that forbids mineral resource activity. Mars needs pressurised process spaces, works at partial gravity, and can use the carbon dioxide atmosphere, ground ice and regolith as feed. Low Earth orbit removes gravity, air and ground together and needs the largest set of alternate units.
- The build order is: profile and loader with the baseline unchanged; code constants moved into the profile; site selection and output namespaces; unit needs and capability decisions; then the locales in order of increasing departure from the baseline: Death Valley, Antarctica, Mars, low Earth orbit.

## 3. How the model represents the site today

### 3.1 Where site values are held

By owner decision the study site is a Dallas–Fort Worth class location (AQS-SITE-002). Table 3.1 lists each environmental input, where it is held and what uses it.

Table 3.1. Environmental inputs in the current model

| Input | Held in | Used by |
| --- | --- | --- |
| Cooling design dry bulb | driver `site_design_dry_bulb_C`; AQS-SITE-002 | `docs-authority/_hot_draw_coolers.py`; make-up air text in `docs-authority/_hvac.py` |
| Heating design dry bulb | AQS-SITE-002 text and `_hvac.py` text only | heating, ventilation and air conditioning (AQS-THM-002) |
| Ambient temperature for insulation | driver `ins_ambient_C` | `docs-authority/_insulation.py` |
| Solar resource | drivers `pv_yield_kWh_kWp_d`, `pv_roof_yield_factor`, `pv_system_derate`, `night_hours`, `crit_autonomy_d`; hourly data in `docs-authority/data/` | roof closure in `flow_graph/param/solver.py`; power in `flow_graph/param/write_graph.py`; storage in `flow_graph/param/ess_tf.py` |
| Photovoltaic (PV) oversize | driver `pv_oversize_factor` | `solver.py` |
| Wind | driver `wt_wind_ms` | `flow_graph/param/water_tower.py`, `solver.py` |
| Snow | driver `roof_snow_kPa` | roof loads in `solver.py` |
| Seismic | AQS-SITE-002 text only | no sizing function |
| Soil bearing and unit weight | drivers `soil_allow_kPa`, `soil_unit_weight_kN_m3` | `docs-authority/_foundation.py` (AQS-BLD-017) |
| Soil resistivity | driver `ELEC.distribution-train.gnd_soil_rho_ohm_m` | `docs-authority/_grounding_study.py` |
| Frost depth | AQS-SITE-002 text only | foundation text |
| Ground heat exchange | drivers `GEO.geo-loop.ghex_*` | `flow_graph/param/geo_loop.py` |
| Latitude and orientation | AQS-SITE-002; AQS-SITE-001 (the dock faces the pole) | site access, array tilt |
| Water make-up | dock make-up stream (Q-002) | balance |
| Logistics | DOCK sector; product `hold_d` drivers set by the dock dispatch campaign | storage sizing |
| Line frequency | driver `MFG.tools-metal-forming-train.mfa_line_hz` | motor design |
| Codes | EDITIONS table in `flow_graph/param/code_basis.py` (AQS-STD-007) | every check document |

### 3.2 Earth-surface conditions fixed in code

These are the places where the model assumes the surface of the Earth without saying so. Each must become a profile value, or a value derived from the profile, before a locale off the Earth's surface can be represented.

- Gravity. Standard gravity is a literal in tank, reactor, evaporator, scrubber, heat battery, geothermal loop, storage and motor sizing, and in the foundation, structural load, fire, hydro and water tower calculators. Find them with `rg -n "9\.80665|9\.81\b" flow_graph docs-authority`.
- Atmospheric pressure. Standard pressure is a literal in the balance, evaporator, scrubber, fire, cold box and pressure node modules and in several studies. Find them with `rg -n "101\.325|101325|1\.01325" flow_graph docs-authority`.
- Air. The balance uses the partial pressures of oxygen, nitrogen and carbon dioxide in Earth air (`HENRY` in `flow_graph/param/balance.py`). Drivers carry air densities for purges, vents and headers and the air carried in with the feed (`hdr_rho_air`, `WTR.grey-black-train.san_air_rho20_kg_m3`, `ELEC.storage-train.ZNBR2.purge_air_rho_kg_m3`, `vs_air_mg_kg`).
- Outside air as a heat sink. DRY_COOLER (HEAT) rejects heat to outside air, and coolers and ventilation are rated at the cooling design dry bulb. There is no radiative or ground-only heat rejection.
- Outside air as an oxidant and a vent. AFTERBURNER, COMB_HEAT, BACKUP_GEN and the sanitation combustion step burn with air. Vents, relief devices and scrubber stacks discharge to the atmosphere.
- Free liquid surfaces and buoyancy. Pumped hydro (HYDRO_SET), the roof and catch tanks, atmospheric tanks, stirred tanks with a gas space, packed scrubbers, flotation (FLOAT_SINK) and the separation of the bromine phase in ZNBR2 depend on gravity to keep gas and liquid apart.
- Ground contact. The foundation, the earthing grid (IEEE 80) and the ground heat exchanger (GEO_GHEX) assume soil.
- A day and a night. PV and storage are sized from one mean day and a fixed number of night hours. Polar seasons, orbital eclipses, the Martian sol and dust storms cannot be represented.
- Road logistics. The dock is a truck dock, hold times are dispatch campaigns, and make-up water arrives at the dock to replace the water carried out in products.
- One jurisdiction. The code basis lists codes for a building on land in the United States, with international standards. It cannot select a jurisdiction or add a treaty or a space agency standard.
- Direct reads of the drivers file. Many scripts open `drivers.json` directly instead of calling `drivers.load()`. A profile applied in the loader would not reach them. Find them with `rg -l "drivers\.json" --glob "*.py"`.

### 3.3 What already helps

- Oxygen comes from water electrolysis (AQS-PAR-005), not from air, so the main oxygen source does not depend on the atmosphere.
- The life support train already uses a carbon dioxide removal basis from the International Space Station (driver `HAB.life-support-train.HABITATION.cdra_half_cycle_min`).
- The feed assay (AQS-ASSAY-001) already has a silicate and oxide case, which is the starting point for regolith feed.
- Graph nodes carry a `presence` field (present, placeholder, retired), which can carry a per-site status.
- `drivers.load()` is a single entry point that already rejects a value with no basis.

## 4. Site profile

### 4.1 File and schema

Each locale has one file, `flow_graph/param/sites/<site_id>.json` (to be created), validated against `flow_graph/schema/site_profile.schema.json` (to be created). Every entry has the form of a driver: `value`, `units`, and a `ref` (a key in `flow_graph/param/refs.py`) or a `register` id, with `needs_verification` and `verification_test` where no published value fixes it. The loader rejects an entry without a basis in the same way as a driver.

Table 4.1 lists the groups the profile carries. A group that does not apply at a locale is present and marked not applicable with its reason, so that a missing value is always an error and never a silent default.

Table 4.1. Site profile groups

| Group | Entries |
| --- | --- |
| Identity | site id, name, body (Earth surface, Earth orbit, Mars surface), coordinates or orbit (altitude, inclination), elevation, site basis document number |
| Gravity | apparent gravity, m/s² (for a rotating structure, the design value at the working radius) |
| Atmosphere | external pressure range, composition as mole fractions, density, and three flags: breathable, usable as a vent sink, usable as an oxidant |
| Thermal environment | cooling and heating design dry bulb, coincident wet bulb, effective radiative sink temperature, ground temperature at depth, freezing risk |
| Solar | resource model (hourly series file, orbit model or monthly table), irradiance above the atmosphere, mean and worst-period yield, longest dark period, soiling or dust loss rate, snow and frost loss |
| Wind | basic wind speed for structures, mean wind speed for generation, air density for dynamic pressure |
| Seismic | mapped accelerations and site class, or the source showing that no seismic code applies |
| Ground | allowable bearing, unit weight, frost or active-layer depth, permafrost or ice-sheet flag, electrical resistivity, thermal conductivity |
| Radiation | ambient dose rate and the shielding basis |
| Water sources | each source with type (aquifer, seawater, snow or ice, ground ice, recycle only), quality, temperature and sustainable yield |
| Local feedstocks | each material available at the site, mapped to a feed case in AQS-ASSAY-001 |
| Logistics | arrival mode (truck, ship, launch, lander), resupply interval, mass cost class, export outlets |
| Electrical | external grid present or not, alternating current frequency or direct current bus voltage, earthing method (earth electrode, floating, structure bonding) |
| Jurisdiction | code families that apply (section 4.6) |
| Capability decisions | per sector or unit: keep, alternate, retire (section 5) |

### 4.2 Binding to the drivers

The profile does not duplicate drivers. Each environmental driver in `drivers.json` gains a `site` field naming the profile entry that supplies it, and `drivers.load()` resolves it from the selected profile. Entries with no driver today, such as gravity and the atmosphere, become new drivers bound in the same way, and the literals in section 3.2 are replaced by reads of those drivers. Quantities that follow from the environment, such as an air density at a given temperature, are computed from the profile in a new module `flow_graph/param/site.py` (to be created), not entered a second time.

The baseline profile, `flow_graph/param/sites/baseline.json` (to be created), carries the present values with their present references and register ids (AQS-SITE-002 and the A-M entries). With it selected, the resolved driver set equals the present `drivers.json` value for value, and `python3 -m flow_graph.param.regen --check` stays clean.

### 4.3 Selecting a profile

- Set the environment variable `AQS_SITE=<site_id>`, or pass `--site <site_id>` to `python3 -m flow_graph.param.regen`. The flag sets the variable for every child stage, which already inherits the environment.
- With neither set, the baseline profile is used. An unknown site id fails before any stage runs.
- Every generated file records the site id and a hash of the resolved profile in its header, and the regeneration receipt records both.

### 4.4 Output namespaces

- Baseline outputs stay where they are, so existing paths and citations do not change.
- Every other locale writes under `sites/<site_id>/`, which mirrors the repository paths of the outputs, for example `sites/<site_id>/flow_graph/plant_flow_graph.json` and `sites/<site_id>/docs-authority/duties/`. Each stage in `flow_graph/param/regen_manifest.json` still declares its outputs once; one path function adds the prefix.
- The base graph stays the sole topology authority. A locale graph is the base graph with the locale's capability decisions applied (section 5); it is a generated output and is never hand-edited.
- `regen --check --site <site_id>` checks one locale. A new `--all-sites` option runs every profile in `flow_graph/param/sites/` (to be created).

### 4.5 Document numbers and identifiers

- A generated document in a locale namespace keeps its base number with the site code as a suffix, for example `AQS-THM-002/MARS`. `docs-authority/_doc_register.py` is extended to register each number and site pair, and `flow_graph/test_doc_numbers.py` fails on a duplicate pair. The alternative, a fresh number for every locale copy, is put to the owner in Q-028.
- A hand-written locale page, such as the site basis of a locale, takes a new number from `python3 docs-authority/_doc_register.py --next AQS-SITE`.
- An alternate unit gets a new unit id in the base graph, present only where a profile selects it. Unit, stream, assumption, task and question ids take the next unused id in their sequence and are never reused.

### 4.6 Code basis per jurisdiction

Each row of the EDITIONS table in `flow_graph/param/code_basis.py` gains a family: building on land in the United States (the present rows), the Antarctic Treaty system, crewed spacecraft, and planetary surface operations. The profile lists the families that apply. A check document cites only codes in the selected families, and a check with no governing clause in those families is reported as open rather than passing. Editions follow the latest-edition rule recorded in Q-018 and are confirmed when a family is added.

## 5. Unit needs and capability decisions

### 5.1 What a unit needs

Each unit states its environmental needs in `flow_graph/param/sites/unit_needs.json` (to be created). Needs are given by unit class, with a unit-level override, so units need not be edited one by one. Table 5.1 lists the needs used in this plan.

Table 5.1. Environmental needs

| Need | Meaning | Examples |
| --- | --- | --- |
| buoyant separation | a minimum apparent gravity to separate gas from liquid or solids from liquid | flotation, settlers, packed columns, stirred tanks with a gas space, electrowinning gas release |
| free surface | a liquid surface open to a gas space | atmospheric tanks, pumped hydro, roof and catch tanks |
| air heat sink | outside air at a usable temperature | DRY_COOLER, air-cooled condensers |
| air oxidant | outside air with oxygen | AFTERBURNER, COMB_HEAT, BACKUP_GEN |
| vent sink | an atmosphere that can take a vent or relief discharge | scrubber stacks, relief devices |
| ground contact | soil or rock for bearing, earthing or heat exchange | foundation, earthing grid, GEO_GHEX |
| liquid water at ambient | external pressure above the triple point of water | any open water surface |

### 5.2 Decisions in the profile

The profile's capability decisions name, for a sector or a unit, one of: keep; alternate, naming the unit that performs the same function; or retire, with the reason and the unit that takes over its role. Resizing is not a decision: the solver resizes every kept unit from the profile.

A check, `flow_graph/param/test_site_capability.py` (to be created), fails when a unit's needs are not met by the profile and no decision is recorded, and when a decision retires an energy or life-support unit without naming a diverse replacement (AGENTS.md, Redundancy). A generated table per locale lists every decision with its reason. Comparing those tables across locales gives the record of what the plant changes in each place.

## 6. Death Valley

### 6.1 Site and environment

Death Valley is a national park, and an industrial plant would sit outside it. The profile uses the climate record at Furnace Creek as the bounding hot desert climate; the parcel is an owner decision (Q-020). Table 6.1 lists the values.

Table 6.1. Death Valley environment

| Quantity | Value | Source |
| --- | --- | --- |
| Station | Death Valley NP, USC00042319, 36.46° N, 116.87° W | [1] |
| Elevation | −59 m (−194 ft) | [1] |
| July mean daily maximum, 1991 to 2020 | 47.4 °C (117.4 °F) | [1] |
| July mean daily minimum, 1991 to 2020 | 32.8 °C (91.0 °F) | [1] |
| Highest recorded air temperature | 56.7 °C (134 °F), 1913-07-10 | [2] |
| Mean annual precipitation, 1991 to 2020 | 56 mm (2.20 in) | [1] |
| Local groundwater | wells on the alluvial fan, about 30 °C (86 °F), moderately mineralised, high silica, fluoride and arsenic; treated by reverse osmosis | [3] |
| Solar resource | hourly series from the National Solar Radiation Database at the parcel, by the same pvlib method as the baseline | [4], [5] |
| Wind, seismic and snow | ASCE Hazard Tool at the parcel | [6] |
| Soil | geotechnical report at the parcel | assumption until then |

The 0.4 % cooling dry bulb for the profile comes from the American Society of Heating, Refrigerating and Air-Conditioning Engineers (ASHRAE) climatic design conditions for the nearest listed station [7], or from the hourly record with an assumption entry until it is confirmed.

### 6.2 Design consequences

- Heat rejection. Outside air is hotter than the return of the low-grade loops for much of the summer, so DRY_COOLER cannot reach its approach. The profile selects a rejection mode per heat ladder level: a heat pump that lifts to a rejection temperature above the design dry bulb, night rejection into the thermal stores used as cold stores, rejection to the ground through GEO_GHEX, or evaporative cooling charged against the water balance.
- Water. Rain is negligible. Groundwater is the make-up source and needs an intake unit (well and reverse osmosis pretreatment for silica, fluoride and arsenic) feeding WTR. The arsenic and fluoride reject becomes a plant stream with a defined outlet.
- Materials. Outdoor thermoplastics and roof equipment run above air temperature in sun. The material temperature check (driver `pvc_u_max_C` and its kin) runs at the design dry bulb plus solar gain.
- PV. The resource is high, but cell temperature losses and soiling grow. The module temperature comes from pvlib at the site temperature. The rule that PV is sized at `pv_oversize_factor` times the nameplate that closes the daily balance is unchanged.
- Thermal stores. Standing losses fall. The lowest-grade store can serve as a cold store for night rejection.
- Crew and ventilation. Cooling dominates the ventilation load. Outdoor work follows the heat illness rules of the state; in California these are Title 8 sections 3395 and 3396 [8].
- Farm. A sunlit greenhouse would need large cooling and water. The profile compares an enclosed, artificially lit grow room with a shaded greenhouse.
- Structure. The region has active faults, so seismic loads come from the hazard tool at the parcel. Saline and sulfate soils set the concrete exposure class (ACI 318, sulfate exposure category, edition per AQS-STD-007). Alluvial fans need flash-flood drainage.
- Local feedstocks. Evaporite minerals (borates, halite, gypsum) and scrap from mining districts are candidate feeds, each mapped to an assay case before use.
- Logistics and codes. The truck dock and the United States building family apply unchanged, with the state codes of the parcel.
- Sectors. None is retired. HEAT, WTR, ELEC and FARM are resized, and a water intake unit is added.

## 7. Antarctica

### 7.1 Site and environment

The default is a coastal site of the McMurdo class, which has sea access and seawater. A plateau site of the South Pole class is a second profile (Q-021). Table 7.1 lists the values.

Table 7.1. Antarctic environment

| Quantity | Value | Source |
| --- | --- | --- |
| McMurdo position | 77°51′ S, 166°40′ E | [9] |
| McMurdo mean annual temperature | −18 °C | [9] |
| McMurdo extremes | 8 °C summer, −50 °C winter | [9] |
| McMurdo wind | mean 12 kn (6.2 m/s); gusts above 100 kn (51 m/s) | [9] |
| Daylight | south of 66.5° S, one long day and one long night each year; the dark period at the site is computed from solar geometry | [9], [5] |
| South Pole elevation | 2835 m | [10] |
| South Pole mean annual temperature | −49.3 °C | [10] |
| South Pole precipitation | about 70 mm water equivalent per year | [10] |
| South Pole ice movement | about 10 m per year | [10] |
| South Pole barometric pressure | about 513 mmHg (68.4 kPa); physiological altitude about 3200 m | [11] |
| McMurdo water supply | seawater at −2 °C (28 °F) warmed with power plant waste heat, then reverse osmosis | [12] |
| Mineral resources | any activity relating to mineral resources, other than scientific research, is prohibited | [13] Article 7 |
| Waste | listed wastes (including polyvinyl chloride, polyurethane foam, polystyrene, rubber and lubricating oils) are removed from the treaty area; open burning is not allowed | [13] Annex III |
| Non-native organisms and soil | introduction of non-native species needs a permit; non-sterile soil is not imported | [13] Annex II |

### 7.2 Design consequences

- Power. PV produces nothing through the dark season, so a daily night-hours basis fails. Storage becomes seasonal. The candidates are the plant's own hydrogen with the fuel cell, sized for the dark season, wind generation as a diverse winter source, and imported fuel as the last resort. The basis for the 200 % PV rule at such a site is an owner decision (Q-024).
- Heat. Heating dominates. Process waste heat becomes a resource: DRY_COOLER becomes a heat recovery coil, and the seawater intake is warmed with waste heat as at McMurdo [12]. All water lines need freeze protection.
- Materials. The material temperature check gains a minimum design temperature. Metals follow the low-temperature limits and impact tests of ASME B31.3-2024 paragraph 323.2.2 [14]. Thermoplastics outside heated space are excluded.
- Water. Seawater reverse osmosis is the default, with snow melt as the diverse second source. Brine and treated waste water discharges follow Annex III [13].
- Feedstock. Article 7 rules out mining, so local feed is limited to station waste and returned cargo. The plant processes waste that Annex III would otherwise send north; whether pyrolysis and AFTERBURNER qualify needs an environmental evaluation under Annex I [13] (Q-025).
- Farm. The grow bed is soilless, which suits Annex II. Seeds and cultures are imported under permit.
- Structure. Snow drift, snow load and wind govern. Coastal sites are on volcanic ground with permafrost; plateau sites are on moving ice and need elevated, jackable structures.
- Earthing. Frozen ground has a high resistivity, so the earthing design follows the profile value rather than the baseline grid.
- Crew. No evacuation is possible for months, so the backup duration for energy and life support is set by the dark season rather than the hours in NFPA 110. At a plateau site the low pressure makes oxygen enrichment of rooms from the plant's own oxygen an option, limited by the fire rules for enriched atmospheres.
- Logistics. Ships and aircraft arrive in the summer season. The resupply interval sets the product `hold_d` values and the spares holding, and products leave once a year.
- Codes. The Antarctic Treaty family is added on top of the operating state's own law; for the United States this is the Antarctic Conservation Act and 45 CFR Part 670 [15].
- Sectors. PUMPED_HYDRO needs heated enclosed reservoirs and is a candidate for an alternate; GEO changes from heat source to heat store; a wind generation unit, a seawater intake unit and seasonal hydrogen storage are added.

## 8. Mars

### 8.1 Site and environment

The default is a mid-latitude site with shallow ground ice, of the Arcadia Planitia class (Q-022). Table 8.1 lists the values.

Table 8.1. Mars environment

| Quantity | Value | Source |
| --- | --- | --- |
| Surface gravity | 3.71 m/s² | [16] |
| Length of the solar day (sol) | 88 775 s (24.66 h) | [16] |
| Synodic period (interval between transfer windows) | 779.94 d | [16] |
| Solar irradiance above the atmosphere | 586.2 W/m² mean | [16] |
| Surface pressure | 0.636 kPa at mean radius, 0.40 kPa to 0.87 kPa with season | [16] |
| Surface density | about 0.020 kg/m³ | [16] |
| Atmospheric composition (mole fraction) | CO2 0.951, N2 0.0259, Ar 0.0194, O2 0.00161, CO 0.00058 | [17] |
| Temperature | about 210 K mean; 184 K to 242 K diurnal range at the Viking 1 site | [16] |
| Surface solar resource | computed from optical depth and solar geometry | [18] |
| Dust settling on arrays | about 0.28 % loss of output per sol | [19] |
| Dust storms | a planet-encircling storm in 2018 ended the Opportunity rover mission | [20] |
| Surface radiation | 0.64 mSv/d dose equivalent at Gale crater | [21] |
| Regolith | basaltic, with an X-ray amorphous fraction | [22] |
| Perchlorate | 0.4 % to 0.6 % by mass at the Phoenix site | [23] |
| Ground ice | excess ice within metres of the surface in Arcadia Planitia | [24], [25] |
| Triple point of water | 611.657 Pa | [26] |
| Seismicity | marsquakes recorded by InSight are small | [27] |
| Oxygen from the atmosphere | solid oxide electrolysis demonstrated on the surface | [28] |

### 8.2 Design consequences

- What a building is. The mean surface pressure is close to the triple point of water, so open liquid water cannot be kept. Habitat and process halls are pressurised shells whose structure is governed by internal pressure, not gravity. Regolith cover gives shielding and part of the load to balance the pressure. A process hall can run at a lower pressure in a carbon dioxide and nitrogen buffer gas, enough to keep water liquid; that pressure is a profile driver so that its effect on structure and safety can be swept.
- Atmosphere as a resource. Carbon dioxide feeds MEOH (methanol synthesis) and a new methanation alternate for propellant. Nitrogen and argon for buffer gas come from separating the atmosphere in CRYO. Solid oxide electrolysis of carbon dioxide [28] is the diverse second oxygen source behind water electrolysis. Taking the atmosphere in needs a compressor or a freezing collector from a fraction of a kilopascal; this is a new unit.
- Heat rejection. The thin atmosphere gives weak convection, so radiators and ground heat exchange replace air coolers. The cold surroundings lower the lift for carbon dioxide condensing and oxygen liquefaction.
- Water. Ground ice extraction and melting is a new unit, with perchlorate removal. Recycling closure matters more than on Earth.
- Feedstock. Regolith enters through the silicate and oxide feed case of AQS-ASSAY-001. Perchlorate is both a hazard and an oxygen source. Imported hardware and packaging are further feeds. Each needs an assay case before use.
- PV and storage. Storage covers the sol night and a dust storm. Array cleaning or a soiling allowance follows the settling rate. A non-solar primary is an owner decision (Q-024).
- Thermal stores. Insulation thickness follows from the profile; stores can be buried in regolith.
- Vents and relief. Nothing vents to an atmosphere that cannot take it. Vents go to recovery. Relief devices discharge against a low back pressure, so the relief register is recalculated with the profile pressure.
- Combustion. The atmosphere has no usable oxygen. AFTERBURNER and BACKUP_GEN run on plant oxygen or are replaced by catalytic oxidation and fuel cells.
- Partial gravity. Settling, flotation and packed columns still work but more slowly; every sizing function takes gravity from the profile.
- Earthing. Dry regolith gives no earth electrode, so the electrical system is floating with insulation monitoring.
- Structure. Pressure loads govern. Wind loads are small because the air density is low. Seismic loads are small [27].
- Crew. Radiation shielding uses regolith and water. Life support follows the crewed spacecraft family.
- Logistics. A landing pad replaces the dock. Resupply follows the transfer windows [16]. Surplus is used locally, stored or made into propellant (Q-026).
- Codes. The Outer Space Treaty [29], the COSPAR policy on planetary protection [30] and the NASA interim directive for crewed Mars missions [31] apply, with NASA-STD-3001 for crew health [32]. Ground ice may lie in a special region under [30] (Q-027).
- Sectors. PUMPED_HYDRO and the roof and catch tanks become alternates or are retired. GEO becomes regolith heat exchange. DOCK becomes a landing pad. Atmosphere intake, ice extraction and methanation are added. FARM moves into a pressurised grow room with a perchlorate-free substrate.

## 9. Low Earth orbit

### 9.1 Site and environment

The default orbit is of the International Space Station class, about 400 km at 51.6° inclination (Q-023). Table 9.1 lists the values.

Table 9.1. Low Earth orbit environment

| Quantity | Value | Source |
| --- | --- | --- |
| Total solar irradiance | 1361 W/m² | [33] |
| Orbit period | about 92 min | [34] |
| Eclipse per orbit | up to about 36 min at low beta angle, none at high beta angle; computed from orbit geometry | [34] |
| Neutral density at 400 km | of order 10⁻¹² kg/m³ to 10⁻¹¹ kg/m³ with solar activity | [35] |
| Radiation inside a pressurised module | 0.59 mSv/d to 0.65 mSv/d dose equivalent (2016) | [36] |
| Radiative sink | deep space with Earth infrared and albedo, by orbit and attitude | [37] |
| Water recovery achieved on the International Space Station | 98 % | [38] |
| Local material | spent upper stages and defunct satellites in nearby orbits | [39] |

### 9.2 Design consequences

- What a building is. Crew and liquid processes are in pressurised modules. PV, radiators and processes that want a vacuum (vacuum casting and melting, the PV cell line deposition steps, vacuum distillation) are on an unpressurised truss. Launch mass and volume drive plant density.
- Heat rejection. Radiators are the only sink. Each rejected kilowatt is sized from radiation at the rejection temperature against the sink [37], so heat is rejected at the highest level of the heat ladder that will take it, and heat pumps lift low-grade heat to the radiator temperature.
- Power. An eclipse occurs on most orbits, so storage cycles many times a day and cycle life governs. The bromine phase in ZNBR2 separates by gravity, so ZNBR2 needs an alternate. PV is sized on the sunlit fraction of the orbit.
- Fluids. With no buoyancy, gas and liquid are separated by rotation or membranes, tanks use bladders or surface-tension devices, boiling and condensing need forced flow, packed scrubbers become rotating packed beds, flotation becomes centrifugal separation, and electrolysis and electrowinning cells remove gas by forced flow. Pumped hydro and the water tower are retired.
- Combustion and fire. Open combustion is avoided: AFTERBURNER becomes a catalytic oxidiser and BACKUP_GEN a fuel cell, with a diverse backup of a different type. Water sprinklers do not apply; fire protection follows the crewed spacecraft family.
- Materials. Exposed polymers are eroded by atomic oxygen, so exposed surfaces are chosen for that.
- Structure. There are no gravity loads. Launch and pressure loads govern, with shielding against micrometeoroids and debris.
- Earthing. The structure is the reference, with bonding and spacecraft charging control.
- Crew. Life support already uses a space station basis. Radiation and exercise needs follow NASA-STD-3001 [32].
- Farm. Plants are grown in chambers with capillary watering and artificial light.
- Logistics. A docking port replaces the dock. Products used in orbit include propellant from water, radiation shielding and structural parts; the plant can make the propellant that keeps the orbit up against drag.
- Gravity by rotation. A rotating section gives a chosen apparent gravity at its working radius. Apparent gravity is a profile value, so this choice can be swept (Q-023).
- Codes. The Outer Space Treaty [29] and the crewed spacecraft family apply, with debris mitigation standards.
- Sectors. PUMPED_HYDRO, GEO and the dock are retired or replaced. DRY_COOLER becomes a radiator. The air separation in CRYO has no air to take and becomes cabin air processing. GAS scrubbers, FLOAT_SINK, ZNBR2 and the melting and casting units of FOUNDRY need alternates.

## 10. Architecture gaps

Table 10.1 lists each gap found in section 3, the locales it blocks, and the parametric way to close it.

Table 10.1. Architecture gaps and their parametric handling

| Gap | Blocks | Handling |
| --- | --- | --- |
| Gravity is a literal | Mars, orbit | gravity driver bound to the profile; every sizing function reads it |
| Atmospheric pressure and air are literals | Antarctic plateau, Mars, orbit | atmosphere group in the profile; densities and partial pressures computed in `site.py` |
| Only an air heat sink exists | Death Valley summer, Mars, orbit | heat rejection mode per heat ladder level (air, evaporative, ground, radiative, heat pump lift); radiator sizing function |
| Solar model is one mean day | Antarctica, Mars, orbit | resource model in the profile; storage sized for the longest dark or low period; PV rule basis per Q-024 |
| Free surfaces and buoyancy assumed | orbit, partly Mars | buoyant separation and free surface needs; alternate units |
| Combustion and vents use air | Mars, orbit | air oxidant and vent sink needs; recovery and catalytic alternates |
| Ground contact assumed | orbit, partly Mars and Antarctica | ground group may be not applicable; foundation, earthing and GEO read it |
| Open liquid water assumed | Mars, orbit | liquid water at ambient need; hall pressure driver |
| Truck logistics assumed | Antarctica, Mars, orbit | logistics group sets hold times, spares and outlets |
| One jurisdiction | Antarctica, Mars, orbit | code families per row of the editions table |
| Feed cases are terrestrial | all | local feedstock group mapped to new assay cases |
| Graph is single-site | all | capability decisions applied to the base graph into a locale namespace |
| Scripts read `drivers.json` directly | all | every read goes through `drivers.load()`; a test rejects a direct read |

## 11. Build order

The work is split into phases, each closed by its own check. Tasks X-LOC-01 to X-LOC-10 in AQS-PLAN-007 track them. Table 11.1 gives the order.

Table 11.1. Build phases

| Task | Phase | Done when |
| --- | --- | --- |
| X-LOC-01 | This plan | AQS-PLAN-011 issued; owner questions logged |
| X-LOC-02 | Profile schema, baseline profile and loader | schema and baseline profile committed; `drivers.load()` applies the profile; every script reads drivers through the loader; baseline regeneration unchanged |
| X-LOC-03 | Constants into the profile | gravity, pressure, air composition and air densities read from the profile; baseline regeneration unchanged |
| X-LOC-04 | Site selection and namespaces | `--site`, `AQS_SITE`, `--all-sites`; outputs under `sites/<site_id>/`; register handles locale numbers |
| X-LOC-05 | Unit needs and capability decisions | needs table, decision check and per-locale decision table generated |
| X-LOC-06 | Heat rejection, solar and storage models | rejection modes, radiator sizing and the solar resource model in the solver |
| X-LOC-07 | Death Valley variant | profile, site basis page, regeneration and closure pass |
| X-LOC-08 | Antarctic variant | as X-LOC-07, with the treaty code family |
| X-LOC-09 | Mars variant | as X-LOC-07, with in-situ feed cases and alternate units |
| X-LOC-10 | Low Earth orbit variant and cross-locale comparison | as X-LOC-07, with microgravity alternates; a generated comparison of decisions and sizes across locales |

## 12. Acceptance checks

These checks are added with the phase that needs them and run in `scripts/check_all.sh`.

- A profile that lacks a required entry, or has an entry without a basis, fails the loader.
- With the baseline profile, the resolved drivers equal `drivers.json` and `regen --check` changes nothing.
- No script reads `drivers.json` except through the loader, and no sizing module contains a gravity or atmospheric pressure literal.
- Every profile in `flow_graph/param/sites/` (to be created) regenerates, and its loop closure and mass and energy balance checks pass within the misfit gate.
- Every unit whose needs a profile does not meet has a decision, and no energy or life-support unit is retired without a diverse replacement.
- Document numbers are unique as number and site pairs, and every locale page has a number from the register tool.
- Every check document in a locale cites a governing clause from that locale's code families or is reported open.

## 13. Owner decisions

The questions below are logged in AQS-OQ-001 with the default the work will proceed on.

- Q-020. The Death Valley parcel: Furnace Creek climate with a parcel outside the park. Default: climate of station USC00042319; parcel to be chosen; United States codes with the state's own.
- Q-021. The Antarctic site class: coastal or plateau. Default: coastal, McMurdo class; plateau as a second profile.
- Q-022. The Mars site: mid-latitude ice or equatorial. Default: mid-latitude with shallow ice, Arcadia Planitia class.
- Q-023. The orbit and gravity: station-class orbit or a sun-synchronous orbit with little eclipse, and whether a rotating section supplies gravity. Default: station-class orbit, no rotation.
- Q-024. The PV rule and non-solar primaries where sunlight fails for long periods. Default: the 200 % rule applied to the worst period the storage must bridge; wind added where a resource is cited; nuclear power recorded as an option only.
- Q-025. Waste processing under the Antarctic Treaty. Default: treat the plant as a waste processing facility that needs a comprehensive environmental evaluation.
- Q-026. Surplus outlets where export is impractical. Default: local use, storage and propellant.
- Q-027. Planetary protection at Mars ice. Default: site outside special regions.
- Q-028. Document numbers for locale copies. Default: base number with a site suffix.
- Q-029. Crew size per locale. Default: the baseline crew at every locale.

## 14. References

1. National Centers for Environmental Information (NCEI), Summary of Monthly Normals 1991–2020, station Death Valley NP, CA US (USC00042319). <https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020&stations=USC00042319&format=pdf&startDate=0001-01-01&endDate=9996-12-31>
2. World Meteorological Organization, World Weather and Climate Extremes Archive, highest recorded temperature (Furnace Creek, 1913-07-10). <https://wmo.asu.edu/>
3. Furnace Creek community water system, Consumer Confidence Report 2018, public water system CA1410505, California State Water Resources Control Board. <https://ear.waterboards.ca.gov/Home/ViewCCR?PwsID=CA1410505&Year=2018&isCert=false>
4. Sengupta M. et al., The National Solar Radiation Data Base (NSRDB), Renewable and Sustainable Energy Reviews 89 (2018) 51–60.
5. Anderson K.S. et al., pvlib python: 2023 project update, Journal of Open Source Software 8(92) (2023) 5994.
6. American Society of Civil Engineers, ASCE Hazard Tool. <https://ascehazardtool.org>
7. ASHRAE Handbook—Fundamentals 2025, Chapter 14, Climatic Design Information.
8. California Code of Regulations, Title 8, sections 3395 (Heat Illness Prevention in Outdoor Places of Employment) and 3396 (Heat Illness Prevention in Indoor Places of Employment).
9. United States Antarctic Program (USAP), Participant Guide 2018–2020, sections on McMurdo Station and the continent. <https://www.usap.gov/USAPgov/travelAndDeployment/documents/ParticipantGuide_2018-20.pdf>
10. Management Plan for Antarctic Specially Managed Area No. 5, Amundsen-Scott South Pole Station, section 1. <https://www.usap.gov/conferencescommitteesandworkshops/usercommittees/documents/Management%20Plan%20for%20ASMA.pdf>
11. Anderson P.J. et al., Incidence and symptoms of high altitude illness in South Pole workers: Antarctic Study of Altitude Physiology, Clinical Medicine Insights: Circulatory, Respiratory and Pulmonary Medicine 5 (2011) 27–35. <https://pmc.ncbi.nlm.nih.gov/articles/PMC3114308/>
12. United States Antarctic Program, McMurdo Water Plant Standard Operating Procedure, description of the system. <https://kh.aquaenergyexpo.com/wp-content/uploads/2023/02/McMurdo-Water-Plant-Standard-Operating-Procedure.pdf>
13. Protocol on Environmental Protection to the Antarctic Treaty (Madrid, 1991), Article 7 and Annexes I to III. <https://www.ats.aq/e/protocol.html>
14. ASME B31.3-2024, Process Piping, paragraph 323.2.2.
15. Antarctic Conservation Act of 1978, 16 U.S.C. 2401 et seq., and 45 CFR Part 670.
16. Williams D.R., Mars Fact Sheet, NASA Space Science Data Coordinated Archive. <https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html>
17. Franz H.B. et al., Initial SAM calibration gas experiments on Mars: quadrupole mass spectrometer results and implications, Planetary and Space Science 138 (2017) 44–54.
18. Appelbaum J., Flood D.J., Solar Radiation on Mars, NASA TM-102299 (1989).
19. Landis G.A., Jenkins P.P., Measurement of the settling rate of atmospheric dust on Mars by the MAE instrument on Mars Pathfinder, Journal of Geophysical Research 105(E1) (2000) 1855–1857.
20. NASA Jet Propulsion Laboratory, NASA's record-setting Opportunity rover mission on Mars comes to end, news release 2019-02-13.
21. Hassler D.M. et al., Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover, Science 343 (2014) 1244797.
22. Blake D.F. et al., Curiosity at Gale Crater, Mars: characterization and analysis of the Rocknest sand shadow, Science 341 (2013) 1239505.
23. Hecht M.H. et al., Detection of perchlorate and the soluble chemistry of Martian soil at the Phoenix lander site, Science 325 (2009) 64–67.
24. Bramson A.M. et al., Widespread excess ice in Arcadia Planitia, Mars, Geophysical Research Letters 42 (2015) 6566–6574.
25. Morgan G.A. et al., Availability of subsurface water-ice resources in the northern mid-latitudes of Mars, Nature Astronomy 5 (2021) 230–236.
26. Wagner W., Pruß A., The IAPWS formulation 1995 for the thermodynamic properties of ordinary water substance for general and scientific use, Journal of Physical and Chemical Reference Data 31 (2002) 387–535.
27. Banerdt W.B. et al., Initial results from the InSight mission on Mars, Nature Geoscience 13 (2020) 183–189.
28. Hoffman J.A. et al., Mars Oxygen ISRU Experiment (MOXIE)—Preparing for human Mars exploration, Science Advances 8 (2022) eabp8636.
29. Treaty on Principles Governing the Activities of States in the Exploration and Use of Outer Space, including the Moon and Other Celestial Bodies (1967), Articles VI and IX.
30. Committee on Space Research (COSPAR), COSPAR Policy on Planetary Protection, latest issue.
31. NASA Interim Directive NID 8715.129, Biological Planetary Protection for Human Missions to Mars (2020).
32. NASA-STD-3001, NASA Space Flight Human-System Standard, Volumes 1 and 2, latest revisions.
33. Kopp G., Lean J.L., A new, lower value of total solar irradiance: evidence and climate significance, Geophysical Research Letters 38 (2011) L01706.
34. Wertz J.R., Everett D.F., Puschell J.J. (eds.), Space Mission Engineering: The New SMAD, Microcosm Press (2011).
35. Picone J.M. et al., NRLMSISE-00 empirical model of the atmosphere, Journal of Geophysical Research 107(A12) (2002) 1468.
36. Berger T. et al., DOSIS and DOSIS 3D: radiation measurements with the DOSTEL instruments onboard the Columbus Laboratory of the ISS in the years 2009–2016, Journal of Space Weather and Space Climate 7 (2017) A8.
37. European Cooperation for Space Standardization (ECSS), ECSS-E-ST-31C, Space engineering: Thermal control general requirements (2008).
38. NASA, NASA achieves water recovery milestone on International Space Station, news release 2023-06-20.
39. European Space Agency (ESA) Space Debris Office, ESA's Annual Space Environment Report, latest issue.
