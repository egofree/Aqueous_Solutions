# MVS equipment issue

Document: AQS-MVS-EQP-001
Date: 2026-10-02; Rev K 2026-10-07; Rev L 2026-10-07; Rev M 2026-10-08
Graph Rev M (envelope changes: CONTINUOUS_RECYCLE line DN15; ratings for HX-5, HX-6, VCD-COMP-01). L×W×H are issued envelopes in millimetres, not vendor nameplates, except the study envelopes in the second table.

## Envelopes

| Unit | L | W | H | Duty |
|---|---:|---:|---:|---|
| WS_PHOS | 800 | 800 | 1100 | Tote class. Own bund. S34B. |
| GLASS_RINSE | 1200 | 600 | 800 | 0.2 kW. Drain before mill. |
| GLASS_MILL | 800 | 600 | 800 | 0.8 kW. |
| GLASS_BURNOUT | 800 | 600 | 1200 | 1.0 kW. Off-gas to oil-vapor header. |
| VCD-COMP-01 | 1400 | 600 | 1200 | 0.11 m³/d, 14–20 kWh/m³, 0.08 kW. |
| REMIN-01 | 600 | 400 | 800 | 10 L/d. 25 mg/L Ca, 10 mg/L Mg. UV after dose. |
| LITHO_COAT | 600 | 500 | 800 | Spin. 2 mL/wafer class. |
| LITHO_ALIGN | 500 | 500 | 800 | 365 nm LED. 1–5 starts/day. |
| LITHO_DEV | 500 | 500 | 800 | Solvent waste leaves to the oil line. |
| LITHO_STUB | 1600 | 800 | 1600 | Parent of the three. Drawn as a 1600 × 800 × 800 bench with the three tools on top (Rev K). |
| ELC-BOOTH-01 | 1200 | 800 | 1800 | Carbon or nickel. Exhaust to MET_AHU. 0.3 kW. |
| BLOW-01 | 1200 | 800 | 1600 | Peak 2–4 kW. Scrap to the oil line. |
| PV-CELL-01 | 2400 | 1200 | 1600 | Texture through IV. 1.0 kW. Not the yard array. |
| EW-1…EW-9 | 600 | 420 | 650 | Pitch 750. Funnel 220 below the box. |
| Q1_A, Q1_B | 800 | 800 | 1200 | Oil, 0.30 m³, 250 °C. 1/2 in thermal relief. |
| Q2_A, Q2_B | 800 | 800 | 1200 | Oil, 0.30 m³, 150 °C. |
| Q3_A, Q3_B | 800 | 800 | 1200 | Water, 0.40 m³, 100 °C. |
| Q4_A, Q4_B | 800 | 800 | 1200 | Water, 0.60 m³, 70 °C. |

Rev K store stands (AQS-DUTY-008 Rev C §14.2): Q1 on the floor, Q2 on 850 mm, Q3 on 1750 mm, Q4 on 2650 mm, both ladders.
| BACKUP_GEN | 2000 | 1000 | 1600 | Outdoor H2 skid. |
| FUEL_CELL | 1800 | 800 | 1600 | PEM. O2 face on the south side. |
| MEOH_FERM | 2200 | 900 | 1400 | First in the train. |
| MEOH_SYNTH | 2200 | 900 | 1400 | Second. |
| MEOH_TANK | 800 | 800 | 1100 | Diked. |
| MEOH_FC | 1800 | 800 | 1600 | Last. Not the PEM. |

## Study envelopes (Rev K)

Physical units with no issued size. Each envelope is derived from the unit duty. These are not issued and not nameplates.

| Unit | L | W | H | Basis |
|---|---:|---:|---:|---|
| HX8 | 600 | 400 | 600 | Ti gasketed plate, 0.51 m² (AQS-DUTY-008 Rev B): 16 plates × 0.032 m² in an M3-class frame, 600 mm carrying bar. |
| NOX_SCRUB | 600 | 400 | 1200 | H₂ genset exhaust 10.4 kg/h (3.6 kg/d H₂ at λ 2, 69.6 kg/kg): about 9.5 m³/h at 40 °C, DN100 packed column at under 0.5 m/s, 0.6 m packing + sump + demister. |
| MEOH_COND | 400 | 400 | 600 | MeOH fuel-cell condensate 5.6 kg/d (2 H₂O per CH₃OH on 5.0 kg/d MeOH): DN150 KO pot, trap and level switch. |
| RELIEF_CRYO | 600 | 400 | 600 | Contingency vent damper section on the CRYO_AHU exhaust: 12 ACH × 216 m³ = 2592 m³/h, 300 × 300 duct at 8 m/s, actuator and flanges. |
| CONTINUOUS_RECYCLE | 1500 | 60 | 60 | Line envelope kept at DN50 OD for routing space. Rev M issues the line as DN15 CPVC with a 25 µm cartridge upstream: IA-REC-01 3.72 m³/d of filtered liquor at 0.22 m/s; clear-liquor service, so no solids-carrying velocity applies (AQS-DUTY-011 §4.12). Rev L DN50 gave 0.02 m/s. |

Existing Features carry two more units (unit map Rev C, Feature names, not unit aliases): FLUE_KO is FLUE_CAP (600 × 700 × 1100; a DN300 KO drum with mesh pad fits it even at the 180 m³/h AQS-GAS-003 NCG case, and it is large for the graph 10.07 kg/h), and RELIEF_H2 is H2_STACK (Ø250 × 8000 H₂ vent stack).

## Ratings issued in Rev M (AQS-DUTY-011)

| Item | Rating | Normal duty | Basis |
|---|---|---|---|
| HX-5 leach trim heater (LEACH_CSTR_1) | 6.0 kW electric | 0.43 kW | Rating case 4.60 kW × 1.25: no Q3, no Q4 preheat, no oxidant credit |
| HX-6 digest trim heater (GLASS_DIGEST) | 2.5 kW electric | 0.80 kW | 1.663 kW × 1.25; 1.5 kW study class retired |
| HX-9 leach make-up preheat (Q4_BUS branch, S100) | — | 0.53 kW | cold make-up to 55 °C from Q4 at 60 °C |
| HX-10 caustic preheat (Q4_BUS branch, S101) | — | 0.28 kW | digest caustic to 55 °C |
| VCD-COMP-01 | 0.40 m³/d | 0.283 m³/d, 0.20 kW | feed × 1.25; 17 kWh/m³ |
| BMED stack (BMED_REGEN) | 9 kW DC | 6.55 kW | 1.25 × average; above the 5–8 kW study class |

HX-9 and HX-10 are coil or plate exchangers on Q4_BUS branches, not HL-* edges and not new graph nodes; their duties are the S100 and S101 edge rates.

## Duties against envelopes (Rev L)

Rev L rates every edge (AQS-DUTY-010). Three issued sizes need checking against the new rates. No envelope changes in Rev L.

| Unit | Rev L duty | Envelope basis | Note |
|---|---|---|---|
| VCD_TRAIN (VCD-COMP-01) | feed 178.9 kg/d (S13 31.5 + S29 104.5 + S52 42.9); distillate S25 161.0 | 0.11 m³/d | Under-rated at Rev L. Rev M: re-issued at 0.40 m³/d |
| NOX_SCRUB | S46 250.6 kg/d = 10.44 kg/h | 10.4 kg/h | Matches (genset run case; Rev M design day 0, GEN on standby) |
| MEOH_COND | S81 5.62 kg/d | 5.6 kg/d | Matches |
| RELIEF_CRYO | S56 / S86 0 continuous; CRYO AHU 2592 m³/h | 2592 m³/h | Contingency only |
| FLUE_KO (FLUE_CAP) | S67 241.7 kg/d + S70 0.05; condensate 4.14 kg/d; S67B 12.75 | 10.07 kg/h | Matches |
| MET_SCRUB | S62 1800 m³/h + S71 720 m³/h; blowdown S72 2.44 kg/d | — | Size check open |
| ACID_POLISH_SCRUB | S65 1500 m³/h at 50 °C; blowdown S66 27.4 kg/d | VENT_SCRUB_EQUIPMENT §2.1 | Matches the band |

LOAD_AGG is class `boundary` since Rev K (S17/S20 electrical accounting, no solid), with BOUNDARY_EXPORT.

Fab room: ISO 14644-1 Class 7 wet bench, Class 6 tool row. Wet bench envelope is the FAB block, 12000 × 10000 × 4000.

Q4 volume basis:

\[
m = 20 \times 3.6\times10^6 / (4180 \times 30) = 574\,\mathrm{kg} \approx 0.60\,\mathrm{m^3}
\]

Relief is blocked-in expansion, not a fire-case orifice. Q1 relief is not a hab vent.

EW solid file: `models/freecad/ew_cascade.step` (2026-10-07), nine cells, eight overflow launders, POLISH_BANK, and the EW-9 → polish pipe. Placement copy: generated by `flow_graph/apply_placement.py` from `placement_seed.json` Rev I (`plant_placed_2026-10-08_revM.FCStd`, derived from the revK copy; Rev I origin moves only); mapped Features for the generator, fuel cell, methanol skids, and glass machines carry the issued envelopes above. The eight ladder stores (at their Rev K elevations), WS_PHOS, VCD_TRAIN, REMIN, the LITHO bench and tools, SOLAR_PV_CELL, ELECTRODE_COAT, BLOW_MOLD and the five study envelopes are created on the copy. Every present node now has a solid or is a header or boundary (112 / 8 / 2, fail 0). Coil packs, cross-tie loops and the Q3 draw, HX-8 and bus duties are in AQS-DUTY-008 Rev C. Origins live in `placement_seed.json`, not here. ORC pad is empty.
