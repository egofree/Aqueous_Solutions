# Bench test - BMED stack polarisation

Document number: AQS-TST-006  
Revision: A  
Date: 2026-10-30  
Authority: AQS-PLAN-007 X-MFG-35; A-M-077 (the 1.8-2.4 kWh/kg acceptance band); A-M-170/171 (the issued triplet construction); EDBM_PILOT_2023 (the pilot class). Generated per the bench-run directive: the apparatus is the issued plant triplet construction at bench scale, defined for build. Style: AQS-DOC-002.

| Rev | Description | Date |
|---|---|---|
| A | First issue: apparatus, instrumentation, procedure and acceptance | 2026-10-30 |

## 1. Purpose, scope and prediction

The bench stack polarisation test measures volts per triplet and current efficiency as functions of current density and salt concentration, replacing the literature-derived basis of A-M-077 (1.8-2.4 kWh per kg acid+base pair) with a measured specific energy for the plant's own triplet construction. Prediction from the issued design: 1.22 V per triplet from physics, 1.67 V measured-pilot class, at CE 0.80 on 2 M product; the acceptance band bounds the specific energy at 1.8-2.4 kWh/kg.

## 2. Apparatus (build from this definition)

1. **Stack**: 10 triplets of the issued construction - PP frames 300 x 300 mm, 0.8 mm PE mesh spacers, one bipolar membrane and two monopolar membranes per triplet (anion + cation), Ti/MMO anode end plate, 316L/Ni cathode end plate (A-M-170). Fastened to the issued torque pattern with gaskets per the membrane maker's class.
2. **Hydraulics**: three peristaltic (or bellows) pump loops - acid, base and salt feed - each PTFE/PVDF tubing, flow 5-15 L/h per compartment pass; polyethylene feed tanks 20 L each with lids and vent filters.
3. **Feed**: sodium chloride solution 20 g/L (2 M equivalent at the product tap: the test runs the concentration ladder 0.5, 1.0, 2.0 M NaOH product).
4. **Power supply**: 0-30 V DC, 0-20 A, constant-current mode, ripple under 5 %; polarity reversible.
5. **Safety**: the acid and base product streams are corrosive - face shield, gloves, splash tray; the hydrogen evolved at the cathode (small, stoichiometric) vents to the room; emergency wash within 10 s walk.

## 3. Instrumentation

| Tag | Measurement | Range | Notes |
|---|---|---|---|
| EI-01 | stack volts | 0-30 V | logged |
| EI-02 | stack amps | 0-20 A | shunt, logged |
| FT-01/02/03 | acid, base, salt flows | 0-20 L/h | per loop |
| CT-01/02 | acid and base product conductivity | 0-200 mS/cm | temperature-compensated |
| PH-01/02 | acid and base product pH | 0-14 | at the product taps |
| TE-01 | stack temperature | 0-60 C | inlet, salt loop |

## 4. Procedure

1. Assemble the stack to the issued torque; leak-test each loop at 0.5 bar for 30 min (no external drop, no cross-loop transfer).
2. Flush all loops with deionised water; verify each compartment conductivity below 5 uS/cm.
3. Polarisation ladder at 20 g/L salt feed: step the current 1, 2, 4, 6, 8, 10, 12 A; at each step record EI-01/02 every 30 s for 10 min after the temperature stabilises.
4. Production runs at 8 A (the plant's per-triplet current class): collect acid and base product for 60 min at each ladder concentration (0.5, 1.0, 2.0 M product); weigh the products, titrate each for molarity, and log EI-01/02, flows and temperature continuously.
5. Compute specific energy: kWh/kg = (V x I x hours) / (kg acid + kg base produced), per run.
6. Repeat the 8 A production run once on a second day to bound the day-to-day drift.

## 5. Acceptance limits (from A-M-077)

- Specific energy at the 2 M product point: **1.8-2.4 kWh per kg acid+base pair** (the band replaces the stack-vendor basis of A-M-077 on pass).
- Current efficiency: 0.80 +/- 0.05 at 2 M product (the governing verification item per the issued sizing).
- Triplet voltage at 8 A, 20 g/L: within 1.22-1.67 V (the physics-to-pilot band).
- A result outside the band re-opens X-MFG-35 with the measured curve as the new basis; no re-test without a design change is permitted.

## 6. Data sheets

The logged records (EI-01/02 every 30 s, the product weights and titrations, the temperature) are the run's data sheets; file them with the completed checklist against the task in the task plan.

## 7. Safety

Acid and base products to 2 M: face shield, acid gloves, splash tray; hydrogen at the cathode vents to the room (no ignition source within 1 m); the DC supply has an RCD on the mains side and the stack frame is earthed.
