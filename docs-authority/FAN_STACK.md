# Fan curves and stack heights

Document number: AQS-GAS-003  
Revision: B  
Date: 2026-09-27  
Measurement: SI

| Rev | Change | Date |
|---|---|---|
| A | First issue. Module 150 kg/day, factory roof ~8 m eave | 2026-09-27 |
| B | Note: stack = upset/contingency; closure per AQS-VENT-001 | 2026-09-28 |
| C | Rewritten to the documentation style guide (AQS-DOC-002): purpose first, sections and table titles, above ground level spelled out. No height, curve or duty changed. | 2026-10-25 |

Site wind rose and building height still govern the final permit stack.
## 1. Purpose and scope

These numbers size the induced-draft fans and freeze the CAD stack solids. The stacks are the upset and contingency path only; continuous vent closure is AQS-VENT-001.

Headers stay four objects. No common fan, no common stack.

**AQS-VENT-001:** Issued stack heights remain valid for **upset /
contingency residual** and ID-fan SP. They do **not** authorize
continuous free outdoor dump as the design end state. Acid train
normal end = ALK + ACID_POLISH → CRU; Br₂ = regen → pos. tank; H₂ =
CRYO_H2 consumers; oil NCG = AFTERBURNER then FLUE_CAP → CRYO.

## 2. Design flows

In-leak and hood capture dominate volume. Process generation does not.

| Header | Duty | Q design | T | Gas after treatment |
|---|---|---|---|---|
| HDR_ACID_GAS | CSTR lid N3 + 9 EW anode hoods + PK-6/9 hose | 0.42 m³/s (1500 m³/h) | 40–60 °C into pack | HCl / Cl2 stripped. Fan sees wet air + residual CO2 |
| HDR_DUST | Hopper / shredder hood | 0.55 m³/s (2000 m³/h) | ambient | Clean air after bags |
| HDR_H2 | 9 cathode hoods, sweep to &lt;25 % LFL | 0.25 m³/s (900 m³/h) | 30–50 °C | H2 + air. Arrestor then dryer |
| HDR_OIL_VAPOR | Pyro nozzle → quench. NCG is forced to AFTERBURNER | 0.05 m³/s (180 m³/h) NCG | 80–150 °C into quench | No ID stack. Afterburner is the sink |
| HDR_CAUSTIC | Digest + BMED BASE mist | 0.08 m³/s (300 m³/h) | 40 °C | After water/HCl pack |

H2 generation at the cathodes is faradaic leftover, not the sweep
volume. Sweep is set by LFL, not by Faraday.

Faraday check (order of magnitude): 50 kg/day Zn-equivalent at 2 e⁻
and 80 % cathode efficiency leaves ~0.2 kg/h H2 if the rest goes to
water reduction. That is ~2.2 Nm³/h H2. Dilute to 1 % v/v → ~220 Nm³/h
sweep. 900 m³/h is 4× that number and covers nine hoods plus leaks.

## 3. System resistance (dirty)

| Train | Pack / bags | Duct + hoods | Stack | Total SP | Fan after |
|---|---|---|---|---|---|
| Acid | 1.2 kPa (50 mm saddles, 1.8 m, 1.2 m/s) | 0.5 kPa | 0.15 kPa | **1.85 kPa** | Yes — impeller sees scrubbed gas |
| Dust | 1.5 kPa dirty bags | 0.4 kPa | 0.10 kPa | **2.0 kPa** | Yes — after baghouse |
| H2 | 0.3 kPa dryer + arrestor | 0.3 kPa | 0.08 kPa | **0.68 kPa** | Small 316L or coated |
| Caustic | 0.8 kPa pack | 0.2 kPa | 0.05 kPa | **1.05 kPa** | FRP or PP |

Add 20 % margin on SP for damper and future hoods.

## 4. Fan selection (bought to class, not a maker type)

| Train | Q | SP | Wheel | Inlet | Shaft power @ 60 % | Motor |
|---|---|---|---|---|---|---|
| Acid ID | 0.50 m³/s | 2.2 kPa | FRP backward-curve | 315 mm | 1.8 kW | 2.2 kW TEFC, VFD |
| Dust ID | 0.66 m³/s | 2.4 kPa | FRP or coated CS | 355 mm | 2.6 kW | 4.0 kW TEFC, VFD |
| H2 ID | 0.30 m³/s | 0.85 kPa | 316L | 200 mm | 0.43 kW | 0.75 kW, explosion-proof per area class |
| Caustic ID | 0.10 m³/s | 1.3 kPa | PP / FRP | 160 mm | 0.22 kW | 0.37 kW TEFC |

Vendor class: Hartzell Series 40 FRP, New York Blower FRP, or equal.
Do not put a CS wheel on HDR_ACID_GAS.

Curve points the vendor must beat (acid fan, 20 °C air equivalent):

| Q (m³/s) | Min SP (kPa) |
|---|---|
| 0.30 | 2.4 |
| 0.42 | 2.2 |
| 0.50 | 2.0 |
| 0.60 | 1.6 |

Set the VFD so the hood faces stay at −50 to −120 Pa. Do not size the
fan from this table without the vendor curve stamped against the
actual duct takeoff.

## 5. Stack heights

Building assumption for the factory (not the 40HC shipping box):
eave 8 m, ridge 10 m, no adjacent high-rise. Acid stack is the tallest
because the discharge can still carry residual Cl2 if the pack is
starved.

| Stack | CAD height (grade to lip) | ID | Material | Rain cap | Notes |
|---|---|---|---|---|---|
| Acid | **12 000 mm** | 360 mm | FRP | no — open cone | 2.5 m above ridge. Velocity ~4.1 m/s at 0.42 m³/s |
| Dust | **8 000 mm** | 250 mm | CS / 304 | yes | Clean air. 7.0 m/s |
| H2 | **8 000 mm** | 250 mm | 316L | no | Buoyant. Keep away from acid stack; 6 m plan spacing min |
| Caustic | **6 000 mm** | 160 mm | PP | yes | Short. Discharge is wet air + CO2 |
| Afterburner | unit stack on AFTERBURNER | 300 mm | 304 / CS | no | Not an ID stack. Q1 flue |

Shipping-module variant: stub each stack at 2 400 mm above ground level with a
companion-flange for the factory riser. The 40HC roof is not the
dispersion height.

H2 stack and acid stack do not share a bridge. Cross-contamination of
a starved alkali pack with hydrogen is a detonation case.

## 5. CAD objects

| Object | File | Height in model |
|---|---|---|
| FAN_STACK (acid) | `mfg_scrubber_train.scad`, `mfg_gas_handling.scad` | 12 000 |
| dust stack | `mfg_gas_handling.scad` | 8 000 |
| H2_STACK | `mfg_gas_handling.scad` | 8 000 |
| caustic stack | `mfg_gas_handling.scad` | 6 000 |

Permit modelling (AERMOD / equivalent) is site work and is not in
this file.
