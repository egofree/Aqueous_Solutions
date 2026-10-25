# Edge rating and node conservation

Document number: AQS-DUTY-010
Revision: A
Date: 2026-10-07
Authority: AQS-FLOW-GRAPH-001 Rev L; AQS-DUTY-008 Rev C; AQS-DUTY-009 Rev B. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue. Every present edge rated; placeholders closed; node conservation run | 2026-10-07 |

Superseded for graph Rev M by AQS-DUTY-011 (`REV_M_CLOSURE_DUTY.md`), which closes the §6 balances and the §7 blockers. This note and `_edge_rating_study.py` remain reproducible against the Rev L graph (commit c4e1818); run on a Rev M tree, the script loads that base.

Licence: CERN-OHL-S-2.0.

## 1. Purpose

Graph Rev K had 83 present edges with no rate and 20 placeholder edges. This note rates every edge and closes each placeholder, either as a present edge or as a retirement. It also checks conservation at every node. The calculation is `docs-authority/_edge_rating_study.py`. It reads the graph, imports AQS-DUTY-008 (`_hl_edges_study.py`) and AQS-DUTY-009 (`_co2_header_study.py`), and reproduces every number below. Run it on Rev K with `--write` and it produces the Rev L graph. Run it on Rev L and it reproduces Rev L byte for byte.

Each rated edge carries `rate_basis`, `rate_source`, `medium`, `conditions` and `rate_kind` in params. `rate_kind` is `derived`, or `by_difference` when the value closes a node balance. Each node with off-graph terms carries them in `params.balance_rev_l`.

## 2. Result

- Edges: 165 (163 present, 2 placeholder). Present edges with no rate: 0.
- Placeholders: 16 made present, 4 retired, S87/S88 demoted to placeholder on HOLD.
- New edge S90 HABITATION → HDR_CO2. Fixes to rated edges: S10 re-derived 10.0 -> 78.34 kg/d: Rev K value omitted S27 rinse and S09; S02 corrected 3.4 -> 3.36 kg/d (0.84 x 4); S79 corrected 1.0 -> 0.292 kW (fuel-limited by S76); S21 corrected 95 -> 120 kg/d (95 was the farm sump band); S14 corrected 4.2 -> 2.4 kg/d (S14X governs the surplus).
- Node conservation at ±1 %: 88 node-layer balances checked. 68 close with independently derived terms, 9 close with one term set by difference, and 11 do not close (§6). Species checks: CRYO_CO2, HDR_CO2 and GROW_BED CO₂ close. AFTERBURNER CO₂ and H2_DRYER H₂ do not close.
- `loops_closed` and every `*_on_site` flag stay false.

## 3. Basis and decisions

Units by layer: mass in kg/d (kg/h for air streams sized in m³/h), thermal in kW (HL-* edges keep the rated duty; conservation uses `duty_normal_kw`), electric in kW. Where two derivations conflict, the one stated as governing below is used, and the other is recorded as a check.

| Decision | Value | Basis |
|---|---|---|
| Design day | daily average, plant running normal, dry weather, one hydro cycle per day | Rev L basis |
| Feed | 150 kg/d wet reference feed; ELECTRICAL mixed WEEE row as the reference point. Feed class is not fixed: AQS-ASSAY-001 Rev C envelope | ELECTRICAL, FEED_ASSAY |
| Au/Ag leach | 0.90 | ELECTRICAL 0.85–0.95 mid |
| Leach slurry to float/sink | 20 wt % solids | Rev L |
| Float cake moisture | 7.5 kg/d (18.5 %) | AQS-DUTY-008 dryer basis governs |
| KO outlet | 30 °C saturated | Rev L |
| Ambient humidity ratio | 0.010 kg/kg | AQS-DUTY-008 |
| Farm air | 24 °C, 70 % RH | Rev L |
| Canopy ET | 3.3 L/m²·d on 28 m² | leafy crop under LED |
| VCD recovery / UPW reject | 0.90 / 0.02 | practice |
| Crew O₂ / RQ | 0.84 kg/p·d / 0.87 | NASA BVAD |
| Hab hygiene water | 30 L/p·d | LIFE_MEP fixture class |
| Food waste / CH₄ yield / MeOH conversion | 15 % / 0.30 Nm³ per kg VS / 70 % | practice |
| ASU | O₂ recovery 0.90, 2-stage to 6 bar a, η_is 0.70 | CRYO_COLD_BOX |
| Stirling cold head | 4.0 kW electric; 40 % heat-leak allowance | CONTINUOUS_KW 2–8 kW class |
| Genset | λ 2, 34.3 kg air per kg H₂, η 0.50 | stoichiometry; S47 |
| DMFC | 0.9 L MeOH per kWh | EFOY class |
| Wafer starts | 3/d; AUD §13 bands interpolated at 3 of 1–5 | ST-LITHO-01; AUD §13 |
| BMED | 12 kWh/d at 2.1 kWh/kg pair; products 2 M | ELECTRICAL |
| Acid polish | Cl₂ slip 1 %, blowdown at 15 % salts; 1500 m³/h at 50 °C | VENT_SCRUB_EQUIPMENT §4.1 |
| Br₂ regen purge | 30 m³/h, 10 ppmv Br₂ | VENT_SCRUB_EQUIPMENT §4.2 |
| CRYO AHU | 2592 m³/h, coil dew 10 °C | RELIEF_CRYO basis; §2.3 |
| MET LEV / aisle | 720 m³/h; 6 ACH × 300 m³ | VENT_SCRUB_EQUIPMENT §4.4 |
| Forming | Cu 50/50 wire/sheet; 10 % swarf; melt fume 0.3 %; atomizer fines 1 %; scrub 2 % solids; mist 2 g/kg | practice |
| Baghouse catch | 0.5 % of feed | shredder fines class |
| GEO_HP | COP 0.45 × Carnot 285 → 328 K = 3.43; lift only on Q4 deficit | HEAT_LADDER |
| ZnBr2 | 120 kWh/d, round trip 0.75 | ESS_DUTY_MATRIX; FLOW_BATTERY 70–80 % |
| Pumped hydro | 200 m³ × 18 m, 7 kWh recoverable, one cycle/d | ESS_DUTY_MATRIX |

## 4. Derivations

### EW / leach
- IA-EW-04 = 0.17 m³/h × 1050 kg/m³ × 24 = 4284 kg/d (AQS-DUTY-008 HX-5/HX-8 basis governs).
- Each cell: out = in − metal deposit − anode Cl₂ (n/2 per metal atom) − side-reaction H₂ and its Cl₂ − evaporation (7.30 kg/h bare × 0.2 ball blanket × 24 / 9 = 3.89 kg/d per cell). S08 42 kg/d is split by leach build-up (scale 42 / 45.18 = 0.930).

| Cell | Metal | In kg/d | Deposit | Cl₂ | H₂ | Out kg/d |
|---|---|---:|---:|---:|---:|---:|
| EW_1 | Au | 4284.0 | 0.0063 | 56.27 | 1.6 | 4222.2 |
| EW_2 | Ag | 4222.2 | 0.0251 | 56.28 | 1.6 | 4160.4 |
| EW_3 | Cu | 4160.4 | 8.7841 | 9.80 | 0 | 4137.9 |
| EW_4 | Pb | 4137.9 | 0.7111 | 0.24 | 0 | 4133.1 |
| EW_5 | Sn | 4133.1 | 0.7111 | 0.42 | 0 | 4128.1 |
| EW_6 | Ni | 4128.1 | 0.7111 | 0.86 | 0 | 4122.6 |
| EW_7 | Fe | 4122.6 | 29.6290 | 37.62 | 0 | 4051.5 |
| EW_8 | Cd | 4051.5 | 0.7111 | 0.45 | 0 | 4046.4 |
| EW_9 | Zn | 4046.4 | 0.7111 | 57.04 | 1.6 | 3983.2 |

- IA-POL-02 = raffinate 3983.2 − bleed 229.4 = 3753.7 kg/d. IA-REC-01 = IA-POL-02 + REGEN LEACH make-up 223.8 = 3977.5 kg/d. The bleed is set by the leach balance (level control).
- Leach solids: undissolved 90.94 kg/d (plastic 33.0 + sink 57.94); slurry liquor at 20 wt % = 363.8 kg/d; IA-WET-FLOAT-01 = liquor − cake moisture = 343.1 kg/d.
- S19 = 0.5 % × 150 = 0.75 kg/d. S68 = 2592 m³/h × 1.17 × (0.010 − 0.00766) × 24 = 173.7 kg/d. S72 = 2.44 kg/d.

### Oil line
- IA-OIL-01 = 0.22 × 150 = 33.0 kg/d. Net volatiles 27.5 = oil 22.5 + NCG 5.0; char 5.5 kg/d to the silicon arc.
- ASF fit: W(≤4)/W(≤28) = 5.0/27.5 gives α = 0.8456. C29+ recycled to extinction: R = 27.5 × (1 − W28)/W28 = 3977.511 kg/d = CUT-4 = C29_RECYCLE = C29_TO_PYRO. IA-OIL-02 = 27.5 + R = 28.90 kg/d.
- CUT-1 11.16 (C5–C10 + S38 + S39B solvent), CUT-2 8.41, CUT-3 3.95 (C19–C28 + S72B mist) kg/d. IA-OIL-03 = NCG_TO_AB = 5.0 kg/d.

### Glass
- IA-GLASS-01 = 30.0 dry cullet + 6.82 drained moisture = 36.82; IA-GLASS-02/03 = 30.0 kg/d dry (DUTY-008 burnout basis = silicate yield).

### BMED / polish
- BMED 12 kWh/d ÷ 2.1 kWh/kg = 5.71 kg/d pair = 75.2 mol/d. IA-BMED-03 38.60 kg/d of 2 M HCl, IA-BMED-04 40.36 kg/d of 2 M NaOH.
- S09 9.28 kg/d (SC-2 1:1:5, HCl volume = SC-2 share of S32, as 2 M). IA-BMED-01 0.646 and IA-BMED-02 0.270 kg/d, 1:1 molar with S34/S35 by resin exchange.
- S65 = 1500 m³/h at 50 °C saturated = 1563 kg/h. S66 = 1 % Cl₂ slip of 219 kg/d → NaCl + NaOCl at 15 % salts = 27.4 kg/d.

### Cryo / gas
- S02 = 0.84 × 4 = 3.36 kg/d. S90 = 3.36 × 0.87 × 44.01/32.00 = 4.021 kg/d. S89 = S85 + S90 = 15.637 kg/d; farm OA 933.5 m³/h.
- S15 = 0: the 0.806 kg/d photosynthetic O₂ leaves with farm exhaust; the hab is sealed and supplied by S02. S83 = S84 = 0 (HDR_O2/HDR_N2 have no consumer edge).
- ASU air 200.5 kg/d. S54 = compressor intercooler heat above the Q4 return + sieve TSA = 0.545 kW. S55 = 4.0 kW electric + 0.284 kW lift = 4.284 kW.
- S03 = 10 slm × 40 min × 3 starts × 1.25 g/L = 1.50 kg/d. S46 = 3.6 + 3.6 × 34.3 × 2 = 250.6 kg/d (10.44 kg/h). S52 = 4.8 × 18.015/2.016 = 42.89 kg/d.
- S56, S86, S24 = 0 (contingency). S70 = 1 %/d of the 5.21 kg dark buffer = 0.052 kg/d.

### Power / electrical / ESS
- IA-ESS-ZNBR2-DIS = 120/24 = 5.0 kW; CHG = 5.0/0.75 = 6.667 kW. IA-ESS-HYDRO-ELEC = 7/24 = 0.292 kW.
- S79 = 1.153 kW MeOH LHV × 0.254 = 0.292 kW. S20 = 5.0 kW (graph GROW_BED continuous_kw, LED canopy share; LED check 3.06 kW in the photoperiod, 2.04 kW daily average).
- S69 = 852.5 kg/d purge; S69B = 8.49 kg/d scrub liquor. S81 = 5.622 kg/d.

### Life / farm / hab
- S21 = 30 × 4 = 120 kg/d; S26 = 10 kg/d; S14 = 0.6 × 4 = 2.4 kg/d (production 4.2 = S14 + S14X).
- Farm water: ET 92.4 kg/d − exhaust vapor 60.9 kg/d (OA 933.5 m³/h light, 251.3 m³/h dark, Δw 0.0031) = S13 31.50 kg/d.
- S29 = 0.95 × 110 = 104.5; S25 = 0.90 × 178.9 = 161.0; S28 = 17.89 kg/d.
- S30 = 4 × (1.5 + 0.12 + 2.5) − 0.05 = 16.43; S78 = 0.15 × 2.4 = 0.36; S77 = 0.0146 kg/d.

### Fab
- S27 = 60 L/d (20–100 band at 3 of 1–5 starts). S31 1.5, S32 3.0, S33 3.0 kg/d dilute. S34 0.665 (2 M HNO₃), S34B 0.625, S35 0.2725, S36 0.01, S37 3.3, S38 0.006, S39 3.31, S39B 0.9875 kg/d.
- S10 = sum of bench inputs − S38 = 78.34 kg/d (by difference; Rev K 10.0 omitted S27 and S09).

### Dock / hydro
- IA-ESS-HYDRO-CHG/DIS = 200 000 kg/d each; S22/S23 = ρVgh 9.81 kWh/24 h = 0.409 kW hydraulic. S40, S41, S42 = 0 (dry design day); ROOF_TANK draws 120 kg/d from storage.
- DOCK_EXPORT_TBD = MFG goods 28.75 kg/d (by difference at MFG_SHOP).

### Heat ladder and Q4 peers
- S53 = (6.664 − 4.0) × (60 − 45)/(60 − 25) = 1.142 kW. S80 = 0.369 kW. S63 = 0.0171 kW.
- S06 = S44 = S43 = 0 on the design day (Q4 bus already above the 3.0 kW life load). Standby: 1.5 + 1.5 kW delivered, 2.126 kW ground heat at COP 3.43, inside GHEX 3.0 kW.

### MFG metals
- S57 4.379, S58 3.941, S59 3.953, S60 3.200, S61 1.197 kg/d. S71 = 720 m³/h = 852 kg/h; S62 = 1800 m³/h = 2131 kg/h; S72B 0.0158 kg/d.

## 5. Placeholder outcomes

| Edge | Outcome |
|---|---|
| IA-OIL-01 | present: dried float to pyrolyzer |
| IA-OIL-02 | present: pyrolysis volatiles to fractionator |
| IA-WET-FLOAT-01 | present: float/sink liquor return |
| S28 | present: VCD brine to REGEN LEACH |
| IA-BMED-03 | present: BMED acid loop make (energy basis) |
| IA-BMED-04 | present: BMED base loop make (energy basis) |
| IA-POL-02 | present: retargeted from the POLISH_BANK self-loop stub to POLISH_BANK -> CONTINUOUS_RECYCLE (raffinate return; STUDIES_COMPLETE precedent) |
| S13 | present: farm sump + farm AHU condensate to VCD |
| S25 | present: VCD distillate to UPW polish |
| S26 | present: REMIN drinking water to HAB |
| S29 | present: treated grey to VCD |
| S52 | present: PEM product water to VCD |
| IA-ESS-HYDRO-ELEC | present: hydro set to bus |
| IA-ESS-ZNBR2-CHG | present: ZnBr2 charge |
| IA-ESS-ZNBR2-DIS | present: ZnBr2 discharge |
| DOCK_EXPORT_TBD | present: MFG goods export (ID stays TBD: no invented DOCK S##) |
| IA-POL-01 | retired: flow does not exist: process liquor never enters the UPW polish skid; post-polish brine goes to the AEM bank -> K split -> BMED (notes/aem_bank.md). Raffinate return is IA-POL-02. |
| S48 | retired: flow does not exist at M1: ST-ORC-01 / GEO_GHEX Q_surplus_kW_th 0 -> P_ORC = eta x 0 = 0; GEO_ORC is a placeholder node. |
| IA-ESS-MEOH-CHG | retired: duplicates S75 (MEOH_SYNTH -> MEOH_TANK, 5.0 kg/d). |
| IA-ESS-MEOH-DIS | retired: duplicates S79 (MEOH_FC -> SOL_ARK_60K). |
| S87 | HOLD placeholder: the surplus O2 is the photosynthetic O2 (0.806 kg/d) in FARM AHU exhaust air at ~21 %. Capturing it means sending farm air into a process header (CRYO_O2), which the rule forbids, and it is already counted in S15. No clean endpoint. |
| S88 | HOLD placeholder: GROW_BED has no N2 demand (farm is outdoor-air ventilated at the DUTY-009 OA rate). Source rule is met (CRYO_N2, not the cryo residual) but there is no sink. No clean endpoint. |

Retired edges are kept whole, as JSON, in the graph field `notes_rev_l_retired`.

## 6. Nodes that do not close

| Node | Balance | Why it does not close | What would close it (decision needed) |
|---|---|---|---|
| H2_DRYER (mass, H₂) | in 4.8, out 9.6 (-50.0 %) | S05 and S64 both leave H2_DRYER for CRYO_H2 at the full 4.8 kg/d pool. Both are authority edges. Probable alias: one dryer, one product. | Retire one of S05/S64, or split the pool between them. Not changed in Rev L (authority values). |
| CRYO_H2 (mass) | in 9.6, out 9.34 (+2.7 %) | In is double-counted (above). With one 4.8 kg/d inlet, S45 3.6 + S49 4.8 + S74 0.94 = 9.34 kg/d are alternative dispatch cases (genset run vs fuel cell run vs MeOH synthesis), not simultaneous draws. | A dispatch rule on the design day: S49 4.8 with S45 = 0 (genset standby) and S74 = 0, or a stated split. The authority S49/S05/S64 values govern until then. |
| NUTRIENT_DOSE / GREY_TREAT (mass) | NUTRIENT_DOSE in 126.43, out 2.5 (+98.0 %); GREY_TREAT in 0, out 104.5 (-100.0 %) | S12 grey water (110 kg/d) lands on NUTRIENT_DOSE, while GREY_TREAT emits S29 (104.5 kg/d) with no grey inlet. Topology error. | Retarget S12 to GREY_TREAT; NUTRIENT_DOSE keeps S30 and S07, with digest-liquor surplus to VCD. Topology change, not done in Rev L. |
| BMED_UPW_POLISH (mass) | in 161, out 168.22 (-4.3 %) | S25 distillate 161.0 kg/d against S01 95 + fab UPW 60 + REMIN 10 + 2 % reject = 168.2 kg/d. Short 7.2 kg/d. | Route S68 (173.7 kg/d clean CRYO AHU condensate, now to leach) to VCD_TRAIN, or cut S01. Either is a topology or rate decision. |
| CRU (mass) | in 27.3623, out 78.9603 (-65.3 %) | CRU's only inlet is S66 (polish blowdown 27.4 kg/d). Its outlets IA-BMED-03/04 are the BMED acid and base loop make from the BMED energy basis (79.0 kg/d). The BMED salt feed (AEM brine from the leach bleed) and the water make-up are not edges. | Add the AEM-brine → BMED salt edge and the BMED water make-up, or re-scope CRU to chlorate only. |
| BMED_ACID (mass) | in 38.602, out 9.9228 (+74.3 %) | 38.6 kg/d of 2 M HCl made; on-graph users S09 and IA-BMED-01 take 9.9 kg/d. The rest is REGEN LEACH make-up with no edge. | Add BMED_ACID → CONTINUOUS_RECYCLE (or LEACH). Chloride capacity note below. |
| BMED_BASE (mass) | in 40.3583, out 0.27 (+99.3 %) | 40.4 kg/d of 2 M NaOH made; on-graph user IA-BMED-02 takes 0.27 kg/d. GLASS_DIGEST needs 23.7 kg/d NaOH (593 mol/d) against 75 mol/d of BMED base. | Add BMED_BASE → GLASS_DIGEST and a caustic source for the 518 mol/d gap. |
| Q4_BUS (energy) | in 6.3167, out 3 (+52.5 %) | Q4 sources at normal duty: ladder 4.244 + S53 1.142 + S54 0.545 + S63 0.017 + S80 0.369 = 6.317 kW, against the 3.0 kW life load. Surplus 3.32 kW with no sink (Rev K surplus was 1.24 kW, before the Q4 peers were rated). GEO_HP (S06/S44/S43) is 0 on the design day for the same reason. | A Q4 heat sink: dry cooler, or ORC on a real surplus (ST-ORC-01), or a larger life load. |
| SOL_ARK_60K (energy) | in 17.0842, out 56.6667 (-69.9 %) | S17 is the 50 kW rectifier peak, not a daily average (RECTIFIER continuous_kw is 12.0 kW; with it the bus is still 1.6 kW short). PV, grid and most process loads have no edges. S20 (5.0 kW farm load) is drawn GROW_BED → SOL_ARK, so it books as a source. | An electrical balance needs the PV/grid source edges, daily-average rectifier load and S20 reversed. |
| ZNBR2 (mass) | in 852.473, out 860.91 (-1.0 %) | S69B returns the purge's saturation water (8.44 kg/d) and NaOH make-up to the electrolyte. Steady accumulation; no electrolyte bleed on the graph. | Dry the purge air before the headspace, or add an electrolyte bleed edge. |
| AFTERBURNER (CO₂ species) | in 15.554, out 15.0 (+3.6 %) | S11 (0.8 kg/d farm trim at 42 % DM, 45 % C) burns in the afterburner and adds 0.554 kg/d CO₂ that is not in the 15.0 kg/d DUTY-008 basis carried by S67/S67B/S85. Total mass closes (+0.33 %). | Fold S11 carbon into the DUTY-008 CO₂ basis. It re-rates S67, S67B, S85, S89 and the Q1 source duty, so it needs a decision. |

Other findings (the node closes, but the input is suspect):

- S68 carries text says "flue condensate"; the endpoint is CRYO_AHU, so Rev L rates it as CRYO AHU coil condensate (173.7 kg/d, latent 4.93 kW, inside the 2–5 kW KO band). Text to fix.
- S56 and S86 are the same pair (CRYO_AHU → RELIEF_CRYO), both contingency, both 0. Probable alias.
- S16 (MFG_SHOP → LEACH, 12 kg/d) returns 29 % of the plated metal to leach. Its composition is unstated; S08 governs Rev L. It also feeds the HX-5 exotherm basis, so it is part of the leach-heater blocker.
- Faraday H₂ 4.8 kg/d (IA-HDR-H2-01/03/04 at 1.6 each): the side-reaction H₂ implies 168.8 kg/d anode Cl₂ at EW_1, EW_2 and EW_9. The EW energy cross-check gives about 0.37 kg/d. The authority value governs in Rev L; it drives the 224 kg/d REGEN LEACH return and the CRU/BMED gap.
- Chloride loop: EW evolves 219.0 kg/d Cl₂ + 4.8 kg/d H₂; the REGEN LEACH return is booked on the element basis (223.8 kg/d). BMED makes 75 mol/d HCl (2.7 kg/d HCl). The Cl loop is not closed by the available regen.
- FUEL_CELL energy closes, but S51 4.0 kW from S49 6.66 kW LHV is η 0.60 against the 0.50–0.55 PEM band. S51 is authority.
- S79 is fuel-limited at 0.293 kW (S76 5.0 kg/d at the EFOY-class 0.9 L/kWh). REQ-MEOH-FC 0.5–2 kW is not met.
- VCD feed is now 178.9 kg/d (0.18 m³/d); the issued VCD feed basis 0.11 m³/d is under-rated.
- Sink residue 27.94 kg/d (assay unassigned 15 % + unleached metal) has no product path in the ELECTRICAL yields table. It leaves GLASS_RINSE as reject.
- Leach-loop brine bleed 229.4 kg/d (by difference, level control) goes to the AEM bank with no edge; it is the BMED salt feed above.
- S20 direction: power flows SOL_ARK → farm; the edge is drawn the other way.
- CONTINUOUS_RECYCLE line envelope DN50 carries IA-REC-01 at 0.158 m³/h (0.02 m/s): below solids-carrying velocity.

## 7. What still blocks a loops_closed review

1. Leach heater rating. HX-5 duty 6.353 kW is all electric trim on the design day (Q3 serves HX-4 and HX-6 first and has nothing left). No issued rating; S16 composition and the Faraday H₂ basis feed it.
2. Digest heater class. GLASS_DIGEST 1.663 kW: 0.579 kW from Q3 and 1.084 kW electric trim. The trim fits the 1.5 kW study class, but the class is not issued as a rating.
3. Q4 surplus. Now 3.32 kW at normal duty with the Q4 peers rated (was 1.24 kW). No sink.
4. Pre-existing CAD overlaps on the placement copy: WS_* inside FAB blocks, H2_STACK through racks, FLUE_CAP × VJ_001, CATCH_TANK × cores; 20 unmoved seed pairs under 600 mm.
5. The eleven open node balances and the AFTERBURNER CO₂ species residual in the exceptions table.
6. S87/S88 on HOLD (placeholders).
7. Topology and alias fixes that need a decision: S05/S64 alias, CRYO_H2 dispatch rule, S12 → GREY_TREAT, S56/S86 alias, BMED/CRU edges, S20 direction.

## 8. Node balances

| Node / layer | In | Out | Residual % | Status |
|---|---:|---:|---:|---|
| ACID_POLISH_SCRUB/mass | 37,535 | 37,535 | -0.00 | closed |
| AFTERBURNER/energy | 2.744 | 2.744 | 0.00 | closed |
| AFTERBURNER/mass | 242.48 | 241.68 | 0.33 | closed |
| AFTERBURNER_FLUE/mass | 241.68 | 241.70 | -0.01 | closed |
| BACKUP_GEN/energy | 4.998 | 4.998 | 0.00 | closed |
| BACKUP_GEN/mass | 250.56 | 250.56 | 0.00 | closed |
| BLACK_DIGEST/mass | 16.48 | 16.48 | 0.00 | closed |
| BMED_ACID/mass | 38.60 | 9.923 | 74.30 | OPEN |
| BMED_BASE/mass | 40.36 | 0.270 | 99.33 | OPEN |
| BMED_UPW_POLISH/mass | 161.00 | 168.22 | -4.29 | OPEN |
| C29_RECYCLE/mass | 1.405 | 1.405 | 0.00 | closed |
| CATCH_TANK/mass | 200,000 | 200,000 | 0.00 | closed |
| COLD_MILL/mass | 4.392 | 4.392 | 0.00 | closed |
| CONTINUOUS_RECYCLE/mass | 3,978 | 3,978 | 0.00 | closed |
| CRU/mass | 27.36 | 78.96 | -65.35 | OPEN |
| CRYO_CO2/mass | 19.62 | 19.68 | -0.27 | closed |
| CRYO_H2/mass | 9.600 | 9.340 | 2.71 | OPEN |
| EW_1/energy | 6.066 | 6.067 | -0.02 | closed |
| EW_1/mass | 4,284 | 4,284 | 0.00 | closed |
| EW_2/mass | 4,222 | 4,222 | -0.00 | closed |
| EW_3/mass | 4,160 | 4,160 | 0.00 | closed |
| EW_4/mass | 4,138 | 4,138 | 0.00 | closed |
| EW_5/mass | 4,133 | 4,133 | -0.00 | closed |
| EW_6/mass | 4,128 | 4,128 | 0.00 | closed |
| EW_7/mass | 4,123 | 4,123 | -0.00 | closed |
| EW_8/mass | 4,051 | 4,051 | -0.00 | closed |
| EW_9/mass | 4,046 | 4,046 | -0.00 | closed |
| FAB_UPW_TANK/mass | 60.00 | 60.00 | 0.00 | closed |
| FLOAT_SINK/mass | 454.71 | 454.71 | -0.00 | closed |
| FLUE_KO/mass | 241.75 | 241.73 | 0.01 | closed |
| FUEL_CELL/energy | 6.664 | 6.664 | 0.00 | closed |
| FUEL_CELL/mass | 43.20 | 43.20 | 0.00 | closed |
| GAS_ATOMIZER/mass | 3.555 | 3.555 | 0.00 | closed |
| GLASS_BURNOUT/energy | 0.870 | 0.870 | 0.00 | closed |
| GLASS_BURNOUT/mass | 30.00 | 30.00 | 0.00 | closed |
| GLASS_DIGEST/energy | 1.664 | 1.663 | 0.06 | closed |
| GLASS_DIGEST/mass | 350.76 | 350.76 | 0.00 | closed |
| GLASS_MILL/mass | 36.82 | 36.82 | 0.00 | closed |
| GLASS_RINSE/mass | 71.11 | 71.11 | 0.00 | closed |
| GREY_TREAT/mass | 0 | 104.50 | -100.00 | OPEN |
| GROW_BED/mass | 114.25 | 113.84 | 0.35 | closed |
| H2_DRYER/mass | 4.800 | 9.600 | -50.00 | OPEN |
| HABITATION/mass | 135.76 | 135.76 | -0.00 | closed (one term by difference) |
| HDR_CO2/mass | 15.64 | 15.64 | 0.00 | closed |
| HDR_H2/mass | 4.800 | 4.800 | 0.00 | closed |
| HDR_UPW/mass | 95.00 | 95.00 | 0.00 | closed |
| HX8/energy | 4.572 | 4.572 | 0.00 | closed |
| LEACH_CSTR_1/energy | 6.353 | 6.353 | 0.00 | closed |
| LEACH_CSTR_1/mass | 4,801 | 4,801 | -0.00 | closed (one term by difference) |
| MEOH_FC/energy | 1.153 | 1.153 | 0.01 | closed |
| MEOH_FC/mass | 12.49 | 12.50 | -0.06 | closed |
| MEOH_FERM/mass | 0.360 | 0.360 | 0.00 | closed (one term by difference) |
| MEOH_SYNTH/mass | 7.840 | 7.811 | 0.37 | closed |
| MEOH_TANK/mass | 5.015 | 5.000 | 0.29 | closed |
| MET_MELT/mass | 4.392 | 4.392 | 0.00 | closed |
| MET_SCRUB/mass | 71,606 | 71,606 | 0.00 | closed |
| MFG_SHOP/mass | 54.29 | 54.29 | 0.00 | closed (one term by difference) |
| NCG_HEADER/mass | 5.000 | 5.000 | 0.00 | closed |
| NORTH_DOCK/mass | 28.75 | 28.75 | 0.00 | closed (one term by difference) |
| NUTRIENT_DOSE/mass | 126.43 | 2.500 | 98.02 | OPEN |
| OIL_DRYER/energy | 0.242 | 0.242 | 0.00 | closed |
| OIL_DRYER/mass | 40.50 | 40.50 | 0.00 | closed |
| OIL_FRAC/mass | 29.91 | 29.91 | -0.00 | closed |
| OIL_PYRO/mass | 34.40 | 34.40 | 0.00 | closed |
| POLISH_BANK/mass | 3,983 | 3,983 | 0.00 | closed (one term by difference) |
| PROD_C29/mass | 1.405 | 1.405 | 0.00 | closed |
| Q1_A/energy | 0.553 | 0.553 | 0.00 | closed |
| Q1_B/energy | 0.553 | 0.553 | 0.00 | closed |
| Q2_A/energy | 0.724 | 0.725 | -0.08 | closed |
| Q2_B/energy | 0.724 | 0.725 | -0.08 | closed |
| Q3_A/energy | 0.603 | 0.603 | -0.02 | closed |
| Q3_B/energy | 0.603 | 0.603 | -0.02 | closed |
| Q4_A/energy | 2.286 | 2.286 | 0.00 | closed |
| Q4_B/energy | 2.286 | 2.286 | 0.00 | closed |
| Q4_BUS/energy | 6.317 | 3.000 | 52.51 | OPEN |
| REMIN/mass | 10.00 | 10.00 | 0.00 | closed |
| ROOF_TANK/mass | 200,120 | 200,120 | 0.00 | closed |
| SOL_ARK_60K/energy | 17.08 | 56.67 | -69.85 | OPEN |
| TERRACE_IRRIG/mass | 0 | 0 | 0.00 | closed |
| VCD_TRAIN/mass | 178.89 | 178.89 | 0.00 | closed |
| WAFER_FAB/mass | 5.797 | 5.797 | 0.00 | closed |
| WET_BENCH/mass | 78.35 | 78.35 | 0.00 | closed (one term by difference) |
| WIRE_DRAW/mass | 4.379 | 4.379 | 0.00 | closed |
| WS_KOH/mass | 0.307 | 0.307 | 0.00 | closed (one term by difference) |
| WS_NITRIC/mass | 0.752 | 0.752 | -0.00 | closed (one term by difference) |
| ZNBR2/energy | 6.667 | 6.667 | -0.00 | closed |
| ZNBR2/mass | 852.47 | 860.91 | -0.98 | OPEN (steady accumulation) |
| ZNBR2_BR2_REGEN/mass | 852.47 | 852.47 | -0.00 | closed |
| AFTERBURNER/CO2 (species) | 15.55 | 15.00 | 3.56 | OPEN |
| CRYO_CO2/CO2 (species) | 19.62 | 19.68 | -0.27 | closed |
| HDR_CO2/CO2 (species) | 15.64 | 15.64 | 0.00 | closed |
| GROW_BED/CO2 (species) | 16.75 | 16.75 | 0.00 | closed |
| H2_DRYER/H2 (species) | 4.800 | 9.600 | 0.00 | OPEN |

## 9. Off-graph terms

| Node | Off-graph terms (daily average) |
|---|---|
| ACID_POLISH_SCRUB | in make-up water + NaOH 25.17 kg/d; out polished air to stack 37,508 kg/d |
| AFTERBURNER | in combustion air 236.68 kg/d; out flue to AFTERBURNER_FLUE 241.68 kg/d; in NCG heat release 2.744 kW; out shell loss 0.137 kW; out HX-7 to burnout 0.632 kW; out flue sensible to KO 0.869 kW |
| AFTERBURNER_FLUE | in flue from AFTERBURNER 241.68 kg/d |
| BACKUP_GEN | in combustion air 246.96 kg/d; in H2 LHV (S45) 4.998 kW; out radiator + exhaust heat 2.498 kW |
| BLACK_DIGEST | in black water 16.48 kg/d; out digester gas 0.0500 kg/d |
| BMED_UPW_POLISH | out fab UPW to FAB_UPW_TANK (S27) 60.00 kg/d; out potable to REMIN (S26) 10.00 kg/d; out polish reject 3.220 kg/d |
| COLD_MILL | in Cu charge from MFG_SHOP 4.392 kg/d; out mill trim to MFG_SHOP scrap bin 0.439 kg/d |
| CONTINUOUS_RECYCLE | in REGEN LEACH make-up (BMED HCl + CRU NaClO3) 223.80 kg/d |
| CRYO_CO2 | out boil-off to CRYO AHU (S70) 0.0521 kg/d |
| EW_1 | out Au cathode harvest (reported on S08) 0.0063 kg/d; out anode Cl2 to HDR_ACID_GAS 56.28 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d; in cell ohmic heat (9 cells) 1.938 kW; in feed sensible above 51 C 4.128 kW; out wall loss 0.533 kW; out evaporation (ball blanket) 0.962 kW |
| EW_2 | out Ag cathode harvest (reported on S08) 0.0251 kg/d; out anode Cl2 to HDR_ACID_GAS 56.28 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_3 | out Cu cathode harvest (reported on S08) 8.784 kg/d; out anode Cl2 to HDR_ACID_GAS 9.802 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_4 | out Pb cathode harvest (reported on S08) 0.711 kg/d; out anode Cl2 to HDR_ACID_GAS 0.243 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_5 | out Sn cathode harvest (reported on S08) 0.711 kg/d; out anode Cl2 to HDR_ACID_GAS 0.425 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_6 | out Ni cathode harvest (reported on S08) 0.711 kg/d; out anode Cl2 to HDR_ACID_GAS 0.859 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_7 | out Fe cathode harvest (reported on S08) 29.63 kg/d; out anode Cl2 to HDR_ACID_GAS 37.62 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_8 | out Cd cathode harvest (reported on S08) 0.711 kg/d; out anode Cl2 to HDR_ACID_GAS 0.449 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| EW_9 | out Zn cathode harvest (reported on S08) 0.711 kg/d; out anode Cl2 to HDR_ACID_GAS 57.05 kg/d; out evaporation to EW hood (ball blanket) 3.893 kg/d |
| FAB_UPW_TANK | in UPW from BMED_UPW_POLISH 60.00 kg/d |
| FLOAT_SINK | in leach train slurry (solids + liquor) 454.71 kg/d; out float cake to OIL_DRYER 40.50 kg/d; out sink cake to GLASS_RINSE 71.11 kg/d |
| FLUE_KO | out KO condensate 4.140 kg/d; out VSA tail gas to stack 224.84 kg/d |
| FUEL_CELL | out cathode excess O2 vent 0.307 kg/d; in H2 LHV (S49) 6.664 kW; out low-grade heat to ambient 1.522 kW |
| GAS_ATOMIZER | in blend charge from MFG_SHOP 3.555 kg/d; out off-spec to MFG_SHOP scrap bin 0.320 kg/d; out ultrafines to MET LEV (S71) 0.0356 kg/d |
| GLASS_DIGEST | in 2 M NaOH digest liquor 320.76 kg/d; out sodium silicate liquor (carries the caustic) 320.76 kg/d; in electric trim 1.084 kW; out digest duty 1.663 kW |
| GROW_BED | in UPW make-up from HDR_UPW (S01) 95.00 kg/d; out CO2 to farm exhaust 15.64 kg/d; out water vapor to farm exhaust 60.90 kg/d; out photosynthetic O2 to farm exhaust 0.806 kg/d |
| HABITATION | out black water to BLACK_DIGEST 16.48 kg/d; out hab AHU condensate + non-grey remainder 4.899 kg/d (by difference) |
| HDR_UPW | out farm make-up to GROW_BED 95.00 kg/d |
| LEACH_CSTR_1 | in fresh shredded feed 150.00 kg/d; in EW cathode harvest booked onto S08 42.00 kg/d; out slurry to FLOAT_SINK 454.71 kg/d; out purge vapor 20.30 kg/d; in electric trim (ladder short) 6.353 kW; out HX-5 duty (regen + shell + shred + purge - exotherm) 6.353 kW |
| MEOH_FC | in air O2 7.490 kg/d; in MeOH LHV (S76) 1.153 kW; out low-grade heat 0.492 kW |
| MEOH_FERM | out digestate + CO2 + water 0.345 kg/d (by difference) |
| MEOH_SYNTH | out synthesis water 2.811 kg/d |
| MET_MELT | in Cu charge from MFG_SHOP 4.392 kg/d; out melt fume to MET LEV (S71) 0.0132 kg/d |
| MET_SCRUB | in scrub make-up water 2.388 kg/d; out scrubbed air to stack 71,604 kg/d |
| MFG_SHOP | in scrap bin returns 1.197 kg/d; out charges to MET_MELT, COLD_MILL, GAS_ATOMIZER 12.34 kg/d; out finished goods to NORTH_DOCK 28.75 kg/d (by difference) |
| NORTH_DOCK | in finished goods from MFG_SHOP 28.75 kg/d |
| OIL_DRYER | in float cake 40.50 kg/d; out dryer vapor 7.500 kg/d; out dryer duty (evaporation) 0.242 kW; in electric trim 0 kW |
| OIL_PYRO | out char to silicon arc 5.500 kg/d |
| POLISH_BANK | out brine bleed to AEM bank -> K split -> BMED 229.45 kg/d (by difference) |
| Q4_BUS | out life load (hab + farm) 3.000 kW |
| ROOF_TANK | in inventory draw (dry design day, no rain) 120.00 kg/d |
| WAFER_FAB | in WS_SOLV solvent (litho/strip) 0.988 kg/d; out N2 purge to fab exhaust 1.500 kg/d |
| WET_BENCH | in resist from the litho track 0.0060 kg/d |
| WIRE_DRAW | out draw swarf to MFG_SHOP scrap bin 0.438 kg/d |
| WS_KOH | in KCl salt 0.0373 kg/d; out spent exchange brine 0.0348 kg/d (by difference) |
| WS_NITRIC | in NaNO3 salt 0.106 kg/d; out spent exchange brine 0.0868 kg/d (by difference) |
| ZNBR2 | in purge air (dry) 843.99 kg/d; out electrolyte accumulation (Na + water from S69B, less Br2) 8.440 kg/d; out round-trip loss 1.667 kW |
| ZNBR2_BR2_REGEN | in 2 M NaOH make-up 0.0003 kg/d; out scrubbed dry air to stack 843.99 kg/d |
| GLASS_RINSE | in sink cake 71.11 kg/d; out sink residue reject (no product path in yields table) 34.29 kg/d |
| GLASS_MILL | out mill dry-step vapor 6.818 kg/d |
| GLASS_BURNOUT | in HX-7 from afterburner 0.632 kW; in electric trim 0.238 kW; out q_offgas_kw 0.0300 kW; out q_end_kw 0.0500 kW; out q_cullet_residual_kw 0.0480 kW |
| REMIN | in UPW from BMED_UPW_POLISH 10.00 kg/d |
| Q1_A | out store standing loss 0.200 kW |
| Q2_A | out store standing loss 0.111 kW; out thermosyphon line loss on arrival 0.0106 kW |
| Q3_A | out store standing loss 0.174 kW; out thermosyphon line loss on arrival 0.0181 kW |
| Q4_A | out store standing loss 0.164 kW |
| Q1_B | out store standing loss 0.200 kW |
| Q2_B | out store standing loss 0.111 kW; out thermosyphon line loss on arrival 0.0106 kW |
| Q3_B | out store standing loss 0.174 kW; out thermosyphon line loss on arrival 0.0181 kW |
| Q4_B | out store standing loss 0.164 kW |

## 10. Totals by subsystem

Sums of edge rates, not net throughput. Air streams are included in the mass sums.

| Subsystem | Edges | Rated in Rev L | Σ mass kg/d | Σ thermal kW (normal) | Σ electric kW |
|---|---:|---:|---:|---:|---:|
| EW / leach | 19 | 17 | 49,592 | 0 | 0 |
| Oil line | 13 | 13 | 100.64 | 0 | 0 |
| Glass | 4 | 3 | 126.82 | 0 | 0 |
| BMED / polish | 9 | 8 | 37,882 | 0 | 0 |
| Cryo / gas headers | 31 | 12 | 623.02 | 4.284 | 0 |
| Power / electrical / ESS | 13 | 8 | 876.58 | 0 | 73.75 |
| Life / farm / hab | 14 | 10 | 443.20 | 0 | 0 |
| Fab | 11 | 11 | 154.02 | 0 | 0 |
| Dock / hydro | 8 | 8 | 400,029 | 0 | 0.818 |
| Heat ladder and Q4 peers | 36 | 7 | 0 | 20.04 | 0 |
| Other (MFG metals) | 7 | 7 | 71,621 | 0 | 0 |

## 11. Rated edges (Rev L, ★ = rated or re-rated in Rev L)

### EW / leach

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| IA-EW-01 ★ | EW_1 → EW_2 | chloride electrolyte overflow | mass | 4,222 | kg/d | EW_1 in 4284.0 - Au deposit 0.006 - anode Cl2 0.003 - side H2 1.60 - side Cl2 56.27 - evaporation 3.89 |
| IA-EW-02 ★ | EW_2 → EW_3 | chloride electrolyte overflow | mass | 4,160 | kg/d | EW_2 in 4222.2 - Ag deposit 0.025 - anode Cl2 0.008 - side H2 1.60 - side Cl2 56.27 - evaporation 3.89 |
| IA-EW-03 ★ | EW_3 → EW_4 | chloride electrolyte overflow | mass | 4,138 | kg/d | EW_3 in 4160.4 - Cu deposit 8.784 - anode Cl2 9.802 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-EW-04 ★ | LEACH_CSTR_1 → EW_1 | chloride leach liquor (HCl/NaClO3, metal chlorides) | mass | 4,284 | kg/d | DUTY-008 concentrate 0.17 m3/h x 1050.0 kg/m3 x 24 h |
| IA-EW-05 ★ | EW_5 → EW_6 | chloride electrolyte overflow | mass | 4,128 | kg/d | EW_5 in 4133.1 - Sn deposit 0.711 - anode Cl2 0.425 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-EW-06 ★ | EW_6 → EW_7 | chloride electrolyte overflow | mass | 4,123 | kg/d | EW_6 in 4128.1 - Ni deposit 0.711 - anode Cl2 0.859 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-EW-07 ★ | EW_7 → EW_8 | chloride electrolyte overflow | mass | 4,051 | kg/d | EW_7 in 4122.6 - Fe deposit 29.629 - anode Cl2 37.620 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-EW-08 ★ | EW_8 → EW_9 | chloride electrolyte overflow | mass | 4,046 | kg/d | EW_8 in 4051.5 - Cd deposit 0.711 - anode Cl2 0.449 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-EW-09 ★ | EW_9 → POLISH_BANK | chloride electrolyte overflow | mass | 3,983 | kg/d | EW_9 in 4046.4 - Zn deposit 0.711 - anode Cl2 0.771 - side H2 1.60 - side Cl2 56.27 - evaporation 3.89 |
| IA-EW-10 ★ | EW_4 → EW_5 | chloride electrolyte overflow | mass | 4,133 | kg/d | EW_4 in 4137.9 - Pb deposit 0.711 - anode Cl2 0.243 - side H2 0.00 - side Cl2 0.00 - evaporation 3.89 |
| IA-POL-02 ★ | POLISH_BANK → CONTINUOUS_RECYCLE | raffinate | mass | 3,754 | kg/d | raffinate 3983.2 less brine bleed 229.4 to the AEM bank (level control) |
| IA-REC-01 ★ | CONTINUOUS_RECYCLE → LEACH_CSTR_1 | regenerated leach liquor | mass | 3,978 | kg/d | recycle = IA-POL-02 3753.7 + REGEN LEACH make-up 223.8 (Cl2 + H2 removed at EW, element basis) |
| IA-WET-FLOAT-01 ★ | FLOAT_SINK → LEACH_CSTR_1 | leach liquor return | mass | 343.10 | kg/d | slurry liquor 363.8 (20 wt % on 90.94 kg/d undissolved) less cake moisture float 7.5 + sink 13.17 |
| S19 ★ | BAGHOUSE → LEACH_CSTR_1 | shredded feed fines | mass | 0.750 | kg/d | baghouse catch 0.5% of shredded feed |
| S28 ★ | VCD_TRAIN → LEACH_CSTR_1 | VCD brine | mass | 17.89 | kg/d | VCD brine 10% of feed |
| S68 ★ | CRYO_AHU → LEACH_CSTR_1 | AHU coil condensate (carries text says flue condensate: flag | mass | 173.67 | kg/d | CRYO AHU 2592 m3/h coil to 10.0 C dew (w 0.01 -> 0.00762); latent 4.93 kW |
| S72 ★ | MET_SCRUB → LEACH_CSTR_1 | metal fines in aqueous scrub liquor | mass | 2.437 | kg/d | fines 0.0487 kg/d (melt fume + atomizer ultrafines) in scrub blowdown at 2% solids |

### Oil line

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| C29_RECYCLE ★ | PROD_C29 → C29_RECYCLE | C29+ heavy cut | mass | 1.405 | kg/d | = CUT-4 |
| C29_TO_PYRO ★ | C29_RECYCLE → OIL_PYRO | C29+ heavy cut | mass | 1.405 | kg/d | = C29_RECYCLE |
| CUT-1 ★ | OIL_FRAC → PROD_C5_C10 | C5-C10 cut | mass | 11.16 | kg/d | ASF C5-C10 share 10.16 of net oil 22.5 + S38 + S39B solvent |
| CUT-2 ★ | OIL_FRAC → PROD_C11_C18 | C11-C18 cut | mass | 8.407 | kg/d | ASF C11-C18 share of net oil 22.5 |
| CUT-3 ★ | OIL_FRAC → PROD_C19_C28 | C19-C28 cut | mass | 3.947 | kg/d | ASF C19-C28 share 3.93 + S72B lube mist |
| CUT-4 ★ | OIL_FRAC → PROD_C29 | C29+ heavy cut | mass | 1.405 | kg/d | C29+ per pass, recycled to extinction |
| IA-OIL-01 ★ | OIL_DRYER → OIL_PYRO | dried plastic/paper float | mass | 33.00 | kg/d | dry plastic + paper float 0.22 x 150.0 |
| IA-OIL-02 ★ | OIL_PYRO → OIL_FRAC | pyrolysis vapor/condensate | mass | 28.90 | kg/d | per-pass volatiles: net 27.5 (oil 22.5 + NCG 5.0) + C29 recycle 1.40 (ASF alpha 0.8456) |
| IA-OIL-03 ★ | OIL_FRAC → NCG_HEADER | NCG (C1-C4 gas) | mass | 5.000 | kg/d | NCG C1-C4 = DUTY-008 afterburner fuel (CO2 15.0 / 3.002) |
| NCG_TO_AB ★ | NCG_HEADER → AFTERBURNER | NCG | mass | 5.000 | kg/d | = IA-OIL-03 (header pass-through) |
| S38 ★ | WET_BENCH → OIL_FRAC | resist and solvent waste | mass | 0.0060 | kg/d | ST-LITHO-01 resist waste 6 g/d |
| S39B ★ | WAFER_FAB → OIL_FRAC | solvent and photoresist | mass | 0.988 | kg/d | WS_SOLV 1.25 L/d (AUD s13 0.5-2 mid) x 0.79 |
| S72B ★ | MET_SCRUB → OIL_FRAC | organic mist (draw/roll lube) | mass | 0.0158 | kg/d | lubricant mist 2.0 g/kg formed x 7.89 kg/d |

### Glass

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| IA-GLASS-01 ★ | GLASS_RINSE → GLASS_MILL | rinsed cullet, drained | mass | 36.82 | kg/d | cullet 30.0 kg/d dry (DUTY-008 burnout basis = silicate yield) + drained moisture 6.82 |
| IA-GLASS-02 ★ | GLASS_MILL → GLASS_BURNOUT | milled cullet, dry | mass | 30.00 | kg/d | dry milled cullet = cullet basis |
| IA-GLASS-03 ★ | GLASS_BURNOUT → GLASS_DIGEST | burned cullet | mass | 30.00 | kg/d | burned cullet; organics burnout negligible (DUTY-008 off-gas 0.03 kW) |

### BMED / polish

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| IA-BMED-01 ★ | BMED_ACID → WS_NITRIC | HCl 2 M | mass | 0.646 | kg/d | 1:1 molar HCl for S34 (1.25 mol/d HNO3) at 2 M, resin exchange |
| IA-BMED-02 ★ | BMED_BASE → WS_KOH | NaOH 2 M | mass | 0.270 | kg/d | 1:1 molar NaOH for S35 (0.50 mol/d KOH) at 2 M, resin exchange |
| IA-BMED-03 ★ | CRU → BMED_ACID | HCl 2 M acid loop | mass | 38.60 | kg/d | BMED 12.0 kWh/d / 2.1 kWh/kg pair = 5.71 kg/d = 74.7 mol/d HCl as 2 M |
| IA-BMED-04 ★ | CRU → BMED_BASE | NaOH 2 M base loop | mass | 40.36 | kg/d | 74.7 mol/d NaOH as 2 M |
| S09 ★ | BMED_ACID → WET_BENCH | HCl 2 M | mass | 9.277 | kg/d | SC-2 1:1:5 -> HCl volume = H2O2 SC-2 share 1.5 L/d (37 % eq, 0.655 kg HCl) delivered as 2 M BMED acid |
| S25 ★ | VCD_TRAIN → BMED_UPW_POLISH | distillate | mass | 161.00 | kg/d | VCD recovery 90% of feed 178.9 (S13 + S29 + S52) |
| S65 ★ | ALK_SCRUBBER → ACID_POLISH_SCRUB | acid-gas residual in moist air | mass | 1,563 | kg/h | polish 1500.0 m3/h at 50.0 C saturated |
| S66 ★ | ACID_POLISH_SCRUB → CRU | hypochlorite/chloride scrub liquor | mass | 27.36 | kg/d | Cl2 slip 1% of 219.0 kg/d EW anode Cl2 -> NaCl + NaOCl 4.10 kg/d at 15% salts |

### Cryo / gas headers

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| S02 ★ | CRYO_O2 → HABITATION | O2 gas | mass | 3.360 | kg/d | 0.84 kg O2/p.d x 4 crew |
| S03 ★ | CRYO_N2 → WAFER_FAB | N2 gas | mass | 1.500 | kg/d | 10.0 slm x 40.0 min x 3 starts at 1.25 g/L |
| S24 ★ | H2_DRYER → RELIEF_H2 | relief gas | mass | 0 | kg/d | contingency relief only; no continuous flow on the design day |
| S46 ★ | BACKUP_GEN → NOX_SCRUB | engine exhaust (H2O, N2, O2, NOx) | mass | 250.56 | kg/d | S45 3.6 + air at lambda 2.0 (34.3 kg/kg stoich) |
| S55 ★ | CRYO_DED_COOL → CRYO_DED_COOL | glycol 30 % | mass/thermal | 4.284 | kW | Stirling reject = electric 4.0 + lift 0.284 kW (O2 + N2 liquefaction + 40% leak) |
| S56 ★ | CRYO_AHU → RELIEF_CRYO | relief gas | mass | 0 | kg/d | contingency relief only; no continuous flow on the design day |
| S70 ★ | CRYO_AHU_COND_CONDENSABLE → FLUE_KO | CO2 vapor (condensables) | mass | 0.0521 | kg/d | CRYO_CO2 boil-off 1%/d of the 5.21 kg dark buffer, vented via the cryo AHU condensables box |
| S83 ★ | CRYO_O2 → HDR_O2 | O2 gas | mass | 0 | kg/d | HDR_O2/HDR_N2 have no consumer edge; hab O2 is S02, N2 is S03. A non-zero fill would double count. |
| S84 ★ | CRYO_N2 → HDR_N2 | N2 gas | mass | 0 | kg/d | HDR_O2/HDR_N2 have no consumer edge; hab O2 is S02, N2 is S03. A non-zero fill would double count. |
| S86 ★ | CRYO_AHU → RELIEF_CRYO | relief gas | mass | 0 | kg/d | contingency relief only; no continuous flow on the design day |
| S89 ★ | HDR_CO2 → GROW_BED | CO2 gas | mass | 15.64 | kg/d | AQS-DUTY-009 Rev B: S85 11.616 + S90 4.021 |
| S90 ★ | HABITATION → HDR_CO2 | CO2 gas (desorbed, dry) | mass | 4.021 | kg/d | AQS-DUTY-010: S02 3.36 kg/d O2 x RQ 0.87 x 44.01/32.00 |

### Power / electrical / ESS

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| IA-ESS-HYDRO-ELEC ★ | HYDRO_SET → SOL_ARK_60K | AC | elec/ess | 0.292 | kW | 7.0 kWh recoverable per cycle over 24 h |
| IA-ESS-ZNBR2-CHG ★ | SOL_ARK_60K → ZNBR2 | DC | elec/ess | 6.667 | kW | discharge / round trip 0.75 (FLOW_BATTERY 70-80 % mid) |
| IA-ESS-ZNBR2-DIS ★ | ZNBR2 → SOL_ARK_60K | DC | elec/ess | 5.000 | kW | 120.0 kWh one cycle/d averaged over 24 h |
| S20 ★ | GROW_BED → SOL_ARK_60K | DC load | elec | 5.000 | kW | GROW_BED continuous_kw (LED canopy share); LED check 3.06 kW in photoperiod at DLI 17.0, 2.7 umol/J |
| S69 ★ | ZNBR2 → ZNBR2_BR2_REGEN | moist air + Br2 vapor | mass | 852.47 | kg/d | headspace purge 30.0 m3/h (VENT_SCRUB 2.2 band 10-50 mid) at ambient humidity + 10 ppmv Br2 |
| S69B ★ | ZNBR2_BR2_REGEN → ZNBR2 | NaBr/NaBrO liquor | mass | 8.487 | kg/d | scrub liquor: saturation water 8.44 + Br2 0.0470 + NaOH make-up 0.0003 |
| S79 ★ | MEOH_FC → SOL_ARK_60K | DC power | elec/ess | 0.292 | kW | DMFC eta 0.2536 (0.9 L/kWh) x S76 LHV 1.153 kW; REQ-MEOH-FC 0.5-2 kW band NOT met |
| S81 ★ | MEOH_FC → MEOH_COND | MeOH FC product water (MeOH trace) | mass | 5.622 | kg/d | CH3OH + 1.5 O2 -> CO2 + 2 H2O on S76 5.0 kg/d |

### Life / farm / hab

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| S13 ★ | GROW_BED → VCD_TRAIN | farm sump + AHU condensate | mass | 31.50 | kg/d | ET 92.4 (3.3 L/m2.d x 28.0 m2) - farm exhaust vapor 60.9 (OA 933.5 m3/h light, 251.3 dark; w 0.0131 - 0.01) |
| S14 ★ | GROW_BED → HABITATION | fresh produce | mass | 2.400 | kg/d | crew ration 0.6 kg/p.d x 4; production 4.2 = S14 + S14X 1.8 |
| S15 ★ | GROW_BED → HABITATION | O2 (none delivered) | mass | 0 | kg/d | photosynthetic O2 (0.806 kg/d) leaves with FARM AHU exhaust; HAB is sealed with its own AHU and is supplied by S02 |
| S21 ★ | ROOF_TANK → HABITATION | potable water | mass | 120.00 | kg/d | hab hygiene water 30.0 L/p.d x 4 |
| S26 ★ | REMIN → HABITATION | remineralized potable | mass | 10.00 | kg/d | REMIN drink_L_d 10 |
| S29 ★ | GREY_TREAT → VCD_TRAIN | treated grey | mass | 104.50 | kg/d | grey treat recovery 95 % of S12 (5 % sludge/backwash) |
| S30 ★ | BLACK_DIGEST → NUTRIENT_DOSE | digest liquor / nutrients | mass | 16.43 | kg/d | black water 16.48 kg/d less digester gas 0.05 |
| S52 ★ | FUEL_CELL → VCD_TRAIN | PEM product water | mass | 42.89 | kg/d | S49 4.8 kg/d H2 x 18.015/2.016 |
| S77 ★ | MEOH_FERM → MEOH_TANK | biogenic MeOH | mass | 0.0146 | kg/d | VS 0.0486 kg/d x 0.3 Nm3 CH4/kg VS -> MeOH at 70% |
| S78 ★ | HABITATION → MEOH_FERM | food waste | mass | 0.360 | kg/d | food waste 15% of ration |

### Fab

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| S10 ★ | WET_BENCH → LEACH_CSTR_1 | spent etch + rinse to REGEN LEACH | mass | 78.34 | kg/d | WS forwards sum completed: all bench inputs (S09, S27, S31-S35, S34B) + resist - S38 |
| S27 ★ | FAB_UPW_TANK → WET_BENCH | UPW >18 MOhm.cm | mass | 60.00 | kg/d | fab UPW 20-100 L/d for 1-5 starts, at 3 starts |
| S31 ★ | WS_HF_ED → WET_BENCH | HF (aq) dilute | mass | 1.500 | kg/d | AUD s13 band 0.5-2.5 L/d at 3 of 1-5 starts, dilute 1.0 kg/L |
| S32 ★ | WS_PEROX → WET_BENCH | H2O2 dilute (SC-1/SC-2) | mass | 3.000 | kg/d | AUD s13 band 1-5 L/d at 3 of 1-5 starts, dilute 1.0 kg/L |
| S33 ★ | WS_AMMONIA → WET_BENCH | NH4OH dilute (SC-1) | mass | 3.000 | kg/d | AUD s13 band 1-5 L/d at 3 of 1-5 starts, dilute 1.0 kg/L |
| S35 ★ | WS_KOH → WET_BENCH | KOH 2 M | mass | 0.273 | kg/d | AUD s13 <0.5 L/d -> 0.25 L/d of 2 M KOH (1.09 kg/L) |
| S36 ★ | WS_DOPE → WAFER_FAB | B/P dopant concentrate | mass | 0.0100 | kg/d | AUD s13 grams/d concentrate -> 10 g/d |
| S37 ★ | WS_SLURRY → WAFER_FAB | colloidal silica slurry | mass | 3.300 | kg/d | AUD s13 1-5 L/d makeup at 3 starts = 3.0 L/d x 1.1 kg/L |
| S39 ★ | WAFER_FAB → LEACH_CSTR_1 | spent slurry and etch liquor | mass | 3.310 | kg/d | spent slurry + dopant residue = S37 + S36 (AUD: spent return same order as forwards) |
| S34 ★ | WS_NITRIC → WET_BENCH | HNO3 2 M | mass | 0.665 | kg/d | AUD s13 WS_NITRIC/WS_PHOS band 0.5-2 L/d at 3 starts = 1.250 L/d, 50/50 split; 2 M HNO3 at 1.064 kg/L |
| S34B ★ | WS_PHOS → WET_BENCH | H3PO4 dilute | mass | 0.625 | kg/d | 50/50 split of the same band, 0.625 L/d dilute 1.0 kg/L |

### Dock / hydro

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| DOCK_EXPORT_TBD ★ | NORTH_DOCK → BOUNDARY_EXPORT | metal goods (solid) | mass | 28.75 | kg/d | MFG_SHOP finished goods (Fe plate, wire, sheet, powder) to export |
| IA-ESS-HYDRO-CHG ★ | CATCH_TANK → ROOF_TANK | water | mass/ess | 200,000 | kg/d | one full 200 m3 cycle per day |
| IA-ESS-HYDRO-DIS ★ | ROOF_TANK → CATCH_TANK | water | mass/ess | 200,000 | kg/d | one full cycle per day |
| S22 ★ | ROOF_TANK → CATCH_TANK | water (potential energy) | ess | 0.409 | kW | hydraulic power: rho V g h = 9.81 kWh/cycle over 24 h |
| S23 ★ | CATCH_TANK → ROOF_TANK | water (potential energy) | ess | 0.409 | kW | hydraulic power: rho V g h = 9.81 kWh/cycle over 24 h |
| S40 ★ | ROOF_TANK → TERRACE_IRRIG | water | mass | 0 | kg/d | event-driven; zero on the dry design day |
| S41 ★ | TERRACE_IRRIG → CATCH_TANK | water | mass | 0 | kg/d | event-driven; zero on the dry design day |
| S42 ★ | TERRACE_IRRIG → GREY_TREAT | water | mass | 0 | kg/d | event-driven; zero on the dry design day |

### Heat ladder and Q4 peers

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| S06 ★ | GEO_HP → GROW_BED | Q4 water | thermal | 0 | kW | GEO_HP dispatch: lift only on Q4 deficit. Normal bus 4.244 kW >= life 3.0 kW, so 0. Standby (ladder down): 1.5 kW to farm |
| S43 ★ | GEO_GHEX → GEO_HP_CLOSED_LOOP | glycol loop | mass/thermal | 0 | kW | ground heat = 0 while GEO_HP is idle. Standby 2.126 kW at COP 3.43 (0.45 Carnot 285 -> 328 K) <= GHEX 3.0 kW |
| S44 ★ | GEO_HP → Q4_BUS | Q4 water | thermal | 0 | kW | GEO_HP dispatch: lift only on Q4 deficit. Normal bus 4.244 kW >= life 3.0 kW, so 0. Standby (ladder down): 1.5 kW to Q4 / hab |
| S53 ★ | FUEL_CELL → Q4_BUS | Q4 water | thermal | 1.142 | kW | FC heat 2.664 kW (LHV 6.664 - S51) x (60.0-45)/(60.0-25) above Q4 return |
| S54 ★ | CRYO_HX_Q4 → Q4_BUS | Q4 water | thermal | 0.545 | kW | ASU air 200.5 kg/d, 2-stage to 6.0 bar a (eta_is 0.7): shaft 0.580 kW x 0.839 above Q4 return + sieve TSA 0.058 |
| S63 ★ | MET_HX_Q4 → Q4_BUS | Q4 water | thermal | 0.0171 | kW | Cu melt sensible + latent on 4.392 kg/d x 0.55 recovered (mold/coil water) |
| S80 ★ | MEOH_FC → Q4_BUS | Q4 water | thermal | 0.369 | kW | DMFC heat 0.861 kW x 0.4286 above Q4 return |

### Other (MFG metals)

| Stream | From → to | Medium | Layer | Rate | Unit | Basis |
|---|---|---|---|---:|---|---|
| S57 ★ | MET_MELT → WIRE_DRAW | Cu billet | mass | 4.379 | kg/d | Cu deposit 8.784 x 0.5 to wire, less melt fume 0.3% |
| S58 ★ | WIRE_DRAW → MFG_SHOP | Cu wire | mass | 3.941 | kg/d | S57 less 10% draw swarf |
| S59 ★ | COLD_MILL → MFG_SHOP | Cu sheet/strip | mass | 3.953 | kg/d | Cu 4.392 to cold mill less 10% trim |
| S60 ★ | GAS_ATOMIZER → MFG_SHOP | metal powder | mass | 3.200 | kg/d | blend deposit 3.555 (Pb/Sn/Ni/Cd/Zn) less 10% off-spec |
| S61 ★ | MFG_SHOP → HOPPER | metal scrap | mass | 1.197 | kg/d | swarf/trim/off-spec from draw, mill and atomizer (less LEV fines) |
| S62 ★ | MET_AHU → MET_SCRUB | air | mass | 2,131 | kg/h | MET aisle general exhaust 6.0 ACH x 300.0 m3 |
| S71 ★ | MET_AHU → MET_SCRUB | air + metal fume/fines/mist | mass | 852.43 | kg/h | MET LEV 720.0 m3/h (VENT_SCRUB 2.4 band 540-900 mid) at 1.184 kg/m3 |
