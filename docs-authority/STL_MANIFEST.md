# STL rebuild manifest

Document number: AQS-STL-001  
Revision: A  
Date: 2026-09-27

OpenSCAD: any `openscad` on PATH (AppImage or distro package). FreeCAD: `/usr/bin/freecadcmd` (1.0).

## Command

```
# This repo:
cd models/openscad/detail && bash build_stls.sh   # when script present
cd ../../freecad && /usr/bin/freecadcmd build_plant.py

# Local working-directory layout (not published): models/openscad/detail + models/freecad
```

`import_mfg.py` skips a missing STL. `stamp_materials.py` runs from
`build_plant.py` against `tables/materials.csv`.

## Expected outputs (`models/export/detail/` or `models/openscad/detail/stl/`)

Every detail `*.scad` compiles to a same-name `.stl`.

Shop files that must exist before the plant tree is considered rebuilt:

- mfg_hopper.stl
- mfg_shredder.stl
- mfg_vibratory_conveyor.stl
- mfg_lid_coaming.stl
- mfg_leach_cstr.stl
- cstr3_flight.stl
- mfg_dewater.stl
- mfg_vibratory_split.stl
- mfg_ew_fitout.stl
- mfg_ew_bund.stl
- cem_cassette.stl
- funnel_valve.stl
- mfg_harvest_vdf.stl
- mfg_precip.stl
- mfg_totes.stl
- mfg_melt.stl
- mfg_bmed_stack.stl
- bmed_cell.stl
- mfg_cru.stl
- mfg_dryer.stl
- mfg_induction_pyrolyzer.stl
- induction_coil.stl
- mfg_quench.stl
- mfg_fractionator.stl
- mfg_afterburner.stl
- mfg_rinse.stl
- mfg_burnout_rotary.stl
- mfg_mill.stl
- mfg_digest.stl
- mfg_scrubber_train.stl
- mfg_baghouse.stl
- mfg_h2_dryer.stl
- mfg_electrical.stl
- znbr2_iem.stl
- mfg_znbr2_skid.stl
- mfg_q4_hvac.stl
- mfg_gas_handling.stl
- mfg_pipe_rack.stl
- mfg_cable_tray.stl
- mfg_fish_tank.stl
- mfg_biofilter.stl
- mfg_grow_bed.stl
- mfg_farm_sump.stl
- mfg_nutrient_dose.stl
- mfg_wet_bench.stl
- mfg_etch_return.stl
- mfg_hab_water.stl
- mfg_hab_waste.stl
- mfg_cold_box.stl
- mfg_life_rack.stl

Pipe racks, trays, and campus envelopes also exist as Part features from
`pipe_services.py` and `campus.py` even if those two STLs are absent.

Existing compiled twins (older, still valid check files under
`models/export/`):

- `leach_cstr.stl`
- `ew_cell.stl`
- `assembly_wet.stl`

## Operator PATH note

When OpenSCAD is available on the **build host** (AppImage or package on
`PATH`), compile STLs before the FreeCAD plant import:

```
cd models/openscad/detail   # or models/openscad/detail/ in the local layout
bash build_stls.sh
```

System package install remains optional; do not force `sudo apt` from an
unattended agent. Record the binary you used in your local build log — do
not commit workstation-absolute paths into this tree.
