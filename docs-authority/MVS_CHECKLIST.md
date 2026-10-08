# MVS checklist

Document: AQS-MVS-CHK-001
Date: 2026-10-02; updated 2026-10-07
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
- [x] HL-* edge duties, media, temperatures, flows, and line sizes (AQS-DUTY-008)
- [x] Ladder energy balance closes, both ladders and single ladder
- [x] S67B CO2-rich cut defined (VSA at FLUE_KO, 12.75 kg/d CO2)
- [x] HX-8 tier: moved to Q4 (HL-HX8-Q4-A/B), 4.57 kW, Q4 return 45 → 49 °C, 6 K approach (AQS-DUTY-008 Rev B §13.1)
- [x] S18 and S67B: S67B carries the claim (12.75 kg/d); S18 at 0 kg/d, edge kept; CRYO_CO2 balanced (§13.3)
- [x] Q3 draws HX-4/HX-5/HX-6 are graph edges with duties 0.242 / 6.353 / 1.663 kW (§13.2)
- [x] Ladder balance closes running and idle, both ladders and single ladder (residual 0.000 kW)
- [x] Cross-tie coils fit inside the stores (Q2 on low-fin tube) (§13.5)
- [ ] Leach heater rating: 6.35 kW electric trim has no issued rating; issue one or adopt recuperator R-1 (§13.7)
- [ ] Digest heater: 1.08 kW trim sits inside the 1.5 kW GLASS_DIGEST study class; issue the class as the rating
- [ ] HDR_CO2 consumer or export for 11.6 kg/d (S85)
- [ ] Q4 bus 4.24 kW running vs 3.0 kW life priority; surplus 1.24 kW to ST-ORC-01 (ORC stays 0)
- [ ] Thermosyphon 0.8 m rise between stores on one floor: stands or level offset

## Fab room

- [x] ISO 14644 class written on the wet bench
- [x] ISO 14644 class written on the tool row

## Placement

- [x] Generator envelope 2000×1000×1600 on the copy
- [x] Fuel-cell envelope 1800×800×1600 on the copy
- [x] Methanol skids 2200×900×1400, 2200×900×1400, 800×800×1100, 1800×800×1600 on the copy
- [x] flow_to_cad.py run against a copy
- [x] plant.FCStd unchanged
- [x] Seed Rev F: BACKUP_GEN × FUEL_CELL and MEOH_SYNTH × MEOH_TANK resolved by origin moves; issued sizes unchanged
- [x] No pair of the 65 seed unit boxes intersects (all 2080 pairs checked)
- [x] Moved boxes keep 600 mm to every neighbour; BACKUP_GEN and FUEL_CELL keep 1100 mm on all faces (NEC 110.26 figure in seed rules)
- [x] FUEL_CELL south (O2) face 7700 mm from BACKUP_GEN, above the 7620 mm oxidizer separation without a 1 h wall
- [x] GEO_ORC pad stays empty; nearest box 700 mm
- [x] Glass envelopes (rinse, mill, burnout) at issued size on the copy
- [x] Seed Rev G: Q1_A..Q4_B reissued (Rev F study origins hit LEACH_CSTR_1, BMED_REGEN and the core); ladder A west wall y 9000, ladder B north-east bay y 15000
- [x] Ladder stores ≥ 700 mm from same-level equipment and walls on the placed copy; 0 intersections; seed all-pairs 0 of 2080
- [x] Ladder stores carried as issued envelopes on `plant_placed_2026-10-07_revJ.FCStd` (`--create-issued-only`)

## Done

- [ ] Every present node has a solid or is a header
- [ ] loops_closed still false until the copy carries the solids
