# UPW polish module bench test (RO permeance, rejection, EDI resistivity)

Document number: AQS-TST-004
Revision: A
Date: 2026-10-19
Authority: AQS-PLAN-007 X-MFG-34. Test procedure for A-M-176 ("Module permeance and EDI resistivity bench test"), design basis AQS-DUTY-070 (`docs-authority/sizing/UPW_POLISH.md`). Study procedure, not run.

Status: **issued 2026-10-19; the run is hardware-gated** - it needs the first RO/EDI module built to the AQS-DUTY-070 design (0.27 m2 flat-sheet TFC element and one 10-cell-pair EDI stack). No test record exists yet; A-M-176 stays `needs_verification` until the data sheets below are completed and the register entry is updated by the assumptions lane.

## 1. Purpose and prediction

The design rests on four assumed values that only this test replaces (A-M-176): membrane permeance A = 3 L/(m2 h bar), RO rejection 0.98, EDI current efficiency CE = 0.10, RO pump efficiency 0.40. Predicted duty at the design point (AQS-DUTY-070): flux 20 LMH at 6.9 bar feed (osmotic correction 192 mbar), RO+EDI specific energy 0.55 kWh/m3 of RO feed, 18 W whole train including the 15 W UV-TOC lamp.

The run measures the real values on one module and one stack of the plant design. The plant numbers are then re-solved through the pipeline; a value inside the acceptance bands of section 5 is a substitution, not a redesign.

## 2. Preconditions

1. One flat-sheet TFC element exactly as specified for the plant (0.27 m2 active area per module; same element in both plant modules).
2. One EDI stack of 10 cell pairs at 4 V (ALVARADO2014 basis), same spacers and electrodes as the plant stacks.
3. Test stand: feed tank of S25-equivalent VCD distillate (target 20 mg/L TDS; make-up by dosing NaCl into distilled water if the still is not running), CPVC/PVC-U plumbing per AQS-STD-002 rules M2/M3 (no bare metal wetted part on the polish path), feed pump rated to 10 bar with the duty point near 6.9 bar, reject and permeate returned to the feed tank except while sampling.
4. Stand relief: PSV or rupture disc set at 1.1 x maximum stand pressure, routed to a drain, sized for full pump flow.
5. Electrical: isolation transformer or RCD on the 4 V DC EDI supply; UV lamp interlocked to flow (no dry lamp operation); 185/254 nm exposure shielded.
6. Calibration: conductivity cells and the DC shunt within certificate; feed pressure gauge deadweight-checked.

## 3. Instrumentation

| Tag | Measurement | Range | Notes |
|---|---|---|---|
| PT-01 | feed pressure | 0-10 bar | at the module inlet |
| FT-01 | permeate flow | 0-2 L/h | gravimetric (balance) or calibrated cylinder |
| CT-01/02/03 | conductivity: feed, permeate (RO), product (EDI) | 0.055 uS/cm to 100 uS/cm | UPW-grade cells, temperature-compensated |
| TE-01 | feed temperature | 0-50 C | flux normalised to 25 C |
| TT-01 | UV lamp housing | 0-100 C | lamp derate check |
| EI-01 | EDI stack volts / amps | 0-10 V, 0-100 mA | shunt + DMM, logged |
| EI-02 | pump electrical power | 0-50 W | power analyser on the feed pump |
| PI-01 | UV lamp power | 0-20 W | logged with EI-02 for the 18 W train check |

## 4. Procedure

1. Flush the stand with distilled water to a background below 10 uS/cm; record stand blank.
2. Pre-soak the TFC element per the element conditioning sheet; flush 30 min at 2 bar, discard permeate.
3. **Permeance**: at 25.0 +/- 1.0 C, step feed pressure 3.0 / 5.0 / 6.9 / 8.0 bar; at each, wait to steady permeate flow (3 min), collect permeate 10 min by mass. Compute A = J / (dP - d pi) in L/(m2 h bar).
4. **Rejection**: at 6.9 bar and design flux, sample feed, RO permeate and reject; three aliquots each; rejection = 1 - Cp/Cf.
5. **Recovery sweep**: throttle reject to pass 90 / 95.5 / 98 % recovery; record permeate conductivity at each (95.5 % is the plant point; IA-UPW-REJ basis).
6. **EDI**: feed the RO permeate to the stack; hold 4 V; log current to steady state; sample EDI product at 30, 60 and 120 min (silica and boron grab samples at 120 min for information). Compute CE from the charge passed against the ions removed.
7. **Specific energy**: with EI-02 and PI-01, record total train power over a 2 h steady block at the design point; convert to kWh/m3 of RO feed.
8. **Post-test**: element dry-out is not required (plant runs wet); record storage disposition.

## 5. Acceptance limits (from the A-M-176 bases)

| Quantity | Design value (assumed) | Acceptance band | If outside |
|---|---|---|---|
| Permeance A | 3 L/(m2 h bar) | >= 2.4 | re-solve area or feed pressure through the pipeline; module count is the lever |
| RO rejection | 0.98 | >= 0.98 at 95.5 % recovery | EDI load grows; re-check CE and stack count |
| EDI CE | 0.10 | >= 0.08 | stack current/area re-solve |
| Product resistivity | not assumed in A-M-176 | record; expectation >= 10 Mohm cm from 20 mg/L feed | feeds the UPW spec decision (fab side) |
| Pump efficiency | 0.40 | >= 0.35 | load-list update (AQS-ELEC-007 path) |
| Train energy | 0.55 kWh/m3 RO feed (no UV) | record and substitute | BMED_UPW_POLISH load re-solved |

The record closes A-M-176 when every row of the data sheets in section 6 is filled and signed; the assumptions lane then sets `needs_verification` false with the measured values and the solver re-runs (driver/register writes are outside the docs lane - handoff).

## 6. Data sheets

Run header: date, operator, element and stack serials, feed batch TDS, calibration due dates.

| Sheet | Columns |
|---|---|
| DS-1 permeance | step no, dP bar, T C, permeate g/10 min, J (25 C) LMH, A LMH/bar, notes |
| DS-2 rejection | sample id, Cp uS/cm, Cf uS/cm, Cr uS/cm, rejection, recovery, notes |
| DS-3 recovery sweep | recovery %, permeate uS/cm, reject flow L/h, notes |
| DS-4 EDI | t min, V, mA, product uS/cm, CE, notes |
| DS-5 energy | t, pump W, UV W, EDI W, feed L/h, kWh/m3, notes |

## 7. Safety

Pressure below 10 bar water with stand relief fitted; UV shielded and flow-interlocked; no chemical hazard beyond the NaCl make-up; electrical work per the site LOTO. The polish train is all-polymer wetted path (AQS-STD-002 M2/M3) - do not substitute metal fittings on the wetted path for convenience.
