# LEACH_CSTR_1 work order

Plan AQS-PLAN-006. Graph Rev BH. Status M2. Study. Not a PE stamp.

W1 Source. `leach_cstr_1.py` (CadQuery) reads `params.json`. Every value not on the graph is in `assumptions` and is labeled.
W2 Envelope. Graph size 2000 × 1200 × 1400 mm at origin 600, 5300, −6000 mm. The model stays inside it. 60 mm on each Y face is reserved for the headers (assumption); the tank body is 2000 × 1080 × 1400 mm.
W3 Internals. Graph says none. No agitator is drawn. The 2.0 kW on the node is an AC parasitics share (study) and does not define a mixer. Held.
W4 Nozzles. Graph rule: inlets at the −Y face center, outlets at the +Y face center, Z 700 mm. 25 inlets and 20 process outlets are carried on one DN50 header per face at 70 mm port pitch (assumption). HL-Q3-A/B-HX5 are DN20 from the edge. The other ports have no calculated bore and are DN25 placeholders (assumption). IA-E-LEACH is a conductor and gets a gland boss on +Y, not a hose port.
W5 Fasteners. `fasteners.csv`. 36 M10 A4-70 on the lid flange at 150 mm pitch (assumption).
W6 Materials. 316L wetted, from duty section 3 (wet or chloride service). No feed-specific choice. The selection is held, not verified, across the AQS-ASSAY-001 Rev C envelope: pit rate is not measured and halide/fluoride loads at the bounding cases are not set. `docs-authority/CSTR_NOZZLE_SCHEDULE.md` names CPVC; that conflict is open.
W7 Pressure. Atmospheric, vented to NOX_SCRUB and FLUE_KO. design_kPa 25.1 is the old head-plus-10 figure, not a set point. Wall 6 mm and floor 8 mm are not checked against hydrostatic load because liquor density is held.
W8 Exports. `export/leach_cstr_1.step`; `export/leach_cstr_1.stl`, one closed solid (trimesh watertight, is_volume, one body). Mass 740 kg at 8000 kg/m³, steel only, empty.
W9 BOM. `bom.csv`.
W10 Fabrication route. Shop weld from 316L sheet: cut, brake, seam weld, header and stubs set-on welded, lid flange welded, lid bolted.
W11 Self-copy relevance. Sheet, weld and bolt work only; no bought internals.
W12 Holds. Port bores; agitator; wall check against liquor density; material confirmation across the assay envelope; CPVC conflict; lid gasket elastomer.
