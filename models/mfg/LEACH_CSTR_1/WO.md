# LEACH_CSTR_1 work order

Plan AQS-PLAN-006. Graph Rev BH. Status M2. Study. Not a PE stamp.

W1 Source. `leach_cstr_1.py` (CadQuery) reads `params.json`. Every value not on the graph is in `assumptions` and is labeled.
W2 Envelope. Graph size 2000 × 1200 × 1400 mm at origin 600, 5300, −6000 mm. The model stays inside it. 60 mm on each Y face is reserved for the headers (assumption); the tank body is 2000 × 1080 × 1400 mm. Wall 12 mm and floor 16 mm CPVC, from AQS-NZ-001.
W3 Internals. Graph says none. No agitator is drawn. The 2.0 kW on the node is an AC parasitics share (study) and does not define a mixer. Held.
W4 Nozzles. Graph rule: inlets at the −Y face center, outlets at the +Y face center, Z 700 mm. 25 inlets and 20 process outlets are carried on one DN50 header per face at 70 mm port pitch (assumption). HL-Q3-A/B-HX5 are DN20 from the edge. The other ports have no calculated bore and are DN25 placeholders (assumption). IA-E-LEACH is a conductor and gets a gland boss on +Y, not a hose port.
W5 Fasteners. `fasteners.csv`. 36 M12 PVDF on the lid flange at 150 mm pitch (assumption). No metal fastener in the head space (AQS-STD-002 M4). FKM gasket from AQS-NZ-001.
W6 Materials. CPVC wetted, per AQS-STD-002 Rev F rules M2 and M5: the leach liquor runs at 70–85 °C (GLOSSARY Leach/Salria; HX-5 basis 77.5 °C in AQS-DUTY-008), above the PVC-U limit of 60 °C and inside the CPVC limit of 93 °C [S3]. No metal wetted part. HX-5 is a borosilicate glass 3.3 coil, 4.22 m², two concentric helices on PTFE pads (AQS-DUTY-049; AQS-STD-002 section 3.3) with a dielectric isolating flange on the Q3 side. Liquor high-temperature trip 88 °C (assumption).
W7 Pressure. Atmospheric, vented to NOX_SCRUB and FLUE_KO. design_kPa 25.1 is the old head-plus-10 figure, not a set point. The CPVC wall is not checked against hydrostatic load or creep because liquor density and temperature are held.
W8 Exports. `export/leach_cstr_1.step`; `export/leach_cstr_1.stl`, one closed solid (trimesh watertight, is_volume, one body). Mass, empty: CPVC tank 260 kg at 1510 kg/m³ (Spears) plus glass coil 25 kg (53.7 m of 25 × 3 mm tube at 2230 kg/m³, ISO 3585). The script's mass figure counts the coil envelope as solid CPVC and is not the part mass.
W9 BOM. `bom.csv`.
W10 Fabrication route. Thermoplastic shop: cut CPVC sheet, hot-gas or extrusion weld the seams, solvent-cement the headers and stubs, weld the lid flange, bolt the lid.
W11 Self-copy relevance. Sheet, plastic weld, and bolt work only; no bought internals.
W12 Holds. Port bores; agitator; wall check against liquor density; CPVC wall strength and creep at 85 °C; lid gasket elastomer.
