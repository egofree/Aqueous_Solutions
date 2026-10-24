# Mass-flow claim status

Document number: AQS-MF-001  
Revision: K  
Date: 2026-10-24  
Basis: AQS-BLD-001, AQS-STR-001 and AQS-HSE-001. End states of gas streams: AQS-VENT-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue | 2026-09-27 |
| B | 1 | S25–S30 water purification (AQS-WTR-001); VCD ≠ roof–catch | 2026-09-27 |
| C | 1 | S31–S39 fab wet-reagent forks (qualitative) | 2026-09-27 |
| D | 1 | S40–S42 terrace irrigation / return (AQS-TRR-001) | 2026-09-27 |
| E | 1 | S43–S48 geothermal / backup genset (AQS-PWR-002) | 2026-09-27 |
| F | 1 | S49–S53 PEM fuel cell (AQS-FC-001); S24 closing via FC+GEN | 2026-09-28 |
| G | 1 | S54–S56 CRYO Q4 / dedicated cool / room vent (AQS-CRY-002) | 2026-09-28 |
| H | 1 | S57–S63 metal forming (AQS-MFG-MET-001) | 2026-09-28 |
| I | 1 | Vent closure S64–S72 (AQS-VENT-001); reclassify former open dumps | 2026-09-28 |
| J | 1 | Graph Rev M (2026-10-08): every edge rated and every node balance closed (AQS-DUTY-011, `REV_M_CLOSURE_DUTY.md`); new streams S91–S102 and IA-BMED-05..10; S05, S86, S87 and S88 retired; S16 is harvest rinse liquor (12.6 kg/d); S68 is CRYO AHU coil condensate | 2026-10-08 |
| K | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; split closure table joined; statuses unchanged | 2026-10-24 |

## 1. Purpose and scope

The plant is meant to recover or recycle every material stream rather than release it. This page records, for each named stream, whether that claim is met: whether the design routes the stream to a named recovery or recycle unit, and how far that route is proven. It is a status record, not a measured mass balance.

The flow rates are not here. They are generated from the plant graph into `flow_graph/derived/MASS_FLOW_DERIVED.md` by `flow_graph/export_authority_md.py`, and those rates take precedence over anything on this page. This page is the human-maintained status narrative kept in step with that file (see `flow_graph/derived/SYNC_POINTER.md`). Do not invent dock stream numbers or fill placeholder rates that the graph leaves empty.

The drawing is `mass_flow_pfd.png`, made by `flow_graph/exporters/matplotlib/mass_flow_pfd.py`.

## 2. Terms

"Closed" means the design sends the stream to a named recovery or recycle unit through a locked header. It does not mean a measured balance. Under AQS-VENT-001, continuous release to open air is not design intent: former vents are "Closure required" (scrubbing and regeneration, or the cryogenic plant) until hardware and permits complete the route. Relief for upsets and contingencies may remain where the authority having jurisdiction and life safety require it. Table 2.1 defines the status tags.

Table 2.1. Status tags

| Tag | Meaning |
|---|---|
| **Closed** | Routed to recovery / recycle; no intentional atmosphere discharge |
| **Claimed** | Design path exists; holdup / capture efficiency still to prove |
| **Partial** | Primary recovery path named and preferred; contingency relief may remain |
| **Closure required** | Unclosed — must finish scrub+regen or CRYO path (AQS-VENT-001); not “open by intent” |
| **Recapturable** | Legacy synonym for Closure required where hardware path already named |

Stream numbers (S01 and so on) and unit names are those of the plant graph and the stream register (AQS-STR-001). Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Stream status S01 to S72

Table 3.1. Status of streams S01 to S72

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
| S13 | Farm sump + HVAC condensate → VCD / polish / salt | Closed | HDR_GREY; VCD_FEED primary |
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
| S42 | Fertigated greenhouse drain → HDR_GREY | Closed / Claimed | only if enclosed food option |
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
| S62 | MET_AHU → MET_SCRUB / baghouse (S71) | Partial / Claimed | dedicated aisle capture; never HAB return; not free outdoor dump |
| S63 | MET_HX_Q4 → Q4 | Closed | warm residual only; peer S06/S44/S53/S54 |
| S64 | H2_DRYER → CRYO_H2 | Partial | Normal H₂ path; closes continuous roof dump |
| S65 | ALK_SCRUBBER residual → ACID_POLISH_SCRUB | Partial / Claimed | Post-alkali polish feed; PFD path named |
| S66 | Acid polish / ALK_SCRUBBER liquor → CRU | Claimed | Regenerable scrub return |
| S67 | AFTERBURNER flue → FLUE_CAP / CRYO | Partial / Claimed | Extends S18; destruction upstream remains; PFD path named |
| S68 | Flue / AHU condensate → S13 class | Claimed | Not potable |
| S69 | ZNBR2_BR2_REGEN → pos. tank | Partial / Claimed | Br⁻ return; never CRU; PFD path named |
| S70 | CRYO_AHU_COND → COLD_BOX | Partial | Condensable return from S56 train; PFD path named |
| S71 | MET_AHU → MET_SCRUB / baghouse | Partial / Claimed | Capture train (feeds from S62); PFD path named |
| S72 | MET scrub / baghouse → CSTR / OIL / ORG | Claimed | Fines S19 class; mist to oil/org |

## 4. Process gas and scrubber paths

The end states are set by AQS-VENT-001; continuous release to open air is not design intent (Table 4.1).

Table 4.1. Gas paths

| Path | Header / unit | Status | End state / discharge |
|---|---|---|---|
| Anode / CSTR hood | HDR_ACID_GAS → DEMISTER → ALK_SCRUBBER → ACID_POLISH_SCRUB | Closure required / Claimed | Liquor → CRU (S66); upset stack residual only |
| Cathode H₂ | HDR_H2 → arrestor → H2_DRYER → S64 CRYO_H2 | Partial | Consumers S45/S49; S24 roof = contingency only |
| Oil vapor | HDR_OIL_VAPOR → QUENCH → AFTERBURNER → FLUE_CAP / CRYO | Closure required / Claimed | Destruction + S67 CO₂ capture; S68 condensate |
| Dust | HDR_DUST → BAGHOUSE | Closed / Claimed | Fines to CSTR 1 (S19) |
| ZnBr2 Br₂ | ZNBR2_BR2_SCRUBBER → ZNBR2_BR2_REGEN | Closure required / Claimed | S69 Br⁻ → pos. tank; not CRU; no continuous dump |
| Hab / farm air | dedicated AHU | Closed vs process | No process-atmosphere duct |
| CRYO room | CRYO_AHU → CRYO_AHU_COND (S70) / S56 residual | Closure required / Partial | Condensables to CRYO; residual contingency; not HAB return |
| MFG metal aisle | MET_AHU → MET_SCRUB / baghouse (S71–S72) | Closure required / Claimed | Scrub/baghouse returns; not HAB return |

## 5. Liquid loops

Table 5.1. Closed and claimed liquid loops

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

## 6. Former open releases

None of these is open by intent. The process flow diagrams name a scrubbing and regeneration route or a return to the cryogenic plant for each. Study duties, flows in Nm³/h and power bounds are issued in AQS-EQP-VENT-001 Rev B and AQS-AUD-001 Rev D; they are labelled study estimates, not supplier nameplates.

1. Hydrogen (S24, S64), Partial: the normal route is S64 to `CRYO_H2`, then S45 and S49; the roof outlet S24 is a contingency only. The generator and fuel-cell ratings remain to be finished within the MAQ.
2. Acid gas, Partial / Claimed: `ALK_SCRUBBER` and `ACID_POLISH_SCRUB` to the CRU (S65 to S66). An upset stack may remain for the AHJ; there is no continuous release.
3. Afterburner flue, Partial / Claimed: destruction remains; the flue products go to `FLUE_CAP` or CRYO (S67, S18), the condensate to S68, and the heat to Q1.
4. Bromine, Partial / Claimed: `ZNBR2_BR2_REGEN` returns bromide to the positive tank by S69. The outdoor skid stays; continuous stack release does not.
5. `CRYO_AHU` (S56), Partial: condensables go through `CRYO_AHU_COND` (S70); the residual is a contingency only.
6. `MET_AHU` (S62), Partial / Claimed: to `MET_SCRUB` and the baghouse (S71 to S72); never to habitation return air.

## 7. Closure routes

Table 7.1 gives the route that closes each remaining open or partial stream, and its constraint.

Table 7.1. Closure routes

| Unclosed / Partial | Closure path (AQS-VENT-001) | Constraint |
|---|---|---|
| H₂ (S24 residual) | S64 → CRYO_H2 → S45 / S49 | MAQ; Class I / Div 2; GEN/FC study bounds AQS-AUD-001 §10 |
| Acid-gas residual | ACID_POLISH + S66 → CRU | Upset stack AHJ; no Br⁻ in liquor |
| Afterburner flue products | S67 / S18 → CRYO; S68 condensate | Destruction upstream remains |
| Br₂ residual | ZNBR2_BR2_REGEN → S69 | Never CRU; outdoor skid OK |
| CRYO room condensables | S70 → COLD_BOX | S56 residual contingency only |
| MET aisle capture | S71–S72 scrub / baghouse returns | Not HAB return; not acid-gas primary |
| Condensate / grey | already S12/S13 | keep off Salria |
| Tank overflow (process) | DRAIN_SEC → CATCH / HDR_GREY | clean water only |
| Roof surplus overflow | ROOF_TANK → OVERFLOW → TERRACE | clean only; never process bund |
| WS_* spent | S10 / S39 → leach / oil / org | OoM study AQS-AUD-001 §13; synth vs seed TBD |
| MeOH CO₂ / H₂ feed | S73 / S74 | Surplus H₂ only; PEM/GEN priority (AQS-REQ-KW-001) |
| MeOH product / fuel | S75–S77 / S76 | MEOH_TANK inventory; PC-11 |
| MeOH ferment feed | S78 | Farm/hab organics — Partial biogenic |
| MeOH FC power / heat / returns | S79–S82 | BATT DC peer; Q4; Claimed CO₂; condensate |
| ORC electric | S48 → Sol-Ark AC | method TBD after GHEX survey (AQS-AUD-001 §10.4) |

## 8. Where mass rests, by level

Table 8.1. Mass by building level

| Level | Mass role |
|---|---|
| L2 | ROOF TANK clean inventory; contingency stack tops (H₂ / acid upset / oil / Br₂); ARRAY_ROOF |
| L1 | HAB / FARM life mass; HDR_UPW gravity-first |
| L0 | Dock solids in; MFG / FAB / CRYO / POWER; ZnBr2 outdoor |
| L-1 | Wet / oil / glass / BMED / scrubbers — dirty liquor |
| L-2 | CATCH TANK clean lower reservoir; hydro set; process sumps (separate) |

The gravity rule is unchanged: dirty liquor does not drain uphill into the living floors.

Surplus clean tower water (batteries full and `ROOF_TANK` full) overflows to the outdoor garden terraces (`OVERFLOW_TERRACE_*` bands) through `OVERFLOW_SPILL_ROOF` and `OVERFLOW_DOWNCOMER_*`; see AQS-SCALE-001 §9–10 and AQS-TRR-001 (planting, open or greenhouse beds, S40 to S42). This is not a process drain. Clean terrace water returns by S41 to the catch tank. Fertigated drain from an enclosed greenhouse goes by S42 to `HDR_GREY` and is never mixed into the catch tank.

## 9. Rebuilding the drawings

Run from the repository root:

```bash
python3 flow_graph/exporters/matplotlib/mass_flow_pfd.py
python3 flow_graph/exporters/matplotlib/vent_closure_pfd.py
```

The authority for vent closure is `docs-authority/VENT_CLOSURE.md` (AQS-VENT-001). Equipment stubs are in `docs-authority/VENT_SCRUB_EQUIPMENT.md` (AQS-EQP-VENT-001).
