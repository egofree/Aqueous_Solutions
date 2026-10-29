# Study close: the skipped nodes

Document number: AQS-STUDY-CLOSE-001  
Revision: B  
Date: 2026-10-29  
Authority: the study units list AQS-EQP-STUDY-001. Superseded for loads by the stub activation of the graph nodes (AQS-EQP-STUDY-001 revision G, assumptions A-M-287 to A-M-296) and for placement by `flow_graph/placement_seed.json`. This is a record, not a vendor nameplate or a stamped design.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: machine studies for the nodes skipped in the first placement pass. | 2026-10-02 |
| B | Identity lines, record of revisions and purpose added to the documentation style guide (AQS-DOC-002); arrows written as sentences. The record is otherwise unchanged. | 2026-10-29 |

## Purpose and scope

This page records the machine studies made on 2026-10-02 for the units that the first placement pass skipped: the blow molder, the electrode coating booth, the organic Rankine cycle, the glass aisle machines, the lithography stub, the solar-cell line, the vapour-compression still and the remineralisation. It gives the reasoning that bounded each unit's duty and refused the industrial-size alternatives. The duties and positions here are those of that date. The current loads are on the graph nodes, set by the stub activation of AQS-EQP-STUDY-001 revision G; the lithography stub has since been replaced by the units LITHO_COAT, LITHO_ALIGN and LITHO_DEV, and the current positions are in `flow_graph/placement_seed.json`.

## Machines

### ST-BLOW-01 — BLOW_MOLD
Polymer line add-on, Precious Plastic class. Clamp plus air. Study duty 0.5 kW average, 2–4 kW while running. A 14–28 kW industrial extrusion blow molder is out of the M1 power budget.
Placement: L0, 20000, 400. Scrap and trim go to the oil line. Not into leach. Not FR-4.

### ST-ELC-01 — ELECTRODE_COAT
M1 coat is carbon or nickel, or a passivation. RuO2–IrO2 DSA stays deferred.
Booth exhaust 0.2–0.75 kW plus cure oven 0.5–2 kW, about 2 h/day, so ~0.3 kW average.
Exhaust goes to MET_AHU and on to MET_SCRUB (S71 and S72). Placement: L0, 15600, 200, downstream of the scrubber skid.

### ST-ORC-01 — GEO_ORC
Organic Rankine on surplus geothermal heat after Q4.
\(P \approx \eta (Q_{GHEX} - Q_4)\) with \(\eta\) 0.08–0.12. If Q4 takes the heat, \(P = 0\). Illustrative only: a surplus of 0 to 20 kW of heat gives 0 to 2 kW of electricity. A 100 kW ORC is refused.
Pad reserved at L0, −3500, 3600. Do not buy the skid until a GHEX survey shows surplus.

### Glass intra-aisle
Order after the vibratory split, on the L-1 glass block:

1. GLASS_RINSE at 2000, 12200. Liquor back to CSTR 1.
2. GLASS_MILL at 3400, 12200. Fines to GLASS_DIGEST. Mill length class 800 mm.
3. GLASS_BURNOUT at 4400, 12200. Organics off the cullet. Off-gas to the oil-vapor header, not the acid header.

GLASS_DIGEST already exists. These three are the missing upstream machines, not a second digest.

### ST-LITHO-01 — LITHO_STUB
Pilot 1–5 starts/day, 150 mm. Coat, align, develop.
Dispense ~2 mL/wafer, ~10% solids gives 0.2–1.0 g/day of dry residual at that start rate. Spin plus softbake plus UV is 0.1 kW average, 0.5–1.5 kW while running.
Placement: L0, 18000, 15000, tool row. Solvent lives in WS_SOLV, not on this bench. UV lamp class is not selected.

### ST-SOLAR-01 — SOLAR_PV_CELL
The train is texture, emitter, PSG etch, anti-reflection coating, contact print, firing and IV test, in that order.
Study share 1.0 kW average. PECVD and belt each 0.5–2 kW average, 5–15 kW peak. A full 80–150 kW cell line is refused for M1.
Texture uses WS_KOH. This is not PV_ARRAY. Placement: L0, 18800, 8200, east fab.

### ST-VCD-01 — VCD_TRAIN
Mechanical vapor compression, not RO.
\(w = \lambda \Delta T / T\). At 340 K and 8 K lift, \(\lambda \approx 2400\,\mathrm{kJ/kg}\):

\[
w = 2400 \times 8 / 340 = 56.5\,\mathrm{kJ/kg} = 15.7\,\mathrm{kWh/m^3}
\]

Inside the issued 14–20 kWh/m³ band. Feed 0.11 m³/d at 16 kWh/m³ is 1.76 kWh/d, 0.073 kW average. Matches the 0.08 kW study mid.
Placement: L-1, 15000, 2000, upstream of remineralization. Compressor model is not selected.

### ST-REMIN-01 — REMIN
Drink make-up 10 L/d. Targets 25 mg/L Ca, 10 mg/L Mg.

\[
10\,\mathrm{L/d} \times 25\,\mathrm{mg/L} = 0.25\,\mathrm{g\,Ca/d}
\]
\[
10\,\mathrm{L/d} \times 10\,\mathrm{mg/L} = 0.10\,\mathrm{g\,Mg/d}
\]

Source is the hydroxide crib, dissolved, not a second leach. UV after dose. Placement: L1, 2800, 200, after grey treat. Blocks any potable-export claim until the mineral source and UV are locked.

## Named pipes, not other units

C29_RECYCLE is the pipe from the PROD_C29 cut tank to the induction pyrolyzer inlet. It is not the wet line. NCG does not ride it.

CONTINUOUS_RECYCLE is the continuous-line liquor return to LEACH CSTR 1. It is not the heat ladder. The ladder keeps the names Q1_A through Q4_B.

### BOUNDARY_EXPORT
North dock door. Freight only. No process stream ID. Goods: metals crib, wafers, food. Not a vessel.

### LOAD_AGG
Sum of S17/S20 at the rectifier. Accounting node. Placed at the rectifier row so the drawing has a tag. Not a process vessel.

### Q4_BUS
Water header, under 80 °C, collecting S06, S44, S53, S54, S63, S80. Not a flue. Spine along the MFG south wall.

## Still external

Compressor selection for VCD. UV lamp class for litho. GHEX survey before any ORC purchase. Booth recipe for the carbon/nickel coat. Wafer starts/day still a pilot band, not a campaign lock.
