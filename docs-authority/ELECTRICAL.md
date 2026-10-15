# Electrical analysis

Document number: AQS-ELC-001  
Revision: B  
Date: 2026-10-01  
Authority: AQS-AUTH-001; Sol-Ark / ZnBr2 / GEN / FC interconnect themes in
AQS-PWR-001, AQS-FC-001, FLOW_BATTERY.md; classified areas AQS-HSE-001 §4;
compliance themes **AQS-CMP-001** §4 (NEC).  
PFD/SLD: `electrical_sld.png`

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Working electrical analysis (pre-identity header) | 2026-09-27 |
| B | 1 | Doc identity; CMP-NEC cross-ref; Wave 2 style | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Not a PE stamp. No invented permits.

## 1. Purpose

State module electrical interconnect, AC/DC load split, and energy
intensity so POWER yard CAD and the single-line stay consistent.

## 2. Scope

In: utility → Sol-Ark → ATS → MCC/RECT; PV; ZnBr2 BATT DC; BACKUP_GEN on
GEN port; FUEL_CELL on BATT DC via FC_DCDC; Faraday-based plating energy.
Out: PE coordination study; arc-flash labels (tracked AQS-CMP-001);
MeOH DMFC (deferred — root `06-energy-carbon-oxygen.md`).

---

Basis: Faraday + published tankhouse voltages. Module is the 40HC + 20HC pair at **150 kg/day wet feed**. 500 kg/day is that pair times ~3 on the wet DC side, not a tighter pack.

`electrical_sld.png` is the single-line: utility left, ATS center, plant loads right.

## Interconnect

Inverter is a Sol-Ark 60K-3P-480V. Native 277/480 V 3φ, 60 kW continuous, 72.3 A out, GRID/LOAD/GEN 200 A terminals, 180 A continuous passthrough, UL 1741 SB / IEEE 1547. One unit covers the module (peak ~50 kW).

- Utility 480 Y / 277 → meter → 200 A fused disco.
- Disco feeds Sol-Ark **GRID** (bidirectional: import and backfeed) and ATS source 1 (mechanical bypass).
- Sol-Ark **LOAD** feeds ATS source 2.
- ATS common → plant main 200 A → MCC (AC) and rectifier skid (DC).
- Break-before-make. Do not parallel S1 and S2.
- Ground-mount PV ~70 kW STC into four MPPTs (inverter allows 78 kW STC, 150–850 V).
- ZnBr2 flow battery, SEM Tech CEM/AEM, ~330 series cells to sit in the 160–700 V battery window, ~120 kWh usable / 60 kW, two 50 A ports. CAN BMS gateway required — the 60K speaks lithium CAN, not raw flow-battery telemetry.
- GEN port → **BACKUP_GEN** (plant H₂ AC genset, AQS-PWR-001 / AQS-EQP-GEN-001).
  Continuous kW **TBD** vendor; **study** continuous from process H₂ ~2.3–2.7 kW_e;
  capacity class upper = module peak ~50 kW / inverter 60 kW (AQS-AUD-001 §10.2).
  Diesel remains external contingency only. Geothermal thermal path: AQS-EQP-GEO-001;
  ORC electric stub: method TBD after GHEX survey (AQS-AUD-001 §10.4);
  do not claim legacy 100 kW on M1.
- Sol-Ark **BATT DC** (160–700 V) ← ZnBr2 **and** **FUEL_CELL** via FC_DCDC
  (PEM, plant H₂ + O₂, AQS-FC-001 / AQS-EQP-FC-001). FC ≠ BACKUP_GEN: stacks
  couple DC only — not the GEN AC port, not RECT process DC. Continuous kW
  **TBD** vendor; **study** continuous from process H₂ ~3–5 kW_dc;
  capacity ≤ ~60 kW BATT window (AQS-AUD-001 §10.3);
  do not claim legacy POWER 100–200 kW on M1.
  Low-grade heat → Q4 via FC_HX_Q4 (S53); product water → condensate (S52).

Sol-Ark already transfers internally in ~15 ms. The external ATS exists so the plant can run on raw utility with the inverter locked out for service.

## Conventions

Ah/kg metal = n × 26.801 / M
kWh/kg = V_cell × Ah/kg / (1000 × CE)

| Metal | n | Ah/kg theory | V_cell used | CE | kWh/kg plated |
|---|---|---|---|---|---|
| Au | 3 | 408 | 1.8 | 0.90 | 0.82 |
| Ag | 1 | 248 | 2.0 | 0.90 | 0.55 |
| Cu | 2 | 844 | 2.2 | 0.85 | 2.18 |
| Pb | 2 | 259 | 2.3 | 0.85 | 0.70 |
| Sn | 2 | 451 | 2.4 | 0.85 | 1.27 |
| Ni | 2 | 913 | 3.0 | 0.80 | 3.42 |
| Fe | 2 | 960 | 3.1 | 0.80 | 3.72 |
| Cd | 2 | 477 | 2.8 | 0.85 | 1.57 |
| Zn | 2 | 820 | 3.4 | 0.80 | 3.49 |
| Co | 2 | 910 | 3.0 | 0.75 | 3.64 |

Al, Mg, Ca, Li, REE are not electrowon here. Their energy is BMED NaOH + mixing, ~0.3–0.6 kWh/kg hydroxide cake.

BMED: 1.8–2.4 kWh per kg of (NaOH + HCl) pair at 50–100 A, 1.8–2.2 V per repeating unit. Superseded for sizing by AQS-PAR-001 Rev B: 6.7 kWh/kg NaOH at 2 M product (EDBM_WHEY_2021), BMED_ACID 26.93 kW; acid and base concentrated to 20 wt% by EVAP_ACID (2.41 kW) and EVAP_BASE (2.40 kW) on 480 V.

Induction pyro: 0.8–1.2 kWh/kg dry plastic to the coil, plus afterburner heat from NCG.
Dryer: 0.70–0.85 kWh/kg water evaporated (Q3 through HX-4). Since graph Rev J the EW reject goes to Q4 through HX-8 (AQS-DUTY-008 Rev B).
Shredder: 10–25 kWh/wet t, peaked.

## AC vs DC

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

Continuous AC parasitics ≈ 9 kW → 216 kWh/day whether the feed is e-waste or dirt. That term dominates every lean feedstock.

## Pulsed DC

Use pulse (10–100 Hz, 20–40 % duty, same average coulombs) when the liquor is below the limiting current or the deposit should be powder.

- PK-1 Co, PK-2 Mn, PK-3 Cr, PK-7 Tl: low tenor. Pulse.
- EW-6 Ni, EW-9 Zn: hydrogen competes. Pulse or pulsed-reverse.
- EW-7 Fe: we want powder. Pulse or periodic interrupt to shed.
- EW-3 Cu sheet: **periodic reverse** (1–5 % anodic time), not on/off pulse. Levels the sheet.
- EW-1 Au powder: pulse acceptable.
- BMED and CRU: **steady**. Pulsing the BPM stack wastes water-split efficiency and hammers membranes.
- Induction: AC. Do not rectify the coil.

## Feedstock assays used

These are working averages, not a contract assay. Real cells vary by decade and country. Each row is a case inside the feedstock envelope of AQS-ASSAY-001 Rev C (`FEED_ASSAY.md`). None of them is the design feed. The plant is checked across that envelope, regolith-like through metal-rich PCB.

| Stream | Fe | Cu | Al | other plateable | Au | Ag | plastic + paper | glass / silicate | moisture |
|---|---|---|---|---|---|---|---|---|---|
| Mixed WEEE | 25 % | 7 % | 5 % | 3 % | 50 ppm | 200 ppm | 22 % | 18 % | 5 % |
| PCB-rich WEEE | 8 % | 16 % | 4 % | 4 % | 150 ppm | 800 ppm | 25 % | 30 % | 3 % |
| MSW (as-received) | 4 % | 0.2 % | 1.5 % | 0.2 % | — | — | 30 %* | 5 % | 25 % |
| Landfill mine, bulk | 2.5 % | 0.15 % | 0.8 % | 0.15 % | trace | trace | 12 % | 8 % + 45 % soil | 20 % |
| Landfill, TBM in a WEEE cell | 15 % | 3 % | 3 % | 1.5 % | 20 ppm | 80 ppm | 18 % | 15 % + 20 % soil | 15 % |
| Porphyry Cu tailings | 8 %** | 0.30 % | 3 % | 0.05 % | 0.1 ppm | 2 ppm | 0 | 70 % | 15 % |
| Au tailings | 5 %** | 0.05 % | 2 % | — | 0.4 ppm | 2 ppm | 0 | 75 % | 18 % |

\* MSW “plastic + paper” is the pyro/dryer load. Paper dries then chars; plastic cracks.
\** Fe in tailings is mostly oxide. Only the fraction that dissolves in Salria shows up on EW-7. Assume 25 % of tailings-Fe is leachable here; the rest reports to grit / digest.

## Energy per wet tonne of feed

kWh/t = plated-metal energy + BMED for that tonne’s acid/base + dryer + pyro + 9 kW aux × hours to process 1 t.

At 150 kg/day a tonne takes 6.7 days, so aux on that tonne is 9 kW × 160 h ≈ **1,440 kWh/t**. That is the container-scale penalty. At 2 t/day the same fans cost 108 kWh/t. Report both.

### Process energy only (no fan penalty)

| Stream | EW metals kWh/t | BMED kWh/t | dryer kWh/t | pyro kWh/t | process total |
|---|---|---|---|---|---|
| Mixed WEEE | 1,180 | 80 | 40 | 220 | **1,520** |
| PCB-rich | 820 | 90 | 25 | 250 | **1,185** |
| MSW | 170 | 40 | 190 | 280 | **680** |
| Landfill bulk | 110 | 50 | 150 | 120 | **430** |
| Landfill TBM / WEEE cell | 640 | 70 | 110 | 180 | **1,000** |
| Cu tailings 0.3 % | 80 | 180 | 110 | 0 | **370** |
| Au tailings | 25 | 160 | 130 | 0 | **315** |

How those EW numbers were built (mixed WEEE per wet t):
- Fe 250 kg × 0.85 leach × 3.72 kWh/kg ≈ 790
- Cu 70 kg × 0.90 leach × 2.18 ≈ 137
- Ni+Zn+Sn+Pb ~30 kg blended ≈ 80
- Al 50 kg is precip, not EW
- Au 50 g × 0.82 kWh/kg ≈ 0.04 (money, not energy)
- Ag 200 g ≈ 0.1

BMED is sized off acid consumed in leach plus caustic to digest glass and to drop Al/Mg/Ca. Tailings and FR-4-rich WEEE pay more BMED.

### With container aux (150 kg/day)

Add 1,440 kWh/t:

| Stream | kWh / wet t | kWh / day at 150 kg | average kW |
|---|---|---|---|
| Mixed WEEE | 2,960 | 444 | 18.5 |
| PCB-rich | 2,625 | 394 | 16.4 |
| MSW | 2,120 | 318 | 13.2 |
| Landfill bulk | 1,870 | 280 | 11.7 |
| Landfill TBM / WEEE cell | 2,440 | 366 | 15.2 |
| Cu tailings | 1,810 | 272 | 11.3 |
| Au tailings | 1,755 | 263 | 11.0 |

Peak remains ~50 kW whenever pyro and the EW string and the shredder overlap. Tailings never turns the coil on, so peak drops to ~25 kW.

## Yields per wet tonne (what leaves the plant)

Leach recovery assumed 85–95 % on exposed metal, 70 % on FR-4-locked copper after burnout, 50 % on oxide iron in tailings.

| Stream | plated metals kg | Al/Mg/Ca cake kg | oil cuts kg | silicate + grit kg |
|---|---|---|---|---|
| Mixed WEEE | 280 | 70 | 150 | 200 |
| PCB-rich | 220 | 50 | 170 | 320 |
| MSW | 45 | 25 | 180 | 80 |
| Landfill bulk | 30 | 20 | 80 | 520 |
| Landfill TBM / WEEE cell | 160 | 50 | 120 | 280 |
| Cu tailings 0.3 % | 25 | 40 | 0 | 850 |
| Au tailings | 8 + 0.4 g Au | 30 | 0 | 880 |

“Plated metals” is Fe+Cu+Ni+Zn+Sn+Pb+precious. Fe dominates WEEE mass and energy. Au dominates WEEE value and is electrically cheap.

## TBM vs bucket wheel

Same plant. Different feed.

- Bucket wheel / strip: high fines, high moisture, high soil. Looks like **landfill bulk**. Dryer and digest run hard. EW string loafs. Aux still 9 kW.
- TBM: you can drive the head into a 1990s e-waste trench or a construction cell. Assays swing toward **TBM / WEEE cell** or toward bulk soil. The electrical plant does not change; RECT-EW current setpoint does.

Do not size the rectifier for the leanest feed. Size RECT-EW at the top of the plateable-metal envelope in AQS-ASSAY-001 Rev C and turn current down for lean feeds. The cell currents are the duty values; the 180 A string figure is superseded by the EW_1 node, 2105 A (AQS-PWR-001 Rev C).

## What the 100 A / 480 V service actually holds

83 kVA. Module peak 50 kW, average 11–19 kW. One service feeds one pair of boxes. A 500 kg/day plant is three wet strings or one larger RECT-EW and a 200 A service.

PV to match the average: 20 kW-ac with a day’s storage covers the module on e-waste. Pyro peaks still need the rectifier skid or a generator.

## Sources for assays and cell voltages

Mixed WEEE metal splits: published WEEE category mixes (ferrous 20–30 %, Cu 3–20 % by device class, plastics 15–30 %). PCB Cu ~20 %, Au 70–250 g/t. MSW metals ~4–8 % total, plastics ~12 %, moisture ~20–25 %. Landfill excavations: soil/fines often 45–60 %, metals 2–4 %, plastic 7–17 %. Porphyry tailings residual Cu commonly 0.2–0.4 %. Chloride / sulfate EW voltages: Cu ~2.0–2.2 V, Ni chloride ~3 V, Zn ~3.4 V, ~1.8–2.2 kWh/kg Cu and ~3.0–3.4 kWh/kg Zn at industrial CE.
