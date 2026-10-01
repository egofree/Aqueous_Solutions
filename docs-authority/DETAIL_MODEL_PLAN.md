# Manufacturing-detail model list

Document number: AQS-MFG-001  
Revision: A  
Date: 2026-09-26  
Measurement: metric

| Rev | Change | Description | Date |
|---|---|---|---|
| — | — | Basic issue. 1.3 conveyor. | 2026-09-26 |
| A | — | Remaining units as `cad/detail/mfg_*.scad`. | 2026-09-26 |

## Import into FreeCAD

```bash
cd cad/detail && bash build_stls.sh
cd ../freecad && /usr/bin/freecadcmd import_mfg.py
```

`import_mfg.py` places `MFG_*` meshes and hides matching stand-ins
(`MASSING_` prefix). Do not fuse meshes into `LEACH_CSTR_1`.
`build_plant.py` calls this at the end. Nudge with Placement if an
origin is off.

## 1. Feed train

- [x] 1.1 HOPPER — `mfg_hopper.scad`
- [x] 1.2 SHREDDER — `mfg_shredder.scad`
- [x] 1.3 VIBRATORY CONVEYOR — `mfg_vibratory_conveyor.scad`
- [x] 1.4 Lid coaming bolt ring — `mfg_lid_coaming.scad`

## 2. LEACH CSTR 1

- [x] 2.1–2.6 Shell, weir, trough, mixer, pump, lid — `mfg_leach_cstr.scad`
- [x] 2.3 flight (helix) — `cstr3_flight.scad`
- [x] 2.7 Nozzle schedule N1–N12 — `CSTR_NOZZLE_SCHEDULE.md`

## 3. Solids fork

- [x] 3.1 / 3.2 FLOAT / SINK DEWATER — `mfg_dewater.scad`
- [x] 3.3 VIBRATORY SPLIT — `mfg_vibratory_split.scad`

## 4. EW aisle

- [x] 4.1 Cell + CEM — `ew_cell.py`, `cem_cassette.scad`
- [x] 4.2 Valve — `funnel_valve.scad`
- [x] 4.3 / 4.4 Overflow + hangers + hoods + GF 546 — `mfg_ew_fitout.scad`
- [x] 4.5 Bund — `mfg_ew_bund.scad`
- [x] 4.6 VDF + pail — `mfg_harvest_vdf.scad`
- [x] 4.7 Instance EW-2…9 — `build_wet.py`

## 5. Wet products

- [x] 5.1 Precip — `mfg_precip.scad`
- [x] 5.2 PK cells — same funnel cell as 4.1; lids in `wet_products.py`
- [x] 5.3 BMED unit — `bmed_cell.scad`
- [x] 5.3b CRU — `mfg_cru.scad`
- [x] 5.4 / 5.5 Totes and bins — `mfg_totes.scad`
- [x] 5.6 MELT — `mfg_melt.scad`

## 6. Oil line

- [x] 6.1 DRYER — `mfg_dryer.scad`
- [x] 6.2 INDUCTION PYROLYZER — `mfg_induction_pyrolyzer.scad`
- [x] 6.3 QUENCH — `mfg_quench.scad`
- [x] 6.4 FRACTIONATOR — `mfg_fractionator.scad`
- [x] 6.5 AFTERBURNER — `mfg_afterburner.scad`

## 7. Glass / ceramic

- [x] 7.1 RINSE — `mfg_rinse.scad`
- [x] 7.2 BURNOUT ROTARY — `mfg_burnout_rotary.scad`
- [x] 7.3 MILL — `mfg_mill.scad`
- [x] 7.4 NaOH DIGEST — `mfg_digest.scad`
- [x] 7.5 Product bins — `mfg_totes.scad`

## 8. Gas and electrical

- [x] 8.1 Scrubber train — `mfg_scrubber_train.scad`
- [x] 8.2 BAGHOUSE — `mfg_baghouse.scad`
- [x] 8.3 H2_DRYER — `mfg_h2_dryer.scad`
- [x] 8.4 Electrical yard — `mfg_electrical.scad`
- [x] ZnBr2 IEM frame — `znbr2_iem.scad`
- [x] Pipe racks — `mfg_pipe_rack.scad` + `freecad/pipe_services.py`
- [x] Cable tray / grounding — `mfg_cable_tray.scad` + `pipe_services.py`
- [x] Fan / stack heights — `FAN_STACK.md` (AQS-GAS-003)

## 9. Campus shop (Wave 4 / 5)

- [x] 9.1 FISH TANK — `mfg_fish_tank.scad` + AQS-NZ-002 F1–F4
- [x] 9.2 BIOFILTER — `mfg_biofilter.scad`
- [x] 9.3 GROW BED — `mfg_grow_bed.scad`
- [x] 9.4 FARM SUMP / NUTRIENT DOSE — `mfg_farm_sump.scad`, `mfg_nutrient_dose.scad`
- [x] 9.5 WET BENCH / ETCH RETURN — `mfg_wet_bench.scad`, `mfg_etch_return.scad`
- [x] 9.6 HAB WATER / WASTE — `mfg_hab_water.scad`, `mfg_hab_waste.scad`
- [x] 9.7 COLD BOX — `mfg_cold_box.scad`
- [x] 9.8 Life racks — `mfg_life_rack.scad` + `pipe_services.py` `_life_racks`
- [x] 9.9 Nozzle stubs without STL — `freecad/campus_shop.py`

## Fidelity note

These are shop-level envelopes: plates, flanges, holes, shafts, coils,
jackets. They are not certified fabrication drawings (no weld symbols,
no full BOM balloon, no tolerance stack). Next tightening is per unit
when a fabricator is picked.
