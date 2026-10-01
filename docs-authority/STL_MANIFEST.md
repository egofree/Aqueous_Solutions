# STL rebuild manifest

Document number: AQS-STL-001  
Revision: A  
Date: 2026-09-27

OpenSCAD: user-local AppImage on PATH (`/home/user/bin/openscad`). FreeCAD: `/usr/bin/freecadcmd`.

## Command

```
cd cad/detail && bash build_stls.sh
cd ../freecad && /usr/bin/freecadcmd build_plant.py
```

`import_mfg.py` skips a missing STL. `stamp_materials.py` runs from
`build_plant.py` against `cad/materials.csv`.

## Expected outputs (`cad/detail/stl/`)

Every `cad/detail/*.scad` compiles to a same-name `.stl`.

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

Existing compiled twins (older, still valid check files):

- `cad/export/leach_cstr.stl`
- `cad/export/ew_cell.stl`
- `cad/export/assembly_wet.stl`

## Operator PATH note (2026-10-01 Wave 3)

`openscad` **available** on Mike's machine via user-local AppImage (no
apt/sudo):

- Binary: `/home/user/bin/OpenSCAD.AppImage` (OpenSCAD 2021.01)
- Symlink: `/home/user/bin/openscad` → AppImage
- apt install of distro package was **blocked** (sudo interactive auth)

Compile:

```
export PATH="/home/user/bin:$PATH"
cd cad/detail && bash build_stls.sh
```

System package install remains optional; do not force `sudo apt`.
