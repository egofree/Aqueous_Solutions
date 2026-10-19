# Hydrogen compressor first-article bench run

Document number: AQS-TST-005
Revision: A
Date: 2026-10-19
Authority: AQS-PLAN-007 X-MFG-36. Test procedure for A-M-169 ("first-article bench run"), design basis AQS-DUTY-067 Rev B (`docs-authority/sizing/H2_COMPRESSOR.md`). Study procedure, not run.

Status: **issued 2026-10-19; the run is hardware-gated** - it needs the first-article 5-stage diaphragm compressor built to the AQS-DUTY-067 Rev B design. No test record exists yet; A-M-169 stays `needs_verification` until the data sheets below are completed and the register entry is updated by the assumptions lane.

## 1. Purpose and prediction

The Rev B design rests on assumed values that only this run replaces (A-M-169): adiabatic efficiency 0.65, volumetric efficiency 0.80, motor efficiency 0.90, speed 300 rpm, cavity depth 3 mm. Predicted duty (AQS-DUTY-067 Rev B): 11.34 kg/d H2, 10 to 200 bar in 5 stages at ratio 1.821, every stage intercooled to 35 C, stage discharge at or below 125 C against the 135 C API 618 limit for hydrogen-rich service, specific work 1.97 kWh/kg, average 0.933 kW, peak 2.798 kW.

Design stage table (acceptance reference):

| Stage | In bar | Out bar | Swept cm3/stroke | Diaphragm D mm |
|---|---|---|---|---|
| 1 | 10.0 | 18.2 | 125.1 | 326 |
| 2 | 18.2 | 33.1 | 68.7 | 241 |
| 3 | 33.1 | 60.3 | 37.7 | 179 |
| 4 | 60.3 | 109.9 | 20.7 | 133 |
| 5 | 109.9 | 200.0 | 11.4 | 98 |

Materials as designed: head and plates 17-4PH H1150 / 316L (hydrogen service, M6 review AQS-REV-H2-001), triple-layer 301 SS diaphragm with leak detection between layers, 316L tube-in-tube intercoolers.

## 2. Preconditions

1. First-article compressor built and inspected to the Rev B drawings: diaphragm stack, cavity depth measured, interlayer leak-detection ports fitted and proven on air.
2. Test stand rated 250 bar with stand PSV set 1.1 x 200 bar = 220 bar, sized for full flow, vented to the roof H2 stack (not the room).
3. Gas source: instrument air or nitrogen for phases A-C; hydrogen (bottled, Grade D per ISO 14687 is enough for the run) only for phase D.
4. Purging: vacuum-and-inert cycles to below 1 % O2 in the loop before any H2 admission (NFPA 2 / ANSI/AIAA G-095 practice for the inerting steps).
5. Test cell: roof-ventilated H2 room or outdoor stand, H2 detection at 25 % LFL alarming and 60 % LFL shutting the run down (AQS-SAF-006 settings), no ignition sources within the classified zone (AQS-ELEC-009 basis), bonding and earthing of the stand.
6. Intercooler CW loop connected and flowing before any run; 35 C set point.
7. Motor drive with a calibrated power analyser; stroke counter and speed readout.
8. Calibration: all PT/TT within certificate; the mass-flow reference (thermal-mass H2 meter or gasometer) proved against a cylinder on a balance.

## 3. Instrumentation

| Tag | Measurement | Range | Notes |
|---|---|---|---|
| PT-1..5 | stage discharge pressure | 0-25 / 40 / 70 / 125 / 250 bar | one per stage |
| PT-0 | suction pressure | 0-16 bar | |
| TT-1..5 | stage discharge temperature | 0-200 C | the 135 C acceptance turns on these |
| TT-CW | intercooler outlet | 0-60 C | 35 C set point |
| FT-H2 | H2 mass flow | 0-1 kg/h | gasometer cross-check each phase |
| EI-M | motor electrical power | 0-5 kW | power analyser; efficiency chain |
| SR-01 | speed | 0-400 rpm | |
| PT-LD | diaphragm interlayer ports | -1 to 25 bar | must stay at atmospheric - the leak test |

## 4. Procedure

1. **Phase A, cold checks**: crank the machine on nitrogen at reduced speed; verify valve timing, no interlayer pressure rise, intercooler flow and the ESD chain (test the PSV lift at the bench before installation).
2. **Phase B, nitrogen run-in**: 10 to 200 bar on N2 at 300 rpm for 4 h; log all PT/TT/EI at 10 min intervals; measure volumetric efficiency per stage from the delivered flow.
3. **Phase C, duty cycle on N2**: 8 h/d profile for 3 days (the plant duty: runs with the electrolyser); check stage temperatures hold <= 125 C at 35 C cooling, and record the peak kW.
4. **Phase D, hydrogen run**: purge to < 1 % O2; run 10 to 200 bar for 8 h at 300 rpm; log as phase B plus FT-H2 and PT-LD continuously; shut down safely from full pressure once (ESD test).
5. **Teardown**: diaphragm layers dye-checked; valve seats inspected; record all wear.

## 5. Acceptance limits (from the A-M-169 / AQS-DUTY-067 Rev B bases)

| Quantity | Design value (assumed) | Acceptance band | If outside |
|---|---|---|---|
| Specific work | 1.97 kWh/kg | <= 2.2 kWh/kg on H2 | stage count/ratio re-solve (Rev B path); below 1.97 substitutes directly |
| Stage discharge temperature | <= 125 C (135 C API 618 limit) | <= 135 C every stage | intercooler or ratio re-solve; no operation above 135 C |
| Volumetric efficiency | 0.80 | >= 0.75 | swept volume / speed re-solve |
| Adiabatic efficiency | 0.65 | record and substitute | feeds the specific-work re-solve |
| Diaphragm interlayer leak | none | zero pressure rise over every phase | teardown and re-layer; no H2 phase after any rise |
| Average / peak power | 0.933 / 2.798 kW | record and substitute | load-list update (AQS-ELEC-007 path) |
| Motor efficiency | 0.90 | >= 0.85 | motor spec update (X-INV-02 basis) |

The record closes A-M-169 when every row of the data sheets in section 6 is filled and signed for phases B-D; the assumptions lane then sets `needs_verification` false with the measured values and the solver re-runs (driver/register writes are outside the docs lane - handoff).

## 6. Data sheets

Run header: date, operators, machine serial, gas and bottle IDs, calibration due dates, cell ventilation checks.

| Sheet | Columns |
|---|---|
| DS-1 phase A/B log | t, rpm, PT-0..5 bar, TT-1..5 C, EI-M kW, FT kg/h, volumetric eta per stage, notes |
| DS-2 duty cycle | day, hours run, kWh, peak kW, average kW, TT max, CW set point drift, notes |
| DS-3 H2 run | t, PT-0..5, TT-1..5, EI-M, FT-H2 kg/h, specific work kWh/kg, PT-LD, notes |
| DS-4 ESD test | init condition, trip source, time to safe state, final PT, notes |
| DS-5 teardown | diaphragm dye-check results per stage, valve seat condition, measured clearances, notes |

## 7. Safety

This is a 200 bar hydrogen machine: the run happens only in the ventilated test cell with detection live, the stand PSV fitted, and the ESD proven (phase D includes one shutdown test on purpose). Nitrogen asphyxiation hazard during purging - O2 monitor worn. Interlayer leak detection is a stop condition, not a trend to watch. No phase runs without CW flow. The old two-stage layout of AQS-DUTY-067 rev A (predicted discharge near 290 C) is withdrawn and must not be rebuilt for test.
