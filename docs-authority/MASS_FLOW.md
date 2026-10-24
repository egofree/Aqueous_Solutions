# Mass-flow claim status

Document number: AQS-MF-001  
Revision: J
Date: 2026-10-01  
Authority: AQS-BLD-001 + AQS-STR-001 + AQS-HSE-001

> **WP-Ap3 derived sync:** Generated excerpt lives at
> `flow_graph/derived/MASS_FLOW_DERIVED.md` (from `plant_flow_graph.json`
> via `flow_graph/export_authority_md.py`). This CAD file remains the human
> claim-status narrative sync target (hybrid — not overwritten wholesale).
> Prefer `derived/` as generated; see `flow_graph/derived/SYNC_POINTER.md`.
> Do not invent DOCK S## or fill null placeholder rates.
>
> **Graph Rev M (2026-10-08):** every edge is rated and every node balance closes (AQS-DUTY-011, `REV_M_CLOSURE_DUTY.md`). New streams S91–S102 and IA-BMED-05..10; S05, S86, S87, S88 retired; S16 is harvest rinse liquor (12.6 kg/d); S68 is CRYO AHU coil condensate. Rates in `flow_graph/derived/MASS_FLOW_DERIVED.md` govern over the claim-status rows below.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue | 2026-09-27 |
| B | 1 | S25–S30 water purification (AQS-WTR-001); VCD ≠ roof–catch | 2026-09-27 |
| C | 1 | S31–S39 fab wet-reagent forks (qualitative) | 2026-09-27 |
| D | 1 | S40–S42 terrace irrigation / return (AQS-TRR-001) | 2026-09-27 |
| E | 1 | S43–S48 geothermal / backup genset (AQS-PWR-001) | 2026-09-27 |
| F | 1 | S49–S53 PEM fuel cell (AQS-FC-001); S24 closing via FC+GEN | 2026-09-28 |
| G | 1 | S54–S56 CRYO Q4 / dedicated cool / room vent (AQS-CRY-002) | 2026-09-28 |
| H | 1 | S57–S63 metal forming (AQS-MFG-MET-001) | 2026-09-28 |
| I | 1 | Vent closure S64–S72 (AQS-VENT-001); reclassify former open dumps | 2026-09-28 |

Professional engineering note: “closed” here means the design routes
the stream to a named recovery or recycle unit with a locked header.
It is not a measured plant balance. Per AQS-VENT-001, free outdoor dump
is **not** design intent — former vents are **Unclosed → Closure
required** (scrub+regen or CRYO) until hardware and permits finish the
path. Contingency / upset relief may remain for AHJ and life safety.

Sheet: `mass_flow_pfd.png` (generator `pfd_scripts/mass_flow_pfd.py`).

---

## 1. Legend

| Tag | Meaning |
|---|---|
| **Closed** | Routed to recovery / recycle; no intentional atmosphere discharge |
| **Claimed** | Design path exists; holdup / capture efficiency still to prove |
| **Partial** | Primary recovery path named and preferred; contingency relief may remain |
| **Closure required** | Unclosed — must finish scrub+regen or CRYO path (AQS-VENT-001); not “open by intent” |
| **Recapturable** | Legacy synonym for Closure required where hardware path already named |

---

## 2. Stream register S01–S72

| ID | Route (short) | Status | Notes |
|---|---|---|---|
| S01 | BMED / UPW → FARM, FAB, HAB (pre-remin) | Closed | HDR_UPW; air gap / RPZ at potable (S26) |
| S02 | CRYO O2 + GROW → HAB | Closed | HDR_O2; never tees HDR_H2 |
| S03 | CRYO N2 → FAB, FARM | Closed | HDR_N2 |
| S04 | CRYO CO2 + HAB AIR → FARM | Closed / Claimed | HDR_CO2; not raw flue |
| S05 | H2_DRYER → CRYO H2 or fuel | Claimed / Partial | Normal → S64 CRYO_H2; S24 contingency only |
| S06 | Q4 HVAC heat → FARM, HAB | Closed | Q4 water only into hab air |
| S07 | P-Al/Mg/Ca + BMED salts → NUTRIENT | Closed | tote / dose; no Salria in beds |
| S08 | Metals / silicate → FAB, MFG | Closed | crib |
| S09 | HCl / NaOH PRODUCT → bench, farm pH | Closed | pipe; no sewer |
| S10 | WET BENCH → REGEN LEACH | Closed | HDR_ETCH; no floor drain |
| S11 | GROW / GALLEY → HOPPER or OIL | Closed | HDR_ORG |
| S12 | HAB WASTE → SALT FEED / dose / HOPPER | Closed | HDR_GREY + HDR_ORG |
| S13 | FARM SUMP + HVAC condensate → VCD / polish / salt | Closed | HDR_GREY; VCD_FEED primary |
| S14 | GROW → HAB food | Closed | tote |
| S15 | GROW → HDR_O2 | Closed | photosynthetic O₂ |
| S16 | MFG scrap → HOPPER | Closed | no FR-4 to pyro |
| S17 | Power bus → loads | Closed | electric; Br₂ stays on ZnBr2 |
| S18 | AFTERBURNER / air → CRYO feed | Retired credit (Rev J) | Claim id only, 0 kg/d; afterburner CO₂ (15.0 kg/d) is counted on S67 and credited at CRYO_CO2 through S67B (12.75 kg/d); not acid-gas header |
| S19 | BAGHOUSE fines → CSTR 1 | Closed | claimed recycle |
| S20 | Loads → SOL_ARK bus | Closed | electric |
| S21 | ROOF TANK → HAB / FARM / UPW | Closed | clean tower water |
| S22 | ROOF → CATCH via HYDRO / penstock | Closed | SHAFT_PENSTOCK; clean only |
| S23 | CATCH → ROOF pump / UPW | Closed | same clean inventory |
| S24 | H2 overpressure → roof contingency | Partial | SHAFT_H2 relief only; normal = S64 → CRYO_H2 → S45/S49 (AQS-VENT-001) |
| S25 | VCD distillate → UPW POLISH | Closed | AQS-WTR-001 |
| S26 | REMIN → HAB potable taps | Closed | RPZ / air gap; not wet bench |
| S27 | FAB_UPW → WET_BENCH | Closed | > 18 MΩ·cm class (doc 03) |
| S28 | VCD brine → REGEN LEACH / SALT | Closed | not HDR_UPW |
| S29 | GREY_TREAT → VCD_FEED / SALT | Closed | not Salria / etch |
| S30 | BLACK_DIGEST → NUTRIENT / SALT | Closed | solids not to VCD evaporators |
| S31 | WS_HF_ED → WET_BENCH (HF) | Closed / Claimed | AQS-EQP-FAB-RGN-001; ED regen path |
| S32 | WS_PEROX → WET_BENCH (H₂O₂) | Claimed | seed procure until electrosynth proven |
| S33 | WS_AMMONIA → WET_BENCH | Claimed | same |
| S34 | WS_NITRIC/PHOS → WET_BENCH | Claimed | etch suite |
| S35 | WS_KOH → bench / solar stub | Claimed | solar branch open |
| S36 | WS_DOPE → FAB_TOOL | Claimed | CRU migration + gas cabinets |
| S37 | WS_SLURRY → LAP_CMP | Claimed | glass silicate make-up |
| S38 | WS_SOLV → FAB_TOOL | Claimed | flammable; oil-line recover |
| S39 | spent slurry/solvent/PR → leach/oil | Closed | with S10 pattern; no floor drain |
| S40 | Roof surplus → terrace irrig | Closed | intermittent; clean only; AQS-TRR-001 |
| S41 | Terrace clean drain → CATCH | Closed | never process bund |
| S42 | Fertigated GH drain → HDR_GREY | Closed / Claimed | only if enclosed food option |
| S43 | GEO_GHEX ↔ GEO_HP | Closed | dedicated loop; not UPW |
| S44 | GEO_HP → Q4 | Closed | same Q4 rule as S06 |
| S45 | CRYO_H2 → BACKUP_GEN | Claimed / Partial | MAQ / NFPA 2; closes S64 with S49 |
| S46 | GEN exhaust → condensate / scrub | Claimed | H₂O primary; not S18 CO₂ |
| S47 | BACKUP_GEN → Sol-Ark GEN | Closed | electric; closes spare |
| S48 | GEO_ORC → Sol-Ark (stub) | Claimed | closure architecture: AC couple; rating TBD — no invent kW |
| S49 | CRYO_H2 → FUEL_CELL | Claimed / Partial | MAQ; PEM; isolated from S45; closes S64 with S45 |
| S50 | CRYO_O2 → FUEL_CELL | Claimed | oxidizer; never HDR_H2 |
| S51 | FUEL_CELL → Sol-Ark BATT DC | Closed | electric; ≠ GEN AC |
| S52 | FC product water → S13 class | Claimed | condensate; not potable w/o remin |
| S53 | FC_HX_Q4 → Q4 | Closed | same Q4 rule as S06 / S44 |
| S54 | CRYO_HX_Q4 → Q4 | Closed | warm residual only; peer to S06/S44/S53 |
| S55 | CRYO_DED_COOL loop | Closed | dedicated; not life AHU / UPW |
| S56 | CRYO_AHU residual → safe vent | Partial | After CRYO_AHU_COND (S70); never HAB return; not continuous dump |
| S57 | PROD_METALS / MET_MELT → forming | Closed | billet/melt/charge; not polymer |
| S58 | WIRE_DRAW → wire bin / crib | Closed | product wire |
| S59 | COLD_MILL → sheet bin / crib | Closed | product sheet |
| S60 | GAS_ATOMIZER → powder crib / FAB | Closed / Claimed | N₂ blanketed hold |
| S61 | Forming scrap → HOPPER / leach | Closed | S16 class; no FR-4 / pyro |
| S62 | MET_AHU → MET_SCRUB / BH (S71) | Partial / Claimed | dedicated aisle capture; never HAB return; not free outdoor dump |
| S63 | MET_HX_Q4 → Q4 | Closed | warm residual only; peer S06/S44/S53/S54 |
| S64 | H2_DRYER → CRYO_H2 | Partial | Normal H₂ path; closes continuous roof dump |
| S65 | ALK residual → ACID_POLISH_SCRUB | Partial / Claimed | Post-alkali polish feed; PFD path named |
| S66 | Acid polish / ALK liquor → CRU | Claimed | Regenerable scrub return |
| S67 | AFTERBURNER flue → FLUE_CAP / CRYO | Partial / Claimed | Extends S18; destruction upstream remains; PFD path named |
| S68 | Flue / AHU condensate → S13 class | Claimed | Not potable |
| S69 | ZNBR2_BR2_REGEN → pos. tank | Partial / Claimed | Br⁻ return; never CRU; PFD path named |
| S70 | CRYO_AHU_COND → COLD_BOX | Partial | Condensable return from S56 train; PFD path named |
| S71 | MET_AHU → MET_SCRUB / baghouse | Partial / Claimed | Capture train (feeds from S62); PFD path named |
| S72 | MET scrub / BH → CSTR / OIL / ORG | Claimed | Fines S19 class; mist to oil/org |


---

## 3. Process gas and scrubber paths (HSE)

Authority for end states: **AQS-VENT-001**. Free outdoor dump ≠ design intent.

| Path | Header / unit | Status | End state / discharge |
|---|---|---|---|
| Anode / CSTR hood | HDR_ACID_GAS → DEMISTER → ALK_SCRUBBER → ACID_POLISH_SCRUB | Closure required / Claimed | Liquor → CRU (S66); upset stack residual only |
| Cathode H₂ | HDR_H2 → arrestor → H2_DRYER → S64 CRYO_H2 | Partial | Consumers S45/S49; S24 roof = contingency only |
| Oil vapor | HDR_OIL_VAPOR → QUENCH → AFTERBURNER → FLUE_CAP / CRYO | Closure required / Claimed | Destruction + S67 CO₂ capture; S68 condensate |
| Dust | HDR_DUST → BAGHOUSE | Closed / Claimed | Fines to CSTR 1 (S19) |
| ZnBr2 Br₂ | ZNBR2_BR2_SCRUBBER → ZNBR2_BR2_REGEN | Closure required / Claimed | S69 Br⁻ → pos. tank; not CRU; no continuous dump |
| Hab / farm air | dedicated AHU | Closed vs process | No process-atmosphere duct |
| CRYO room | CRYO_AHU → CRYO_AHU_COND (S70) / S56 residual | Closure required / Partial | Condensables to CRYO; residual contingency; not HAB return |
| MFG metal aisle | MET_AHU → MET_SCRUB / BH (S71–S72) | Closure required / Claimed | Scrub/baghouse returns; not HAB return |

---

## 4. Closed / claimed liquid loops

| Loop | Path | Status |
|---|---|---|
| Scrubber → CRU | alkali blowdown / salt to CRU | Claimed |
| Baghouse → CSTR | fines S19 | Closed |
| BMED ↔ CRU | acid / base / chlorate regen | Closed |
| Etch return | HDR_ETCH → REGEN LEACH | Closed |
| Grey / UPW | HDR_GREY → treat → VCD / salt; HDR_UPW out; S26 potable | Closed |
| Roof–catch clean water | S21–S23, SHAFT_PENSTOCK | Closed |
| VCD regeneration | S13/S29 → VCD → S25/S28 (AQS-WTR-001) | Closed / Claimed |
| Fab wet reagents | WS_* → S31–S38 → bench/tool; S10/S39 return | Claimed |
| Terrace overflow irrig | S40 → bands; S41 → CATCH; S42 fertigated → grey | Closed / Claimed |
| Geothermal loop | S43 ↔ GEO_HP; S44 → Q4 | Closed |
| Backup GEN AC | S47 → Sol-Ark GEN | Closed |
| GEN exhaust / H₂ fuel | S45 / S46 | Claimed |
| Fuel-cell DC | S51 → Sol-Ark BATT DC | Closed |
| FC H₂ / O₂ / heat / water | S49 / S50 / S53 / S52 | Claimed / Closed (S51/S53) |
| CRYO warm reject → Q4 | S54 via CRYO_HX_Q4 | Closed |
| CRYO dedicated cool | S55 | Closed |
| Metal forming products | S57–S60 | Closed / Claimed |
| Metal forming scrap | S61 → HOPPER | Closed |
| MET_HX_Q4 → Q4 | S63 | Closed |
| EW liquor cascade | CSTR 1 → EW-1…9 → precip / polish | Closed |
| Float / sink liquor | dewater return → CSTR 1 | Closed |

---

## 5. Former opens → Partial / Claimed (AQS-VENT-001)

**None are “open by intent.”** PFD architecture names scrub+regen or CRYO returns.
Study duties / Nm³/h / kW bounds issued in AQS-EQP-VENT-001 Rev B and AQS-AUD-001 Rev D (labeled study estimates — not vendor nameplates).

1. **H₂ (S24 / S64)** — **Partial**: normal S64 → CRYO_H2 → S45+S49; S24 roof = contingency only. Finish GEN/FC kW within MAQ.
2. **Acid-gas** — **Partial / Claimed**: ALK + ACID_POLISH → CRU (S65–S66). Upset stack may remain for AHJ; not continuous dump.
3. **Afterburner flue** — **Partial / Claimed**: destruction remains; flue products → FLUE_CAP / CRYO (S67/S18); condensate S68; heat to Q1.
4. **Br₂** — **Partial / Claimed**: ZNBR2_BR2_REGEN → S69 pos. tank. Outdoor skid stays; continuous stack dump does not.
5. **CRYO_AHU (S56)** — **Partial**: condensables via CRYO_AHU_COND (S70); residual contingency only.
6. **MET_AHU (S62)** — **Partial / Claimed**: MET_SCRUB / baghouse (S71–S72); never HAB return.

---

## 6. Closure paths (scrub / regen or CRYO)

| Unclosed / Partial | Closure path (AQS-VENT-001) | Constraint |
|---|---|---|
| H₂ (S24 residual) | S64 → CRYO_H2 → S45 / S49 | MAQ; Class I / Div 2; GEN/FC study bounds AQS-AUD-001 §10 |
| Acid-gas residual | ACID_POLISH + S66 → CRU | Upset stack AHJ; no Br⁻ in liquor |
| Afterburner flue products | S67 / S18 → CRYO; S68 condensate | Destruction upstream remains |
| Br₂ residual | ZNBR2_BR2_REGEN → S69 | Never CRU; outdoor skid OK |
| CRYO room condensables | S70 → COLD_BOX | S56 residual contingency only |
| MET aisle capture | S71–S72 scrub / BH returns | Not HAB return; not acid-gas primary |
| Condensate / grey | already S12/S13 | keep off Salria |
| Tank overflow (process) | DRAIN_SEC → CATCH / HDR_GREY | clean water only |
| Roof surplus overflow | ROOF_TANK → OVERFLOW → TERRACE | clean only; never process bund |
| WS_* spent | S10 / S39 → leach / oil / org | OoM study AQS-AUD-001 §13; synth vs seed TBD |

| MeOH CO₂ / H₂ feed | S73 / S74 | Surplus H₂ only; PEM/GEN priority (AQS-REQ-KW-001) |
| MeOH product / fuel | S75–S77 / S76 | MEOH_TANK inventory; PC-11 |
| MeOH ferment feed | S78 | Farm/hab organics — Partial biogenic |
| MeOH FC power / heat / returns | S79–S82 | BATT DC peer; Q4; Claimed CO₂; condensate |
| ORC electric | S48 → Sol-Ark AC | method TBD after GHEX survey (AQS-AUD-001 §10.4) |

---

## 7. Building level map (mass resting place)

| Level | Mass role |
|---|---|
| L2 | ROOF TANK clean inventory; contingency stack tops (H₂ / acid upset / oil / Br₂); ARRAY_ROOF |
| L1 | HAB / FARM life mass; HDR_UPW gravity-first |
| L0 | Dock solids in; MFG / FAB / CRYO / POWER; ZnBr2 outdoor |
| L-1 | Wet / oil / glass / BMED / scrubbers — dirty liquor |
| L-2 | CATCH TANK clean lower reservoir; hydro set; process sumps (separate) |

Gravity rule unchanged: dirty liquor does not drain uphill into life.

Surplus clean tower water (batteries full + `ROOF_TANK` full) overflows
to external garden terraces (`OVERFLOW_TERRACE_*` bands) via
`OVERFLOW_SPILL_ROOF` / `OVERFLOW_DOWNCOMER_*` — see AQS-SCALE-001 §6–7
and AQS-TRR-001 (planting / open vs greenhouse / S40–S42). Not a
process drain path. Clean terrace return is S41 → CATCH; fertigated
enclosed-greenhouse drain is S42 → HDR_GREY — never mixed into CATCH.

---

## 8. Rebuild

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 mass_flow_pfd.py
python3 vent_closure_pfd.py
```

Vent closure authority: `docs-authority/VENT_CLOSURE.md` (AQS-VENT-001).
Equipment stubs: `docs-authority/VENT_SCRUB_EQUIPMENT.md` (AQS-EQP-VENT-001).
