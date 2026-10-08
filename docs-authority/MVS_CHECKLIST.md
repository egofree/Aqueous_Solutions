# MVS checklist

Document: AQS-MVS-CHK-001
Date: 2026-10-02
Plan: docs-authority/MVS_PLAN.md
Graph topology is the baseline. Check an item only when the solid or the number exists.

## Nodes

- [x] WS_PHOS node added, 800×800×1100
- [x] WS_PHOS bund separate from HF
- [x] S34 split shows phosphoric etch on WS_PHOS

## EW aisle

- [x] ew_cascade_present.py run on the operator box
- [x] ew_cascade.FCStd written
- [x] plant.FCStd not opened by that run
- [x] EW-1 through EW-9, each 600×420×650, at 750 mm pitch
- [x] Overflow order EW-1 → EW-9 → polish confirmed on the solid
- [x] ew_cascade.step re-exported with the nine cells, eight launders, POLISH_BANK, and the EW-9 → polish pipe (2026-10-07)

## Machines

- [x] GLASS_RINSE 1200×600×800 and nozzles
- [x] GLASS_MILL 800×600×800 and nozzles
- [x] GLASS_BURNOUT 800×600×1200 and nozzles
- [x] Burnout off-gas on the oil-vapor header
- [x] Glass order is rinse, drain, mill, burnout, existing digest
- [x] VCD-COMP-01 1400×600×1200, 14–20 kWh/m³ at 0.11 m³/d
- [x] VCD equipment ID issued
- [x] REMIN-01 600×400×800, hydroxide crib
- [x] REMIN 10 L/d, 25 mg/L Ca, 10 mg/L Mg
- [x] UV after the remineralizer dose
- [x] LITHO_COAT 600×500×800, ALIGN 500×500×800, DEV 500×500×800
- [x] Wafer starts/day locked in the 1–5 band
- [x] UV lamp class selected
- [x] ELC-BOOTH-01 1200×800×1800, carbon or nickel
- [x] Electrode exhaust to MET_AHU
- [x] BLOW-01 1200×800×1600, peak 2–4 kW
- [x] Blow-mold scrap to the oil line
- [x] PV-CELL-01 2400×1200×1600: texture, emitter, PSG etch, ARC, contact, fire, IV
- [x] Solar train uses WS_KOH and is not the yard array
- [x] GEO_ORC pad remains empty

## Ladder

- [x] Q1_A 800×800×1200, oil, 0.30 m³, 250 °C, 1/2 in relief
- [x] Q1_B 800×800×1200, oil, 0.30 m³, 250 °C, 1/2 in relief
- [x] Q2_A 800×800×1200, oil, 0.30 m³, 150 °C, 1/2 in relief
- [x] Q2_B 800×800×1200, oil, 0.30 m³, 150 °C, 1/2 in relief
- [x] Q3_A 800×800×1200, water, 0.40 m³, 100 °C, 1/2 in relief
- [x] Q3_B 800×800×1200, water, 0.40 m³, 100 °C, 1/2 in relief
- [x] Q4_A 800×800×1200, water, 0.60 m³, 70 °C, 1/2 in relief
- [x] Q4_B 800×800×1200, water, 0.60 m³, 70 °C, 1/2 in relief
- [x] One thermosyphon per step
- [x] Q1 fluid is oil or ceramic
- [x] Q4 fluid is water
- [x] Q1 relief is not a hab vent

## Fab room

- [x] ISO 14644 class written on the wet bench
- [x] ISO 14644 class written on the tool row

## Placement

- [ ] Generator envelope 2000×1000×1600 on the copy
- [ ] Fuel-cell envelope 1800×800×1600 on the copy
- [ ] Methanol skids 2200×900×1400, 2200×900×1400, 800×800×1100, 1800×800×1600 on the copy
- [ ] flow_to_cad.py run against a copy
- [ ] plant.FCStd unchanged

## Done

- [ ] Every present node has a solid or is a header
- [ ] loops_closed still false until the copy carries the solids
