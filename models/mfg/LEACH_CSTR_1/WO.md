# LEACH_CSTR_1 work order

Plan AQS-PLAN-006. Graph Rev BH. Status M2. Study. Not a PE stamp.

W1 Source. `leach_cstr_1.py` (CadQuery) reads `params.json`. Every value not on the graph is in `assumptions` and is labeled.
W2 Envelope. Graph size 2000 × 1200 × 1400 mm at origin 600, 5300, −6000 mm. The model stays inside it. 60 mm on each Y face is reserved for the headers (assumption); the tank body is 2000 × 1080 × 1400 mm. Wall 12 mm and floor 16 mm PVC-U, from AQS-NZ-001.
W3 Internals. Graph says none. No agitator is drawn. The 2.0 kW on the node is an AC parasitics share (study) and does not define a mixer. Held.
W4 Nozzles. Graph rule: inlets at the −Y face center, outlets at the +Y face center, Z 700 mm. 25 inlets and 20 process outlets are carried on one DN50 header per face at 70 mm port pitch (assumption). HL-Q3-A/B-HX5 are DN20 from the edge. The other ports have no calculated bore and are DN25 placeholders (assumption). IA-E-LEACH is a conductor and gets a gland boss on +Y, not a hose port.
W5 Fasteners. `fasteners.csv`. 36 M12 PVDF on the lid flange at 150 mm pitch (assumption). No metal fastener in the head space (AQS-STD-002 M4). FKM gasket from AQS-NZ-001.
W6 Materials. PVC-U wetted, per AQS-STD-002 Rev A rules M1 and M2. No metal wetted part. This replaces the earlier 316L and resolves the 316L / CPVC conflict with AQS-NZ-001 in favor of PVC. Liquor temperature is not on the graph. HL-Q3-A/B-HX5 supply Q3 water at 95 °C (graph), above the PVC-U limit of 60 °C and the usual CPVC limit of 93 °C (both assumptions from published data). The HX-5 ports and coil are PVDF (AQS-STD-002 section 3.2), with a dielectric isolating flange where the Q3 metal piping ends. The coil is not modeled; its area is held.
W7 Pressure. Atmospheric, vented to NOX_SCRUB and FLUE_KO. design_kPa 25.1 is the old head-plus-10 figure, not a set point. The PVC wall is not checked against hydrostatic load or creep because liquor density and temperature are held.
W8 Exports. `export/leach_cstr_1.step`; `export/leach_cstr_1.stl`, one closed solid (trimesh watertight, is_volume, one body). Mass 241 kg at 1400 kg/m³ (assumption), PVC only, empty.
W9 BOM. `bom.csv`.
W10 Fabrication route. Thermoplastic shop: cut PVC-U sheet, hot-gas or extrusion weld the seams, solvent-cement the headers and stubs, weld the lid flange, bolt the lid.
W11 Self-copy relevance. Sheet, plastic weld, and bolt work only; no bought internals.
W12 Holds. Port bores; agitator; wall check against liquor density; PVC creep and temperature at the liquor; HX-5 port temperature (95 °C); lid gasket elastomer.
