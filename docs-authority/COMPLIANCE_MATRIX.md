# Compliance matrix — design intent vs code themes

Document number: AQS-COMPL-001  
Renumbered 2026-10-15 from AQS-CMP-001 to clear a duplicate (AQS-REG-001).
Revision: D
Date: 2026-10-16  
Authority: AQS-AUTH-001, AQS-HSE-001, AQS-SITE-001, hub `ELECTRICAL.md`,
AQS-VENT-001, AQS-WLD-001, AQS-AUD-001.  
Jurisdiction assumed: USA (Dallas-class / Texas AHJ).  
**Not a PE stamp. Not a permit set.** Permits and clause quotations are not invented here.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: NFPA / NEC / OSHA / ASME / ISO theme map | 2026-10-01 |
| B | 1 | Wave 3: AQS-EGR-001 + AQS-ASM-001; CMP-ASM-01 Gap→Partial; egress annex | 2026-10-01 |
| C | 1 | Egress controlling-code rule; CRYO_EGRESS stubs; layout locks (PV/terrace/dock) | 2026-10-01 |
| D | 11 | X-COD-01: every row closed to a state with evidence (section 11) | 2026-10-16 |

Licence: CERN-OHL-S-2.0. `SCALE_M = 1.0`.

## 1. Purpose

Map Aqueous plant design **themes** to the codes already referenced in
authority docs. Status is design-intent only:

| Status | Meaning |
|---|---|
| **Compliant-intent** | Architecture and named controls aim to satisfy the theme; still needs AHJ / PE confirmation |
| **Partial** | Hooks, envelopes, or programs exist; quantitative calc, detail, or vendor proof missing |
| **Gap** | Theme acknowledged; no credible plant control yet |

Editions cited are those already locked in AQS-HSE-001 / ELECTRICAL /
SITE (notably NEC / NFPA family **2026** design basis). Confirm City of
Dallas amendments and AHJ edition before permit. Do **not** treat this
matrix as clause text.

## 2. Scope

In scope: campus fire / H₂ / gas / ESS, electrical yard (Sol-Ark, ZnBr2,
FC DC, GEN), OSHA egress & LEV hooks, ASME pressure/piping class notes,
relevant ISO process/safety themes.  
Out of scope: invented permits, PE stamps, root narrative folders.
Egress study annex: AQS-EGR-001 (tracked under AQS-SITE-001 §6). Out of scope still includes
(`06-energy-…` etc.).

Cross-refs: `docs-authority/HAZARD_SEPARATION.md`, `docs-authority/SITE_ACCESS.md`,
`ELECTRICAL.md` (hub), `docs-authority/VENT_CLOSURE.md`, `docs-authority/WELD_MAP.md`,
`docs-authority/DOC_STYLE.md` (AQS-DOC-002).

---

## 3. NFPA (fire, hydrogen, gases, ESS, life safety hooks)

| ID | Requirement theme | Edition / note | Aqueous control / doc | Status | Action |
|---|---|---|---|---|---|
| CMP-NFPA-01 | H₂ generation, storage, use; separation / detection | NFPA 2 (2026 design basis in AQS-HSE-001) | AQS-HSE-001; AQS-VENT-001; CRYO_EGRESS_DOOR/LOBBY stubs; CRYO_H2 MAQ cap | Compliant-intent | Confirm AHJ edition; shop-rate CRYO lobby; holdup kg TBD |
| CMP-NFPA-02 | Compressed / cryogenic gases; O₂ / N₂ / Ar product | NFPA 55 (2026 design basis) | AQS-CRY-002; AQS-EQP-CRY-001; FB_CRYO / FB_CRYO_PROCESS; no shared HVAC return | Compliant-intent | VJ isometrics + Stirling duties TBD |
| CMP-NFPA-03 | NEC cross-ref for classified areas / emergency power | NFPA 70 → see §4 | AQS-HSE-001 §4 Div system; ELECTRICAL.md SLD | Partial | Formal area classification drawings for permit |
| CMP-NFPA-04 | Means of egress concepts (travel, exits, discharge) | NFPA 101 + most-restrictive rule (AQS-EGR-001 §2.1) | AQS-EGR-001 Rev B; STAIR_*; CRYO_EGRESS_*; dock ELEV_DOCK | Partial | AHJ verify clear widths; CRYO lobby rating; NEC 700 fixtures |
| CMP-NFPA-05 | Oxidizer / corrosive occupancy & MAQ | NFPA 400 / mixed-use with IBC overlays | AQS-HSE-001 §§1–3; fire areas; FB_* ratings | Compliant-intent | Document control-area vs H upgrade when MAQ hit |
| CMP-NFPA-06 | Explosion prevention (H₂ < 25% LFL) | NFPA 69 | AQS-HSE-001 §6; detection trips rectifiers / H₂ isolation | Compliant-intent | Commissioning setpoints + SIL/reliability TBD |
| CMP-NFPA-07 | Flow-battery ESS outdoor preference | NFPA 855-2026 | ZnBr2 outdoor skid; FB_ESS; FLOW_BATTERY.md | Compliant-intent | BMS gateway + listing package with AHJ |
| CMP-NFPA-08 | Flammable liquids / oil line | NFPA 30 | OIL fire area; quench → afterburner; diked cuts | Compliant-intent | Indoor MAQ ledger for fractionator holdup |
| CMP-NFPA-09 | Sprinklers | NFPA 13 | AQS-HSE-001 §8: throughout except outdoor ESS / AHJ exceptions | Partial | Hydraulic calc + oxidizer-room special design |
| CMP-NFPA-10 | Electrical safety work practices (arc flash) | NFPA 70E | AQS-HSE-001 §7 (labels on 480 V); ELECTRICAL.md | Partial | Arc-flash study / labels after final SLD |

---

## 4. NEC / NFPA 70 (electrical yard, Sol-Ark, ZnBr2, FC DC, GEN)

| ID | Requirement theme | Edition / note | Aqueous control / doc | Status | Action |
|---|---|---|---|---|---|
| CMP-NEC-01 | Service, disconnects, overcurrent | NEC 2026 Art. 110 / 230 (theme) | ELECTRICAL.md: 480Y/277 → meter → 200 A fused disco → Sol-Ark GRID / ATS | Compliant-intent | Short-circuit / coordination study |
| CMP-NEC-02 | Interactive inverter / DER interconnection | UL 1741 SB / IEEE 1547 cited on Sol-Ark 60K | ELECTRICAL.md interconnect; `electrical_sld.png` | Compliant-intent | Utility interconnection agreement (site-specific) |
| CMP-NEC-03 | Energy storage / battery systems | NEC Art. 706 theme; NFPA 855 for ZnBr2 | ZnBr2 on BATT DC 160–700 V; outdoor ESS; CAN BMS gateway | Partial | Listing / BMS protocol proof; working clearances on yard plan |
| CMP-NEC-04 | Class I Div 2 Group B (H₂) wiring | NEC Art. 500 / 501 (Div; 505 optional) | AQS-HSE-001 §4 envelopes; XP / purged instruments on H₂ train | Partial | Seal-off / tray schedule on construction drawings |
| CMP-NEC-05 | Generators / transfer equipment | NEC Art. 445 / 700 theme | BACKUP_GEN on Sol-Ark **GEN** port; break-before-make ATS; diesel external contingency only | Partial | Vendor continuous kW; GEN set listing; exhaust scrub path S46 |
| CMP-NEC-06 | Fuel cell DC couple (not GEN AC) | NEC / product listing theme | FUEL_CELL → FC_DCDC → Sol-Ark **BATT DC**; ≠ BACKUP_GEN; AQS-FC-001 | Partial | FC continuous kW TBD; FC_DCDC listing in BATT window |
| CMP-NEC-07 | Emergency lighting / exit signs | NEC Art. 700 | AQS-HSE-001 §8 | Partial | Fixture schedule with egress annex |
| CMP-NEC-08 | Grounding / bonding / cable tray | NEC Art. 250 theme | `mfg_cable_tray.scad`, `freecad/pipe_services.py`; AQS-REM-001 §6.4 | Partial | Grounding electrode / equipotential plan |
| CMP-NEC-09 | Working space about equipment | NEC 110.26 theme | SITE yard CLEAR_* / KO_* stubs (AQS-SITE-001 §4) | Partial | Dimensioned yard plan for AHJ |

---

## 5. OSHA (egress, LEV / MET_SCRUB, H areas)

| ID | Requirement theme | Citation theme | Aqueous control / doc | Status | Action |
|---|---|---|---|---|---|
| CMP-OSH-01 | Means of egress | 29 CFR 1910.36 / .37 | AQS-EGR-001; AQS-SITE-001 §6; AQS-HSE-001 §8; hab path ≠ H areas | Partial | AHJ verify; outdoor discharge survey |
| CMP-OSH-02 | Walking-working surfaces | 1910.22 / .29 | AQS-HSE-001 §7 mezzanine guardrails | Partial | Guardrail schedule on life / shop MEP |
| CMP-OSH-03 | Permit-required confined spaces | 1910.146 | CSTR 1, fractionator, scrubber vessels listed | Partial | Written PRCS program + permits |
| CMP-OSH-04 | LOTO | 1910.147 | Rectifiers, shredder, pyro, MET_MELT, Sol-Ark | Partial | Energy-isolation procedures |
| CMP-OSH-05 | Respiratory protection | 1910.134 | Salria / Cl₂ / Br₂ tasks | Partial | IH survey + written program |
| CMP-OSH-06 | Hazard communication | 1910.1200 | SDS at gate; AQS-HSE-001 §2 incompatibles | Compliant-intent | Keep SDS set current with chemistry locks |
| CMP-OSH-07 | Local exhaust / process ventilation | 1910.94 / industry LEV practice | Hoods → HDR_*; MET_AHU → MET_SCRUB (S71–S72); ACID_POLISH; CRYO_AHU_COND; AQS-VENT-001 | Partial | Capture velocities / duct balances (study duties exist; vendor curves TBD) |
| CMP-OSH-08 | PSM threshold awareness | 1910.119 | AQS-HSE-001 §3 inventory caps intentionally under triggers | Compliant-intent | Re-check if CRYO_H2 / Br₂ holdup grows |
| CMP-OSH-09 | Electrical / arc flash | 1910.303 / .305 / .333 + 70E | AQS-HSE-001 §7 | Partial | Same as CMP-NFPA-10 / CMP-NEC-* |
| CMP-OSH-10 | Machine guarding / noise | 1910.212 / .219 / .95 | Shredder / induction called out | Partial | Guarding drawings + noise survey |

---

## 6. ASME (pressure vessels / piping)

| ID | Requirement theme | Edition / note | Aqueous control / doc | Status | Action |
|---|---|---|---|---|---|
| CMP-ASM-01 | Pressure vessels (stamp / U-stamp class) | ASME BPVC Sec. VIII theme | AQS-ASM-001 vessel inventory (Atm / VIII-study / Vendor / TBD); P/T mostly TBD | **Partial** | Issue design P/T datasheets; U-stamp where required |
| CMP-ASM-02 | Process piping metallic | ASME B31.3 theme | AQS-ASM-001 PC-01…10 templates; materials from AQS-WLD-001; P/T TBD | **Partial** | Numeric P/T; hydro procedures |
| CMP-ASM-03 | Nonmetallic / thermoplastic piping | B31.3 nonmetallic / manufacturer rules | Salria CPVC/PVDF; BMED PP fusion (AQS-WLD-001) | Partial | Formal thermoplastic joining procedure + hydro |
| CMP-ASM-04 | Weld map / WPS / PQR | ASME IX / AWS themes | AQS-WLD-001 is joint **register only** — explicitly not stamped | Gap | Fabricator WPS/PQR package outside this repo |
| CMP-ASM-05 | Relief / overpressure | BPVC / B31.3 + process relief practice | FAB/CRY relief noted Wave 1; upset stacks AHJ residuals (AQS-VENT-001) | Partial | Relief device schedule with set pressures |

**NOTE:** Where piping class or MAWP is not detailed in authority docs,
status is **TBD / Gap** — class ratings are not assigned without verified basis.

---

## 7. ISO (process / safety — applicability)

| ID | Theme | Typical standard (reference only) | Aqueous relevance | Status | Action |
|---|---|---|---|---|---|
| CMP-ISO-01 | Quality / document control | ISO 9001 | House style AQS-DOC-002; doc numbers / revs | Partial | Apply style to authority hub; not a certified QMS |
| CMP-ISO-02 | Occupational H&S management | ISO 45001 | Complements OSHA hooks; not adopted as system | Gap | Optional management-system decision — not claimed |
| CMP-ISO-03 | Risk / HAZOP-style process safety | ISO 31000 / IEC 61511 themes | Inventory caps, Class I envelopes, vent closure | Partial | Formal HAZOP / LOPA before construction |
| CMP-ISO-04 | Environmental management | ISO 14001 | Closed vent / scrub end states; no outdoor dump intent | Partial | Optional EMS; AEROD/site modeling deferred |
| CMP-ISO-05 | Hydrogen technologies vocabulary / safety | ISO/TR 15916 & related H₂ docs | Aligns with NFPA 2 design intent; not primary US code | Partial | Prefer NFPA 2/55 for AHJ; use ISO as reference only |
| CMP-ISO-06 | Cleanrooms / fab airborne | ISO 14644 | Wafer fab H-5 analog; UPW / wet benches | Partial | Cleanliness class TBD if fab tooling proceeds |
| CMP-ISO-07 | Pressure equipment (EU) | PED / ISO vessel norms | **Not applicable** as primary US design code | Gap / N/A | US = ASME; do not claim PED |

Do **not** claim ISO certification. Prefer US NFPA / NEC / OSHA / ASME
for permit. ISO rows are applicability mapping only.

---

## 8. Gap count (this Rev B)

| Status | Count |
|---|---|---|
| Compliant-intent | 10 |
| Partial | 26 |
| Gap (incl. N/A recorded as gap) | 4 |
| **Total rows** | **39** |

**Gap IDs:** CMP-ASM-04, CMP-ISO-02, CMP-ISO-07 (N/A primary), and
remaining gaps above. CMP-ASM-01 moved Gap → Partial (inventory
issued; MAWP still TBD). CMP-NFPA-04 / CMP-OSH-01 remain Partial with
AQS-EGR-001 study annex (AHJ verify).

Primary construction blockers now: AHJ verification of egress, vessel
MAWP / relief set pressures, vendor nameplates.

### 8.1 Blocks design-freeze language (pointer)

Formal PE stamp / permits remain **out of scope**. The
following still **block “design freeze” / AQS-MVS-001 freeze
language** until evidence tables exist — checklist owned by planning
`MVS_GAP_AUDIT.md` (AQS-MVS-GAP-001) §4.8; PE stamps and vendor
nameplates are not fabricated to clear them:

| Blocker class | CMP / EGR refs | Study status |
|---|---|---|
| AHJ egress clear widths / CRYO lobby | CMP-NFPA-04, CMP-OSH-01; AQS-EGR-001 | Partial |
| Controlling code edition | §2; AQS-EGR-001 §2.1 | Study |
| Vessel MAWP / relief set pressures | CMP-ASM-01/05; AQS-ASM-001 | TBD / Partial |
| Vendor nameplates (GEN/FC/ORC/CRYO/MFG/ZnBr₂) | AQS-AUD-001; AQS-REQ-KW-001 | Study / TBD |
| Arc-flash / sprinkler hydraulic | CMP-NEC / CMP-NFPA-09/10 | Partial |
| Area classification drawings | CMP-NFPA-03 | Partial |
| CRYO holdup vs MAQ | CMP-NFPA-01 | Study |
| SITE_LAT / potable VCD·remin | seed / AQS-WTR-001 | Unknown / Missing |

---

## 9. Cross-ref updates (Wave 2)

| Doc | Update |
|---|---|
| AQS-HSE-001 | §10 pointer to this matrix; LEV / MET_SCRUB row explicit |
| AQS-SITE-001 | §6 points here for compliance tracking |
| `ELECTRICAL.md` | Header + CMP-NEC-* pointer |
| AQS-AUTH-001 | Lists AQS-CMP-001 / AQS-DOC-002 |

## 10. Sync

Canonical in this tree: `docs-authority/COMPLIANCE_MATRIX.md`

## 11. Closure per item (X-COD-01, rev D)

Generated by `docs-authority/_compliance.py`. States: Closed (study) = evidence exists in a generated document, AHJ/PE confirmation still applies; Open (design) = deliverable missing, closing task named; Open (external) = site, AHJ, utility, fire engineer or physical test; Open (owner) = programme or management-system decision.

| ID | Evidence | State | Remaining |
|---|---|---|---|
| CMP-NFPA-01 | AQS-SAF-004 relief; AQS-SAF-005 flame and H2 detection, water spray, auto depressuring; AQS-HSE-001 | Closed (study) | AHJ edition |
| CMP-NFPA-02 | AQS-DUTY-069 cold box (no cryogenic column); AQS-SAF-004/005 receivers | Closed (study) | - |
| CMP-NFPA-03 | AQS-HSE-001 envelopes | Open (design) | X-ELS-09 area classification drawings |
| CMP-NFPA-04 | AQS-EGR-001, AQS-EGR-002; AQS-BLD-014 reservoir storeys (maintenance access, stairs to roof) | Closed (study) | AHJ clear widths |
| CMP-NFPA-05 | AQS-BLD-011 incompatible storage separation and quantities | Closed (study) | - |
| CMP-NFPA-06 | ess_tf purge at 25 % LFL; AQS-SAF-005 detector setpoints 10 % alarm, 25 % trip | Open (design) | X-SAF-01 HAZOP then X-CTL-03 SIF/SIL |
| CMP-NFPA-07 | FLOW_BATTERY.md, AQS-SAF-005 (NFPA 855 detection row) | Closed (study) | listing with the AHJ |
| CMP-NFPA-08 | OIL fire area; AQS-SAF-005 L0 EH1 | Open (design) | indoor NFPA 30 quantity ledger for the fractionator hold-up (X-SAF-09) |
| CMP-NFPA-09 | AQS-SAF-005 density/area demand, 451 m3 gravity reserve, NFPA 20 pump | Open (external) | hydraulic calculation from the riser by the fire engineer of record |
| CMP-NFPA-10 | AQS-ELEC-006 protection and coordination | Closed (study) | labels after the final one-line |
| CMP-NEC-01 | AQS-ELEC-002 one-line; AQS-ELEC-006 coordination | Closed (study) | - |
| CMP-NEC-02 | AQS-ELEC-002; IEEE 1547 / UL 1741 SB basis | Open (external) | utility interconnection agreement |
| CMP-NEC-03 | AQS-ELEC-002; AQS-BLD-012 working space | Closed (study) | - |
| CMP-NEC-04 | AQS-HSE-001 envelopes | Open (design) | X-ELS-09 (seal-offs and tray schedule follow) |
| CMP-NEC-05 | AQS-ELEC-003 load list (continuous kW from need); AQS-ELEC-002; AQS-OPS-002 NFPA 110 tests | Closed (study) | - |
| CMP-NEC-06 | AQS-ELEC-002 FC on the DC bus | Closed (study) | - |
| CMP-NEC-07 | AQS-HSE-001 section 8 | Open (design) | emergency lighting fixture schedule (X-THM-02 / X-DWG) |
| CMP-NEC-08 | AQS-ELEC-005 grounding and bonding | Closed (study) | - |
| CMP-NEC-09 | AQS-BLD-012 NEC 110.26 working-space check | Closed (study) | - |
| CMP-OSH-01 | as CMP-NFPA-04 | Closed (study) | AHJ |
| CMP-OSH-02 | AQS-BLD-012 ISO 14122-2 walkways | Open (design) | guardrail schedule on the level drawings |
| CMP-OSH-03 | AQS-OPS-002 lists confined spaces (reservoir cells, vessels) | Open (owner) | written permit-space programme (X-OPS-01) |
| CMP-OSH-04 | AQS-OPS-002 maintenance tasks | Open (owner) | energy-isolation procedures (X-OPS-01) |
| CMP-OSH-05 | - | Open (owner) | industrial hygiene survey and written programme |
| CMP-OSH-06 | AQS-HSE-001 section 2 | Closed (study) | - |
| CMP-OSH-07 | AQS-DUTY-061 vent scrubber; house scrubbers on the graph | Closed (study) | capture velocity test at commissioning |
| CMP-OSH-08 | H2 inventory 17 kg against the 10,000 lb (4,536 kg) flammable threshold of 29 CFR 1910.119 App. A | Closed (study) | re-check if hold-ups grow |
| CMP-OSH-09 | as CMP-NFPA-10 | Closed (study) | - |
| CMP-OSH-10 | - | Open (design) | guarding drawings and noise survey |
| CMP-ASM-01 | AQS-ASME-002 code intent per unit from the graph design pressures; receivers to B31.3 (ID under 152 mm) | Closed (study) | PE review |
| CMP-ASM-02 | AQS-ASM-001 class sheets; design pressures from cases (A-M-174); AQS-QA-001 tests | Closed (study) | - |
| CMP-ASM-03 | AQS-WLD-002 WPS-03..07; AQS-QA-001 route R4 | Closed (study) | - |
| CMP-ASM-04 | AQS-WLD-002 WPS-01..08 and PQR tests | Open (external) | PQR coupons welded and tested (physical) |
| CMP-ASM-05 | AQS-SAF-004 relief register with set pressures; AQS-SAF-005 fire case | Closed (study) | - |
| CMP-ISO-01 | DOC_REGISTER; AQS-QA-001 | Closed (study) | not a certified QMS |
| CMP-ISO-02 | - | Open (owner) | ISO 45001 adoption decision |
| CMP-ISO-03 | inventory caps, relief and fire cases | Open (design) | X-SAF-01 HAZOP, LOPA |
| CMP-ISO-04 | closed vents and scrubbers | Open (owner) | ISO 14001 adoption decision |
| CMP-ISO-05 | NFPA 2 primary | Closed (study) | - |
| CMP-ISO-06 | wafer fab, UPW | Open (design) | cleanliness class with the fab tool set |
| CMP-ISO-07 | US basis is ASME | N/A | - |

Closed (study): 23, Open (design): 9, Open (owner): 5, Open (external): 3, N/A: 1 (of 41).
