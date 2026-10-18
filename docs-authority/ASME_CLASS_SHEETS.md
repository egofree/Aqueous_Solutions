# ASME vessel inventory & B31.3 piping class sheets (templates)

Document number: AQS-ASM-001  
Revision: C  
Date: 2026-10-01  
Authority: AQS-WLD-001, AQS-CMP-001 (CMP-ASM-*), AQS-EQP-* equipment
lists, AQS-VENT-001 / AQS-CRY-002 / AQS-WTR-001, AQS-MeOH-001,
AQS-REQ-KW-001, `cad/process/*`.  
**Not a PE stamp. Not a U-stamp package.** Study MAWP / relief below are
**labeled study requirements** from first principles + typical ASME
practice + stand-in vessel ratings — not purchased U-stamp data.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Vessel inventory + piping class templates; filled where known, TBD elsewhere | 2026-10-01 |
| B | Wave 4 | VJ_001…005 FreeCAD envelope stubs (not fabricator isos); MAWP still TBD | 2026-10-01 |
| C | Req fill | Study MAWP / relief ≤ MAWP margins; WPS class notes; MeOH PC-11; stand-ins | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001. `SCALE_M = 1.0`.

---

## 1. Purpose

Advance CMP-ASM-01 / CMP-ASM-02 from Gap/TBD toward **Partial** by
issuing (a) a plant vessel inventory with code vs non-code flags and
(b) piping class sheet templates keyed to fluids already locked in
AQS-WLD-001. Design pressure / temperature left **TBD** unless already
documented (e.g. dryer jacket hydro 6 bar).

## 2. Scope

| In | Out |
|---|---|
| Named vessels / tanks / KO from EQP lists + weld register | Fake U-stamp numbers / forged PQRs |
| **Study** MAWP + relief set ≤ MAWP (labeled; §3.1 / §5) | Claiming PE-stamped final design P without AHJ |
| Piping class fluid / material / joint method from AQS-WLD-001 | Full qualified WPS/PQR package (still Gap — CMP-ASM-04); **class notes** OK |
| Code-vs-atmospheric classification study | PED / EU claims (CMP-ISO-07 N/A) |

---

## 3. Vessel / tank inventory

Superseded for code intent by AQS-ASME-002 (`ASME_CODE_INTENT.md`, X-MFG-40), generated from the graph design pressures; the table below is kept for its joint and evidence columns.

Legend — **Code intent:**  
- **Atm** = atmospheric / sheet / rotomold / fusion tank (not Sec. VIII intent)  
- **VIII-study** = candidate for BPVC Sec. VIII when P/T issued  
- **In-house** = designed in-house (owner decision 2026-10-15: no bought skids); code intent set by X-MFG-40  
- **TBD** = not classified this pass

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
| ALK SCRUBBER | Acid-gas scrub | PP/FRP | TBD | TBD | In-house (X-MFG-40) | JW-021 |
| ZnBr2 tanks | ESS electrolyte | PP fusion | Atm | Ambient | Atm | JW-025; NFPA 855 outdoor |
| Br₂ tower | ZnBr2 Br₂ | PVDF | TBD | Ambient | In-house / Atm | FLOW_BATTERY |
| ACID_POLISH_SCRUB | Post-ALK polish | TBD (scrub train) | TBD | TBD | TBD | AQS-EQP-VENT-001 |
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

**Count this Rev A:** Atm **≈ 20** | VIII-study / Vendor **≈ 12** | TBD **≈ 10**  
Only **one** numeric design pressure is locked in authority docs today:
dryer jacket **6 bar** hydro (JW-012). All other P/T = **TBD**.

---

## 4. Piping class templates (B31.3 theme)

Fill **known** columns from AQS-WLD-001 / nozzle schedules. Leave P/T
and NDE class **TBD** unless noted.

### PC-01 — Salria / anolyte / acid (wetted)

| Field | Value |
|---|---|
| Class ID | PC-01 |
| Fluids | Salria, anolyte, acid etch, HDR_ETCH |
| Material | CPVC or PVDF (no metallic fillet on wetted face) |
| Joint | Solvent (CPVC Weld-On 724) or PVDF IR/butt |
| Design P / T | **TBD** |
| NDE / hydro | Visual + hydro (CSTR family); JW-001…009 |
| Notes | Process-header tees forbidden on life nozzles (AQS-NZ-002) |

### PC-02 — BMED BASE / digest / alkaline liquor

| Field | Value |
|---|---|
| Class ID | PC-02 |
| Fluids | BMED BASE, digest liquor, NaOH product branches |
| Material | PP |
| Joint | Fusion / extrusion weld |
| Design P / T | **TBD** |
| NDE | Spark / leak (JW-019/020) |

### PC-03 — Hydrogen gas

| Field | Value |
|---|---|
| Class ID | PC-03 |
| Fluids | HDR_H2, SHAFT_H2, CRYO_H2 branches, FC/GEN H₂ rough-ins |
| Material | 316L |
| Joint | GTAW, purge both sides; arrestor upstream of consumers |
| Design P / T | **TBD** (do not invent) |
| NDE | PT + purge record (JW-022) |
| Notes | Class I Div 2 Group B wiring theme — CMP-NEC-04 |

### PC-04 — Oil vapor / pyro jacket

| Field | Value |
|---|---|
| Class ID | PC-04 |
| Fluids | HDR_OIL_VAPOR; dryer / pyro jackets |
| Material | 304 inner; CS outer jacket (not welded to Ti pyro) |
| Joint | GTAW inner; CS fillet jacket only |
| Design P / T | Jacket: **6 bar hydro known on DRYER**; others TBD |
| NDE | Visual / hydro jacket (JW-012/023) |

### PC-05 — Titanium pyro shell interfaces

| Field | Value |
|---|---|
| Class ID | PC-05 |
| Fluids | Pyro process wall only |
| Material | Ti Grade 2 |
| Joint | GTAW ERTi-2; B16.5 NPS 12 Cl.150 theme on nozzle |
| Design P / T | **TBD** |
| NDE | 100 % PT + RT sample (JW-013/014) |

### PC-06 — UPW / potable / grey utility

| Field | Value |
|---|---|
| Class ID | PC-06 |
| Fluids | HDR_UPW, potable, grey, farm makeup |
| Material | PP-R / PP (see AQS-NZ-002) |
| Joint | Fusion / utility valves (non-vented) |
| Design P / T | Gravity-first roof; booster TBD |
| Notes | Never mix Salria / etch into this class |

### PC-07 — Q4 / chilled / heating water

| Field | Value |
|---|---|
| Class ID | PC-07 |
| Fluids | Q4 water to AHUs / HX |
| Material | **TBD** (CS or SS study) |
| Joint | **TBD** |
| Design P / T | **TBD** |
| Notes | No Q1 flue in life AHU |

### PC-08 — Cryogenic product gas (O₂ / N₂ / Ar / CO₂)

| Field | Value |
|---|---|
| Class ID | PC-08 |
| Fluids | HDR_O2 / HDR_N2 / HDR_CO2 / CRYO product |
| Material | **TBD** (cryo-rated SS study) |
| Joint | **TBD**; VJ (vacuum-jacketed) where required |
| Design P / T | **TBD** |
| Notes | VJ isometric schedule — see §6; NFPA 55 |

### PC-09 — Thermoplastic scrub / Br₂

| Field | Value |
|---|---|
| Class ID | PC-09 |
| Fluids | Br₂ header, scrub liquor, pregnant alkali |
| Material | PVDF / PP / FRP per unit |
| Joint | Fusion / vendor |
| Design P / T | **TBD** |
| Notes | CMP-ASM-03 thermoplastic joining procedure still Partial |

### PC-10 — Flue / acid-gas shaft (metallic duct)

| Field | Value |
|---|---|
| Class ID | PC-10 |
| Fluids | HDR_ACID_GAS, AFTERBURNER flue, SHAFT_OIL |
| Material | CS / 304 per JW-017/024 |
| Joint | SMAW / GMAW / GTAW as register |
| Design P / T | Draft / slight positive TBD |
| Notes | Atmosphere isolated from life core |

---

## 5. Relief device schedule

See **§5.1** for study set pressures (Rev C). Placeholder rows retired.
Do not treat study sets as PE-final without orifice calc + AHJ.

---

## 6. Vacuum-jacketed (VJ) isometric schedule

Full fabricator isometrics remain **out**. Doc schedule + FreeCAD **envelope corridors** (`VJ_001`…`VJ_005` in `freecad/cryo.py`) issued Wave 4. Envelopes ≠ issued OD / iso drawings:

| ISO stub | Service | From → To | Priority |
|---|---|---|---|
| VJ-001 | LOX / GOX | COLD_BOX → HDR_O2 / life rack | High |
| VJ-002 | LIN / GN2 | COLD_BOX → HDR_N2 | High |
| VJ-003 | LCO2 / GCO2 | COLD_BOX → HDR_CO2 | Medium |
| VJ-004 | LH2 / GH2 (if liquefied path used) | COLD_BOX → CRYO_H2 | High — MAQ |
| VJ-005 | CRYO → FC / GEN H₂ rough-in | CRYO_H2 → yard UTIL_ROUGH_H2 | Medium |

Issue drawing numbers under AQS-ISO-* when fabricator pack starts.
CMP-NFPA-02 remains Partial (fabricator VJ isometrics TBD; envelopes only).

---

## 7. CMP matrix movement

| ID | Before | After AQS-ASM-001 | Still open |
|---|---|---|---|
| CMP-ASM-01 | **Gap** | **Partial** (inventory + code flags; P/T TBD) | Datasheets; stamps |
| CMP-ASM-02 | Partial (TBD class specs) | **Partial** (PC-01…10 templates filled where known) | Numeric P/T; hydro procedures |
| CMP-ASM-03 | Partial | Partial | Formal thermoplastic procedure |
| CMP-ASM-04 | Gap | Gap | WPS/PQR outside repo |
| CMP-ASM-05 | Partial | Partial | Relief set pressures |

---



---

## 3.1 Study MAWP fill (labeled — Rev C)

**Method:** operating pressure from process intent + typical ASME VIII /
B31.3 practice + stand-in vessel class. **Study MAWP ≥ expected max
operating.** Relief set **≤ MAWP** (UG-125: single PSV set ≤ MAWP;
accumulation ≤ 10% MAWP / 3 psi). Normal operating ≤ ~90% of set
(Appendix M practice theme).

**Stand-in vessel ratings (not BOM):**

| Stand-in ID | Class | Cited rating | Use |
|---|---|---|---|
| SI-V-01 | Jacketed process vessel hydro | Dryer jacket **6 bar** hydro already in authority (JW-012) | Anchor for oil-line jackets |
| SI-V-02 | Shop air / gas receiver class | Typical ASME stamped air receiver **10–16 barg** MAWP class | CRYO_H2 / GEN / FC buffer study ceiling |
| SI-V-03 | Atmospheric FRP/PP tank | Atm + **0.5 barg** design contingency | Scrub / ZnBr2 / leach / MeOH tank |
| SI-V-04 | Methanol process reactor (literature) | Catalytic MeOH synth **50–100 bar** class (SI-MEOH-01 P-T) | MEOH_SYNTH study only |

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
| ALK SCRUBBER / ACID_POLISH | Fan discharge slight + | **1.0 barg** study | PSV / vent ≤ MAWP | Fan after pack | In-house |
| ZnBr2 tanks / Br₂ tower | Atm | **Atm / 0.5 barg** | Cons. vent | NFPA 855 outdoor | Atm |
| COLD_BOX (in-house, X-MFG-33) | TBD | **TBD (X-MFG-40)** | In-house PSVs sized to API 520 | — | In-house |
| CRYO_H2 receiver (gas) | Buffer 5–20 barg study | **20 barg** study | PSE/PSV **≤ 20 barg** | Under MAQ kg; SI-V-02 class | VIII-study / NFPA 2 |
| CRYO O₂ / N₂ / CO₂ receivers | 10–20 barg study | **20 barg** study | PSV ≤ MAWP | NFPA 55 | VIII-study |
| GEN_H2_BUFFER / FC purge buffer | ≤ 16 barg manifold | **16 barg** study | PSV ≤ 16 barg | Arrestor upstream consumer | VIII-study / TBD |
| ROOF_TANK / CATCH / FISH / FARM_SUMP | Atm | **Atm** | Overflow | — | Atm |
| **MEOH_SYNTH** | 50–100 bar class (stand-in SI-MEOH-01) | **110 barg** study (≈ 1.1× top of range) | PSV **≤ 110 barg**; multi-valve to 105% MAWP if needed | Op ≤ 90% set; **IEM soft path preferred** to avoid high-P at M1 pilot | VIII-study |
| **MEOH_TANK / DAY_TANK** | Atm liquid | **Atm / 1.5 barg** | Cons. vent + flame arrester; emergency vent | NFPA 30 | Atm / VIII-study if pressurized |
| MEOH_COND / DIST | Distillation mild | **3.0 barg** study | PSV ≤ MAWP | — | VIII-study |
| KO pots (scrub / quench / MEOH_VENT_KO) | Slight + | **1.0 barg** | PSV ≤ MAWP | — | TBD / VIII-study |

**IEM soft path note:** MEOH_IEM_CELL is intended near-ambient /
low-P electrochemical — prefer this for M1 continuous duty so the
110 barg catalytic MAWP remains a **optional scaled stand-in**, not the
only path.

---

## 5.1 Relief device schedule (study fill — Rev C)

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
| PSV-MEOH-DIST | MEOH_DIST / COND | **≤ 3.0 barg** | Study | Study |
| PSE-H2 | H₂ receivers (supplement) | Per NFPA 2 | Dual protection theme | Study |
| ConsVent-MEOH | MEOH_TANK | Atm / 1.5 barg | NFPA 30 flame arrester | Study |
| Upset stack | Scrub residual | AHJ residual | AQS-VENT-001 | Partial |

**Rule:** Relief set pressure **≤ MAWP** for each protected vessel.
Accumulation limited per UG-125 (≤ 10% MAWP / 3 psi theme).

---

## 5.2 WPS / PQR class notes (not qualified PQRs)

CMP-ASM-04 remains **Gap** for stamped fabricator WPS/PQR packages.
This section issues **welding class notes** only — suitable for RFQ /
procedure outline, **not** fake qualified PQRs.

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

Fabricator shall submit **real** WPS/PQR under their ASME stamp /
AWS qualification. Do not treat WPS-N-* as qualified procedures.

---

### PC-11 — Methanol liquid / vapor (new Rev C)

| Field | Value |
|---|---|
| Class ID | PC-11 |
| Fluids | MEOH_TANK, day tank, MEOH_FC anode feed, crude MeOH from COND/DIST |
| Material | 316L or MeOH-compatible SS; PTFE/FFKM seats; **no** Al / Zn / incompatible plastics on long-term wet MeOH |
| Joint | GTAW (WPS-N-09) or flanged; bonded/grounded |
| Design P / T | Tank: Atm / **1.5 barg** study; DIST: **3 barg** study; SYNTH high-P: see §3.1 if used |
| NDE / hydro | Visual + hydro; LEL zoning |
| Notes | NFPA 30; flame arrestors on vents; HSE AQS-MeOH-001 §5 |

---

## 7. CMP matrix movement (Rev C update)

| ID | Before Rev C | After Rev C | Still open |
|---|---|---|---|
| CMP-ASM-01 | Partial | **Partial→stronger** (study MAWP table) | PE stamp; in-house design data |
| CMP-ASM-02 | Partial | Partial (PC-11 added; numeric study P/T) | Hydro procedures final |
| CMP-ASM-03 | Partial | Partial | Formal thermoplastic procedure binder |
| CMP-ASM-04 | Gap | Gap (**class notes** only — not PQRs) | Fabricator WPS/PQR outside repo |
| CMP-ASM-05 | Partial | **Partial→stronger** (relief schedule with set ≤ MAWP) | Final orifice sizing / AHJ |


## 8. Sync

Canonical in this tree: `docs-authority/ASME_CLASS_SHEETS.md`  
