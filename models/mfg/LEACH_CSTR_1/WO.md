# LEACH_CSTR_1 work order

Plan AQS-PLAN-006. Graph Rev BH. Status M2. Study. Not a PE stamp.

W1 Source. `leach_cstr_1.py` (CadQuery) reads `params.json`. Every value not on the graph is in `assumptions` and is labeled.
W2 Envelope. Graph size 2000 × 1200 × 1400 mm at origin 600, 5300, −6000 mm. The model stays inside it except the agitator drive (W3). 60 mm on each Y face is reserved for the headers (assumption); three FRP belts 56 mm deep sit inside that zone on the Y faces and on the X ends. Tank body 1888 × 1080 × 1400 mm. Wall 16 mm, floor 16 mm CPVC (AQS-DUTY-050).
W3 Internals. Agitator per AQS-DUTY-050 (study): 4-blade 45° pitched-blade turbine, D 450 mm, 150 rpm, 403 W shaft, 0.75 kW gearmotor; PVDF-sheathed shaft through a lid seal, solid PVDF impeller at Z 250 inside the coil. The drive sits on a lid bridge about 400 mm above the envelope and is not modeled. HX-5 glass coil envelope on four pads.
W4 Nozzles. Graph rule: inlets at the −Y face center, outlets at the +Y face center, Z 700 mm. 25 inlets and 20 process outlets are carried on one DN50 header per face at 70 mm port pitch (assumption). HL-Q3-A/B-HX5 are DN20 from the edge. The other ports have no calculated bore and are DN25 placeholders (assumption). IA-E-LEACH is a conductor and gets a gland boss on +Y, not a hose port.
W5 Fasteners. `fasteners.csv`. 36 M12 PVDF on the lid flange at 150 mm pitch (assumption). No metal fastener in the head space (AQS-STD-002 M4). FKM gasket from AQS-NZ-001.
W6 Materials. CPVC wetted, per AQS-STD-002 Rev F rules M2 and M5: the leach liquor runs at 70–85 °C (GLOSSARY Leach/Salria; HX-5 basis 77.5 °C in AQS-DUTY-008), above the PVC-U limit of 60 °C and inside the CPVC limit of 93 °C [S3]. No metal wetted part. HX-5 is a borosilicate glass 3.3 coil, 4.22 m², two concentric helices on PTFE pads (AQS-DUTY-049; AQS-STD-002 section 3.3) with a dielectric isolating flange on the Q3 side. Liquor high-temperature trip 88 °C (assumption).
W7 Pressure. Atmospheric, vented to NOX_SCRUB and FLUE_KO. Hydrostatic 11.9 kPa at the floor at 1100 mm working level and 1100 kg/m³ (study). Wall panels between belts 1.37 MPa maximum against 3.03 MPa CPVC allowable at 85 °C; belts 17.1 MPa against 50 MPa FRP, deflection L/490 (AQS-DUTY-050). design_kPa 25.1 is the old head-plus-10 figure, not a set point.
W8 Exports. `export/leach_cstr_1.step`; `export/leach_cstr_1.stl`, one closed solid (trimesh watertight, is_volume, one body). Mass, empty, by part from the script: CPVC tank 297.6 kg (1510 kg/m³, Spears), FRP belts 66.5 kg (1900 kg/m³, assumption), glass coil 24.8 kg from the tube (not the envelope; 2230 kg/m³, ISO 3585), PTFE pads 2.5 kg, PVDF agitator 9.6 kg; total 401 kg. Operating, add 2354 kg liquor.
W9 BOM. `bom.csv`.
W10 Fabrication route. Thermoplastic shop: cut CPVC sheet, hot-gas or extrusion weld the seams, solvent-cement the headers and stubs, weld the lid flange, bolt the lid.
W11 Self-copy relevance. Sheet, plastic weld, and bolt work only; no bought internals.
W12 Holds. Port bores; lid gasket elastomer; in-house just-suspended speed test (Zwietering) on the agitator; drive bridge and seal; FRP channel coupon tests (X-MAT-21).
