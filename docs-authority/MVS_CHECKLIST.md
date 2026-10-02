# MVS checklist

Document: AQS-MVS-CHK-001
Date: 2026-10-02
Plan: docs-authority/MVS_PLAN.md
Graph topology is the baseline. Check an item only when the solid or the number exists.

## Nodes

- [x] WS_PHOS node added
- [x] WS_PHOS bund separate from HF
- [x] S34 split shows phosphoric etch on WS_PHOS

## EW aisle

- [ ] ew_cascade_present.py run on the operator box
- [ ] ew_cascade.FCStd written
- [ ] plant.FCStd not opened by that run
- [ ] EW-1 through EW-9 at 750 mm pitch
- [ ] Overflow order EW-1 → EW-9 → polish confirmed on the solid

## Machines

- [x] GLASS_RINSE solid and nozzles
- [x] GLASS_MILL solid and nozzles
- [x] GLASS_BURNOUT solid and nozzles
- [x] Burnout off-gas on the oil-vapor header
- [x] Glass order is rinse, drain, mill, burnout, existing digest
- [x] VCD compressor selected inside 14–20 kWh/m³ at 0.11 m³/d
- [x] VCD equipment ID issued
- [x] REMIN dose from hydroxide crib
- [x] REMIN 10 L/d, 25 mg/L Ca, 10 mg/L Mg
- [x] UV after the remineralizer dose
- [x] LITHO_COAT, LITHO_ALIGN, LITHO_DEV issued
- [x] Wafer starts/day locked in the 1–5 band
- [x] UV lamp class selected
- [x] ELECTRODE_COAT booth, carbon or nickel
- [x] Electrode exhaust to MET_AHU
- [x] BLOW_MOLD clamp and air, peak 2–4 kW
- [x] Blow-mold scrap to the oil line
- [x] SOLAR_PV_CELL train: texture, emitter, PSG etch, ARC, contact, fire, IV
- [x] Solar train uses WS_KOH and is not the yard array
- [x] GEO_ORC pad remains empty

## Ladder

- [x] Q1_A volume, fluid, temperature, relief orifice
- [x] Q1_B volume, fluid, temperature, relief orifice
- [x] Q2_A volume, fluid, temperature, relief orifice
- [x] Q2_B volume, fluid, temperature, relief orifice
- [x] Q3_A volume, fluid, temperature, relief orifice
- [x] Q3_B volume, fluid, temperature, relief orifice
- [x] Q4_A volume, fluid, temperature, relief orifice
- [x] Q4_B volume, fluid, temperature, relief orifice
- [x] One thermosyphon per step
- [x] Q1 fluid is oil or ceramic
- [x] Q4 fluid is water
- [x] Q1 relief is not a hab vent

## Fab room

- [x] ISO 14644 class written on the wet bench
- [x] ISO 14644 class written on the tool row

## Placement

- [ ] Generator envelope replaced with the issued size
- [ ] Fuel-cell envelope replaced with the issued size
- [ ] Methanol skid envelopes replaced with the issued sizes
- [ ] flow_to_cad.py run against a copy
- [ ] plant.FCStd unchanged

## Done

- [ ] Every present node has a solid or is a header
- [ ] loops_closed still false until the copy carries the solids
