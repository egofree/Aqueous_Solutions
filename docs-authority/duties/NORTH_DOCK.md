# NORTH_DOCK

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 84.88 kg/d. Mass out 84.88 kg/d. Electrical duty 0.0000 kW. In: IA-N2-VENT 0 kg/d (nitrogen vent); IA-NA-PURGE 5.106 kg/d (sodium salt purge equal to the make-up mass); IA-O2-SHIP 43.43 kg/d (O2 cylinders shipped at the dock); IA-MEOH-SHIP 25.24 kg/d (methanol shipped at the dock); 3 more. Out: DOCK_EXPORT_TBD 0 kg/d (returned freight); IA-AIR-IN 0 kg/d (intake air); IA-NAOH-MU 5.106 kg/d (purchased NaOH flake make-up); IA-H2O-MU 79.77 kg/d (water make-up for H and O leaving as product).

2. Size.
- No mass throughput. No volume is invented.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. No process nozzle.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/NORTH_DOCK.stl`.

8. Open items. None.

9. Revision (NaOH balance, owner decision 2026-10-15). Receives purchased NaOH flake and issues it on IA-NAOH-MU to EVAP_BASE; receives the equal-mass sodium salt purge IA-NA-PURGE from LEACH_CSTR_1 for export.
