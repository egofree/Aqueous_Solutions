# CRYO_ASU

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 238.2 kg/d. Mass out 238.2 kg/d. Electrical duty 1.7455 kW. In: IA-AIR-IN 0 kg/d (intake air); IA-NOX-CO2 22.78 kg/d (scrubbed CO2 to the cold box); IA-NOX-N2 215.4 kg/d (scrubbed flue nitrogen to the cold box); IA-H2-AIR 0 kg/d (sweep air from the hydrogen hood); 4 more. Out: IA-ASU-N2 213.6 kg/d (nitrogen product); IA-ASU-O2 1.832 kg/d (oxygen product); IA-ASU-CO2 22.78 kg/d (CO2 product).

2. Size.
- Column diameter 150 mm. 20 trays × 0.3 m = 6.0 m. The column is a pipe beside the 600×600×800 mm base. Not a packed scrubber.

3. Material. 316L. Condensation. No carbon steel. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Feed DN25 at the column base. Product nozzles DN15. No flange class. The column is not a transport vessel. The vent returns to the column feed, not the room.

5. Instruments. Pressure and temperature. High pressure trips the feed.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is `cad/stl/CRYO_ASU.stl`, from `models/mfg/CRYO_ASU/cryo_asu.py` (AQS-PLAN-006). Drawings at `models/mfg/CRYO_ASU/drawings/`. The build leaves the study registry box on x and y; the misfit is reported on the tracker board and nothing is resized.

8. Open items. Tray efficiency is not measured.
9. Balance (AQS-PAR-003 Rev C). IA-ASU-O2 31.087 kg/d; IA-LEACH-ASU 0.796 kg/d under the Henry bound (T5, T6).
