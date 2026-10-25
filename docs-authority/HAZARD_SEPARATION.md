# Hazard separation and containment

Document number: AQS-HSE-001  
Revision: H  
Date: 2026-10-24  
Jurisdiction assumed: USA. Design codes: NFPA 70-2026 (NEC); NFPA 1, 400, 2, 55, 69, 70E and 855, 2026 editions; 29 CFR 1910 (OSHA). The edition adopted by the authority having jurisdiction (AHJ), with its local amendments, governs construction. This is not a document stamped by a professional engineer.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue | 2026-09-27 |
| B | 1 | FC + GEN + CRYO_H2 Class I / MAQ co-location (AQS-FC-001) | 2026-09-28 |
| C | 1 | CRYO room vent stream S56 + Q4 peer CRYO_HX_Q4 (AQS-CRY-002) | 2026-09-28 |
| D | 1 | MFG metal-aisle MET_AHU S62 + MET_HX_Q4 S63 (AQS-MFG-MET-001) | 2026-09-28 |
| E | 1 | North dock + STAIR_SERVICE egress separation (AQS-SITE-001) | 2026-09-28 |
| F | 1 | Vent closure: scrub/CRYO end states (AQS-VENT-001); no outdoor dump intent | 2026-09-28 |
| G | 1 | AQS-COMPL-001 compliance matrix; LEV/MET_SCRUB + CMP cross-ref | 2026-10-01 |
| H | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; rules and values unchanged | 2026-10-24 |

## 1. Purpose and scope

The plant puts recycling chemistry, hydrogen, cryogenics, a wafer fab, a farm and living quarters under one roof. This document sets the rules that keep those hazards apart: fire areas and barriers, incompatible materials, inventory limits, hazardous electrical areas, spill containment, ventilation, the OSHA programmes and the escape routes. These rules take priority over convenience in layout.

Table 1.1 states what this document may and may not change. It does not rename locked units or mix headers.

Table 1.1. Limits of this document

| May change | Must not change |
|---|---|
| Fire-barrier ratings between campus blocks | Header list (four process + life) |
| Inventory caps, MAQ strategy | Salria chemistry, E° order |
| Classified-area envelopes | ZnBr2 isolated from CRU / CRYO |
| Secondary-containment volumes | FR-4 out of pyro |

Jurisdiction note: as of late September 2026, several states, including Texas, enforce NEC 2026. Confirm the City of Dallas amendments before applying for a permit.

## 2. Terms

Fire area: part of a building separated from the rest by fire barriers of a stated rating, in hours. One roof is not one fire area.

Occupancy group: the IBC classification of a space by use, for example R-2 residential, F-1 factory, H-2 to H-5 high hazard.

Maximum allowable quantity (MAQ): the largest amount of a hazardous material allowed in one control area before the space must be classed as an H occupancy (IBC; NFPA 400).

Control area: a space that keeps hazardous materials at or below the MAQ.

Protection level (PL): the NFPA 400 equivalent of an H occupancy group.

Classified area: a space where flammable gas, vapour or dust may be present, so that electrical equipment must be specially protected (NEC Article 500). "Class I, Division 2, Group B" means flammable gas (Class I), present only under abnormal conditions (Division 2), of the hydrogen group (Group B).

Lower flammable limit (LFL): the lowest concentration of a gas in air that can burn.

Secondary containment (bund): a basin or dike that holds a spill from a tank.

Process safety management (PSM) and risk management programme (RMP): the OSHA 1910.119 and EPA rules that apply above set inventory thresholds.

Header names (for example `HDR_H2`) and unit names are locked plant graph names. Stream numbers such as S64 refer to the stream register. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Occupancy and fire areas

The building is a mixed-use building under the IBC and NFPA 5000, with NFPA 400 Table 6.2.1.3 for hazardous materials. Table 3.1 assigns each fire area its occupancy and its barrier to the habitation.

Table 3.1. Fire areas

| Fire area | Occupancy (design) | High-hazard overlay | Barrier to HABITATION |
|---|---|---|---|
| RECYCLE CORE | F-1 / industrial special | H-3 (oxidizer + corrosive) if MAQ exceeded; else control-area | 3 h min (PL-3 vs residential). Prefer 4 h. |
| OIL / PYRO / AFTERBURNER | F-1 + H-3 flammable vapor | NFPA 30 / 69 | 3 h |
| ZnBr2 skid | Outdoor ESS / H-4 toxic | NFPA 855-2026 flow battery | 2 h if enclosed; outdoor preferred |
| CRYO | H-2 if GH2 > MAQ; else control area | NFPA 2 / 55 | 2 h + no shared HVAC return |
| WAFER FAB | H-5 analog (corrosive use) | closed etch return | 2 h |
| FARM | F-2 / U accessory | no oxidizer storage | 1 h to core; 2 h to hab if grease/NH3 |
| HABITATION | R-2 analog | none | — |
| MFG SHOP | F-1 | no Salria | 1 h to hab |
| POWER YARD | outdoor electrical + H₂ GEN/FC | NEC 110 / 706; NFPA 2 if H₂ | not inside hab |

Moving from Protection Level 1 into the habitation is not permitted. By design, the plant holds no Class 4 oxidizer.

### 3.1 Barrier objects in the CAD model

Table 3.2 names the fire barriers as they appear in the model.

Table 3.2. Locked barrier objects

| Name | Rating | Between |
|---|---|---|
| FB_HAB_CORE | 3 h | HABITATION ↔ recycle / oil |
| FB_HAB_FARM | 2 h | HABITATION ↔ FARM |
| FB_FAB_CORE | 2 h | WAFER_FAB ↔ recycle |
| FB_CRYO | 2 h | CRYO ↔ all occupied |
| FB_CRYO_PROCESS | 2 h | L-1 process aisle ↔ CRYO (no process-air duct) |
| FB_ESS | 2 h or open-air | ZnBr2 ↔ occupied |
| HA_L1_L0 | 3 h horizontal | LIFE plate ↔ GRADE |
| HA_L0_Lm1 | 3 h horizontal | GRADE ↔ BASEMENT |
| HA_Lm1_Lm2 | 2 h horizontal | BASEMENT ↔ CATCH TANK room |
| SHAFT_H2 / ACID / OIL | 2 h | dedicated; no hab openings |
| SHAFT_EGRESS | 2 h | L1 → L0 only |
| CORE_LIFE | 2 h room | STAIR_P, ELEV_SVC, SHAFT_UTIL, SHAFT_PENSTOCK |
| CORE_PROCESS | 2 h room | H2, acid, oil, dust risers. Not the elevator. |

The vertical stack is in `docs-authority/BUILDING_STACK.md`. IBC 2027 Table 508.4 allows a residential floor over an H-3 occupancy only if the building is sprinklered, with a 2 h separation. The plant standard is 3 h. A residential floor over an H occupancy without sprinklers is not permitted.

No duct carrying process atmosphere passes through these barriers. Ventilation across a fire area uses a listed damper and a separate air-handling unit, or energy recovery through the Q4 water loop only.

## 4. Incompatible materials

The header layout already keeps most incompatible materials apart; Table 4.1 makes the rules mandatory (NFPA 400; OSHA 1910.1200).

Table 4.1. Materials to keep apart

| Keep apart | Why | How |
|---|---|---|
| NaClO3 (Class 3 oxidizer) × organics / oil / FR-4 | oxidizer + fuel | chlorate only in CRU / REGEN LEACH / CSTR 1. Not FARM, not HAB, not OIL LINE |
| HDR_H2 × HDR_O2 | explosive mix | separate headers, separate cryo product tags, 25 ft ignition rule indoors |
| HDR_H2 × HDR_ACID_GAS / Cl2 | not a fuel issue; mixed atmospheres hide leaks | already separate |
| HDR_OIL_VAPOR × any oxidizer gas | fire | already separate; afterburner only after quench |
| Free Br2 × organics / ammonia / H2 | toxic + reactive | ZnBr2 own tower; no tee to CRU |
| Salria × PP / HDPE / Ti tank wall | material failure | CPVC/PVDF only |
| Etch × sewer / HDR_GREY | metals + acid to environment / farm | HDR_ETCH → REGEN LEACH only |
| Q1 flue × HAB AIR | CO / NOx | Q4 water only into hab |

Oxidizer containers are kept at least 25 ft from combustible liquids, or separated by a 1 h partition (NFPA 400 chapter 15 practice).

## 5. Inventory limits

The design keeps inventories below the OSHA 1910.119 (PSM) and EPA RMP thresholds where the process allows, and below the MAQ. If a limit is exceeded, PSM becomes a central part of the project rather than an afterthought. Table 5.1 gives the thresholds and the design limits.

Table 5.1. Inventory thresholds and design limits

| Substance | Trigger | Design cap |
|---|---|---|
| Cl2 | PSM 1,500 lb; RMP 2,500 lb | No liquid-Cl2 receiver. Generate → alkali scrubber → CRU. Free Cl2 inventory target < 100 lb equivalent in gas space |
| H2 | PSM 10,000 lb flammable gas | CRYO_H2 + H2_DRYER hold < 150 lb (~27,000 scf). No bulk tube trailer inside the building |
| Br2 | PSM 1,500 lb | Free Br2 (uncomplexed) in vapour space < 50 lb. Complexed Br3− stays in PVDF tank. Outdoor skid |
| Aqueous HCl | PSM does **not** cover muriatic; RMP 15,000 lb if ≥37% | BMED acid tanks sized and bunded; keep ≥37% inventory documented |
| NaClO3 solid | NFPA 400 Class 3 oxidizer MAQ | Store wet or in solution in CRU. No dry bag warehouse next to oil line |
| Oil cuts | NFPA 30 / 1910.106 | Fractionator holdup + product totes; indoor flammable liquid < MAQ or H-3 room |

Hydrogen made at the cathode is a flow, not a stored inventory, until it reaches `CRYO_H2`. The dryer, `BACKUP_GEN` and `FUEL_CELL` are sized so that their combined holdup stays below the limit (AQS-PWR-002, AQS-FC-001).

## 6. Hazardous electrical areas

The plant uses the Class and Division system of NEC 2026 Articles 500 and 501; the Zone system of Article 505 is optional. Table 6.1 gives each classified envelope.

Table 6.1. Classified areas

| Envelope | Class / Div / Group | Extent (design) | Wiring |
|---|---|---|---|
| HDR_H2 duct, H2_DRYER, CRYO_H2, cathode hood interior | I / 2 / B | 3 ft around flanges; 5 ft around dryer | XP or purged, 316 tray |
| GEN_H2_BUFFER / BACKUP_GEN fuel train | I / 2 / B | 3 ft around flanges; outdoor pad preferred | XP instruments; flame arrestors |
| FC_H2_MANIFOLD / FUEL_CELL anode flanges | I / 2 / B | 3 ft around flanges; 5 ft around stack enclosure vents | XP or purged; H₂ detection 25% LFL |
| FC_O2_MANIFOLD | oxidizer (not Class I fuel) | keep ≥ 25 ft or 1 h from H₂ / organics | per NFPA 55 / 400 |
| OIL LINE vapor space, quench inlet, fractionator relief | I / 2 / D | 3 ft around open vents | XP or purged |
| AFTERBURNER burner front | I / 2 / D | per burner listing | listed train |
| SHREDDER / HOPPER dust | II / 2 / G (organic dust) | 10 ft around dump | dust-tight |
| CSTR 1 / EW aisle general | unclassified if hood capture ≥ 90% and LEL < 10% documented | — | ordinary + GFCI wet |
| Alkali / Br2 scrubber rooms | unclassified toxic; not Class I unless H2 present | — | corrosion-resistant |
| ZnBr2 skid outdoor | I / 2 / D if Br2/H2 off-gas can accumulate under lid | 3 ft around tank vents | XP instruments |
| HAB / FARM / FAB general | unclassified | — | wet-location where water |

No ordinary sparking device is allowed in a Division 2 envelope. The rectifiers and the Sol-Ark inverters stay in the power yard, outside Class I areas.

NEC 110.26 working space is 3 ft 6 in in front of 480 V equipment (condition 2), and NEC 110.27 requires live parts to be guarded.

Energy storage follows NEC Article 706 and NFPA 855-2026. The zinc-bromide (ZnBr2) battery is a flow battery, for which the indoor threshold has historically been 20 kWh. The 120 kWh pack therefore stays outdoors, 10 ft from building openings, with its own emergency power-off (EPO) and a listed disconnect.

## 7. Spill containment

Table 7.1 gives the primary and secondary containment for each unit.

Table 7.1. Containment

| Unit | Primary | Secondary | Code hook |
|---|---|---|---|
| LEACH CSTR 1 | CPVC tank | EW aisle bund + tank pad, 110% of CSTR working volume | UFC / IFC hazardous materials; plant already has bund |
| EW-1…9 / PK-9 | cell | same bund, sloped to CSTR return | no sewer |
| BMED acid / base / CRU | tanks | dedicated acid-resistant sump, 110% largest | NFPA 400 corrosive |
| OIL cuts / quench | steel / 304 | NFPA 30 diked area, remote from oxidizer | 1910.106 |
| ZnBr2 pos / neg | PP / PVDF | 110% of one tank, outdoor | FLOW_BATTERY.md already |
| ETCH RETURN | PVDF | closed; no floor drain | CWA / local pretreatment ban |
| FARM SUMP / HAB WATER | PP | double-wall or indoor drain to HDR_GREY only | plumbing code; not Salria |
| H2_DRYER knockout | 316 | drained to safe vent, not hab | NFPA 2 |

Spills of process liquor go to the bund and then to CSTR 1 or the CRU, never to storm drains, the farm or the habitation.

## 8. Ventilation and gas handling

The end state of every gas stream follows AQS-VENT-001: continuous release to open air is not design intent. Relief for upsets and contingencies may remain where the AHJ and life safety require it. Table 8.1 gives the rule for each space.

Table 8.1. Ventilation and end states

| Space | Rate / rule | End state / discharge |
|---|---|---|
| CSTR / EW anode | hood → HDR_ACID_GAS → DEMISTER → ALK_SCRUBBER → ACID_POLISH | Liquor → CRU (S66); upset stack residual only (AQS-GAS-003) |
| EW cathode | hood → HDR_H2 → arrestor → dryer → S64 CRYO_H2 | Consumers S45/S49; S24 roof contingency only; not hab |
| Oil vapor | quench → HDR_OIL_VAPOR → afterburner → FLUE_CAP / CRYO | Destruction + S67 capture; S68 condensate; not hab |
| Dust | baghouse | fines to CSTR 1 (S19) |
| CRYO room | NFPA 2 / 55 via CRYO_AHU → CRYO_AHU_COND (S70); H2 @ 25% LFL trip | Condensables to CRYO; S56 residual contingency; never HAB return |
| ZnBr2 | own Br2 tower + ZNBR2_BR2_REGEN | S69 Br⁻ → pos. tank; not CRU; no continuous dump |
| HAB | dedicated AHU; Q4 water only | — |
| FAB wet bench | exhausted enclosure; not process acid header | ETCH closed liquid |
| MFG metal forming | MET_AHU → MET_SCRUB / baghouse (S71–S72) | Scrub/BH returns; never HAB return |

Hydrogen is kept below 25 % of its LFL by capture and dilution (NFPA 69). Gas detection trips the rectifiers and closes the hydrogen isolation valves.

## 9. OSHA programmes

These programmes apply at all times, even when inventories are below the PSM thresholds:

- 1910.147 lockout/tagout on the rectifiers, shredder, pyrolysis unit, `MET_MELT`, mills and Sol-Ark inverters;
- 1910.146 permit-required confined spaces: CSTR 1, the fractionator and the scrubber vessels;
- 1910.134 respirator programme for work with Salria, chlorine (Cl2) and bromine (Br2);
- 1910.1200 hazard communication, with safety data sheets at the gate;
- 1910.212 and 1910.219 machine guarding on the shredder;
- 1910.95 noise survey at the shredder and the induction equipment;
- 1910.303, 1910.305 and 1910.333 electrical safety, with NFPA 70E arc-flash labels on 480 V equipment;
- 1910.119 only if a limit in section 5 is exceeded;
- walking-working surfaces under 1910.22, and guardrails on mezzanines under 1910.29.

## 10. Escape routes, water and accessibility

- The recycling aisle has two exits. The habitation sleeping areas have their own escape route, which does not pass through H areas (IBC 1016; NFPA 101).
- The sleeping-area route uses `STAIR_P` (L2 to L0, with no door on L-1) and `STAIR_S1` and `STAIR_S2` (L1 to L0). It reaches grade without passing through the basement.
- Secondary escape and service access for the basement use `STAIR_SERVICE` on the north face and `STAIR_MAINT` (operators only). `STAIR_SERVICE` discharges to the north apron through `SERVICE_ENTRY`, not through `CORE_PROCESS` as a habitation route (AQS-SITE-001).
- `STAIR_MAINT` must not be counted as the only public exit from an H room. The full travel-distance and exit-width calculation belongs to the next compliance pass of this document.
- Sprinklers to NFPA 13 throughout, except the outdoor energy storage and any spaces the AHJ lists as unsprinklered (oxidizer rooms may need a special design).
- Emergency lighting and exit signs to NEC 700.
- Drinking water is protected from process water by an air gap or a reduced-pressure zone (RPZ) backflow preventer on `HDR_UPW` wherever it supplies process make-up (IPC; UPC).
- Accessibility under the Architectural Barriers Act (ABA) and the Americans with Disabilities Act (ADA) applies to the habitation and shop only; the process aisle is restricted.

## 11. Hydrogen users in the power yard

The backup generator, the fuel cell and the hydrogen hold `CRYO_H2` share the L0 power yard (AQS-PWR-002, AQS-FC-001).

1. `CRYO_H2` feeds separate, isolated branches to `BACKUP_GEN` (S45) and `FUEL_CELL` (S49). They must not share one manifold without flame arrestors and labelled isolation valves.
2. The `BACKUP_GEN` exhaust (S46) goes to condensate handling or the scrubber only, never as flue gas into the habitation or farm air-handling units or the Q4 water.
3. `FUEL_CELL` heat goes to Q4 through `FC_HX_Q4` (S53) as water only. Its purge goes to a safe vent or the scrubber; the `AFTERBURNER` is not the main sink.
4. The combined hydrogen inventory (`CRYO_H2`, the dryer and the generator and fuel-cell manifolds) shall respect the design limit of section 5. The normal path is S64 to `CRYO_H2`; the roof outlet (S24) is for contingencies only (AQS-VENT-001).
5. The Sol-Ark inverters, the rectifiers and the ZnBr2 battery stay outside Class I envelopes. `FC_DCDC` and the inverter sit in ordinary power-yard space, with hydrogen detection that trips the isolation of the fuel trains.

### 11.1 Cryogenic plant heat and ventilation (AQS-CRY-002, AQS-VENT-001)

- Warm residual heat goes to Q4 through `CRYO_HX_Q4` (S54) only, as water below 80 °C.
- Heat rejected from the Stirling coolers and deep cooling goes to `CRYO_DED_COOL` (S55), not to a life air-handling unit.
- The room air-handling unit sends condensables through `CRYO_AHU_COND` (S70) to `COLD_BOX`. S56 is a residual contingency only. The habitation and CRYO never share return air, and there is no continuous release to open air.

### 11.2 Metal-forming ventilation and heat (AQS-MFG-MET-001, AQS-VENT-001)

- Aisle capture goes through `MET_AHU` to `MET_SCRUB` and the baghouse (S71 to S72). The habitation and the metal aisle never share return air, and release to open air is not a design end state.
- Warm residual heat goes to Q4 through `MET_HX_Q4` (S63) only, as water below 80 °C.
- Hot gas from the melt and the atomizer never enters Q4 as flue gas.
- `MET_MELT` is not the `INDUCTION_PYROLYZER`; FR-4 and polymers never go into the metal melt.

## 12. Implementation in the CAD model

`freecad/campus.py` holds the envelopes. Fire barriers are named objects in `freecad/fire_barriers.py`. The classified envelopes exist only in this document until they are placed on the site plan.

From the 2026-09-27 CAD massing (Rev K): `FB_HAB_CORE` (3 h, 300 mm thick) is the core enclosure facing the habitation plus the centreline segment through the core band in Y (habitation to `CORE_PROCESS` and recycling). `FB_HAB_FARM` (2 h, 200 mm thick) is the party wall between habitation and farm outside the core band. The two are separate objects. They are repeated for each of `LIFE_LEVELS` (`FB_HAB_*_S{n}` for n ≥ 2).

This document governs procurement and layout reviews without a rebuild of the model.
