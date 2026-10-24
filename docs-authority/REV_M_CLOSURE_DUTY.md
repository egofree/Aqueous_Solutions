# Rev M closure: node balances, chloride loop, heater ratings and Q4 sinks

Document number: AQS-DUTY-011
Revision: A
Date: 2026-10-08
Authority: AQS-FLOW-GRAPH-001 Rev M; AQS-DUTY-010 Rev A; AQS-DUTY-008 Rev C; AQS-DUTY-009 Rev B; ELECTRICAL AQS-ELC-001 Rev B. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue. Closes the eleven Rev L open node balances and the AFTERBURNER CO₂ residual; resolves the six routing decisions; rates the leach and digest heaters; assigns the Q4 surplus; retires S87/S88 | 2026-10-08 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose

AQS-DUTY-010 (Rev L) rated every present edge and left eleven node balances and one species check open (§6 of that note), together with six topology decisions, two heater ratings, the Q4 surplus and the S87/S88 hold. This note resolves each item from first principles and records the result in graph Rev M.

The calculation is `docs-authority/_rev_m_closure_study.py`. It reads the Rev L graph from commit c4e1818 (or `--base FILE`), reruns the AQS-DUTY-010 rating pass, applies the Rev M topology and rates, and checks conservation at every node. `--write` produces the Rev M graph; a rerun reproduces it byte for byte. Each Rev M rate carries `rate_status: study`, a note beginning `AQS-DUTY-011:` and the Rev L value in `params.rev_l_value`. Node off-graph terms move from `params.balance_rev_l` to `params.balance_rev_m`. Retargeted edges carry `params.rev_l_from` / `params.rev_l_to`.

AQS-DUTY-010 remains reproducible against its Rev L base: run on a Rev M working tree, `_edge_rating_study.py` loads c4e1818 automatically.

## 2. Result

- Graph Rev M: 123 nodes, 179 edges, all present. Placeholders: none. Present edges with no rate: none.
- Retired: S05, S86, S87, S88. New: IA-BMED-05, IA-BMED-06, IA-BMED-07, IA-BMED-08, IA-BMED-09, IA-BMED-10, S91, S92, S93, S94, S95, S96, S97, S98, S99, S100, S101, S102. Retargeted: IA-BMED-03, IA-BMED-04, IA-HDR-H2-01, IA-HDR-H2-03, IA-HDR-H2-04, S12, S20, S68.
- Node conservation at ±1 % (daily average): 94 node-layer balances checked. 74 close with independently derived terms; 20 close with one term set by difference; none open. Three of the 74 carry zero flow on the design day (BACKUP_GEN, FUEL_CELL and TERRACE_IRRIG mass; standby or dry-weather cases).
- Species checks: 9 checked, all close (AFTERBURNER/CO2, CRYO_CO2/CO2, HDR_CO2/CO2, H2_DRYER/H2, CRYO_H2/H2, LEACH/electrons, LEACH_LOOP/Cl, SALT_FEED/Na, BMED/pairs).
- `loops_closed` and every `*_on_site` flag stay false. The MVS energy-surplus criterion is not met on the design day: the bus imports 40.0 kW average from the utility (§4.9).

## 3. Basis and decisions

The design day is the AQS-DUTY-010 basis: daily average, plant running normal, dry weather, one hydro cycle per day. Rev M study decisions are named `A_RM_*` in the script. Values marked (P) are provisional; all provisional decisions are listed in §5.

| Decision | Value | Basis |
|---|---|---|
| EW current efficiency | Au/Ag 0.90; Cu/Pb/Sn/Cd 0.85; Ni/Fe/Zn 0.80 | ELECTRICAL CE table |
| EW cell voltage | Au/Ag/Cu 2.2 V; Fe 3.1 V; others 3.4 V | ELECTRICAL V_cell |
| Side reaction | every non-deposit electron evolves H₂ at the cathode; the anode evolves Cl₂ for every electron | upper bound on H₂ (chloride EW, pH ≈ 1) |
| H₂ collection | EW_7 (Fe), EW_3 (Cu), EW_9 (Zn) hooded to HDR_H2; other cells vent through the hood sweep | 96 % of H₂ is at EW_7 and EW_3 |
| Harvest entrainment / rinse | 0.10 kg electrolyte per kg deposit; 2 displacement volumes | practice |
| Cl₂ absorption in leach sparge | 0.95 (P) | sparged CSTR with Fe²⁺/Cu⁺ present; RS-CL2-SPARGE |
| O₂ sparge utilization | 0.90 | fine-bubble sparge, 77.5 °C chloride liquor |
| Free HCl in raffinate and bleed | 0.10 mol/L | chloride EW at pH ≈ 1 |
| Stream temperatures | raffinate 50 °C; BMED HCl 35 °C; CRU 40 °C; float return 60 °C; S28 40 °C; Q4 preheat outlet 55 °C | stack limit ≤ 40 °C for BMED; Q4 supply 60 °C less 5 K approach |
| Heater rating | ceil(rating-case duty × 1.25) to 0.5 kW | AQS-DUTY-008 margin |
| Filter cake | 50 wt % solids | filter press, hydroxide/silicate cake |
| PV yield | 1550 kWh/kWp·yr, 70 kWp → 12.39 kW average | SITE_LAT 33 sandbox, fixed tilt |
| Rectifier / inverter | η 0.95; Sol-Ark conversion loss 3 % of AC delivered | vendor class |
| Fuel cell | η 0.52 LHV at 4.0 kW; standby with 8 h inventory | PEM system band 0.50–0.55 |
| ZnBr₂ electrolyte | water activity 0.78; purge outlet at 0.5 approach to equilibrium humidity | 2–3 M ZnBr₂ |
| Grey sludge | 0.05 of grey inflow to BLACK_DIGEST | practice |
| Micronutrient dose | 0.02 kg/d | hydroponic trace salts |
| VCD SEC | 17 kWh/m³ | ELECTRICAL 14–20 band mid |
| Glass insolubles | 0.15 of cullet (CaO/MgO/Al₂O₃) | soda-lime 0.72 SiO₂ / 0.13 Na₂O |
| S11 heating value | 17.5 MJ/kg dry | crop residue |
| CONTINUOUS_RECYCLE line | DN15 CPVC, 25 µm cartridge upstream | clear-liquor service (§4.12) |
| Reduction enthalpy released per mol e⁻ | Cl₂ 167.2 kJ; ClO₃⁻ 153.4 kJ; O₂ 142.9 kJ | standard enthalpies of formation, aq, 25 °C |

## 4. Resolution by item

### 4.1 Faraday H₂ and EW electron chain (item 3)
Rev L carried 1.6 kg/d H₂ on each of IA-HDR-H2-01/03/04 (4.8 kg/d). With the ELECTRICAL CE table, the cathodic side reaction at every cell is n_side = n_dep (1 − CE)/CE. Total deposit electrons are 1415.4 mol/d and side electrons 331.2 mol/d, which gives 0.334 kg/d H₂ in total. This is an upper bound: it books all inefficiency as H₂, where some is Fe³⁺/Fe²⁺ shuttling. The anode evolves Cl₂ for every electron: 61.9 kg/d (873.3 mol/d). The EW DC power from the same chain is 5.75 kW against the 6.0 kW issued rectifier share, which confirms the basis.

| Cell | Metal | Deposit kg/d | e⁻ dep mol/d | e⁻ side mol/d | Cl₂ kg/d | H₂ kg/d | Collected | DC kW |
|---|---|---|---|---|---|---|---|---|
| EW_1 | Au | 0.006 | 0.1 | 0.0 | 0.004 | 0.0000 | hood | 0.000 |
| EW_2 | Ag | 0.025 | 0.2 | 0.0 | 0.009 | 0.0000 | hood | 0.001 |
| EW_3 | Cu | 8.784 | 276.5 | 48.8 | 11.531 | 0.0492 | yes | 0.799 |
| EW_4 | Pb | 0.711 | 6.9 | 1.2 | 0.286 | 0.0012 | hood | 0.031 |
| EW_5 | Sn | 0.711 | 12.0 | 2.1 | 0.500 | 0.0021 | hood | 0.054 |
| EW_6 | Ni | 0.711 | 24.2 | 6.1 | 1.074 | 0.0061 | hood | 0.115 |
| EW_7 | Fe | 29.629 | 1061.1 | 265.3 | 47.025 | 0.2674 | yes | 4.592 |
| EW_8 | Cd | 0.711 | 12.7 | 2.2 | 0.528 | 0.0022 | hood | 0.057 |
| EW_9 | Zn | 0.711 | 21.8 | 5.4 | 0.964 | 0.0055 | yes | 0.103 |

Collected H₂ is 0.322 kg/d; 0.0117 kg/d leaves with the hood sweep at < 1 % LFL. IA-HDR-H2-01 now originates at EW_7 and IA-HDR-H2-03 at EW_3 (Rev L: EW_1, EW_2); IA-HDR-H2-04 stays at EW_9 with corrected text. Each carries the H₂ with its saturation water at 50 °C. H2_DRYER condensate returns to EW_9.

Consequences: the REGEN LEACH return, the CRU/BMED duty and the leach exotherm in Rev L were all driven by the 4.8 kg/d basis. They are re-derived below.

### 4.2 S05/S64 alias, H2_DRYER and CRYO_H2 (items 1, 2)

S05 and S64 both carried the full H₂ pool from H2_DRYER to CRYO_H2. They are the same pipe. S05 is retired (alias of S64); S64 carries 0.3221 kg/d. H2_DRYER now closes on H₂ and on total mass; CRYO_H2 closes with one inlet.

### 4.3 CRYO_H2 dispatch (item 2)

With 0.322 kg/d of H₂ the three Rev L outlets cannot run together. The fuel cell at 4.0 kW and η 0.52 needs 5.54 kg/d (0.231 kg/h), seventeen times the supply.

Dispatch rule (P): on the design day all collected H₂ goes to MEOH_SYNTH (S74 0.3221 kg/d). FUEL_CELL and BACKUP_GEN are on standby: S45, S46, S47, S49, S50, S51, S52 and S53 are 0 on the design day and carry their standby rating in params. The fuel-cell store holds an 8 h inventory (1.85 kg H₂); after a fuel-cell run S74 is diverted to refill it, which takes 5.7 days at the collected rate. The MeOH chain is rated stoichiometrically: S73 2.344 kg/d, S75 1.706 kg/d, S76 1.721 kg/d, S79 0.1007 kW, S80 0.127 kW, S81 1.935 kg/d, S82 2.364 kg/d.

Alternative: send H₂ to the fuel-cell store only and retire MeOH synthesis from the design day. Rejected for the design day because the MeOH tank is the long-duration carrier and the fuel cell is an outage asset.

Fuel-cell efficiency (item 3): Rev L S51 4.0 kW from S49 4.8 kg/d implied η 0.60, above the PEM band. Rev M uses η 0.52; the standby-case water is 49.5 kg/d and the heat to Q4 3.69 kW when running. REQ-MEOH-FC (0.5–2 kW) is not met by MEOH_FC at 0.1007 kW; this is a supply limit, recorded in §7.

### 4.4 S12 to GREY_TREAT and NUTRIENT_DOSE (items 1, 2)

S12 grey water is retargeted HABITATION → GREY_TREAT (114.9 kg/d, by difference on the HABITATION balance). GREY_TREAT sends 0.95 to VCD_TRAIN as S29 (109.2 kg/d) and 0.05 as sludge to BLACK_DIGEST. NUTRIENT_DOSE takes S30 (22.17 kg/d) and adds 0.02 kg/d trace salts; S07 is 22.19 kg/d. GREY_TREAT and NUTRIENT_DOSE both close.

### 4.5 S56/S86 alias (item 2)

S56 and S86 are the same CRYO_AHU → RELIEF_CRYO contingency relief. S86 is retired; S56 stays as contingency relief at 0 (not product).

### 4.6 Chloride loop, BMED and CRU (items 1, 2, 3)
**Electron balance at the leach.** Metal oxidized in LEACH_CSTR_1 per day: deposited metal 1415.4 mol e⁻, metal dissolved but not plated (undeposited, carried to the bleed) 107.3 mol e⁻, and aluminium 708.9 mol e⁻ (236.3 mol Al). Demand is 2231.5 mol e⁻/d. Oxidant supply:

| Oxidant | mol e⁻/d | Source |
|---|---|---|
| Anode Cl₂ absorbed in the leach sparge (0.95) | 1659.2 | all EW anodes |
| Chlorate in CRU liquor (IA-BMED-09) | 87.3 | ALK_SCRUBBER hypochlorite disproportionation |
| O₂ sparge S95 | 485.0 | 134.7 mol O₂ = 4.311 kg/d at 0.90 utilization |

The O₂ term closes the electron balance; it is drawn from HDR_O2 (S83 4.311 kg/d) and does not tee into habitation air or BOUNDARY_EXPORT. Unabsorbed Cl₂ (43.7 mol/d) and unused O₂ leave with the lid purge to ALK_SCRUBBER.

**Chloride.** Anode Cl₂ that is not re-absorbed reaches ALK_SCRUBBER and leaves as NaCl/NaClO₃ in CRU liquor (IA-BMED-08 49.75 kg/d, IA-BMED-09 50.14 kg/d to CONTINUOUS_RECYCLE). ALK caustic is IA-BMED-07 (46.69 kg/d, 86.5 mol NaOH). S66 polish blowdown to CRU is re-rated to 0.3868 kg/d.

Leach level is held by a brine bleed from POLISH_BANK to SALT_FEED: IA-BMED-05 782.2 kg/d (978.0 mol/d Cl⁻, 74.5 mol/d free HCl, Al 236.3 mol/d). At SALT_FEED, BMED base (IA-BMED-10 161.6 kg/d) and the digest liquor (S92 326 kg/d) raise pH to 9; Al(OH)₃, metal hydroxides, silica and sodium aluminosilicate leave as filter cake S97 (91.08 kg/d). The clarified NaCl brine feeds BMED (IA-BMED-03 505.8 kg/d to the acid compartment, IA-BMED-04 528.8 kg/d to the base compartment; the Rev L CRU origin is replaced by SALT_FEED). BMED splits 979.2 mol/d NaCl (74.9 kg/d) at 6.55 kW DC. HCl returns to CONTINUOUS_RECYCLE (IA-BMED-06 495.8 kg/d, 960.0 mol/d), with fab draws S09/IA-BMED-01 (17.96 and 1.25 mol/d). NaOH serves GLASS_DIGEST (S91 320.8 kg/d), ALK_SCRUBBER (IA-BMED-07), SALT_FEED (IA-BMED-10) and IA-BMED-02. The diluate leaves SALT_FEED to VCD_TRAIN (S98 144.1 kg/d, by difference). The fixed point converges in 11 iterations.

The loop closes on Cl, Na and electrons (§9). BMED_ACID and BMED_BASE close on mass with 2 M products.

Option chosen (P): Option B, anode Cl₂ sparged into the leach. Alternative Option A sends all anode Cl₂ to ALK_SCRUBBER and regenerates the oxidant as HCl + O₂; it needs about 16 kW of BMED DC instead of 6.6 kW, because each Cl₂ would cost two NaCl splits. Lever: eddy-current Al removal upstream of the shredder cuts the Al electron demand (32 % of total) and with it about 60 % of the BMED duty. The BMED rating is 9 kW (1.25 × 6.55 kW rounded up), above the 5–8 kW RECT-BMED study class; the RECTIFIER `continuous_kw` is updated to the Rev M average.

**Sodium.** Glass Na (cullet Na₂O, the only net Na input to the loop, 125.8 mol/d) is fixed in the pH-9 cake as sodium aluminosilicate, limited by Al (125.8 mol/d). This is RS-DSP; if the bench shows less Na fixation, the excess leaves with the diluate and the BMED duty rises by the same molar amount.

### 4.7 Glass digest (items 1, 4)

Rev L booked cullet both as an export (S08G 30 kg/d) and as digest feed. In Rev M the cullet is digested by S91 NaOH (593 mol/d, 297 L/d 2 M); the silicate liquor S92 goes to SALT_FEED and leaves as cake. S08G now carries only the insoluble fraction (4.5 kg/d).

### 4.8 Water: BMED_UPW_POLISH, VCD and export (items 1, 3)

VCD_TRAIN feed is S13 29.91 kg/d + S29 109.2 kg/d + S98 144.1 kg/d = 283.2 kg/d. VCD returns S28 brine to leach at 10 % of feed (28.32 kg/d), S25 distillate to BMED_UPW_POLISH (150.3 kg/d) and exports the excess as clean water S99 (104.6 kg/d). S25 covers S01 77.28 kg/d (farm make-up 74.9 + ZnBr₂ make-up 2.37 kg/d), fab UPW 60 kg/d, REMIN 10 kg/d and the 2 % reject. BMED_UPW_POLISH, HDR_UPW and VCD_TRAIN close.

VCD capacity (item 3): the Rev M feed is 0.283 m³/d against the issued 0.11 m³/d. The VCD rating is re-issued at 0.40 m³/d (feed × 1.25, rounded up); average power 0.201 kW at 17 kWh/m³.

The S99 export (104.6 kg/d) is the MVS clean-water surplus.

### 4.9 Electrical bus: SOL_ARK_60K, RECTIFIER, LOAD_AGG (items 1, 2)
New S93 PV_ARRAY → SOL_ARK_60K (12.39 kW, 70 kWp × 1550 kWh/kWp·yr). S17 is the daily-average rectifier draw (13.48 kW = (EW 5.75 + BMED 6.55 + PK 0.5) / 0.95), replacing the 50 kW peak. S20 is reversed to SOL_ARK_60K → GROW_BED (5 kW). New S94 SOL_ARK_60K → LOAD_AGG (31.13 kW) carries the itemized process and life loads:

| Load | kW |
|---|---|
| MFG_SHOP | 12.000 |
| HABITATION | 3.000 |
| CRYO cold head (CRYO_H2 node 4.0 kW) | 4.000 |
| LEACH_CSTR_1 parasitics | 2.000 |
| WAFER_FAB | 2.000 |
| WET_BENCH | 1.000 |
| AFTERBURNER | 0.500 |
| ALK_SCRUBBER | 0.400 |
| H2_DRYER | 0.300 |
| MEOH_SYNTH | 0.500 |
| NUTRIENT_DOSE | 0.100 |
| GLASS_RINSE | 0.200 |
| GLASS_MILL | 0.800 |
| GLASS_BURNOUT electric trim | 0.238 |
| LITHO_STUB | 0.100 |
| ELECTRODE_COAT | 0.300 |
| BLOW_MOLD | 0.500 |
| SOLAR_PV_CELL | 1.000 |
| UPW polish (EDI) | 0.100 |
| VCD_TRAIN | 0.201 |
| ASU compressor | 0.118 |
| hydro pump | 0.545 |
| HX-4 trim | 0.000 |
| HX-5 trim | 0.430 |
| HX-6 trim | 0.802 |
| GEO_HP (idle) | 0.000 |

Supply on the design day: PV 12.39 kW, ZnBr₂ discharge 5.0 kW, hydro 0.29 kW, MEOH_FC 0.1007 kW. Demand including ZnBr₂ charge, S17, S20, S94 and the 1.49 kW conversion loss: 57.76 kW. The utility import at the GRID port closes the bus by difference: **39.99 kW average (960 kWh/d)**. SOL_ARK_60K closes with that term; the MVS energy-surplus criterion is not met. Closing it on site requires about 226 kWp of additional PV at the sandbox yield, or load reduction (MFG_SHOP 12 kW is the largest item). This is recorded in §7.

### 4.10 ZnBr₂ humidity (item 1)

Rev L condensed the purge-air saturation water (8.44 kg/d) back into the electrolyte. A ZnBr₂ electrolyte at water activity 0.78 loses water to purge air; it does not gain it. With the purge outlet at 0.5 approach to equilibrium humidity, the electrolyte loses 2.37 kg/d to the purge, replaced from HDR_UPW. S69B is re-rated to 0.0473 kg/d and ZNBR2 closes on mass without accumulation.

### 4.11 AFTERBURNER CO₂ (item 1)

S11 farm trim (0.8 kg/d wet, 42 % DM, 45 % C) adds 0.554 kg/d CO₂ and 0.068 kW to the afterburner. It is folded into the CO₂ basis: 15.554 kg/d. S67 is 242.5 kg/d, S67B 13.22 kg/d, S85 12.08 kg/d and S89 16.1 kg/d. AFTERBURNER, CRYO_CO2 and HDR_CO2 close on CO₂.

### 4.12 Other item-3 findings

- **27.94 kg/d sink residue.** Unleached metal, fillers and the unassigned 15 % assay leave GLASS_RINSE as S96 to BOUNDARY_EXPORT (34.29 kg/d with drained moisture). Disposal or sale requires leachate characterization (RS-RESIDUE-TCLP).
- **S16 composition.** S16 is redefined as harvest rinse liquor: entrained electrolyte plus two displacement rinse volumes (12.6 kg/d). The 12 kg/d metal that Rev L returned to leach is product; DOCK_EXPORT_TBD goods rise to 40.75 kg/d.
- **S68 text.** S68 carries "CRYO AHU coil condensate (acid trace, flue-cap zone)" (173.7 kg/d); the route to LEACH_CSTR_1 stays (acid trace, not UPW quality).
- **CONTINUOUS_RECYCLE velocity.** IA-REC-01 is 3.72 m³/d of filtered liquor. DN50 gave 0.02 m/s. Rev M issues DN15 CPVC at 0.22 m/s with a 25 µm cartridge upstream; the line carries clear liquor, so no solids-carrying velocity applies. CONTINUOUS_RECYCLE still discharges only to LEACH_CSTR_1 and stays off the heat ladder.

### 4.13 Leach heater HX-5 (item 4)
Rev L rated HX-5 at 6.353 kW from a 35 °C regen return of the whole 4284 kg/d recirculation. Rev M re-derives the leach energy balance at 77.5 °C:

| Term | kW | Note |
|---|---|---|
| Warm returns below 77.5 °C (IA-REC-01 at 48.0 °C, float at 60 °C, S19) | 5.195 | mixed recycle temperature from raffinate 50 °C, BMED HCl 35 °C, CRU 40 °C |
| Cold make-up (S68, S10, S16, S39, S72, S28) | 0.852 | 10–40 °C |
| Shell, shredder and purge losses | 1.118 | AQS-DUTY-008 |
| Metal dissolution exotherm, lowest credit | −2.562 | AQS-DUTY-008 leach basis |
| **Rating case** (no Q3, no Q4 preheat, no oxidant credit) | **4.602** | |
| Q4 make-up preheat HX-9 (S100) | −0.532 | cold streams to 55 °C |
| Oxidant credit above the rating case | −3.640 | Cl₂ re-absorption returns the EW chemical energy; O₂ reduction |
| **Normal duty** | **0.430** | |

HX-5 rating: ceil(4.602 × 1.25) = **6.0 kW** electric trim heater (Rev L 6.353 kW unissued). HL-Q3-A/B-HX5 rated duty is 5.753 kW. On the design day Q3 serves HX-4 (0.242 kW) and HX-6 (0.579 kW) first and has nothing left for HX-5; the normal HX-5 trim is 0.430 kW.

The rating case covers loss of the Cl₂ sparge, where ALK_SCRUBBER takes all anode Cl₂ and needs a NaOH day tank. Startup from 25 °C (about 2.7 m³ liquor, 153 kWh) takes about 30 h at the rated heater less the 1.1 kW shell, shredder and purge losses.

Alternative (not adopted): a recuperator R-1 between raffinate and recycle return. Rejected because CONTINUOUS_RECYCLE is locked off the heat ladder.

### 4.14 Digest heater HX-6 (item 4)

GLASS_DIGEST at 80 °C: AQS-DUTY-008 duty 1.663 kW. HX-10 preheats the caustic from Q4 (0.282 kW, S101), so the normal duty is 1.381 kW: 0.579 kW from Q3 and 0.802 kW electric trim. HX-6 rating: ceil(1.663 × 1.25) = **2.5 kW** (rating case without HX-10 and Q3). The 1.5 kW study class is retired.

### 4.15 Q4 surplus (item 5)

Q4 sources at normal duty: ladder 4.244 kW + S54 0.100 + S63 0.017 + S80 0.127 = 4.488 kW (S53 is 0 with the fuel cell on standby; Rev L surplus 3.32 kW). Sinks: life load 3.0 kW, HX-9 leach make-up preheat (S100 0.532 kW), HX-10 caustic preheat (S101 0.282 kW), and the remainder to the borefield (S102 Q4_BUS → GEO_GHEX, 0.674 kW, by difference). Q4_BUS remains the Q4 water header only; HX-9 and HX-10 are on Q4_BUS branches, not HL-* edges. The ORC pad stays reserved at 0 kW.

Borefield recharge at 0.67 kW continuous into a 100 m bore raises the ground temperature by about 5 K over 10 years (line-source estimate, k = 2 W/m·K). This favours GEO_HP in winter; it is RS-GHEX-RECHARGE because the field data are design_survey_locked.

### 4.16 S87/S88 (item 7)

Both are retired; neither carries a physical flow.

- S87 GROW_BED → CRYO_O2 (surplus O₂ capture). Photosynthetic O₂ is 0.806 kg/d, a 0.003 % enrichment of the farm exhaust air at the DUTY-009 outdoor-air rate. Recovering it is air separation, which the cold box already performs on intake air, and any endpoint would send farm air into a process header.
- S88 CRYO_N2 → GROW_BED (N₂ make-up). GROW_BED has no N₂ demand; it is ventilated with outdoor air. The only candidate N₂ consumer is habitation cabin-leak make-up from HDR_N2 (not from the cryo residual). Reinstating that path needs the habitation envelope leak rate at operating pressure (RS-HAB-N2); with it, the edge is HDR_N2 → HABITATION at the leak rate.

### 4.17 Routing summary (item 2)

| Decision | Rev M | Status |
|---|---|---|
| S05/S64 duplicate | S05 retired; S64 carries H₂ | final |
| CRYO_H2 dispatch | all H₂ to MeOH; FC/GEN standby | provisional |
| S12 destination | GREY_TREAT | final |
| S56/S86 duplicate | S86 retired | final |
| BMED/CRU edges | IA-BMED-03/04 from SALT_FEED; IA-BMED-05…10, S91, S92, S97, S98 added | provisional (Option B) |
| S20 direction | SOL_ARK_60K → GROW_BED | final |

## 5. Provisional decisions (for review)

| # | Decision | Alternatives |
|---|---|---|
| P1 | CRYO_H2 dispatch: all H₂ to MeOH, FC/GEN standby with 8 h inventory | H₂ to FC store only |
| P2 | Chloride Option B: Cl₂ sparged into leach (0.95), O₂ sparge for the deficit | Option A all Cl₂ to ALK (≈16 kW BMED); eddy-current Al removal upstream |
| P3 | Glass Na fixed as sodium aluminosilicate in the pH-9 cake | Na to diluate and BMED |
| P4 | Cullet digested; S08G insolubles only | Export cullet, retire GLASS_DIGEST from the design day |
| P5 | HX-5 rating case excludes oxidant credit; normal includes it | Rate on normal with Cl₂ interlock |
| P6 | Q4 remainder to borefield (S102) | Dry cooler; ORC (pad reserved) |
| P7 | S16 as rinse liquor; 12 kg/d metal to dock goods | Metal back to leach (Rev L) |
| P8 | VCD re-issued at 0.40 m³/d | — |
| P9 | Utility import closes the electrical bus | Additional PV / load shedding |
| P10 | S87/S88 retired | Reinstate S88 after RS-HAB-N2 |

## 6. Required studies

| ID | What is needed |
|---|---|
| RS-LEACH-H2 | Leach lid H₂ under oxidant upset (Cl₂ sparge or O₂ off): purge dilution to < 25 % LFL and interlock |
| RS-HAB-N2 | Habitation envelope leak rate at operating pressure; sets HDR_N2 → HABITATION make-up (S88) |
| RS-RESIDUE-TCLP | S96 sink residue and S97 cake leachate characterization before disposal or sale |
| RS-DSP | Bench confirmation that glass Na leaves in the pH-9 cake as sodium aluminosilicate (Na ≤ Al) |
| RS-CL2-SPARGE | Anode Cl₂ absorption in LEACH_CSTR_1 (0.95 basis) and the Fe³⁺ effect on EW CE |
| RS-GHEX-RECHARGE | Borefield temperature drift under S102 continuous recharge |
| RS-CAD-HYDRO | Pumped-hydro massing (CATCH_TANK, HYDRO_SET, ROOF_TANK, ARRAY_ROOF) against the cores and corridors: no 12 × 8 m slot exists at L-2 with SHAFT_PENSTOCK connected; needs a hydro layout decision |
| RS-CAD-YARD | GH_ENV_W against the yard rows, and yard sub-features (ATS, UTIL_ROUGH_*, ZnBr₂ tanks, GEN_*/FC_* skids, CLEAR_*/KO_*) not moved with their parents in seed Rev F |
| RS-CAD-LEGACY | L-1 corridors drawn through the process aisle; oil-line, wet-train and PK legacy massing; FAB_PREP inside CORE_PROCESS; GROW_BED against STAIR_S2/TOILET; MFG and cryo legacy massing; OVERFLOW_APRON_E/W drawn 3 m inside the walls |

## 7. What still blocks a loops_closed review

1. Energy surplus: the design day imports 40.0 kW average from the utility.
2. REQ-MEOH-FC 0.5–2 kW is not met (MEOH_FC 0.1007 kW, H₂-limited).
3. The provisional decisions in §5 and the required studies in §6.
4. CAD clearance on the Rev M placement copy. Seed Rev I (`placement_seed.json`) moves 24 origins: 71 seed boxes, 2485 pairs, 0 intersections and 0 pairs under 600 mm within a level (1100 mm at BACKUP_GEN and FUEL_CELL); Rev L had 20 pairs under 600 mm. `plant_placed_2026-10-08_revM.FCStd` is derived from the revK copy by `apply_placement.py` (39 applied, 9 resized, 0 gaps); `plant.FCStd` is not touched. Every moved Feature has 0 intersections and at least 600 mm to same-level equipment, except MET_AHU and MET_SCRUB, which sit on OVERFLOW_APRON_E as drawn. An all-pairs common-volume check on the copy (423 solids) gives 1016 intersecting pairs (1075 on revK): 598 allowed (assembly, nozzle, penetration, containment), 210 for review and 208 clashes (245 on revK). The remaining clashes are legacy massing in RS-CAD-HYDRO, RS-CAD-YARD and RS-CAD-LEGACY (§6); details in the unpublished planning note REV_M_CLOSURE.

## 8. Node balances

Status: closed = within ±1 % with independently derived terms; closed (one term by difference) = one term sets the balance. Units: mass kg/d, energy kW.

| Node / layer | In | Out | Residual % | Status |
|---|---|---|---|---|
| ACID_POLISH_SCRUB/mass | 3.751e+04 | 3.751e+04 | +0.000 | closed |
| AFTERBURNER/energy | 2.812 | 2.812 | +0.000 | closed |
| AFTERBURNER/mass | 242.5 | 242.5 | +0.000 | closed |
| AFTERBURNER_FLUE/mass | 242.5 | 242.5 | +0.000 | closed |
| ALK_SCRUBBER/mass | 3.756e+04 | 3.756e+04 | +0.000 | closed |
| BACKUP_GEN/mass | 0 | 0 | +0.000 | closed |
| BLACK_DIGEST/mass | 22.23 | 22.22 | +0.000 | closed |
| BMED_ACID/mass | 505.8 | 505.8 | +0.001 | closed |
| BMED_BASE/mass | 528.8 | 529.3 | -0.101 | closed |
| BMED_UPW_POLISH/mass | 150.3 | 150.3 | -0.001 | closed (one term by difference) |
| C29_RECYCLE/mass | 1.405 | 1.405 | +0.000 | closed |
| CATCH_TANK/mass | 2e+05 | 2e+05 | +0.000 | closed |
| COLD_MILL/mass | 4.392 | 4.392 | +0.000 | closed |
| CONTINUOUS_RECYCLE/mass | 3904 | 3904 | -0.000 | closed |
| CRU/mass | 50.14 | 50.14 | +0.000 | closed |
| CRYO_CO2/mass | 15.58 | 15.58 | -0.001 | closed (one term by difference) |
| CRYO_H2/mass | 0.3221 | 0.3221 | +0.000 | closed |
| CRYO_N2/mass | 1.5 | 1.5 | +0.000 | closed |
| CRYO_O2/mass | 7.671 | 7.671 | +0.000 | closed |
| EW_1/energy | 6.066 | 6.067 | -0.016 | closed |
| EW_1/mass | 4284 | 4284 | -0.000 | closed |
| EW_2/mass | 4280 | 4280 | -0.000 | closed |
| EW_3/mass | 4276 | 4276 | +0.000 | closed |
| EW_4/mass | 4251 | 4251 | -0.000 | closed |
| EW_5/mass | 4246 | 4246 | +0.000 | closed |
| EW_6/mass | 4241 | 4241 | +0.000 | closed |
| EW_7/mass | 4235 | 4235 | +0.000 | closed |
| EW_8/mass | 4151 | 4151 | -0.000 | closed |
| EW_9/mass | 4146 | 4146 | +0.013 | closed |
| FAB_UPW_TANK/mass | 60 | 60 | +0.000 | closed |
| FLOAT_SINK/mass | 454.7 | 454.7 | -0.001 | closed |
| FLUE_KO/mass | 242.5 | 242.5 | -0.000 | closed |
| FUEL_CELL/mass | 0 | 0 | +0.000 | closed |
| GAS_ATOMIZER/mass | 3.555 | 3.555 | +0.000 | closed |
| GEO_GHEX/energy | 0.6738 | 0.6738 | +0.000 | closed (one term by difference) |
| GLASS_BURNOUT/energy | 0.87 | 0.87 | +0.000 | closed |
| GLASS_BURNOUT/mass | 30 | 30 | +0.000 | closed |
| GLASS_DIGEST/energy | 1.664 | 1.663 | +0.042 | closed |
| GLASS_DIGEST/mass | 350.8 | 350.8 | +0.000 | closed |
| GLASS_MILL/mass | 36.82 | 36.82 | +0.000 | closed |
| GLASS_RINSE/mass | 71.11 | 71.11 | +0.000 | closed |
| GREY_TREAT/mass | 114.9 | 114.9 | +0.004 | closed (one term by difference) |
| GROW_BED/mass | 114.3 | 114.3 | +0.000 | closed (one term by difference) |
| H2_DRYER/mass | 0.8536 | 0.8536 | +0.000 | closed |
| HABITATION/mass | 135.8 | 135.8 | -0.001 | closed (one term by difference) |
| HDR_CO2/mass | 16.1 | 16.1 | +0.000 | closed (one term by difference) |
| HDR_H2/mass | 0.8535 | 0.8536 | -0.012 | closed |
| HDR_O2/mass | 4.311 | 4.311 | +0.000 | closed |
| HDR_UPW/mass | 77.28 | 77.28 | +0.000 | closed (one term by difference) |
| HX8/energy | 4.572 | 4.572 | +0.000 | closed |
| LEACH_CSTR_1/energy | 0.9624 | 0.9624 | +0.000 | closed |
| LEACH_CSTR_1/mass | 4805 | 4805 | +0.000 | closed (one term by difference) |
| LOAD_AGG/energy | 31.13 | 31.13 | +0.000 | closed |
| MEOH_FC/energy | 0.397 | 0.397 | +0.000 | closed |
| MEOH_FC/mass | 4.299 | 4.299 | +0.002 | closed |
| MEOH_FERM/mass | 0.36 | 0.36 | +0.000 | closed (one term by difference) |
| MEOH_SYNTH/mass | 2.666 | 2.666 | +0.004 | closed |
| MEOH_TANK/mass | 1.721 | 1.721 | -0.000 | closed |
| MET_MELT/mass | 4.392 | 4.392 | +0.000 | closed |
| MET_SCRUB/mass | 7.161e+04 | 7.161e+04 | +0.000 | closed |
| MFG_SHOP/mass | 66.89 | 66.89 | +0.000 | closed (one term by difference) |
| NCG_HEADER/mass | 5 | 5 | +0.000 | closed |
| NORTH_DOCK/mass | 40.75 | 40.75 | +0.000 | closed (one term by difference) |
| NUTRIENT_DOSE/mass | 22.19 | 22.19 | +0.000 | closed |
| OIL_DRYER/energy | 0.242 | 0.242 | +0.000 | closed |
| OIL_DRYER/mass | 40.5 | 40.5 | +0.000 | closed |
| OIL_FRAC/mass | 29.91 | 29.91 | -0.000 | closed |
| OIL_PYRO/mass | 34.4 | 34.4 | +0.000 | closed |
| POLISH_BANK/mass | 4140 | 4140 | -0.000 | closed (one term by difference) |
| PROD_C29/mass | 1.405 | 1.405 | +0.000 | closed |
| Q1_A/energy | 0.553 | 0.553 | +0.000 | closed |
| Q1_B/energy | 0.553 | 0.553 | +0.000 | closed |
| Q2_A/energy | 0.724 | 0.7246 | -0.083 | closed |
| Q2_B/energy | 0.724 | 0.7246 | -0.083 | closed |
| Q3_A/energy | 0.603 | 0.6031 | -0.017 | closed |
| Q3_B/energy | 0.603 | 0.6031 | -0.017 | closed |
| Q4_A/energy | 2.286 | 2.286 | +0.000 | closed |
| Q4_B/energy | 2.286 | 2.286 | +0.000 | closed |
| Q4_BUS/energy | 4.488 | 4.488 | +0.000 | closed (one term by difference) |
| RECTIFIER/energy | 13.48 | 13.48 | -0.001 | closed |
| REMIN/mass | 10 | 10 | +0.000 | closed |
| ROOF_TANK/mass | 2.001e+05 | 2.001e+05 | +0.000 | closed |
| SALT_FEED/mass | 1270 | 1270 | -0.001 | closed (one term by difference) |
| SOL_ARK_60K/energy | 57.76 | 57.76 | -0.000 | closed (one term by difference) |
| TERRACE_IRRIG/mass | 0 | 0 | +0.000 | closed |
| VCD_TRAIN/mass | 283.2 | 283.2 | -0.000 | closed (one term by difference) |
| WAFER_FAB/mass | 5.797 | 5.797 | +0.000 | closed |
| WET_BENCH/mass | 78.35 | 78.35 | +0.000 | closed (one term by difference) |
| WIRE_DRAW/mass | 4.379 | 4.379 | +0.000 | closed |
| WS_KOH/mass | 0.3073 | 0.3073 | +0.000 | closed (one term by difference) |
| WS_NITRIC/mass | 0.7518 | 0.7518 | -0.000 | closed (one term by difference) |
| ZNBR2/energy | 6.667 | 6.667 | -0.000 | closed |
| ZNBR2/mass | 854.8 | 854.9 | -0.000 | closed |
| ZNBR2_BR2_REGEN/mass | 854.9 | 854.8 | +0.000 | closed |

## 9. Species checks

| Check | In | Out | Status | Note |
|---|---|---|---|---|
| AFTERBURNER/CO2 | 15.554 | 15.554 | closed | S11 trim carbon folded into the S67 CO2 basis (Rev M) |
| CRYO_CO2/CO2 | 15.585 | 15.585 | closed (one term by difference) |  |
| HDR_CO2/CO2 | 16.101 | 16.101 | closed |  |
| H2_DRYER/H2 | 0.3221 | 0.3221 | closed |  |
| CRYO_H2/H2 | 0.3221 | 0.3221 | closed |  |
| LEACH/electrons | 2231.5 | 2231.5 | closed | oxidant e- (Cl2 sparge + chlorate + O2) = metal e- dissolved (deposited + undeposited + Al) |
| LEACH_LOOP/Cl | 2724.5 | 2724.5 | closed | Cl in: BMED HCl + CRU (NaCl + NaClO3) + fab HCl on S10 + absorbed anode Cl2; out: anode Cl2 + bleed |
| SALT_FEED/Na | 1105.4 | 1103.8 | closed | Na in: bleed (CRU Na) + digest NaOH + glass Na + IA-BMED-10; out: NaCl to BMED (= Cl in bleed) + Na retained in the cake |
| BMED/pairs | 979.2 | 979.2 | closed | HCl made = NaOH made; NaOH uses: S91 + IA-BMED-07 + IA-BMED-10 + IA-BMED-02 |

## 10. Edge changes Rev L → Rev M

| Stream | From → To | Rev L | Rev M | Unit | Change |
|---|---|---|---|---|---|
| DOCK_EXPORT_TBD | NORTH_DOCK → BOUNDARY_EXPORT | 28.75 | 40.75 | kg/d | re-rated |
| HL-Q3-A-HX5 | Q3_A → LEACH_CSTR_1 | 7.941 | 5.753 | kW | re-rated |
| HL-Q3-B-HX5 | Q3_B → LEACH_CSTR_1 | 7.941 | 5.753 | kW | re-rated |
| IA-BMED-03 | SALT_FEED → BMED_ACID | 38.6 | 505.8 | kg/d | retargeted (Rev L CRU → BMED_ACID) |
| IA-BMED-04 | SALT_FEED → BMED_BASE | 40.36 | 528.8 | kg/d | retargeted (Rev L CRU → BMED_BASE) |
| IA-EW-01 | EW_1 → EW_2 | 4222 | 4280 | kg/d | re-rated |
| IA-EW-02 | EW_2 → EW_3 | 4160 | 4276 | kg/d | re-rated |
| IA-EW-03 | EW_3 → EW_4 | 4138 | 4251 | kg/d | re-rated |
| IA-EW-05 | EW_5 → EW_6 | 4128 | 4241 | kg/d | re-rated |
| IA-EW-06 | EW_6 → EW_7 | 4123 | 4235 | kg/d | re-rated |
| IA-EW-07 | EW_7 → EW_8 | 4051 | 4151 | kg/d | re-rated |
| IA-EW-08 | EW_8 → EW_9 | 4046 | 4146 | kg/d | re-rated |
| IA-EW-09 | EW_9 → POLISH_BANK | 3983 | 4140 | kg/d | re-rated |
| IA-EW-10 | EW_4 → EW_5 | 4133 | 4246 | kg/d | re-rated |
| IA-HDR-H2-01 | EW_7 → HDR_H2 | 1.6 | 0.7087 | kg/d | retargeted (Rev L EW_1 → HDR_H2) |
| IA-HDR-H2-02 | HDR_H2 → H2_DRYER | 4.8 | 0.8536 | kg/d | re-rated |
| IA-HDR-H2-03 | EW_3 → HDR_H2 | 1.6 | 0.1303 | kg/d | retargeted (Rev L EW_2 → HDR_H2) |
| IA-HDR-H2-04 | EW_9 → HDR_H2 | 1.6 | 0.0145 | kg/d | re-rated |
| IA-POL-02 | POLISH_BANK → CONTINUOUS_RECYCLE | 3754 | 3358 | kg/d | re-rated |
| IA-REC-01 | CONTINUOUS_RECYCLE → LEACH_CSTR_1 | 3978 | 3904 | kg/d | re-rated |
| S01 | BMED_UPW_POLISH → HDR_UPW | 95 | 77.28 | kg/d | re-rated |
| S07 | NUTRIENT_DOSE → GROW_BED | 2.5 | 22.19 | kg/d | re-rated |
| S08G | GLASS_DIGEST → BOUNDARY_EXPORT | 30 | 4.5 | kg/d | re-rated |
| S12 | HABITATION → GREY_TREAT | 110 | 114.9 | kg/d | retargeted (Rev L HABITATION → NUTRIENT_DOSE) |
| S13 | GROW_BED → VCD_TRAIN | 31.5 | 29.91 | kg/d | re-rated |
| S16 | MFG_SHOP → LEACH_CSTR_1 | 12 | 12.6 | kg/d | re-rated |
| S17 | SOL_ARK_60K → RECTIFIER | 50 | 13.48 | kW | re-rated |
| S20 | SOL_ARK_60K → GROW_BED | 5 | 5 | kW | retargeted (Rev L GROW_BED → SOL_ARK_60K) |
| S25 | VCD_TRAIN → BMED_UPW_POLISH | 161 | 150.3 | kg/d | re-rated |
| S28 | VCD_TRAIN → LEACH_CSTR_1 | 17.89 | 28.32 | kg/d | re-rated |
| S29 | GREY_TREAT → VCD_TRAIN | 104.5 | 109.2 | kg/d | re-rated |
| S30 | BLACK_DIGEST → NUTRIENT_DOSE | 16.43 | 22.17 | kg/d | re-rated |
| S45 | CRYO_H2 → BACKUP_GEN | 3.6 | 0 | kg/d | re-rated |
| S46 | BACKUP_GEN → NOX_SCRUB | 250.6 | 0 | kg/d | re-rated |
| S47 | BACKUP_GEN → SOL_ARK_60K | 2.5 | 0 | kW | re-rated |
| S49 | CRYO_H2 → FUEL_CELL | 4.8 | 0 | kg/d | re-rated |
| S50 | CRYO_O2 → FUEL_CELL | 38.4 | 0 | kg/d | re-rated |
| S51 | FUEL_CELL → SOL_ARK_60K | 4 | 0 | kW | re-rated |
| S52 | FUEL_CELL → VCD_TRAIN | 42.89 | 0 | kg/d | re-rated |
| S53 | FUEL_CELL → Q4_BUS | 1.142 | 0 | kW | re-rated |
| S54 | CRYO_HX_Q4 → Q4_BUS | 0.5448 | 0.1001 | kW | re-rated |
| S55 | CRYO_DED_COOL → CRYO_DED_COOL | 4.284 | 4.061 | kW | re-rated |
| S64 | H2_DRYER → CRYO_H2 | 4.8 | 0.3221 | kg/d | re-rated |
| S66 | ACID_POLISH_SCRUB → CRU | 27.36 | 0.3868 | kg/d | re-rated |
| S67 | AFTERBURNER_FLUE → FLUE_KO | 241.7 | 242.5 | kg/d | re-rated |
| S67B | FLUE_KO → CRYO_CO2 | 12.75 | 13.22 | kg/d | re-rated |
| S68 | CRYO_AHU → LEACH_CSTR_1 | 173.7 | 173.7 | kg/d | text |
| S69 | ZNBR2 → ZNBR2_BR2_REGEN | 852.5 | 854.9 | kg/d | re-rated |
| S69B | ZNBR2_BR2_REGEN → ZNBR2 | 8.487 | 0.0473 | kg/d | re-rated |
| S73 | CRYO_CO2 → MEOH_SYNTH | 6.9 | 2.344 | kg/d | re-rated |
| S74 | CRYO_H2 → MEOH_SYNTH | 0.94 | 0.3221 | kg/d | re-rated |
| S75 | MEOH_SYNTH → MEOH_TANK | 5 | 1.706 | kg/d | re-rated |
| S76 | MEOH_TANK → MEOH_FC | 5 | 1.721 | kg/d | re-rated |
| S79 | MEOH_FC → SOL_ARK_60K | 0.2925 | 0.1007 | kW | re-rated |
| S80 | MEOH_FC → Q4_BUS | 0.3689 | 0.127 | kW | re-rated |
| S81 | MEOH_FC → MEOH_COND | 5.622 | 1.935 | kg/d | re-rated |
| S82 | MEOH_FC → CRYO_CO2 | 6.875 | 2.364 | kg/d | re-rated |
| S83 | CRYO_O2 → HDR_O2 | 0 | 4.311 | kg/d | re-rated |
| S85 | CRYO_CO2 → HDR_CO2 | 11.62 | 12.08 | kg/d | re-rated |
| S89 | HDR_CO2 → GROW_BED | 15.64 | 16.1 | kg/d | re-rated |
| IA-BMED-05 | POLISH_BANK → SALT_FEED | — | 782.2 | kg/d | new |
| IA-BMED-06 | BMED_ACID → CONTINUOUS_RECYCLE | — | 495.8 | kg/d | new |
| IA-BMED-07 | BMED_BASE → ALK_SCRUBBER | — | 46.69 | kg/d | new |
| IA-BMED-08 | ALK_SCRUBBER → CRU | — | 49.75 | kg/d | new |
| IA-BMED-09 | CRU → CONTINUOUS_RECYCLE | — | 50.14 | kg/d | new |
| IA-BMED-10 | BMED_BASE → SALT_FEED | — | 161.6 | kg/d | new |
| S91 | BMED_BASE → GLASS_DIGEST | — | 320.8 | kg/d | new |
| S92 | GLASS_DIGEST → SALT_FEED | — | 326 | kg/d | new |
| S93 | PV_ARRAY → SOL_ARK_60K | — | 12.39 | kW | new |
| S94 | SOL_ARK_60K → LOAD_AGG | — | 31.13 | kW | new |
| S95 | HDR_O2 → LEACH_CSTR_1 | — | 4.311 | kg/d | new |
| S96 | GLASS_RINSE → BOUNDARY_EXPORT | — | 34.29 | kg/d | new |
| S97 | SALT_FEED → BOUNDARY_EXPORT | — | 91.08 | kg/d | new |
| S98 | SALT_FEED → VCD_TRAIN | — | 144.1 | kg/d | new |
| S99 | VCD_TRAIN → BOUNDARY_EXPORT | — | 104.6 | kg/d | new |
| S100 | Q4_BUS → LEACH_CSTR_1 | — | 0.5322 | kW | new |
| S101 | Q4_BUS → GLASS_DIGEST | — | 0.2822 | kW | new |
| S102 | Q4_BUS → GEO_GHEX | — | 0.6738 | kW | new |
| S05 | H2_DRYER → CRYO_H2 | 4.8 | — | kg/d | retired |
| S86 | CRYO_AHU → RELIEF_CRYO | 0.0 | — | kg/d | retired |
| S87 | GROW_BED → CRYO_O2 | placeholder | — | — | retired |
| S88 | CRYO_N2 → GROW_BED | placeholder | — | — | retired |

## 11. Reproduction

```
cd docs-authority
python3 _rev_m_closure_study.py --json out/revm.json          # report from Rev L base c4e1818
python3 _rev_m_closure_study.py --write ../flow_graph/plant_flow_graph.json
cd ../flow_graph && python3 export_candidate_mvs.py && python3 check_authority_contract.py
```
