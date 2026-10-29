# Localization plan: site profiles and locale variants

Document number: AQS-PLAN-011
Revision: K
Date: 2026-10-29

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-25 |
| B | Scaling model replaces keep, alternate and retire; per-site power portfolio; floating island locale added; build order updated | 2026-10-25 |
| C | Section 4 matches the built profile: entries bind drivers, snow group added, pending groups, locale regeneration refused until section 4.4 exists | 2026-10-25 |
| D | Section 4.5 states the number and site pair rules as built | 2026-10-25 |
| E | Section 3.2 records the gravity, pressure and air values now read from the profile, and Q-032 | 2026-10-25 |
| F | Q-032 closed; every gravity and air density reads the profile | 2026-10-25 |
| G | Sections 4.3 and 4.4 describe locale selection and the per-site output folders as built | 2026-10-25 |
| H | Section 5.4 describes the scaling actions, capabilities and checks as built; capabilities group added to Table 4.1 | 2026-10-25 |
| I | Section 5.5 describes the power portfolio and function redundancy as built; an import path no longer counts as an energy or life-support source | 2026-10-25 |
| J | Section 5.5 adds storage coverage of the worst stretch and the heat rejection modes as built; X-LOC-06 done | 2026-10-25 |
| K | Section 2 and section 13 no longer describe the site profiles as future work; Table 12.1 lists every X-LOC task with the status of the task plan, checked by `flow_graph/test_localization_plan.py`, and the evidence from locale runs on 2026-10-29 | 2026-10-29 |

## 1. Purpose and scope

The plant is meant to work wherever it can be built. This plan sets out how the parametric model will take the site as an input, so that one design produces a variant for each locale and the differences between locales are a generated result. It covers the first locales to be studied: Death Valley (hot desert), Antarctica (polar), a floating island (open sea), Mars (planetary surface) and low Earth orbit.

The full single-building plant in the base graph is the reference ideal: every function the design can perform, each sized for the baseline site. It is not a build target. A real plant is the reference with each sector and unit sized up, sized down, duplicated or eliminated to suit the power and resources of its site. The extreme locales test whether the parametric model can make all of those changes; the same method applies to any real site on Earth and, later, off it.

This page is the investigation and the plan. It does not change the plant graph, the drivers or any generated output. It records:

- how the model represents the site today, and where conditions on the surface of the Earth are fixed in code (section 3);
- the site profile, one data file per locale that carries every environmental input (section 4);
- how each sector and unit is scaled to a site, and how the power sources are chosen (section 5);
- the environmental values and the design consequences for each locale (sections 6 to 10);
- the gaps in the current architecture and how to close them parametrically (section 11);
- the build order (section 12), the acceptance checks (section 13) and the decisions the owner must take (section 14).

Every value in sections 6 to 10 cites a published source. A value enters the model only through a site profile entry that carries that source, or through an entry in the assumptions register (AQS-REG-002) with the test that will confirm it.

## 2. Summary

- When this plan was first issued, the site was not an input. The study site values were in AQS-SITE-002 (`docs-authority/SITE_BASIS.md`) and in `flow_graph/param/drivers.json`, mixed with process drivers. Several facts about the surface of the Earth are constants in code: standard gravity, standard atmospheric pressure, the composition and density of air, and the use of outside air as a heat sink, an oxidant and a vent destination.
- A site profile per locale, `flow_graph/param/sites/<site_id>.json`, holds every environmental input in the same form as a driver (value, units, reference or register id, verification test). The driver loader applies the selected profile. The baseline profile carries the present values, so the baseline output does not change.
- The full building is the reference ideal, not a build target. A profile scales each sector and unit: sized up, sized down, duplicated, replaced by a unit of another technology, or eliminated. Eliminating a function needs an import path or a replacement of a different technology. Each unit states its environmental needs, such as a minimum gravity for buoyant separation, outside air for heat rejection, or ground contact; an unmet need forces a replacement or an elimination. The generated table of these scaling actions is the record of what the plant changes to work in each place.
- Power sources are chosen per site from what the local resource supports: PV, wind, geothermal, hydro, wave and ocean thermal energy where cited, fuel cells on plant-made fuels, and storage. Fission and other sources enter only as flagged options with their own studies. The generation that closes the energy balance through the worst stretch at the site is oversized by `pv_oversize_factor`, and redundancy is kept.
- Death Valley keeps the architecture and stresses heat rejection, water supply and material temperatures. Antarctica stresses a dark season, freezing, and a treaty that forbids mineral resource activity. Mars needs pressurised process spaces, works at partial gravity, and can use the carbon dioxide atmosphere, ground ice and regolith as feed. A floating island loses the ground and gains the sea: seawater for cooling, water and minerals, wave and ocean thermal energy, but every kilogram counts against buoyancy and stability, and motion disturbs gravity separation. Low Earth orbit removes gravity, air and ground together and needs the most replacement units.
- The build order is: profile and loader with the baseline unchanged; code constants moved into the profile; site selection and output namespaces; sector and unit scaling with the power portfolio; then the locales, Earth sites first: Death Valley, the floating island, Antarctica, Mars and low Earth orbit.

## 3. How the model represents the site today

### 3.1 Where site values are held

By owner decision the study site is a Dallas–Fort Worth class location (AQS-SITE-002). Table 3.1 lists each environmental input, where it is held and what uses it.

Table 3.1. Environmental inputs in the current model

| Input | Held in | Used by |
| --- | --- | --- |
| Cooling design dry bulb | driver `site_design_dry_bulb_C`; AQS-SITE-002 | `docs-authority/_hot_draw_coolers.py`; make-up air text in `docs-authority/_hvac.py` |
| Heating design dry bulb | site profile entry `thermal.heating_dry_bulb_C`; AQS-SITE-002 text and `_hvac.py` text | heating, ventilation and air conditioning (AQS-THM-002) |
| Ambient temperature for insulation | driver `ins_ambient_C` | `docs-authority/_insulation.py` |
| Solar resource | drivers `pv_yield_kWh_kWp_d`, `pv_roof_yield_factor`, `pv_system_derate`, `night_hours`, `crit_autonomy_d`; hourly data in `docs-authority/data/` | roof closure in `flow_graph/param/solver.py`; power in `flow_graph/param/write_graph.py`; storage in `flow_graph/param/ess_tf.py` |
| Photovoltaic (PV) oversize | driver `pv_oversize_factor` | `solver.py` |
| Wind | driver `wt_wind_ms` | `flow_graph/param/water_tower.py`, `solver.py` |
| Snow | driver `roof_snow_kPa` | roof loads in `solver.py` |
| Seismic | drivers `wt_SDS`, `wt_SD1`, `wt_TL_s` | `flow_graph/param/water_tower.py` |
| Soil bearing and unit weight | drivers `soil_allow_kPa`, `soil_unit_weight_kN_m3` | `docs-authority/_foundation.py` (AQS-BLD-017) |
| Soil resistivity | driver `ELEC.distribution-train.gnd_soil_rho_ohm_m` | `docs-authority/_grounding_study.py` |
| Frost depth | site profile entry `ground.frost_depth_m`; AQS-SITE-002 | foundation text |
| Ground heat exchange | drivers `GEO.geo-loop.ghex_*` | `flow_graph/param/geo_loop.py` |
| Latitude and orientation | AQS-SITE-002; AQS-SITE-001 (the dock faces the pole) | site access, array tilt |
| Water make-up | dock make-up stream (Q-002) | balance |
| Logistics | DOCK sector; product `hold_d` drivers set by the dock dispatch campaign | storage sizing |
| Line frequency | driver `MFG.tools-metal-forming-train.mfa_line_hz` | motor design |
| Codes | EDITIONS table in `flow_graph/param/code_basis.py` (AQS-STD-007) | every check document |

### 3.2 Earth-surface conditions fixed in code

These are the places where the model assumes the surface of the Earth without saying so. Each must become a profile value, or a value derived from the profile, before a locale off the Earth's surface can be represented.

- Gravity. The profile entry `gravity.g_m_s2` holds the apparent gravity, and every sizing module and calculator reads it through `flow_graph/param/site.py` (Q-032 closed). `flow_graph/param/test_site_constants.py` fails on a gravity literal in model code. Concrete in the foundation calculator is still entered as a unit weight in kN/m³, which holds Earth gravity; it becomes a density times the profile gravity in a later step.
- Atmospheric pressure. The profile entry `atmosphere.pressure_Pa` holds the external pressure, and the balance, evaporator, scrubber, fire, cold box, pressure node, graph writer and relief modules read it through `site.py`. Two literals stay, each with its reason in the test: the carbon dioxide solubility bound in the balance (pure gas at one standard atmosphere) and the unit conversion in the scrubber's diffusivity correlation. The one-shot studies in `docs-authority/` that are not regeneration stages keep their literals.
- Air. The balance takes the partial pressures of oxygen and nitrogen from the profile entry `atmosphere.composition_mole_fraction` and the external pressure (`HENRY` in `flow_graph/param/balance.py`). Air densities for the gas headers, the sanitation superficials and the zinc-bromine battery purge are computed by `site.air_density()` from the profile pressure and molar mass at a driver temperature; no driver holds an air density. The air carried in with the feed (`vs_air_mg_kg`) remains a feed property.
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

Each locale has one file, `flow_graph/param/sites/<site_id>.json`, validated against `flow_graph/schema/site_profile.schema.json`. Every entry has the form of a driver: `value`, `units`, and a `ref` (a key in `flow_graph/param/refs.py`) or a `register` id, with `needs_verification` and `verification_test` where no published value fixes it. The loader rejects an entry without a basis in the same way as a driver.

Table 4.1 lists the groups the profile carries. A group that does not apply at a locale is present and marked not applicable with its reason, so that a missing value is always an error and never a silent default. A group that a later task will fill is marked pending with that task's id. Identity, thermal environment, electrical and jurisdiction carry entries at every site. The schema's `x-groups` list holds the entries each group must carry; the list grows as each task in section 12 adds the entries its sizing functions read, so the table states the full scope and the schema states the entries in use.

Table 4.1. Site profile groups

| Group | Entries |
| --- | --- |
| Identity | site id, name, body (Earth surface, Earth orbit, Mars surface), coordinates or orbit (altitude, inclination), elevation, site basis document number |
| Gravity | apparent gravity, m/s² (for a rotating structure, the design value at the working radius) |
| Atmosphere | external pressure range, composition as mole fractions, density, and three flags: breathable, usable as a vent sink, usable as an oxidant |
| Thermal environment | cooling and heating design dry bulb, coincident wet bulb, effective radiative sink temperature, ground temperature at depth, freezing risk |
| Solar | resource model (hourly series file, orbit model or monthly table), irradiance above the atmosphere, mean and worst-period yield, longest dark period, soiling or dust loss rate, snow and frost loss |
| Wind | basic wind speed for structures, mean wind speed for generation, air density for dynamic pressure |
| Snow | roof snow load, or the source showing that no snow load applies |
| Seismic | mapped accelerations and site class, or the source showing that no seismic code applies |
| Ground | allowable bearing, unit weight, frost or active-layer depth, permafrost or ice-sheet flag, electrical resistivity, thermal conductivity |
| Radiation | ambient dose rate and the shielding basis |
| Water sources | each source with type (aquifer, seawater, snow or ice, ground ice, recycle only), quality, temperature and sustainable yield |
| Local feedstocks | each material available at the site, mapped to a feed case in AQS-ASSAY-001 |
| Logistics | arrival mode (truck, ship, launch, lander), resupply interval, mass cost class, export outlets |
| Electrical | external grid present or not, alternating current frequency or direct current bus voltage, earthing method (earth electrode, floating, structure bonding) |
| Jurisdiction | code families that apply (section 4.6) |
| Power portfolio | candidate sources with their resource basis, the worst stretch, the oversize factor and the redundancy rule (section 5.5) |
| Motion | for floating sites: design heel, roll and pitch angles, periods and heave acceleration |
| Scaling | per sector or unit: size factor, unit count, replacement, elimination with its import path (section 5) |
| Capabilities | for each environmental need in Table 5.2, whether the site provides it (section 5.4) |

### 4.2 Binding to the drivers

The profile does not duplicate drivers. A profile entry that supplies an environmental driver carries a `binds` field naming that `drivers.json` key, and `drivers.load()` replaces the driver with the entry from the selected profile. The units of the entry and the driver must match, or the load fails. `drivers.json` keeps the baseline entry, so the file itself does not change. Entries with no driver today, such as gravity and the atmosphere, are read through `flow_graph/param/site.py` and do not enter the driver set, so the model workbook and the driver listing do not change; the literals in section 3.2 are replaced by those reads. Quantities that follow from the environment, such as an air density at a given temperature, are computed in `site.py` from the profile, not entered a second time.

The baseline profile, `flow_graph/param/sites/baseline.json`, carries the present values with their present references and register ids (AQS-SITE-002 and the A-M entries). With it selected, the resolved driver set equals the present `drivers.json` value for value, and `python3 -m flow_graph.param.regen --check` stays clean. The test `flow_graph/param/test_site_profile.py` checks this equality, the failure on a missing group or entry, the failure on an entry without a basis, the failure on an unknown site, and that no script opens `drivers.json` except the loader. Until the output namespaces of section 4.4 exist, regeneration with a site other than the baseline is refused, so that a locale run cannot overwrite the baseline outputs.

### 4.3 Selecting a profile

- Pass `--site <site_id>` to `python3 -m flow_graph.param.regen`. With no flag the baseline profile is used. An unknown or invalid profile fails before any stage runs.
- `--all-sites` regenerates the baseline in place and then every locale profile in `flow_graph/param/sites/`. With `--check`, each locale is regenerated and compared with its folder, and nothing is written.
- The environment variable `AQS_SITE` selects the profile for a script run on its own. Regeneration in this working tree refuses a locale set this way, so a locale can never overwrite the baseline outputs.

### 4.4 Output namespaces

- Baseline outputs stay where they are, so existing paths and citations do not change.
- A locale is regenerated in a temporary git worktree of the current commit, by `flow_graph/param/site_outputs.py`, with the locale's profile selected. The profile must be committed. The outputs that differ from the baseline are copied to `sites/<site_id>/` under their repository paths, for example `sites/<site_id>/docs-authority/duties/`. Every path is checked to stay inside that folder, and the folder is the only place written.
- `sites/<site_id>/SITE_OUTPUTS.json` lists the copied outputs, the outputs the locale removes, and the hash of the profile. An output not listed is the same as the baseline output at the same commit. The derived revisions register is not copied, because its content names commits.
- No generator script needs a locale path: the worktree isolates each run, and the collection step adds the prefix.
- The base graph stays the sole topology authority. A locale graph is the base graph with the locale's scaling actions applied (section 5); it is a generated output and is never hand-edited.
- `flow_graph/param/test_site_outputs.py` checks the path guard, the refusal of an in-place locale run, the document number suffix and the collection step.

### 4.5 Document numbers and identifiers

- A generated document in a locale namespace keeps its base number with the site code as a suffix, for example `AQS-THM-002/MARS`. `docs-authority/_doc_register.py` registers each number and site pair. The register reports a problem, and `flow_graph/test_doc_numbers.py` fails, when a pair is claimed twice, when a suffix is not the `site_code` of a locale profile, when a suffix is used for the baseline, when no baseline page claims the base number, or when a page under `sites/<site_id>/` does not carry that site's code. The alternative, a fresh number for every locale copy, is put to the owner in Q-028.
- A hand-written locale page, such as the site basis of a locale, is kept in `docs-authority/` and takes a new number from `python3 docs-authority/_doc_register.py --next AQS-SITE`.
- A replacement unit gets a new unit id in the base graph, present only where a profile selects it. Unit, stream, assumption, task and question ids take the next unused id in their sequence and are never reused.

### 4.6 Code basis per jurisdiction

Each row of the EDITIONS table in `flow_graph/param/code_basis.py` gains a family: building on land in the United States (the present rows), the Antarctic Treaty system, crewed spacecraft, and planetary surface operations. The profile lists the families that apply. A check document cites only codes in the selected families, and a check with no governing clause in those families is reported as open rather than passing. Editions follow the latest-edition rule recorded in Q-018 and are confirmed when a family is added.

## 5. Sector and unit scaling

### 5.1 The reference plant

The base graph describes the full single-building plant: every function the design can perform, each sized for the baseline site. It is the reference ideal and the source of every unit's design, not a plan to be built as drawn. A plant for a real site is the reference with each sector and unit scaled to the power and resources available there.

### 5.2 Scaling actions

Table 5.1 lists the actions a profile may apply to a sector or a unit.

Table 5.1. Scaling actions

| Action | Meaning | Rule |
| --- | --- | --- |
| size up or size down | the solver sizes the unit from local demand and resource; an optional factor biases the result, for example for a saleable surplus | the factor is a profile entry with a stated basis |
| duplicate | the unit is built as a number of parallel units, for capacity or for redundancy | the count is a profile entry; it is never below the count the redundancy rule needs |
| replace | a unit of a different technology performs the same function, for example a radiator for DRY_COOLER | the replacement is a unit in the base graph with its own sizing function |
| eliminate | the function is not performed at the site | the profile names an import path (a boundary stream with its resupply interval and holding) or a replacement of a different technology |

For an energy or life-support function, eliminating or replacing a unit must leave the function with at least the sources the redundancy rule needs: a spare unit, or a second source of a different technology, sized for a defined outage (AGENTS.md, Redundancy). An import path does not count as a source: an energy or life-support unit is eliminated only with a replacement of a different technology (owner, 2026-10-25).

### 5.3 What a unit needs

Each unit states its environmental needs in `flow_graph/param/unit_needs.json`. Needs are given by unit class, with a unit-level override, so units need not be edited one by one. A need the profile does not meet forces a replacement or an elimination; every other action is a free design choice. Table 5.2 lists the needs used in this plan.

Table 5.2. Environmental needs

| Need | Meaning | Examples |
| --- | --- | --- |
| buoyant separation | a minimum apparent gravity, steady in direction, to separate gas from liquid or solids from liquid | flotation, settlers, packed columns, stirred tanks with a gas space, electrowinning gas release |
| free surface | a liquid surface open to a gas space | atmospheric tanks, pumped hydro, roof and catch tanks |
| air heat sink | outside air at a usable temperature | DRY_COOLER, air-cooled condensers |
| air oxidant | outside air with oxygen | AFTERBURNER, COMB_HEAT, BACKUP_GEN |
| vent sink | an atmosphere that can take a vent or relief discharge | scrubber stacks, relief devices |
| ground contact | soil or rock for bearing, earthing or heat exchange | foundation, earthing grid, GEO_GHEX |
| liquid water at ambient | external pressure above the triple point of water | any open water surface |

### 5.4 Scaling in the profile and its check

The profile's `scaling` group lists the actions, each on a unit or on a sector (`sector:<SECTOR_ID>`) and each with its basis. The `capabilities` group states, for each need in Table 5.2, whether the site provides it; a capability may not claim more than the profile's physical values allow (no buoyant separation or free surface without gravity, no liquid water at or below the triple point pressure, the vent and oxidant flags as in the atmosphere group). `flow_graph/param/scaling.py` resolves the actions against the graph and fails when:

- a present unit has a need the site does not provide and is neither replaced nor eliminated, or a replacement has such a need;
- an elimination has neither an import path nor a replacement;
- a replacement is the same technology (the same unit class) as the unit it replaces, or does not perform the same function;
- an energy or life-support unit is eliminated without a replacement of a different technology; an import path alone does not keep the function;
- a size factor is not above zero, a duplicate count is below 2, or an action has no basis.

`flow_graph/param/test_site_scaling.py` checks each rule. Regeneration writes `docs-authority/SITE_SCALING.md` (AQS-SITE-004) for the selected site: its capabilities, its actions and the status of every unit with a need. A locale's copy under `sites/<site_id>/` is its scaling table, and comparing those tables across locales gives the record of what the plant changes in each place. The redundancy count per function (section 5.2) is checked when the power portfolio and the life-support sources are modelled (X-LOC-06).

### 5.5 Power portfolio

Each profile lists the power sources the local resource supports, each with its resource basis: PV, wind, geothermal power and heat, hydro where the terrain allows, wave energy and ocean thermal energy conversion where a cited resource exists, fuel cells and engines on plant-made fuels, and storage (electrochemical, hydrogen, thermal, and pumped hydro where the terrain allows). Fission and other sources enter only as flagged options, each with its own study before it enters a balance.

The portfolio is sized by one rule at every site. The solver finds the generation that closes the energy balance through the worst stretch the site presents: a night, a dark season, a calm, a dust storm, an eclipse or a storm at sea. The installed generation is that amount times the oversize factor (`pv_oversize_factor` at the baseline, generalised to the whole portfolio). Storage covers the worst stretch. Every energy function keeps a spare or a source of a different technology. The share of each source is a profile entry with a stated basis; the default is the least installed capacity that meets the rule.

As built, the profile's `power_portfolio` group lists the sources (primary, backup, or flagged option, each with its unit and basis), the storage, the worst stretch (kind and the profile entry that gives its hours) and the oversize factor, which binds `pv_oversize_factor`. `flow_graph/param/portfolio.py` solves the daily balance through the worst stretch: primary sources share the mean generation, each gives a stated fraction of its mean rate during the stretch, and storage carries the rest at the storage round trip. With PV alone and no output in the stretch this is the reference balance, so the PV correction it passes to the roof closure in `flow_graph/param/solver.py` and to `docs-authority/_power_sizing.py` is exactly 1 at the baseline. A primary source other than PV needs a capacity factor with its basis; fission and other new technologies are refused unless they are flagged options. A stretch longer than a day needs the seasonal storage model, which comes with the first polar locale.

`flow_graph/param/redundancy.json` lists the source units of each energy and life-support function (power, power storage, thermal storage, heat rejection, oxygen, water, carbon dioxide removal, food, sanitation). After the scaling actions, each function must keep at least two source units, counting a unit's stated parallel trains and replacements. Units named there are energy or life-support units for the scaling rules of section 5.4. Regeneration writes `docs-authority/SITE_POWER.md` (AQS-SITE-005) for the selected site, and `flow_graph/param/test_site_power.py` checks each rule. Each storage entry names the graph parameter that gives its stored energy, and the document compares the total with the energy the worst stretch draws at the plant demand. Sizing a primary source other than PV in the power sizing comes with the first locale that selects one; until then the power sizing stops on such a portfolio.

The profile's `heat_rejection` group lists, per level of the heat ladder, the unit that rejects the heat, its mode (air, evaporative, ground, seawater, radiative, or heat pump with a sink mode) and the graph parameter that gives its duty. `flow_graph/param/heat_rejection.py` checks each mode against the site capabilities: air needs an air heat sink; evaporative also needs a vent sink and liquid water; ground needs ground contact; seawater needs liquid water and a seawater source. A radiative level needs the radiator emissivity and the sink temperature in the group, and is sized by the Stefan-Boltzmann law with the constant from CODATA 2018 [55]. A heat pump states its source and rejection temperatures, and the document gives its lift and the Carnot bound on its coefficient of performance. Every heat rejection unit that remains after the scaling actions needs a level, so a replacement brings its own mode. The modes appear in `docs-authority/SITE_POWER.md`.

## 6. Death Valley

### 6.1 Site and environment

Death Valley is a national park, and an industrial plant would sit outside it. The profile uses the climate record at Furnace Creek as the bounding hot desert climate; the parcel is an owner decision (Q-033). Table 6.1 lists the values.

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
- Scaling. No sector is eliminated. HEAT, WTR, ELEC and FARM are sized up, and a water intake unit is added.

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

- Power. PV produces nothing through the dark season, so a daily night-hours basis fails. Storage becomes seasonal. The candidates are the plant's own hydrogen with the fuel cell, sized for the dark season, wind generation as a diverse winter source, and imported fuel as the last resort. The power portfolio (section 5.5) applies the oversize rule to the dark season.
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
- Scaling. PUMPED_HYDRO needs heated enclosed reservoirs and is a candidate for elimination with hydrogen storage as the replacement; GEO changes from heat source to heat store; a wind generation unit, a seawater intake unit and seasonal hydrogen storage are added.

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
- Atmosphere as a resource. Carbon dioxide feeds MEOH (methanol synthesis) and a new methanation unit for propellant. Nitrogen and argon for buffer gas come from separating the atmosphere in CRYO. Solid oxide electrolysis of carbon dioxide [28] is the diverse second oxygen source behind water electrolysis. Taking the atmosphere in needs a compressor or a freezing collector from a fraction of a kilopascal; this is a new unit.
- Heat rejection. The thin atmosphere gives weak convection, so radiators and ground heat exchange replace air coolers. The cold surroundings lower the lift for carbon dioxide condensing and oxygen liquefaction.
- Water. Ground ice extraction and melting is a new unit, with perchlorate removal. Recycling closure matters more than on Earth.
- Feedstock. Regolith enters through the silicate and oxide feed case of AQS-ASSAY-001. Perchlorate is both a hazard and an oxygen source. Imported hardware and packaging are further feeds. Each needs an assay case before use.
- PV and storage. Storage covers the sol night and a dust storm. Array cleaning or a soiling allowance follows the settling rate. Non-solar sources enter through the power portfolio (section 5.5).
- Thermal stores. Insulation thickness follows from the profile; stores can be buried in regolith.
- Vents and relief. Nothing vents to an atmosphere that cannot take it. Vents go to recovery. Relief devices discharge against a low back pressure, so the relief register is recalculated with the profile pressure.
- Combustion. The atmosphere has no usable oxygen. AFTERBURNER and BACKUP_GEN run on plant oxygen or are replaced by catalytic oxidation and fuel cells.
- Partial gravity. Settling, flotation and packed columns still work but more slowly; every sizing function takes gravity from the profile.
- Earthing. Dry regolith gives no earth electrode, so the electrical system is floating with insulation monitoring.
- Structure. Pressure loads govern. Wind loads are small because the air density is low. Seismic loads are small [27].
- Crew. Radiation shielding uses regolith and water. Life support follows the crewed spacecraft family.
- Logistics. A landing pad replaces the dock. Resupply follows the transfer windows [16]. Surplus is used locally, stored or made into propellant (Q-026).
- Codes. The Outer Space Treaty [29], the COSPAR policy on planetary protection [30] and the NASA interim directive for crewed Mars missions [31] apply, with NASA-STD-3001 for crew health [32]. Ground ice may lie in a special region under [30] (Q-027).
- Scaling. PUMPED_HYDRO and the roof and catch tanks are replaced or eliminated. GEO becomes regolith heat exchange. DOCK becomes a landing pad. Atmosphere intake, ice extraction and methanation are added. FARM moves into a pressurised grow room with a perchlorate-free substrate.

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
- Power. An eclipse occurs on most orbits, so storage cycles many times a day and cycle life governs. The bromine phase in ZNBR2 separates by gravity, so ZNBR2 needs a replacement. PV is sized on the sunlit fraction of the orbit.
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
- Scaling. PUMPED_HYDRO, GEO and the dock are eliminated or replaced. DRY_COOLER becomes a radiator. The air separation in CRYO has no air to take and becomes cabin air processing. GAS scrubbers, FLOAT_SINK, ZNBR2 and the melting and casting units of FOUNDRY need replacements.

## 10. Floating island

### 10.1 Site and environment

The floating island is a self-contained platform at sea, moored or free-floating. The default is a moored platform in tropical waters deep enough for an ocean thermal gradient (Q-030), designed to ride out the design storm on its moorings, with relocation as an option (Q-031). Table 10.1 lists the values.

Table 10.1. Floating island environment

| Quantity | Value | Source |
| --- | --- | --- |
| Reference salinity of standard seawater | 35.165 g/kg at practical salinity 35 | [40] |
| Sodium and chloride | 10.78 g/kg and 19.35 g/kg | [40] |
| Magnesium | 1.284 g/kg | [40] |
| Bromide | 0.067 g/kg | [40] |
| Lithium | about 0.18 mg/kg | [41] |
| Ocean thermal gradient | at least about 20 °C between the surface and about 1000 m depth is needed; it is found year-round in tropical waters | [42] |
| Wave power | about 2.11 TW crossing the world's coasts and open-ocean contours, unevenly spread | [43] |
| Least energy to desalinate seawater | 1.06 kWh/m³ at 50 % recovery | [44] |
| Strongest hurricanes | Category 5, sustained wind of 70 m/s (157 mph) or more | [45] |
| Atmospheric corrosivity | offshore category CX | [46] |
| Packed columns in motion | static tilt harms liquid distribution more than motion of the same amplitude; a bed height of two to three column diameters is recommended; published packing height margins range from 1.1 to 2.0 | [47] |
| Columns in roll | structured packing keeps a loss of efficiency under motion; random packing recovers at higher motion frequency | [48] |
| Wind, wave, current and design storm at the site | metocean data and the class society's environmental load method | [49] |

### 10.2 Design consequences

- What a building is. The plant is a hull. Its whole mass, including structure, equipment, liquid inventories and ballast, is limited by the displacement, and its centre of gravity and the free surfaces of its liquids set its stability and freeboard. Mass and centre of gravity become sizing outputs summed over the scaled units, with stability and freeboard as checks under the class rules [50], [49]. Liquid inventories are divided into compartments to limit the free-surface effect, and building height is limited by stability.
- Loads. Wave, wind and current act on the hull and the moorings, with salt spray and green water on deck. Exposed steel follows the offshore corrosivity category [46].
- Motion. Roll, pitch and heave tilt and vary the apparent gravity. Settlers, flotation, open tanks, stirred tanks, electrowinning cells and the bromine phase in ZNBR2 are checked against the design heel and motion. Packed columns are sized with a motion margin and a limited bed height [47], [48]. Tanks are checked for sloshing. Motion is a profile group so that every sizing function that uses gravity also sees the tilt.
- Seawater as a resource. Seawater is the cooling medium, the water source and a mineral feed. Desalination replaces the dock water make-up. The reject brine feeds salt by evaporation, magnesium as the hydroxide, bromine by oxidation and stripping, and lithium by sorption [40], [41]; sodium chloride brine also feeds the existing bipolar membrane electrodialysis units (BMED_ACID, BMED_BASE) for acid and base. Each needs a feed case in AQS-ASSAY-001.
- Heat rejection. Seawater exchangers replace DRY_COOLER. Deep cold water, where an intake reaches it, cools to a lower temperature and can also serve ventilation. Seawater wetted parts need materials for chloride and fouling.
- Power. Deck area limits PV. Wind, wave energy and ocean thermal energy conversion [42] enter the power portfolio where the site supports them. Pumped hydro on a hull has little head and costs stability, so it is a candidate for elimination with another storage technology as the replacement. The ground loop is replaced by seawater-source heat exchange.
- Feedstock. Seawater minerals, floating plastic debris, seaweed and waste delivered by ship are candidate feeds, each mapped to an assay case before use.
- Farm. The grow bed is soilless and suits a platform. Aquaculture and the nutrients in deep water are options for a later study.
- Structure and earthing. There is no soil. Hull structure and moorings follow the class society's rules. Earthing is to the sea through the hull, with cathodic protection.
- Logistics. A berth with cranes replaces the truck dock. Transfers are limited by sea state, so the resupply interval and the weather window set the hold times. Products leave by ship.
- Safety and discharges. Fire protection, life-saving appliances and evacuation follow the Safety of Life at Sea convention [51]. Discharges of oil, sewage, garbage and air emissions follow MARPOL [52].
- Codes. The marine family is added: the class society's rules [49], SOLAS [51], MARPOL [52], the Code for the Construction and Equipment of Mobile Offshore Drilling Units as the model for a manned floating installation [53], the International Code on Intact Stability [50], and the port facility and ship security code where the platform trades internationally [54]. The flag or coastal state decides which apply (Q-030).
- Crew. Habitability under motion is a check, and the crew has a sea evacuation route.
- Scaling. PUMPED_HYDRO is eliminated with a replacement storage; GEO is replaced by seawater exchange; the roof and catch tanks are sized down for mass and free surface; DOCK becomes a berth; heavy FOUNDRY units are sized down for mass; seawater intake, desalination, mineral recovery, wave and ocean thermal units are added.

## 11. Architecture gaps

Table 11.1 lists each gap found in sections 3 and 10, the locales it blocks, and the parametric way to close it.

Table 11.1. Architecture gaps and their parametric handling

| Gap | Blocks | Handling |
| --- | --- | --- |
| Gravity is a literal | Mars, orbit | gravity driver bound to the profile; every sizing function reads it |
| Atmospheric pressure and air are literals | Antarctic plateau, Mars, orbit | atmosphere group in the profile; densities and partial pressures computed in `site.py` |
| Only an air heat sink exists | Death Valley summer, Mars, orbit | heat rejection mode per heat ladder level (air, evaporative, ground, radiative, heat pump lift); radiator sizing function |
| Solar model is one mean day | Antarctica, Mars, orbit | resource model in the profile; storage sized for the longest dark or low period; PV rule basis per Q-024 |
| Free surfaces and buoyancy assumed | orbit, partly Mars and the floating island | buoyant separation and free surface needs; replacement units |
| Apparent gravity assumed steady and vertical | floating island | motion group in the profile; tilt and motion margins in the sizing functions; sloshing checks |
| Mass, centre of gravity and stability not modelled | floating island, orbit | operating mass and centre of gravity summed over the scaled units; stability and freeboard checks |
| Seawater is not a feed or a heat sink | floating island, coastal Antarctica | seawater intake, desalination and mineral recovery units; seawater feed case |
| Combustion and vents use air | Mars, orbit | air oxidant and vent sink needs; recovery and catalytic replacements |
| Ground contact assumed | floating island, orbit, partly Mars and Antarctica | ground group may be not applicable; foundation, earthing and GEO read it |
| Open liquid water assumed | Mars, orbit | liquid water at ambient need; hall pressure driver |
| Truck logistics assumed | Antarctica, floating island, Mars, orbit | logistics group sets hold times, spares and outlets |
| One jurisdiction | Antarctica, floating island, Mars, orbit | code families per row of the editions table |
| Feed cases are terrestrial | all | local feedstock group mapped to new assay cases |
| Graph is single-site | all | scaling actions applied to the base graph into a locale namespace |
| Power sized from PV and one mean day | all | power portfolio solved through the worst stretch with the oversize factor (section 5.5) |
| Scripts read `drivers.json` directly | all | every read goes through `drivers.load()`; a test rejects a direct read |

## 12. Build order

The work is split into phases, each closed by its own check. The X-LOC tasks in AQS-PLAN-007 track them. The status column gives the state of each task in that plan; `flow_graph/test_localization_plan.py` fails when the two disagree. A locale run writes its outputs under `sites/<site_id>/`, which is not committed, so the evidence for a variant is reproduced by running `python3 -m flow_graph.param.regen --site <site_id>`. Earth sites come before off-world sites. Table 12.1 gives the order.

Table 12.1. Build phases

| Task | Phase | Done when | Status |
| --- | --- | --- | --- |
| X-LOC-01 | This plan | AQS-PLAN-011 issued; owner questions logged | done |
| X-LOC-02 | Profile schema, baseline profile and loader | schema and baseline profile committed; `drivers.load()` applies the profile; every script reads drivers through the loader; baseline regeneration unchanged | done |
| X-LOC-03 | Constants into the profile | gravity, pressure, air composition and air densities read from the profile; baseline regeneration unchanged | done |
| X-LOC-04 | Site selection and namespaces | `--site`, `AQS_SITE`, `--all-sites`; outputs under `sites/<site_id>/`; register handles locale numbers | done |
| X-LOC-05 | Sector and unit scaling | needs table, scaling map, scaling check and per-locale scaling table generated | done |
| X-LOC-06 | Power portfolio, heat rejection and storage models | portfolio solved through the worst stretch with the oversize factor; rejection modes and radiator sizing; solar and other resource models in the solver | done |
| X-LOC-07 | Death Valley variant | profile, site basis page, regeneration and closure pass | done: the locale run on 2026-10-29 passes the site design check once intake units are skipped by the per-unit mass balance (they draw from outside the plant) |
| X-LOC-11 | Floating island variant | as X-LOC-07, with the motion group, mass and stability checks, seawater feed case and the marine code family | open: the locale run on 2026-10-29 passes the site design check and the hull check (AQS-SITE-012), but SW_INTAKE and DESAL_RO stay placeholders in the profile and no mineral-recovery unit is in the graph |
| X-LOC-08 | Antarctic variant | as X-LOC-07, with the treaty code family | done: the locale run on 2026-10-29 passes the site design check; the wind-primary power write stage that blocked the first run is in `flow_graph/param/write_graph.py` |
| X-LOC-09 | Mars variant | as X-LOC-07, with in-situ feed cases and replacement units | done: replacement and in-situ resource units in the graph; the locale run on 2026-10-29 passes the site design check |
| X-LOC-10 | Low Earth orbit variant | as X-LOC-07, with microgravity replacements and radiators | done: the locale run on 2026-10-29 passes the site design check |
| X-LOC-12 | Cross-locale comparison | a generated comparison of scaling actions, power portfolios and unit sizes across every profile | done: AQS-SITE-011, written by `docs-authority/_site_comparison.py` from the locale outputs |
| X-LOC-13 | Evaporative rejection water charge | spray water at evaporative sites booked against the water balance and closed by the groundwater intake | done: booked in `flow_graph/param/balance.py`; the Death Valley run closes with it |

## 13. Acceptance checks

These checks are added with the phase that needs them and run in `scripts/check_all.sh`.

- A profile that lacks a required entry, or has an entry without a basis, fails the loader.
- With the baseline profile, the resolved drivers equal `drivers.json` and `regen --check` changes nothing.
- No script reads `drivers.json` except through the loader, and no sizing module contains a gravity or atmospheric pressure literal.
- Every profile in `flow_graph/param/sites/` regenerates, and its loop closure and mass and energy balance checks pass within the misfit gate.
- Every unit whose needs a profile does not meet is replaced or eliminated; every elimination has an import path or a replacement; no energy or life-support function is left with fewer sources than the redundancy rule needs.
- Each profile's power portfolio closes the energy balance through its worst stretch with the oversize factor applied.
- Document numbers are unique as number and site pairs, and every locale page has a number from the register tool.
- Every check document in a locale cites a governing clause from that locale's code families or is reported open.

## 14. Owner decisions

The questions below are logged in AQS-OQ-001 with the default the work will proceed on.

- Q-033. The Death Valley parcel: Furnace Creek climate with a parcel outside the park. Default: climate of station USC00042319; parcel to be chosen; United States codes with the state's own.
- Q-021. The Antarctic site class: coastal or plateau. Default: coastal, McMurdo class; plateau as a second profile.
- Q-022. The Mars site: mid-latitude ice or equatorial. Default: mid-latitude with shallow ice, Arcadia Planitia class.
- Q-023. The orbit and gravity: station-class orbit or a sun-synchronous orbit with little eclipse, and whether a rotating section supplies gravity. Default: station-class orbit, no rotation.
- Q-024. Closed by the owner: power sources are chosen per site from the local resource (section 5.5); the oversize rule applies per site to the worst stretch; fission and other sources are flagged options with their own studies.
- Q-025. Waste processing under the Antarctic Treaty. Default: treat the plant as a waste processing facility that needs a comprehensive environmental evaluation.
- Q-026. Surplus outlets where export is impractical. Default: local use, storage and propellant.
- Q-027. Planetary protection at Mars ice. Default: site outside special regions.
- Q-028. Document numbers for locale copies. Default: base number with a site suffix.
- Q-029. Crew size per locale. Default: the baseline crew at every locale.
- Q-030. The floating island site and jurisdiction: moored or free-floating, and under which flag or coastal state. Default: moored in tropical waters with an ocean thermal gradient; class society rules with SOLAS and MARPOL.
- Q-031. Storm strategy for the floating island: ride out the design storm on the moorings, or relocate ahead of it. Default: ride it out, with relocation as an option.
- Q-032. Closed (owner, 2026-10-25): hard-coded values are a gap; every module reads the profile gravity, and the baseline keeps the standard values, flagged for verification.

## 15. References

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
40. Millero F.J. et al., The composition of Standard Seawater and the definition of the Reference-Composition Salinity Scale, Deep-Sea Research I 55 (2008) 50–72.
41. Wright D.G. et al., Absolute Salinity, "Density Salinity" and the Reference-Composition Salinity Scale: present and future use in the seawater standard TEOS-10, Ocean Science 7 (2011) 1–26, section 3.1.
42. NOAA Office for Coastal Management, Ocean Thermal Energy Conversion (OTEC) Technology, technical fact sheet. <https://coast.noaa.gov/data/czm/media/technicalfactsheet.pdf>
43. Gunn K., Stock-Williams C., Quantifying the global wave power resource, Renewable Energy 44 (2012) 296–304.
44. Elimelech M., Phillip W.A., The future of seawater desalination: energy, technology, and the environment, Science 333 (2011) 712–717.
45. NOAA National Hurricane Center, Saffir-Simpson Hurricane Wind Scale. <https://www.nhc.noaa.gov/aboutsshws.php>
46. ISO 12944-2:2017, Paints and varnishes — Corrosion protection of steel structures by protective paint systems — Part 2: Classification of environments.
47. Effects of Tower Motion on Packing Efficiency, Society of Petroleum Engineers paper 143766 (2011). <https://doi.org/10.2118/143766-MS>
48. Schultes M., Marinization of mass transfer columns for floating liquefied natural gas applications, Distillation and Absorption 2018 conference. <https://skoge.folk.ntnu.no/prost/proceedings/Distillation&Absorption-2018/papers/17schultes.pdf>
49. A classification society's offshore rules for stability and watertight integrity, position mooring and environmental loads (for example the DNV offshore standards and recommended practices), latest editions.
50. International Maritime Organization, International Code on Intact Stability, 2008 (2008 IS Code).
51. International Maritime Organization, International Convention for the Safety of Life at Sea, 1974, as amended (SOLAS).
52. International Maritime Organization, International Convention for the Prevention of Pollution from Ships (MARPOL), Annexes I to VI.
53. International Maritime Organization, Code for the Construction and Equipment of Mobile Offshore Drilling Units, 2009 (2009 MODU Code).
54. International Maritime Organization, International Ship and Port Facility Security Code (ISPS Code).
55. Tiesinga E. et al., CODATA recommended values of the fundamental physical constants: 2018, Reviews of Modern Physics 93 (2021) 025010.
