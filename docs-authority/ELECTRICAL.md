# Electrical analysis

Document number: AQS-ELC-001  
Revision: D  
Date: 2026-10-24  
Basis: AQS-AUTH-001. Interconnection of the Sol-Ark inverter, zinc-bromide battery, generator and fuel cell: AQS-PWR-002, AQS-FC-001 and `FLOW_BATTERY.md`. Hazardous electrical areas: AQS-HSE-001 §6. Compliance themes: AQS-COMPL-001 §4 (NEC). Single-line diagram: `electrical_sld.png`.  
Licence: CERN-OHL-S-2.0. This is not a document stamped by a professional engineer, and no permits are claimed.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Working electrical analysis (pre-identity header) | 2026-09-27 |
| B | 1 | Document number added; cross-reference to compliance items CMP-NEC; style update | 2026-10-01 |
| C | 2 | Rev N (AQS-DUTY-012): CE column redefined as HER-only intrinsic efficiency; Au/Ag/Cu at 1.00, Fe at 0.415 (Liu et al. 2025, B2); per-cell current model; Fe EW basis; BMED repeating-unit model; RECT-EW topology | 2026-10-08 |
| C | 3 | Merged with the Rev BH/AC line: RECT-EW nine-channel 16500 A, BMED_EVAP sizing per AQS-PAR-001 Rev B; Rev C CE column and BMED repeating-unit method retained, sizing numbers superseded | 2026-10-17 |
| D | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; one merged table row split; values unchanged | 2026-10-24 |

## 1. Purpose and scope

This document describes how one plant module is connected electrically, which loads are AC and which DC, and how much energy each feedstock needs per tonne. It keeps the power-yard CAD model and the single-line diagram consistent.

In scope: the path from the utility through the Sol-Ark inverter and the automatic transfer switch (ATS) to the motor control centre (MCC) and the rectifiers; PV; the zinc-bromide (ZnBr2) battery on the inverter's battery DC port; `BACKUP_GEN` on the generator port; `FUEL_CELL` on the battery DC port through `FC_DCDC`; and the plating energy from Faraday's law.

Out of scope: the protection coordination study by a professional engineer; arc-flash labels (tracked in AQS-CMP-001); and the direct methanol fuel cell, which is deferred (root chapter `06-energy-carbon-oxygen.md`).

## 2. Terms

Electrowinning (EW): recovering a metal by passing current through a solution so the metal plates on the cathode. Cells `EW_1` to `EW_9` each recover one metal.

Current efficiency (CE): the share of the cell current that does the intended reaction. In this document the CE column means efficiency against hydrogen evolution only (section 4).

Hydrogen evolution reaction (HER): the side reaction that makes hydrogen at the cathode instead of metal.

Faradaic efficiency (FE): the same quantity as current efficiency, as reported in the cited papers.

Bipolar membrane electrodialysis (BMED): the process that splits salt into acid and base; a repeating unit is one cell pair in the stack.

Wet tonne: one tonne of feed as received, including its moisture.

Auxiliary load (aux): the fans, pumps and other loads that run regardless of feed.

Feedstock names: WEEE is waste electrical and electronic equipment; PCB is printed circuit board; MSW is municipal solid waste; TBM is a tunnel boring machine used to mine a landfill.

Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Interconnection

The calculations use Faraday's law and published tankhouse cell voltages. A module is the 40 ft high-cube and 20 ft high-cube container pair at 150 kg/day of wet feed. A 500 kg/day plant is that pair multiplied by about 3 on the wet DC side, not a denser pack. In `electrical_sld.png` the utility is on the left, the ATS in the centre and the plant loads on the right.

The inverter is a Sol-Ark 60K-3P-480V: 277/480 V three-phase, 60 kW continuous, 72.3 A output, 200 A GRID, LOAD and GEN terminals, 180 A continuous pass-through, listed to UL 1741 SB and IEEE 1547. One unit covers the module, whose peak is about 50 kW.

- The utility supply, 480Y/277 V, goes through the meter to a 200 A fused disconnect.
- The disconnect feeds the Sol-Ark GRID port (two-way: import and export) and ATS source 1 (mechanical bypass).
- The Sol-Ark LOAD port feeds ATS source 2.
- The ATS common output feeds the 200 A plant main, which feeds the MCC (AC) and the rectifier skid (DC).
- The ATS breaks before it makes. Sources 1 and 2 must never be paralleled.
- The ground-mounted PV array, about 70 kW at standard test conditions (STC), connects to four maximum power point trackers (MPPT). The inverter accepts up to 78 kW STC at 150 to 850 V.
- The ZnBr2 flow battery (SEM Tech CEM/AEM) has about 330 cells in series to sit in the 160 to 700 V battery window, about 120 kWh usable at 60 kW, with two 50 A ports. A CAN battery-management (BMS) gateway is required, because the 60K inverter speaks the lithium-battery CAN protocol, not raw flow-battery telemetry.
- The GEN port connects `BACKUP_GEN`, the plant's hydrogen AC generator (AQS-PWR-002, AQS-EQP-GEN-001). Its continuous rating is to be set by the supplier. The study gives about 2.3 to 2.7 kW electrical continuous from process hydrogen; the upper limit of its capacity class is the module peak of about 50 kW, or the inverter's 60 kW (AQS-AUD-001 §10.2). Diesel remains an external contingency only. The geothermal heat path is in AQS-EQP-GEO-001; an organic Rankine cycle (ORC) generator is a stub whose method waits for the ground heat exchanger (GHEX) survey (AQS-AUD-001 §10.4). The earlier 100 kW figure for M1 must not be claimed.
- The Sol-Ark battery DC port (160 to 700 V) takes the ZnBr2 battery and also `FUEL_CELL` through `FC_DCDC`. The fuel cell is a PEM stack on plant hydrogen and oxygen (AQS-FC-001, AQS-EQP-FC-001). It is not `BACKUP_GEN`: the stacks connect on DC only, not to the GEN AC port and not to the rectifier process DC. Its continuous rating is to be set by the supplier; the study gives about 3 to 5 kW DC continuous from process hydrogen, with capacity up to about 60 kW in the battery window (AQS-AUD-001 §10.3). The earlier power figure of 100 to 200 kW for M1 must not be claimed. Low-grade heat goes to Q4 through `FC_HX_Q4` (S53), and product water to condensate (S52).

The Sol-Ark already transfers internally in about 15 ms. The external ATS exists so that the plant can run on the utility alone with the inverter locked out for service.

## 4. Plating energy

The charge and energy per kilogram of metal plated are:

Ah/kg metal = n × 26.801 / M

kWh/kg = V_cell × Ah/kg / (1000 × CE)

where n is the number of electrons per atom, M the molar mass in g/mol, V_cell the cell voltage and CE the current efficiency. Table 4.1 gives the values used.

Table 4.1. Plating energy by metal

| Metal | n | Ah/kg theory | V_cell used | CE | kWh/kg plated |
|---|---|---|---|---|---|
| Au | 3 | 408 | 1.8 | 1.00 | 0.73 |
| Ag | 1 | 248 | 2.0 | 1.00 | 0.50 |
| Cu | 2 | 844 | 2.2 | 1.00 | 1.86 |
| Pb | 2 | 259 | 2.3 | 0.85 | 0.70 |
| Sn | 2 | 451 | 2.4 | 0.85 | 1.27 |
| Ni | 2 | 913 | 3.0 | 0.80 | 3.42 |
| Fe | 2 | 960 | 3.1 | 0.415 | 7.17 |
| Cd | 2 | 477 | 2.8 | 0.85 | 1.57 |
| Zn | 2 | 820 | 3.4 | 0.80 | 3.49 |
| Co | 2 | 910 | 3.0 | 0.75 | 3.64 |

The CE column (Rev C) is the efficiency against hydrogen evolution only, measured or assumed in a solution without a soluble redox shuttle. It is not the overall cell efficiency. In the cascade solution each cell also reduces Fe³⁺ to Fe²⁺ and Cu²⁺ to Cu⁺ at the mass-transfer limit, so the overall efficiency of each cell is derived from the solution composition in AQS-DUTY-012 (`docs-authority/_rev_n_corrections_study.py`, function `ew_model`). The kWh/kg in Table 4.1 is the HER-only value. Table 4.2 gives the per-cell values on the Rev N design day.

Table 4.2. Cell currents and current shares on the Rev N design day

| Cell | Metal | I (A) | Deposition share | Fe³⁺/Cu²⁺ share | H₂ share | DC kW |
|---|---|---|---|---|---|---|
| EW_1 | Au | 572 | 0.0002 | 0.9998 | 0 | 1.03 |
| EW_2 | Ag | 205 | 0.0013 | 0.9987 | 0 | 0.41 |
| EW_3 | Cu | 228 | 0.678 | 0.322 | 0 | 0.50 |
| EW_4 | Pb | 35 | 0.218 | 0.744 | 0.038 | 0.08 |
| EW_5 | Sn | 25 | 0.533 | 0.374 | 0.094 | 0.06 |
| EW_6 | Ni | 37 | 0.728 | 0.090 | 0.182 | 0.11 |
| EW_7 | Fe | 2857 | 0.415 | 0.0006 | 0.585 | 8.86 |
| EW_8 | Cd | 17 | 0.846 | 0.005 | 0.149 | 0.05 |
| EW_9 | Zn | 30 | 0.799 | 0.001 | 0.200 | 0.10 |
| Total | | | 0.356 overall | | | 11.20 |

Basis: mass-transfer coefficient k_m 2.2 × 10⁻⁵ m/s (range 1.1 to 3.3 × 10⁻⁵; Griffiths et al. 2005, AIChE J. 51, doi 10.1002/aic.10311); cathode area 2.205 m² per cell (7 cathodes, two faces, 0.35 × 0.45 m; assumption RS-EW-AREA); leach oxidation-reduction potential 1.05 V against the standard hydrogen electrode (Fe(III) fraction 0.9999). The Cu(I) carried by the shuttle is deposited first on `EW_3`, one electron per copper atom. Gold and silver are at 1.00 HER-only because on those cells the current goes to the Fe³⁺ shuttle, not to hydrogen.

### 4.1 Iron electrowinning basis (EW_7, Rev C)

Table 4.3. Iron electrowinning options

| Item | Value | Source |
|---|---|---|
| Undivided cell, chloride liquor, pH ~1 (Rev N design basis) | FE 41.5 %, 7.17 kWh/kg at 3.1 V | Liu et al. 2025, ChemRxiv doi 10.26434/chemrxiv-2024-stwdn, case B2 (1 M NaCl) |
| Membrane-divided cell, catholyte pH 2–3 (cascade note basis) | FE 98.9 %, 3.2 V, 4.6 kWh/kg | Liu et al. 2025, case B1 |
| Membrane-divided, sulphate/chloride, CE 95 % | 3.53 kWh/kg | Badenhorst et al. 2019, Membranes 9, 137, https://www.mdpi.com/2077-0375/9/11/137 |
| Cascade note range | 3.5–4.6 kWh/kg | Electrochem-Cascade.md (divided cell, pH 2–3) |

The 3.5 to 4.6 kWh/kg range applies only to a membrane-divided cell with a pH 2 to 3 catholyte and Fe³⁺ kept out of the catholyte. The Rev N graph uses the undivided pH ~1 cell at 0.415, because that is the cell in the graph; the divided cell is option RS-EW-SELECT (sensitivity: at CE 0.80 the grid import is 36.3 kW, at 0.95 it is 35.8 kW). Fe(OH)₃ forms above pH 2 on the anolyte side (Liu et al. 2025), so a divided cell needs catholyte pH control. Current efficiency falls below about 5 g/L Fe (Badenhorst et al. 2019). `EW_7` at 2857 A needs 9.5 m² of cathode at 300 A/m²; the envelope provides 2.205 m².

### 4.2 Electrowinning rectifier topology (RECT-EW, Rev C)

On the Rev N design day the cell currents range from 17 A (`EW_8`) to 572 A (`EW_1`), and 2857 A on `EW_7`. A single series string (0 to 36 V, 0 to 250 A) cannot carry them. RECT-EW is re-rated to 14 kW (11.20 kW DC × 1.25) as per-cell current-controlled channels, with `EW_7` on its own low-voltage, high-current channel unless the iron route changes (RS-EW-SELECT).

### 4.3 Other process energy

Aluminium, magnesium, calcium, lithium and the rare earth elements are not electrowon here. Their energy is BMED sodium hydroxide plus mixing, about 0.3 to 0.6 kWh/kg of hydroxide cake.

BMED (Rev C): the specific energy comes from the repeating-unit voltage, P = n_pairs · F · V_ru / CE, with V_ru 2.0 V (1.8 to 2.2 V per repeating unit) and CE 0.65 for feed-and-bleed operation (63 to 67 %; Cassaro et al. 2023, Membranes 13, 217, https://pmc.ncbi.nlm.nih.gov/articles/PMC9945178/). This gives 2.06 kWh/kg NaOH, inside the 1.9 to 2.6 kWh/kg feed-and-bleed range reported there (1.4 kWh/kg in closed loop). On the Rev N design day: 1811 pairs/d, 6.22 kW DC, rated 8 kW (1.25 × P, rounded up).

- Induction pyrolysis: 0.8 to 1.2 kWh/kg of dry plastic to the coil, plus afterburner heat from the non-condensable gas.
- Dryer: 0.70 to 0.85 kWh/kg of water evaporated (Q3 through HX-4). Since graph Rev J, the electrowinning reject heat goes to Q4 through HX-8 (AQS-DUTY-008 Rev B).
- Shredder: 10 to 25 kWh per wet tonne, at peak.

## 5. AC and DC loads

Table 5.1 lists the module loads by supply type.

Table 5.1. AC and DC loads

| Load | Kind | Module rating |
|---|---|---|
| Site service | AC 480 Y / 277 V 3φ | 100 A, 83 kVA |
| Shredder | AC 480 V | 7.5 kW peak |
| Pumps + CSTR agitators | AC 480 V | 2.5 kW |
| Fans + baghouse + scrubber | AC 480 V | 3.0 kW |
| VDF, mill, vibratory | AC 480 V | 2.0 kW |
| HVAC / makeup | AC 480 V | 1.5 kW |
| Induction coil drive | AC 5–20 kHz | 0–25 kW |
| RECT-EW | Nine channels, 6 V, 250–4000 A frames, 16500 A total (AQS-ELEC-004 Rev B; cell 2.12 V, CE 0.85) | 99 kW nameplate; 38.7 kW AC at the bounding case |
| RECT-BMED | DC 0–80 V, 0–120 A steady | 5–8 kW class (study row; graph BMED_ACID books 26.93 kW, AQS-PAR-001 Rev B) |
| EVAP_ACID, EVAP_BASE | AC 480 V, MVR compressor | 2.41 kW and 2.40 kW (AQS-PAR-001 Rev B; X-PAR-06) |
| RECT-PK | DC 0–12 V, 0–40 A avg, pulsed | <0.5 kW |

The continuous AC auxiliary load is about 9 kW, or 216 kWh/day whether the feed is e-waste or soil. That term dominates the energy of every lean feedstock.

## 6. Pulsed DC

Pulsed current (10 to 100 Hz, 20 to 40 % duty, same average charge) is used when the solution is below the limiting current or when the deposit should be a powder.

- PK-1 Co, PK-2 Mn, PK-3 Cr, PK-7 Tl: low concentration; pulse.
- EW-6 Ni, EW-9 Zn: hydrogen competes; pulse or pulse-reverse.
- EW-7 Fe: powder is wanted; pulse or periodic interruption to shed the deposit.
- EW-3 Cu sheet: periodic reverse (1 to 5 % anodic time), not on/off pulsing. It levels the sheet.
- EW-1 Au powder: pulsing is acceptable.
- BMED and CRU: steady current. Pulsing the bipolar-membrane stack wastes water-splitting efficiency and damages the membranes.
- Induction: AC. The coil supply is not rectified.

## 7. Feedstock assays

Table 7.1 gives working average compositions, not contract assays; real material varies with decade and country. Each row is a case inside the feedstock envelope of AQS-ASSAY-001 Rev C (`FEED_ASSAY.md`), and none is the design feed. The plant is checked across that envelope, from regolith-like material to metal-rich PCB.

Table 7.1. Feedstock assays used

| Stream | Fe | Cu | Al | other plateable | Au | Ag | plastic + paper | glass / silicate | moisture |
|---|---|---|---|---|---|---|---|---|---|
| Mixed WEEE | 25 % | 7 % | 5 % | 3 % | 50 ppm | 200 ppm | 22 % | 18 % | 5 % |
| PCB-rich WEEE | 8 % | 16 % | 4 % | 4 % | 150 ppm | 800 ppm | 25 % | 30 % | 3 % |
| MSW (as-received) | 4 % | 0.2 % | 1.5 % | 0.2 % | — | — | 30 %* | 5 % | 25 % |
| Landfill mine, bulk | 2.5 % | 0.15 % | 0.8 % | 0.15 % | trace | trace | 12 % | 8 % + 45 % soil | 20 % |
| Landfill, TBM in a WEEE cell | 15 % | 3 % | 3 % | 1.5 % | 20 ppm | 80 ppm | 18 % | 15 % + 20 % soil | 15 % |
| Porphyry Cu tailings | 8 %** | 0.30 % | 3 % | 0.05 % | 0.1 ppm | 2 ppm | 0 | 70 % | 15 % |
| Au tailings | 5 %** | 0.05 % | 2 % | — | 0.4 ppm | 2 ppm | 0 | 75 % | 18 % |

\* For MSW, "plastic + paper" is the pyrolysis and dryer load. Paper dries and then chars; plastic cracks.
\** Iron in tailings is mostly oxide. Only the part that dissolves in Salria reaches EW-7. The study assumes 25 % of tailings iron is leachable; the rest goes to grit or digestion.

## 8. Energy per wet tonne of feed

kWh/t = plated-metal energy + BMED for that tonne's acid and base + dryer + pyrolysis + 9 kW auxiliary load × hours to process 1 t.

At 150 kg/day a tonne takes 6.7 days, so the auxiliary energy on that tonne is 9 kW × 160 h ≈ 1,440 kWh/t. That is the penalty of container scale. At 2 t/day the same fans cost 108 kWh/t. Both figures should be reported.

### 8.1 Process energy only, without the auxiliary load

Table 8.1. Process energy per wet tonne

| Stream | EW metals kWh/t | BMED kWh/t | dryer kWh/t | pyro kWh/t | process total |
|---|---|---|---|---|---|
| Mixed WEEE | 1,180 | 80 | 40 | 220 | **1,520** |
| PCB-rich | 820 | 90 | 25 | 250 | **1,185** |
| MSW | 170 | 40 | 190 | 280 | **680** |
| Landfill bulk | 110 | 50 | 150 | 120 | **430** |
| Landfill TBM / WEEE cell | 640 | 70 | 110 | 180 | **1,000** |
| Cu tailings 0.3 % | 80 | 180 | 110 | 0 | **370** |
| Au tailings | 25 | 160 | 130 | 0 | **315** |

The per-tonne tables in this section are on the Rev B basis (iron at 3.72 kWh/kg). On the Rev C basis, iron in an undivided pH ~1 cell needs 7.17 kWh/kg; the tables have not been recalculated (open item in AQS-DUTY-012).

How the electrowinning figures were built for mixed WEEE, per wet tonne:

- Fe 250 kg × 0.85 leach × 3.72 kWh/kg ≈ 790
- Cu 70 kg × 0.90 leach × 2.18 ≈ 137
- Ni, Zn, Sn and Pb, about 30 kg blended ≈ 80
- Al 50 kg is precipitated, not electrowon
- Au 50 g × 0.82 kWh/kg ≈ 0.04 (value, not energy)
- Ag 200 g ≈ 0.1

BMED is sized from the acid consumed in leaching plus the caustic needed to digest glass and to precipitate aluminium, magnesium and calcium. Tailings and WEEE rich in FR-4 board need more BMED.

### 8.2 Including the container auxiliary load (150 kg/day)

Adding 1,440 kWh/t gives Table 8.2.

Table 8.2. Energy per wet tonne including the auxiliary load

| Stream | kWh / wet t | kWh / day at 150 kg | average kW |
|---|---|---|---|
| Mixed WEEE | 2,960 | 444 | 18.5 |
| PCB-rich | 2,625 | 394 | 16.4 |
| MSW | 2,120 | 318 | 13.2 |
| Landfill bulk | 1,870 | 280 | 11.7 |
| Landfill TBM / WEEE cell | 2,440 | 366 | 15.2 |
| Cu tailings | 1,810 | 272 | 11.3 |
| Au tailings | 1,755 | 263 | 11.0 |

The peak stays at about 50 kW whenever pyrolysis, the electrowinning string and the shredder overlap. Tailings never switch the coil on, so their peak drops to about 25 kW.

## 9. Yields per wet tonne

Leach recovery is assumed to be 85 to 95 % on exposed metal, 70 % on copper locked in FR-4 after burnout, and 50 % on oxide iron in tailings (Table 9.1).

Table 9.1. Products per wet tonne

| Stream | plated metals kg | Al/Mg/Ca cake kg | oil cuts kg | silicate + grit kg |
|---|---|---|---|---|
| Mixed WEEE | 280 | 70 | 150 | 200 |
| PCB-rich | 220 | 50 | 170 | 320 |
| MSW | 45 | 25 | 180 | 80 |
| Landfill bulk | 30 | 20 | 80 | 520 |
| Landfill TBM / WEEE cell | 160 | 50 | 120 | 280 |
| Cu tailings 0.3 % | 25 | 40 | 0 | 850 |
| Au tailings | 8 + 0.4 g Au | 30 | 0 | 880 |

"Plated metals" means Fe, Cu, Ni, Zn, Sn, Pb and the precious metals. Iron dominates the mass and energy of WEEE. Gold dominates its value and costs little electricity.

## 10. Excavation method: tunnel boring machine or bucket wheel

The plant is the same; the feed differs.

- A bucket wheel or strip excavation gives high fines, moisture and soil. The feed looks like landfill bulk: the dryer and digestion work hard, the electrowinning string is lightly loaded, and the auxiliary load is still 9 kW.
- A TBM can be driven into a 1990s e-waste trench or a construction cell. The assay then swings towards the "TBM in a WEEE cell" case or towards bulk soil. The electrical plant does not change; only the RECT-EW current setpoint does.

The rectifier is not sized for the leanest feed. RECT-EW is sized at the top of the plateable-metal envelope in AQS-ASSAY-001 Rev C, and the current is turned down for lean feeds. The cell currents are the duty values; the 180 A string figure is superseded by the `EW_1` node, 2105 A (AQS-PWR-001 Rev C).

## 11. What a 100 A, 480 V service supports

Such a service supplies 83 kVA. The module peak is 50 kW and its average 11 to 19 kW. One service feeds one pair of containers. A 500 kg/day plant needs three wet strings, or one larger RECT-EW and a 200 A service.

To match the average with PV, 20 kW AC with one day of storage covers the module on e-waste. Pyrolysis peaks still need the rectifier skid or a generator.

## 12. Sources for assays and cell voltages

Mixed WEEE metal splits come from published WEEE category mixes (ferrous 20 to 30 %, Cu 3 to 20 % by device class, plastics 15 to 30 %). PCB: Cu about 20 %, Au 70 to 250 g/t. MSW: metals about 4 to 8 % in total, plastics about 12 %, moisture about 20 to 25 %. Landfill excavations: soil and fines often 45 to 60 %, metals 2 to 4 %, plastic 7 to 17 %. Porphyry tailings: residual Cu commonly 0.2 to 0.4 %. Chloride and sulphate electrowinning voltages: Cu about 2.0 to 2.2 V, Ni chloride about 3 V, Zn about 3.4 V; about 1.8 to 2.2 kWh/kg Cu and 3.0 to 3.4 kWh/kg Zn at industrial current efficiency. Specific papers: Griffiths et al. 2005; Liu et al. 2025; Badenhorst et al. 2019; Cassaro et al. 2023 (cited in section 4).
