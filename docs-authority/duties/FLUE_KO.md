# FLUE_KO

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 277.7 kg/d. Mass out 277.7 kg/d. Electrical duty 0.0000 kW. In: S67 117.4 kg/d (flue N2/O2/CO2/NOx); S70 0.0521 kg/d (condensables); IA-LEACH-FLUE 135.9 kg/d (leach vent); IA-FLUE-QUENCH 24.31 kg/d (flue quench water). Out: S67B 14.05 kg/d (CO2-rich gas after KO); IA-FLUE-EXH 263.6 kg/d (flue to the NOx scrubber).

2. Size.
- In 253.4 kg/d, out 253.4 kg/d. No holdup claimed.

3. Material. FRP vinyl ester with C-veil liner, PVDF mesh pad, borosilicate glass 3.3 inlet spool (AQS-STD-002 section 4.3). No metal wetted part. S67 at 300 °C is spray-quenched in the glass inlet spool by IA-FLUE-QUENCH, 24.31 kg/d tower water from ROOF_TANK (X-SAF-07): 30 439 kJ/d removed cooling to 60 °C evaporates 12.15 kg/d; spray is 2.0 times evaporation (assumption) so the spool stays wetted. Gas leaves the spool at about 60 °C, below the FRP vinyl ester limit. Loss of quench water trips the afterburner flue damper (held for X-CTL).

4. Nozzles. Origin 18800, 7200, -6000 mm. Size 600 × 700 × 1100 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-LEACH-FLUE, inlet, -Y face center, 19100, 7200, -5450 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S67, inlet, -Y face center, 19100, 7200, -5450 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, S70, inlet, -Y face center, 19100, 7200, -5450 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-FLUE-EXH, outlet, +Y face center, 19100, 7900, -5450 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, IA-FLUE-QUENCH, inlet, glass inlet spool spray nozzle. Rating hose, atmospheric.
- N5, S67B, outlet, +Y face center, 19100, 7900, -5450 mm. Height 550 mm from the bottom. DN15 from the edge. Rating hose, atmospheric.
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/FLUE_KO.stl` is the box, not the internal. FreeCAD is not in this session.

8. Open items. No holdup basis for this class.
