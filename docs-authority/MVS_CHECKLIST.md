# MVS checklist

Document: AQS-MVS-CHK-001
Date: 2026-10-02
Plan: docs-authority/MVS_PLAN.md
Graph topology is the baseline. Check an item only when the solid or the number exists.

## Nodes

- [ ] WS_PHOS node added
- [ ] WS_PHOS bund separate from HF
- [ ] S34 split shows phosphoric etch on WS_PHOS

## EW aisle

- [ ] ew_cascade_present.py run on the operator box
- [ ] ew_cascade.FCStd written
- [ ] plant.FCStd not opened by that run
- [ ] EW-1 through EW-9 at 750 mm pitch
- [ ] Overflow order EW-1 → EW-9 → polish confirmed on the solid

## Machines

- [ ] GLASS_RINSE solid and nozzles
- [ ] GLASS_MILL solid and nozzles
- [ ] GLASS_BURNOUT solid and nozzles
- [ ] Burnout off-gas on the oil-vapor header
- [ ] Glass order is rinse, drain, mill, burnout, existing digest
- [ ] VCD compressor selected inside 14–20 kWh/m³ at 0.11 m³/d
- [ ] VCD equipment ID issued
- [ ] REMIN dose from hydroxide crib
- [ ] REMIN 10 L/d, 25 mg/L Ca, 10 mg/L Mg
- [ ] UV after the remineralizer dose
- [ ] LITHO_COAT, LITHO_ALIGN, LITHO_DEV issued
- [ ] Wafer starts/day locked in the 1–5 band
- [ ] UV lamp class selected
- [ ] ELECTRODE_COAT booth, carbon or nickel
- [ ] Electrode exhaust to MET_AHU
- [ ] BLOW_MOLD clamp and air, peak 2–4 kW
- [ ] Blow-mold scrap to the oil line
- [ ] SOLAR_PV_CELL train: texture, emitter, PSG etch, ARC, contact, fire, IV
- [ ] Solar train uses WS_KOH and is not the yard array
- [ ] GEO_ORC pad remains empty

## Ladder

- [ ] Q1_A volume, fluid, temperature, relief orifice
- [ ] Q1_B volume, fluid, temperature, relief orifice
- [ ] Q2_A volume, fluid, temperature, relief orifice
- [ ] Q2_B volume, fluid, temperature, relief orifice
- [ ] Q3_A volume, fluid, temperature, relief orifice
- [ ] Q3_B volume, fluid, temperature, relief orifice
- [ ] Q4_A volume, fluid, temperature, relief orifice
- [ ] Q4_B volume, fluid, temperature, relief orifice
- [ ] One thermosyphon per step
- [ ] Q1 fluid is oil or ceramic
- [ ] Q4 fluid is water
- [ ] Q1 relief is not a hab vent

## Fab room

- [ ] ISO 14644 class written on the wet bench
- [ ] ISO 14644 class written on the tool row

## Placement

- [ ] Generator envelope replaced with the issued size
- [ ] Fuel-cell envelope replaced with the issued size
- [ ] Methanol skid envelopes replaced with the issued sizes
- [ ] flow_to_cad.py run against a copy
- [ ] plant.FCStd unchanged

## Done

- [ ] Every present node has a solid or is a header
- [ ] loops_closed still false until the copy carries the solids
