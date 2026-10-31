# Bench test - ZNBR2 flow-cell round trip

Document number: AQS-TST-007  
Revision: A  
Date: 2026-10-30  
Authority: AQS-PLAN-007 X-MFG-41; the plant duty (ZNBR2 continuous discharge 217.87 kW, X-ELS-02 solved); the zinc-bromine flow-battery chemistry class (aqueous ZnBr2, carbon-plastic electrodes, microporous separator, two electrolyte loops - the published flow-battery class the plant unit belongs to). Generated per the bench-run directive: the bench cell is defined for build, and the test replaces the battery-vendor basis of A-M-062 with measured round-trip efficiency and derate. Style: AQS-DOC-002.

| Rev | Description | Date |
|---|---|---|
| A | First issue: apparatus, instrumentation, procedure and acceptance | 2026-10-30 |

## 1. Purpose, scope and prediction

The bench flow-cell test measures round-trip efficiency and the discharge derate of the plant's zinc-bromine chemistry at bench scale, replacing the vendor basis of A-M-062 with measured numbers scaled to the plant duty (217.87 kW continuous at the plant scale; the bench scales by electrode area). Prediction from the chemistry class: round-trip 65-75 % at the bench current density, with the self-discharge (bromine crossover) visible as an overnight hold loss; the acceptance band below bounds the measured values.

## 2. Apparatus (build from this definition)

1. **Flow cell**: one cell pair - two carbon-plastic electrodes (the plant electrode class) pressed on a microporous separator, graphite bipolar plates, PP end blocks, active area 100 cm2; compression to the electrode maker's deflection class.
2. **Electrolyte loops**: two PP tanks (2 L anolyte, 2 L catholyte - aqueous ZnBr2 1.5-2 M class), two magnetically coupled centrifugal pumps, PTFE/PVDF tubing; the catholyte loop carries the bromine complex (the quaternary salt phase-setting additive per the chemistry class).
3. **Charge/discharge**: a bidirectional DC supply or charger + electronic load, 0-10 A at 0-3 V per cell (the zinc/bromine couple is about 1.85 V open circuit).
4. **Thermal**: the cells and loops sit in a fume hood at room temperature (20-25 C); bromine vapour is captured by the hood and a thiosulfate scrubber tray.
5. **Safety**: bromine is corrosive and volatile - the hood is mandatory, nitrile gloves and face shield, a thiosulfate neutraliser for spills; the electrolyte is toxic to aquatic life - all rinses collect in the scrubber tray.

## 3. Instrumentation

| Tag | Measurement | Range | Notes |
|---|---|---|---|
| EI-01 | cell volts | 0-3 V | logged every 1 s |
| EI-02 | cell amps | 0-10 A | logged every 1 s |
| FT-01/02 | anolyte, catholyte flows | 0-5 L/min | rotameter per loop |
| TE-01 | catholyte temperature | 0-50 C | efficiency corrected to 25 C |
| DI-01 | electrolyte density (bromine charge state) | 1.0-1.5 g/cm3 | hydrometer, sampled |

## 4. Procedure

1. Build the cell to the compression class; leak-test both loops with water at the working flow for 30 min.
2. Fill with the prepared electrolyte; circulate 15 min without current; record the open-circuit voltage.
3. Charge at 5 mA/cm2 to the 1.85 V class cutoff; rest 10 min; record the self-discharge hold curve for 12 h (the crossover measurement).
4. Discharge at 5, 10 and 20 mA/cm2 to the 0.9 V class cutoff; integrate EI-01 x EI-02 for the delivered amp-hours and watt-hours per cycle.
5. Compute round-trip efficiency = discharged Wh / charged Wh per cycle at each current density; repeat for three full cycles at 10 mA/cm2 and report the mean and the cycle-to-cycle drift.
6. Derate: repeat the 10 mA/cm2 cycle at 30 C and at 15 C (the plant envelope's edges) and report the efficiency and capacity deltas.

## 5. Acceptance limits (from the plant duty)

- Round-trip efficiency at 10 mA/cm2, 25 C: **65-75 %** (the chemistry-class band; the plant's derate derives from the measured value and this band).
- Capacity fade over three cycles: under 5 % per cycle pair.
- The self-discharge hold loss bounds the plant's standing loss line; a measured hold loss above 20 %/12 h re-opens the electrolyte additive choice.
- A result outside the band re-opens X-MFG-41 with the measured curve as the new basis; no re-test without a design change is permitted.

## 6. Data sheets

The logged EI-01/EI-02 series, the density samples and the integrated cycle energies are the run's data sheets; file them with the completed checklist against the task in the task plan.

## 7. Safety

Bromine and the complex phase are volatile, corrosive and aquatic-toxic: the fume hood is mandatory, the thiosulfate scrubber tray sits under the cell, and all rinses collect for neutralisation. Zinc salts dispose as heavy-metal waste. The DC side is current-limited; the cell frame is earthed.
