# NORTH_DOCK

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 122.2 kg/d. Mass out 122.2 kg/d. Electrical duty 0.0000 kW. In: IA-N2-VENT 3.1 kg/d (nitrogen vent); IA-NA-PURGE 4.394 kg/d (sodium salt purge equal to the make-up mass); IA-C5-SHIP 7.131 kg/d (C5-C10 product shipped); IA-C11-SHIP 1.512 kg/d (C11-C18 surplus shipped); 12 more. Out: IA-H2O-MU 64.41 kg/d (water make-up for H and O leaving as product); IA-NAOH-MU 4.394 kg/d (purchased NaOH flake make-up); IA-AIR-IN 0 kg/d (intake air); IA-SOLV-MU 0.21 kg/d (solvent resupply (ethanol and acetone)); 13 more.

2. Size.
- No mass throughput. No volume is invented.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. No process nozzle.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/NORTH_DOCK.stl`.

8. Open items. None.

9. Revision (NaOH balance, owner decision 2026-10-15). Receives purchased NaOH flake and issues it on IA-NAOH-MU to EVAP_BASE; receives the equal-mass sodium salt purge IA-NA-PURGE from LEACH_CSTR_1 for export.
