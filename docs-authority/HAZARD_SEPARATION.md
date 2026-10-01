# Hazard separation and containment — design locks

Document number: AQS-HSE-001  
Revision: G  
Date: 2026-10-01  
Jurisdiction assumed: USA; design to NFPA 70-2026 + NFPA 1/400/2/55/69/70E/855-2026 + 29 CFR 1910.  
AHJ edition and local amendments govern construction. This file is not a PE stamp.

Texas note: as of late Sept 2026 several states including Texas enforce NEC 2026. Confirm City of Dallas amendments before permit.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue | 2026-09-27 |
| B | 1 | FC + GEN + CRYO_H2 Class I / MAQ co-location (AQS-FC-001) | 2026-09-28 |
| C | 1 | CRYO room vent stream S56 + Q4 peer CRYO_HX_Q4 (AQS-CRY-002) | 2026-09-28 |
| D | 1 | MFG metal-aisle MET_AHU S62 + MET_HX_Q4 S63 (AQS-MFG-MET-001) | 2026-09-28 |
| E | 1 | North dock + STAIR_SERVICE egress separation (AQS-SITE-001) | 2026-09-28 |
| F | 1 | Vent closure: scrub/CRYO end states (AQS-VENT-001); no outdoor dump intent | 2026-09-28 |
| G | 1 | AQS-CMP-001 compliance matrix; LEV/MET_SCRUB + CMP cross-ref | 2026-10-01 |

---

## 0. What this file is allowed to change

These rules override convenience. They do not rename locked units or mix headers.

| May change | Must not change |
|---|---|
| Fire-barrier ratings between campus blocks | Header list (four process + life) |
| Inventory caps, MAQ strategy | Salria chemistry, E° order |
| Classified-area envelopes | ZnBr2 isolated from CRU / CRYO |
| Secondary-containment volumes | FR-4 out of pyro |

---

## 1. Occupancy and fire areas

One roof is not one fire area. IBC/NFPA 5000 mixed-use + NFPA 400 Table 6.2.1.3.

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

NP (not permitted) from Protection Level 1 into habitation. This plant has no Class 4 oxidizer by design.

### Locked barrier objects (CAD)

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
| CORE_LIFE | 2 h room | STAIR_P, ELEV_SVC, UTIL, PENSTOCK |
| CORE_PROCESS | 2 h room | H2, acid, oil, dust risers. Not the elevator. |

Vertical stack: `cad/BUILDING_STACK.md`. IBC 2024 Table 508.4 allows R over H-3 only if the building is sprinklered (2 h). Plant standard is 3 h. Non-sprinklered R over H is not permitted.

No duct that carries process atmosphere through these walls. HVAC across a fire area is a listed damper + separate AHU or energy-recovery only on Q4 water.

---

## 2. Incompatible materials (NFPA 400 / OSHA 1910.1200)

Already implied by headers. Now mandatory:

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

Minimum 25 ft or a 1 h partition between oxidizer containers and combustible liquids (NFPA 400 Ch. 15 practice).

---

## 3. Inventory caps (PSM / RMP / MAQ)

Stay under OSHA 1910.119 and EPA RMP where the process allows. If a cap is hit, PSM is the project, not an afterthought.

| Substance | Trigger | Design cap |
|---|---|---|
| Cl2 | PSM 1,500 lb; RMP 2,500 lb | No liquid-Cl2 receiver. Generate → alkali scrubber → CRU. Free Cl2 inventory target < 100 lb equivalent in gas space |
| H2 | PSM 10,000 lb flammable gas | CRYO_H2 + H2_DRYER hold < 150 lb (~27,000 scf). No bulk tube trailer inside the building |
| Br2 | PSM 1,500 lb | Free Br2 (uncomplexed) in vapour space < 50 lb. Complexed Br3− stays in PVDF tank. Outdoor skid |
| Aqueous HCl | PSM does **not** cover muriatic; RMP 15,000 lb if ≥37% | BMED acid tanks sized and bunded; keep ≥37% inventory documented |
| NaClO3 solid | NFPA 400 Class 3 oxidizer MAQ | Store wet or in solution in CRU. No dry bag warehouse next to oil line |
| Oil cuts | NFPA 30 / 1910.106 | Fractionator holdup + product totes; indoor flammable liquid < MAQ or H-3 room |

Hydrogen generated at the cathode is a rate, not a tank, until CRYO_H2. Size the dryer, **BACKUP_GEN**, and **FUEL_CELL** so combined holdup stays under the cap (AQS-PWR-001 / AQS-FC-001).

---

## 4. Classified electrical areas (NEC 2026 Art. 500 / 501)

Zone system (Art. 505) is optional. This plant uses Division.

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

No ordinary sparking device in a Div 2 envelope. Rectifiers and Sol-Ark stay in the POWER YARD, outside Class I.

NEC 110.26 working space: 3 ft 6 in in front of 480 V gear (condition 2). 110.27 live parts guarded.

ESS: NEC Art. 706 + NFPA 855-2026. ZnBr2 is a flow battery; indoor threshold historically 20 kWh. This 120 kWh pack stays **outdoors**, 10 ft from building openings, dedicated EPO, listed disconnect.

---

## 5. Containment

| Unit | Primary | Secondary | Code hook |
|---|---|---|---|
| LEACH CSTR 1 | CPVC tank | EW aisle bund + tank pad, 110% of CSTR working volume | UFC / IFC hazardous materials; plant already has bund |
| EW-1…9 / PK | cell | same bund, sloped to CSTR return | no sewer |
| BMED acid / base / CRU | tanks | dedicated acid-resistant sump, 110% largest | NFPA 400 corrosive |
| OIL cuts / quench | steel / 304 | NFPA 30 diked area, remote from oxidizer | 1910.106 |
| ZnBr2 pos / neg | PP / PVDF | 110% of one tank, outdoor | FLOW_BATTERY.md already |
| ETCH RETURN | PVDF | closed; no floor drain | CWA / local pretreatment ban |
| FARM SUMP / HAB WATER | PP | double-wall or indoor drain to HDR_GREY only | plumbing code; not Salria |
| H2_DRYER knockout | 316 | drained to safe vent, not hab | NFPA 2 |

Spill path: process liquor → bund → CSTR 1 or CRU. Never to storm, farm, or hab.

---

## 6. Ventilation and gas

End states per **AQS-VENT-001** — free outdoor dump is not design intent.
Upset / contingency relief may remain for AHJ and life safety.

| Space | Rate / rule | End state / discharge |
|---|---|---|
| CSTR / EW anode | hood → HDR_ACID_GAS → DEMISTER → ALK → ACID_POLISH | Liquor → CRU (S66); upset stack residual only (AQS-GAS-003) |
| EW cathode | hood → HDR_H2 → arrestor → dryer → S64 CRYO_H2 | Consumers S45/S49; S24 roof contingency only; not hab |
| Oil vapor | quench → HDR_OIL_VAPOR → afterburner → FLUE_CAP / CRYO | Destruction + S67 capture; S68 condensate; not hab |
| Dust | baghouse | fines to CSTR 1 (S19) |
| CRYO room | NFPA 2 / 55 via CRYO_AHU → CRYO_AHU_COND (S70); H2 @ 25% LFL trip | Condensables to CRYO; S56 residual contingency; never HAB return |
| ZnBr2 | own Br2 tower + ZNBR2_BR2_REGEN | S69 Br⁻ → pos. tank; not CRU; no continuous dump |
| HAB | dedicated AHU; Q4 water only | — |
| FAB wet bench | exhausted enclosure; not process acid header | ETCH closed liquid |
| MFG metal forming | MET_AHU → MET_SCRUB / baghouse (S71–S72) | Scrub/BH returns; never HAB return |

NFPA 69: keep H2 < 25% LFL by capture + dilution. Detection trips rectifiers and closes H2 isolation.

---

## 7. OSHA program hooks (always on, even under PSM caps)

- 1910.147 LOTO on rectifiers, shredder, pyro, MET_MELT / mills, Sol-Ark
- 1910.146 permit spaces: CSTR 1, fractionator, scrubber vessels
- 1910.134 respirator program for Salria / Cl2 / Br2 tasks
- 1910.1200 HazCom + SDS at the gate
- 1910.212 / 219 machine guarding shredder
- 1910.95 noise survey at shredder and induction
- 1910.303 / 305 / 333 electrical; 70E arc-flash labels on 480 V gear
- 1910.119 only if a cap in §3 is exceeded
- Walking-working surfaces 1910.22; mezzanine guardrails 1910.29

---

## 8. Water, life safety, accessibility

- Egress: two exits from recycle aisle; hab sleeping has independent egress that does not pass through H areas (IBC 1016 / NFPA 101)
- Hab sleeping path: STAIR_P (L2–L0, **no L-1 door**) + STAIR_S1/S2 (L1–L0). Discharge at grade without walking the basement.
- Basement secondary egress / service: STAIR_SERVICE (north face) + STAIR_MAINT (operators only). STAIR_SERVICE discharges to north apron via SERVICE_ENTRY — not through CORE_PROCESS as a hab route (AQS-SITE-001).
- Do not credit STAIR_MAINT as the sole public exit from an H room. Full travel-distance / exit-width calc = next HSE compliance pass.
- Sprinklers: NFPA 13 throughout except outdoor ESS and spaces listed as unsprinklered by AHJ (oxidizer rooms may need special design)
- Emergency lights / exit signs NEC 700
- Potable vs process water: air gap or RPZ on HDR_UPW from any process makeup (IPC / UPC)
- ADA / ABA on hab and shop access only; process aisle is restricted


---

## 8a. POWER yard H₂ consumers (GEN + FC + CRYO_H2)

Co-located on L0 POWER yard (AQS-PWR-001 / AQS-FC-001):

1. **CRYO_H2** hold feeds isolated branches to BACKUP_GEN (S45) and
   FUEL_CELL (S49). Do not common a single unisolated manifold into
   both without flame arrestors and labeled isolation valves.
2. **BACKUP_GEN** exhaust (S46) → condensate / scrubber only — never
   into HAB / FARM AHU or Q4 water as flue gas.
3. **FUEL_CELL** heat → Q4 via FC_HX_Q4 (S53) water only; purge to
   safe vent / scrub — not AFTERBURNER as primary sink.
4. Combined H₂ inventory (CRYO_H2 + dryer + GEN/FC manifolds) shall
   respect §3 MAQ design cap. Normal path S64 → CRYO_H2; roof (S24)
   remains contingency only (AQS-VENT-001).
5. Sol-Ark, RECT, and ZnBr2 stay outside Class I envelopes; FC_DCDC
   and inverter live in ordinary POWER yard space with H₂ detection
   trips isolating fuel trains.

### CRYO heat / ventilation (AQS-CRY-002 / AQS-VENT-001)

- Warm residual → Q4 via `CRYO_HX_Q4` (S54) only (< 80 °C water).
- Stirling / deep reject → `CRYO_DED_COOL` (S55) — not life AHU.
- Room AHU → `CRYO_AHU_COND` condensables (S70) → COLD_BOX; S56 residual
  contingency only — no shared return HAB↔CRYO; no continuous outdoor dump.

### MFG metal forming HVAC / heat (AQS-MFG-MET-001 / AQS-VENT-001)

- Aisle capture → `MET_AHU` → `MET_SCRUB` / baghouse (S71–S72); no shared
  return HAB↔MFG metal aisle; no free outdoor dump as design end state.
- Warm residual → Q4 via `MET_HX_Q4` (S63) only (< 80 °C water).
- Melt / atomizer hot gas shall not enter Q4 as flue.
- MET_MELT ≠ INDUCTION_PYROLYZER; FR-4 / polymer never into metal melt.

---

## 9. Implementation in CAD

`freecad/campus.py` keeps envelopes. Fire barriers are named objects in `freecad/fire_barriers.py`. Classified blobs are documentation until the operator places them on the site plan.

CAD massing (2026-09-27 Rev K): **FB_HAB_CORE** (3 h, T=300 mm) is the CORE enclosure toward HABITATION plus the centreline segment through the CORE Y-band (HAB ↔ CORE_PROCESS / recycle). **FB_HAB_FARM** (2 h, T=200 mm) is the HAB ↔ FARM party wall *outside* the CORE Y-band. The two objects no longer share one co-located box. Replicated per `LIFE_LEVELS` (`FB_HAB_*_S{n}` when n≥2).

Rebuild is not required for this file to govern procurement and layout reviews.
