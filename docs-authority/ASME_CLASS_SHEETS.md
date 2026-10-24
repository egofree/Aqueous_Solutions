# Pressure vessel inventory and process piping class sheets

Document number: AQS-ASM-001  
Revision: D  
Date: 2026-10-24  
Basis: AQS-WLD-001 (weld register), AQS-COMPL-001 (compliance matrix, items CMP-ASM-*), the AQS-EQP-* equipment lists, AQS-VENT-001, AQS-CRY-002, AQS-WTR-001, AQS-MeOH-001 and AQS-REQ-KW-001.  
Licence: CERN-OHL-S-2.0. `SCALE_M = 1.0`.

This is a study. It is not stamped by a professional engineer and is not an ASME U-stamp package. The maximum allowable working pressures and relief settings in it are study requirements derived from first principles, typical ASME practice and stand-in vessel ratings, not data from purchased, stamped vessels.

| Rev | Description | Date |
|---|---|---|
| A | Vessel inventory and piping class templates; filled where known, to be determined elsewhere | 2026-10-01 |
| B | Vacuum-jacketed line envelopes VJ_001 to VJ_005 added as FreeCAD envelopes (not fabricator isometrics); MAWP still to be determined | 2026-10-01 |
| C | Study MAWP and relief settings at or below MAWP; welding class notes; methanol piping class PC-11; stand-in ratings | 2026-10-01 |
| D | Rewritten to DOC_STYLE (AQS-DOC-002) and put in reading order; values unchanged | 2026-10-24 |

## 1. Purpose and scope

This document lists the plant's vessels and tanks with their pressure-code intent, and gives a piping class sheet for each fluid service. It moves compliance items CMP-ASM-01 and CMP-ASM-02 from "gap" towards "partial". Code intent for vessels designed in-house is now set by AQS-ASME-002 (`docs-authority/ASME_CODE_INTENT.md`, task X-MFG-40), which is generated from the design pressures in the plant graph; the inventory here is kept for its joint and evidence columns.

Table 1.1 states what the document covers.

Table 1.1. Scope

| In | Out |
|---|---|
| Named vessels / tanks / KO from the equipment lists and the weld register | Invented U-stamp numbers or PQRs |
| **Study** MAWP + relief set ≤ MAWP (labeled; §3.1 / §5) | Claiming PE-stamped final design P without AHJ |
| Piping class fluid / material / joint method from AQS-WLD-001 | Full qualified WPS/PQR package (still Gap — CMP-ASM-04); **class notes** OK |
| Code-vs-atmospheric classification study | PED / EU claims (CMP-ISO-07 N/A) |

## 2. Terms

Table 2.1 defines the code-intent classes used in the inventory. Other terms are defined in `docs-authority/GLOSSARY.md`, among them the maximum allowable working pressure (MAWP), pressure safety valve (PSV), welding procedure specification (WPS), procedure qualification record (PQR), nondestructive examination (NDE), postweld heat treatment (PWHT) and authority having jurisdiction (AHJ).

Table 2.1. Code-intent classes

| Class | Meaning |
|---|---|
| Atm | Atmospheric tank (sheet, rotomoulded or fusion-welded); not intended for ASME BPVC Section VIII |
| VIII-study | Candidate for ASME BPVC Section VIII once its design pressure and temperature are issued |
| In-house | Designed in-house (owner decision 2026-10-15: no bought skids); code intent set by task X-MFG-40 |
| TBD | Not yet classified |

## 3. Vessel and tank inventory

Table 3.1 lists each named vessel, tank and knock-out drum from the equipment lists and the weld register. When Rev A was issued, the only documented design pressure was the dryer jacket hydrostatic test at 6 bar (JW-012); section 4 adds study values for the others.

Table 3.1. Vessel and tank inventory

| Tag | Duty | Material / joint (known) | Design P | Design T | Code intent | Evidence |
|---|---|---|---|---|---|---|
| LEACH CSTR 1 | Salria leach | CPVC solvent (JW-001…005) | Atm / near-atm | Process TBD | Atm | AQS-WLD-001; AQS-NZ-001 |
| CSTR 2 weir | Float/sink | CPVC | Atm | TBD | Atm | JW-006 |
| CSTR 3 trough | Sink lift | CPVC | Atm | TBD | Atm | JW-007 |
| EW-1…9 | Electrowin cells | CPVC / rotomold | Atm | TBD | Atm | JW-008 |
| CRU | Chlorine recovery | CPVC + CS jacket bosses | Jacket TBD | TBD | Atm shell; jacket TBD | JW-026 |
| DRYER | Oil-line dryer | 304 trough; jacket | **Jacket hydro 6 bar** (known) | Q3 TBD | VIII-study (jacket) | JW-011/012 |
| INDUCTION PYROLYZER | Oil pyro shell | Ti Gr.2 GTAW | TBD | High-T TBD | VIII-study / SB-338 theme | JW-013/014 |
| QUENCH | Pyro quench | 304 GTAW | TBD | TBD | VIII-study | JW-015 |
| FRACTIONATOR | Oil cuts | 304 GTAW | TBD | TBD | In-house / VIII-study | JW-016 |
| AFTERBURNER | NCG burn | CS / 304 | Atm / slight draft | Q1 TBD | Atm / In-house | JW-017 |
| BURNOUT ROTARY | Glass burnout | SiC / Alloy 600 | TBD | TBD | In-house (X-MFG-40) | JW-018 |
| NaOH DIGEST | Glass digest | PP extrusion | Atm | TBD | Atm | JW-019 |
| BMED stack | Bipolar ED | PP fusion frames | Atm / low | TBD | Atm | JW-020 |
| ALK_SCRUBBER | Acid-gas scrub | PP/FRP | TBD | TBD | In-house (X-MFG-40) | JW-021 |
| ZnBr2 tanks | ESS electrolyte | PP fusion | Atm | Ambient | Atm | JW-025; NFPA 855 outdoor |
| Br₂ tower | ZnBr2 Br₂ | PVDF | TBD | Ambient | In-house / Atm | FLOW_BATTERY |
| ACID_POLISH_SCRUB | Polish after ALK_SCRUBBER | TBD (scrub train) | TBD | TBD | TBD | AQS-EQP-VENT-001 |
| ZNBR2_BR2_REGEN | Hold / regen | TBD | Atm class | Ambient | Atm | study 50–150 L |
| CRYO_AHU_COND | Condensate KO | TBD | TBD | Cryo-adjacent | TBD | AQS-EQP-VENT-001 |
| MET_SCRUB | Metal fume scrub | TBD | TBD | TBD | TBD | AQS-EQP-VENT-001 |
| COLD_BOX | Air sep / H₂ cold box | In-house cold box (X-MFG-33) | TBD | 77–90 K class | In-house (X-MFG-40) | AQS-CRY-002 |
| CRYO_H2 receiver | H₂ holdup | TBD | TBD | Cryo / gas | VIII-study / NFPA 2 | MAQ / kg TBD |
| CRYO O₂ / N₂ / CO₂ receivers | Product gas | TBD | TBD | Cryo / gas | VIII-study / NFPA 55 | AQS-EQP-CRY-001 |
| ROOF_TANK | Clean tower water | Noncombustible tank | Atm | Ambient | Atm | AQS-BLD-001 |
| CATCH_TANK | Lower reservoir | Noncombustible | Atm | Ambient | Atm | AQS-BLD-001 |
| POTABLE_TANK | Remin holdup | TBD | Atm | Ambient | Atm | AQS-EQP-HAB-001 |
| FAB_UPW_TANK | Fab loop | TBD | Atm / low | Ambient | Atm | AQS-EQP-FAB-UPW-001 |
| FISH_TANK | Aquaculture | PP | Atm | Ambient | Atm | AQS-EQP-FRM-001 |
| FARM_SUMP | Nutrient sump | Double-wall intent | Atm | Ambient | Atm | AQS-LIFE-001 |
| GEN_H2_BUFFER | Backup gen buffer | TBD | TBD | Ambient | TBD | AQS-EQP-GEN-001 |
| FC purge / buffer | FC H₂ side | TBD | TBD | Ambient | TBD | AQS-EQP-FC-001 |
| Fractionator cut tanks | Oil cuts | TBD | Atm / low | TBD | Atm / TBD | oil line |
| KO pots (scrub / quench) | Knockout | TBD | TBD | TBD | TBD | vent / oil |

## 4. Study maximum allowable working pressure

The study MAWP is set from the operating pressure intended by the process, typical ASME Section VIII and ASME B31.3 practice, and the rating of a stand-in vessel class. The study MAWP is at least the expected maximum operating pressure. A single relief valve is set at or below the MAWP, and the accumulation is limited to 10 % of MAWP or 3 psi (ASME BPVC Section VIII, UG-125). Normal operation is kept below about 90 % of the set pressure, following the practice of Section VIII Appendix M.

Table 4.1 gives the stand-in vessel ratings used. They are reference ratings, not bill-of-materials items.

Table 4.1. Stand-in vessel ratings

| Stand-in ID | Class | Cited rating | Use |
|---|---|---|---|
| SI-V-01 | Jacketed process vessel hydro | Dryer jacket **6 bar** hydro already in authority (JW-012) | Anchor for oil-line jackets |
| SI-V-02 | Shop air / gas receiver class | Typical ASME stamped air receiver **10–16 barg** MAWP class | CRYO_H2 / GEN / FC buffer study ceiling |
| SI-V-03 | Atmospheric FRP/PP tank | Atm + **0.5 barg** design contingency | Scrub / ZnBr2 / leach / MeOH tank |
| SI-V-04 | Methanol process reactor (literature) | Catalytic MeOH synth **50–100 bar** class (SI-MEOH-01 P-T) | MEOH_SYNTH study only |

Table 4.2 gives the study MAWP and relief setting for each vessel.

Table 4.2. Study MAWP and relief settings

| Tag | Expected max operating (study) | **Study MAWP** | Relief set (study) | Margin note | Code intent |
|---|---|---|---|---|---|
| LEACH CSTR 1…3 / EW-1…9 | Atm + static head | **Atm / 0.5 barg** | Conservation vent / overflow | Atm family | Atm |
| CRU shell | Atm | **Atm / 0.5 barg** | Vent to scrub | — | Atm |
| CRU jacket | Hot water / steam class TBD | **6 barg** study (peer dryer) | PSV @ **≤ 6 barg** | Set ≤ MAWP | VIII-study |
| DRYER jacket | ≤ 5 barg working | **6 barg** (known hydro) | PSV **5.4–6.0 barg** | Set ≤ MAWP; op ≤ 90% set | VIII-study |
| INDUCTION PYROLYZER | Near-atm process + N₂ | **1.0 barg** study | PSV **≤ 1.0 barg** + rupture as AHJ | Draft / slight + | VIII-study |
| QUENCH | Near-atm | **1.0 barg** | PSV ≤ MAWP | — | VIII-study |
| FRACTIONATOR | Distillation mild P | **3.0 barg** study | PSV ≤ 3.0 barg | In-house design (X-MFG-40) | In-house / VIII |
| AFTERBURNER | Draft / slight + | **Atm / 0.5 barg** | Explosion relief per NFPA 86 theme | Atm | Atm / In-house |
| ALK_SCRUBBER / ACID_POLISH | Fan discharge slight + | **1.0 barg** study | PSV / vent ≤ MAWP | Fan after pack | In-house |
| ZnBr2 tanks / Br₂ tower | Atm | **Atm / 0.5 barg** | Cons. vent | NFPA 855 outdoor | Atm |
| COLD_BOX (in-house, X-MFG-33) | TBD | **TBD (X-MFG-40)** | In-house PSVs sized to API 520 | — | In-house |
| CRYO_H2 receiver (gas) | Buffer 5–20 barg study | **20 barg** study | PSE/PSV **≤ 20 barg** | Under MAQ kg; SI-V-02 class | VIII-study / NFPA 2 |
| CRYO O₂ / N₂ / CO₂ receivers | 10–20 barg study | **20 barg** study | PSV ≤ MAWP | NFPA 55 | VIII-study |
| GEN_H2_BUFFER / FC purge buffer | ≤ 16 barg manifold | **16 barg** study | PSV ≤ 16 barg | Arrestor upstream consumer | VIII-study / TBD |
| ROOF_TANK / CATCH / FISH / FARM_SUMP | Atm | **Atm** | Overflow | — | Atm |
| **MEOH_SYNTH** | 50–100 bar class (stand-in SI-MEOH-01) | **110 barg** study (≈ 1.1× top of range) | PSV **≤ 110 barg**; multi-valve to 105% MAWP if needed | Op ≤ 90% set; **IEM soft path preferred** to avoid high-P at M1 pilot | VIII-study |
| **MEOH_TANK / DAY_TANK** | Atm liquid | **Atm / 1.5 barg** | Cons. vent + flame arrester; emergency vent | NFPA 30 | Atm / VIII-study if pressurized |
| MEOH_COND / MEOH_DIST | Distillation mild | **3.0 barg** study | PSV ≤ MAWP | — | VIII-study |
| KO pots (scrub / quench / MEOH_VENT_KO) | Slight + | **1.0 barg** | PSV ≤ MAWP | — | TBD / VIII-study |

The ion-exchange membrane methanol cell (MEOH_IEM_CELL) runs near ambient pressure. It is the preferred route for continuous duty at the M1 scale, so the 110 barg MAWP of the catalytic route remains an optional, scaled stand-in rather than the only route.

## 5. Relief devices

Each relief device is set at or below the MAWP of the vessel it protects, with accumulation limited as in section 4. Table 5.1 gives the study set pressures. They are not final until each orifice is sized and the AHJ accepts the design.

Table 5.1. Relief device schedule

| Tag | Protected equipment | Set P (study) | Basis | Status |
|---|---|---|---|---|
| PSV-DRY-JKT | DRYER jacket | **5.4 barg** (≤ 6 barg MAWP) | UG-125; SI-V-01 | Study |
| PSV-CRU-JKT | CRU jacket | **≤ 6 barg** | Peer dryer | Study |
| PSV-PYRO | INDUCTION PYROLYZER | **≤ 1.0 barg** | Study MAWP | Study |
| PSV-FRAC | FRACTIONATOR | **≤ 3.0 barg** | Study | Study |
| PSV-H2-RCV | CRYO_H2 receiver | **≤ 20 barg** | Study MAWP; NFPA 2 | Study |
| PSV-OX-RCV | CRYO_O2 / N2 / CO2 | **≤ 20 barg** | NFPA 55 | Study |
| PSV-GEN-BUF / PSV-FC-BUF | GEN/FC H₂ buffers | **≤ 16 barg** | Study | Study |
| PSV-MEOH-SYN | MEOH_SYNTH (if catalytic high-P used) | **≤ study MAWP** | UG-125; SI-V-04 | Study — prefer IEM soft |
| PSV-MEOH-DIST | MEOH_DIST / MEOH_COND | **≤ 3.0 barg** | Study | Study |
| PSE-H2 | H₂ receivers (supplement) | Per NFPA 2 | Dual protection theme | Study |
| ConsVent-MEOH | MEOH_TANK | Atm / 1.5 barg | NFPA 30 flame arrester | Study |
| Upset stack | Scrub residual | AHJ residual | AQS-VENT-001 | Partial |

## 6. Piping class sheets

Each class sheet covers one fluid service under ASME B31.3. The fluid, material and joint method come from AQS-WLD-001 and the nozzle schedules. Design pressure, temperature and the NDE class are to be determined unless a value is given.

### 6.1 PC-01: Salria / anolyte / acid (wetted)

Table 6.1. Piping class PC-01

| Field | Value |
|---|---|
| Class ID | PC-01 |
| Fluids | Salria, anolyte, acid etch, HDR_ETCH |
| Material | CPVC or PVDF (no metallic fillet on wetted face) |
| Joint | Solvent (CPVC Weld-On 724) or PVDF IR/butt |
| Design P / T | **TBD** |
| NDE / hydro | Visual + hydro (CSTR family); JW-001…009 |
| Notes | Process-header tees forbidden on life nozzles (AQS-NZ-002) |

### 6.2 PC-02: BMED BASE / digest / alkaline liquor

Table 6.2. Piping class PC-02

| Field | Value |
|---|---|
| Class ID | PC-02 |
| Fluids | BMED BASE, digest liquor, NaOH product branches |
| Material | PP |
| Joint | Fusion / extrusion weld |
| Design P / T | **TBD** |
| NDE | Spark / leak (JW-019/020) |

### 6.3 PC-03: Hydrogen gas

Table 6.3. Piping class PC-03

| Field | Value |
|---|---|
| Class ID | PC-03 |
| Fluids | HDR_H2, SHAFT_H2, CRYO_H2 branches, FC/GEN H₂ rough-ins |
| Material | 316L |
| Joint | GTAW, purge both sides; arrestor upstream of consumers |
| Design P / T | **TBD** (do not invent) |
| NDE | PT + purge record (JW-022) |
| Notes | Class I Div 2 Group B wiring theme — CMP-NEC-04 |

### 6.4 PC-04: Oil vapor / pyro jacket

Table 6.4. Piping class PC-04

| Field | Value |
|---|---|
| Class ID | PC-04 |
| Fluids | HDR_OIL_VAPOR; dryer / pyro jackets |
| Material | 304 inner; CS outer jacket (not welded to Ti pyro) |
| Joint | GTAW inner; CS fillet jacket only |
| Design P / T | Jacket: **6 bar hydro known on DRYER**; others TBD |
| NDE | Visual / hydro jacket (JW-012/023) |

### 6.5 PC-05: Titanium pyro shell interfaces

Table 6.5. Piping class PC-05

| Field | Value |
|---|---|
| Class ID | PC-05 |
| Fluids | Pyro process wall only |
| Material | Ti Grade 2 |
| Joint | GTAW ERTi-2; B16.5 NPS 12 Cl.150 theme on nozzle |
| Design P / T | **TBD** |
| NDE | 100 % PT + RT sample (JW-013/014) |

### 6.6 PC-06: UPW / potable / grey utility

Table 6.6. Piping class PC-06

| Field | Value |
|---|---|
| Class ID | PC-06 |
| Fluids | HDR_UPW, potable, grey, farm makeup |
| Material | PP-R / PP (see AQS-NZ-002) |
| Joint | Fusion / utility valves (non-vented) |
| Design P / T | Gravity-first roof; booster TBD |
| Notes | Never mix Salria / etch into this class |

### 6.7 PC-07: Q4 / chilled / heating water

Table 6.7. Piping class PC-07

| Field | Value |
|---|---|
| Class ID | PC-07 |
| Fluids | Q4 water to AHUs / HX |
| Material | **TBD** (CS or SS study) |
| Joint | **TBD** |
| Design P / T | **TBD** |
| Notes | No Q1 flue in life AHU |

### 6.8 PC-08: Cryogenic product gas (O₂ / N₂ / Ar / CO₂)

Table 6.8. Piping class PC-08

| Field | Value |
|---|---|
| Class ID | PC-08 |
| Fluids | HDR_O2 / HDR_N2 / HDR_CO2 / CRYO product |
| Material | **TBD** (cryo-rated SS study) |
| Joint | **TBD**; VJ (vacuum-jacketed) where required |
| Design P / T | **TBD** |
| Notes | VJ isometric schedule — see §6; NFPA 55 |

### 6.9 PC-09: Thermoplastic scrub / Br₂

Table 6.9. Piping class PC-09

| Field | Value |
|---|---|
| Class ID | PC-09 |
| Fluids | Br₂ header, scrub liquor, pregnant alkali |
| Material | PVDF / PP / FRP per unit |
| Joint | Fusion / vendor |
| Design P / T | **TBD** |
| Notes | CMP-ASM-03 thermoplastic joining procedure still Partial |

### 6.10 PC-10: Flue / acid-gas shaft (metallic duct)

Table 6.10. Piping class PC-10

| Field | Value |
|---|---|
| Class ID | PC-10 |
| Fluids | HDR_ACID_GAS, AFTERBURNER flue, SHAFT_OIL |
| Material | CS / 304 per JW-017/024 |
| Joint | SMAW / GMAW / GTAW as register |
| Design P / T | Draft / slight positive TBD |
| Notes | Atmosphere isolated from life core |

### 6.11 PC-11: Methanol liquid / vapor

Table 6.11. Piping class PC-11

| Field | Value |
|---|---|
| Class ID | PC-11 |
| Fluids | MEOH_TANK, day tank, MEOH_FC anode feed, crude methanol from MEOH_COND and MEOH_DIST |
| Material | 316L or MeOH-compatible SS; PTFE/FFKM seats; **no** Al / Zn / incompatible plastics on long-term wet MeOH |
| Joint | GTAW (WPS-N-09) or flanged; bonded/grounded |
| Design P / T | Tank: Atm / **1.5 barg** study; MEOH_DIST: **3 barg** study; SYNTH high-P: see §3.1 if used |
| NDE / hydro | Visual + hydro; LEL zoning |
| Notes | NFPA 30; flame arrestors on vents; HSE AQS-MeOH-001 §5 |

## 7. Welding class notes

Compliance item CMP-ASM-04 remains a gap: there are no stamped welding procedure packages from a fabricator. Table 7.1 gives welding class notes only, for use in a request for quotation or a procedure outline. The notes WPS-N-* are not qualified procedures. The fabricator shall submit qualified WPS and PQR documents under its own ASME stamp or AWS qualification.

Table 7.1. Welding class notes

| Class note ID | Material / joint | ASME IX theme | Suggested essential vars (outline) | Where used |
|---|---|---|---|---|
| WPS-N-01 | CPVC solvent Weld-On 724 | Not IX metal — thermoplastic procedure | Primer/cement brand; cure time; ambient T | PC-01; JW-001…009 |
| WPS-N-02 | PP fusion / extrusion | Thermoplastic | Heater T; force; bead; spark test | PC-02 / PC-09; BMED / digest |
| WPS-N-03 | 316L GTAW H₂ service | P-No 8 / A-No 8; ER316L | Purge O₂ < 0.1%; joint design; PWHT = none typical | PC-03; JW-022 |
| WPS-N-04 | 304 GTAW oil vapor / quench | P-No 8; ER308/308L | Purge; visual + PT sample | PC-04; JW-015/016 |
| WPS-N-05 | Ti Gr.2 GTAW ERTi-2 | P-No 51 theme; pure Ar | Trailing shield; 100% PT + RT sample | PC-05; JW-013/014 |
| WPS-N-06 | CS SMAW/GMAW flue duct | P-No 1 | Visual; paint after | PC-10 |
| WPS-N-07 | PVDF IR/butt | Thermoplastic | Bead geometry; spark | PC-09 Br₂ |
| WPS-N-08 | SS cryo / VJ attachments | P-No 8; cryo toughness note | Impact testing theme if AHJ; vendor VJ often owns weld | PC-08; VJ-001…005 |
| WPS-N-09 | MeOH stainless / compatible alloy GTAW | P-No 8; MeOH SCC awareness | Low-Cl consumables; no brass in MeOH | **PC-11** |

## 8. Vacuum-jacketed line schedule

Table 8.1 lists the vacuum-jacketed (VJ) cryogenic lines. Each has an envelope corridor in FreeCAD (`VJ_001` to `VJ_005` in `models/freecad/cryo.py`). The envelopes are not issued outside diameters or isometric drawings, and full fabricator isometrics are outside this document. Drawing numbers will be issued under AQS-ISO-* when the fabricator package starts. Compliance item CMP-NFPA-02 remains partial until those isometrics exist.

Table 8.1. Vacuum-jacketed lines

| ISO stub | Service | From → To | Priority |
|---|---|---|---|
| VJ-001 | LOX / GOX | COLD_BOX → HDR_O2 / life rack | High |
| VJ-002 | LIN / GN2 | COLD_BOX → HDR_N2 | High |
| VJ-003 | LCO2 / GCO2 | COLD_BOX → HDR_CO2 | Medium |
| VJ-004 | LH2 / GH2 (if liquefied path used) | COLD_BOX → CRYO_H2 | High — MAQ |
| VJ-005 | CRYO → FC / GEN H₂ rough-in | CRYO_H2 → yard UTIL_ROUGH_H2 | Medium |

## 9. Compliance matrix status

Tables 9.1 and 9.2 record how this document moved the compliance items in AQS-COMPL-001.

Table 9.1. Compliance items at Rev A and B

| ID | Before | After AQS-ASM-001 | Still open |
|---|---|---|---|
| CMP-ASM-01 | **Gap** | **Partial** (inventory + code flags; P/T TBD) | Datasheets; stamps |
| CMP-ASM-02 | Partial (TBD class specs) | **Partial** (PC-01…10 templates filled where known) | Numeric P/T; hydro procedures |
| CMP-ASM-03 | Partial | Partial | Formal thermoplastic procedure |
| CMP-ASM-04 | Gap | Gap | WPS/PQR outside repo |
| CMP-ASM-05 | Partial | Partial | Relief set pressures |

Table 9.2. Compliance items at Rev C

| ID | Before Rev C | After Rev C | Still open |
|---|---|---|---|
| CMP-ASM-01 | Partial | **Partial→stronger** (study MAWP table) | PE stamp; in-house design data |
| CMP-ASM-02 | Partial | Partial (PC-11 added; numeric study P/T) | Hydro procedures final |
| CMP-ASM-03 | Partial | Partial | Formal thermoplastic procedure binder |
| CMP-ASM-04 | Gap | Gap (**class notes** only — not PQRs) | Fabricator WPS/PQR outside repo |
| CMP-ASM-05 | Partial | **Partial→stronger** (relief schedule with set ≤ MAWP) | Final orifice sizing / AHJ |

## 10. Related documents

| Document | Role |
|---|---|
| `docs-authority/ASME_CODE_INTENT.md` (AQS-ASME-002) | Code intent of in-house vessels, from the graph |
| `docs-authority/COMPLIANCE_MATRIX.md` (AQS-COMPL-001) | Compliance items |
| `docs-authority/DOC_STYLE.md` (AQS-DOC-002) | Style |
