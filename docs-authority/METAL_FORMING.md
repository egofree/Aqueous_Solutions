# Metal forming: wire drawing, cold rolling and gas atomising

Document number: AQS-MFG-MET-001  
Revision: D  
Date: 2026-10-29  
Equipment: AQS-EQP-MFG-MET-001 (`docs-authority/METAL_FORMING_EQUIPMENT.md`)  
Authority: the plant flow graph `flow_graph/plant_flow_graph.json`; the tool list AQS-MFG-010; the stream register AQS-STR-001; the hazard separation register AQS-HSE-001; the vent and scrubber list AQS-EQP-VENT-001.  
Licence: CERN-OHL-S-2.0.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: wire drawing, cold mill and atomiser path with its air handling and heat recovery. | 2026-09-28 |
| B | Metal-aisle scrubber and its streams added; no free discharge to outdoors. | 2026-09-28 |
| C | Rewritten against the plant graph and the documentation style guide (AQS-DOC-002). Bulk melting now belongs to the foundry, and the shop melt furnace takes only electrowon sheet and atomiser remelt. Tags that are no longer on the graph (product bins, powder crib, nitrogen blanket, electrode blank station) and references to documents outside the repository were removed. Nitrogen as atomising gas replaced by the argon of the tool list. Rates and loads are no longer stated here; they are in the generated equipment list. | 2026-10-29 |
| D | The atomiser argon is held in a receiver between heats, and the tool design (die schedule, mill gauge and width, atomiser batch) is now derived from the graph throughputs (A-M-416); Section 3.4 points to it. | 2026-10-29 |

## Purpose and scope

The plant turns part of the metal it recovers into wire, sheet and powder for its own use: cable and fasteners, panels and electrode blanks, and powder for sintering and printing. This page describes that process: the route of the metal, the choices that fix it, the air handling and heat recovery, and the hazards. It covers the units MET_MELT, WIRE_DRAW, COLD_MILL, GAS_ATOMIZER, MET_AHU, MET_SCRUB and MET_HX_Q4.

The rates, loads, tool nameplates and mass balances are in the generated equipment list AQS-EQP-MFG-MET-001, and the tools are designed in AQS-MFG-010. This page gives no values of its own, so it does not go out of date when the graph changes. Bulk melting and casting belong to the foundry and are not covered here.

## 1. Terms

- Cold rolling: reducing the thickness of metal strip between rolls at room temperature.
- Wire drawing: pulling rod through a series of dies to reduce its diameter.
- Gas atomising: breaking a stream of molten metal into droplets with a jet of gas, which freeze into powder.
- Remelt: metal returned to the melt furnace, here the atomiser fines and oversize.
- Q4 header: the low-grade warm-water loop that heats the habitation air.

## 2. Route of the metal

The shop melt furnace MET_MELT takes electrowon sheet from the last electrowinning cell (stream IA-EW-SHEET) and the remelt from the atomiser (IA-ATOM-REMELT). It sends melt to three tools:

- the wire drawer WIRE_DRAW, on stream S57, which makes wire (S58);
- the cold mill COLD_MILL, on IA-MELT-MILL, which makes sheet and strip (S59);
- the gas atomiser GAS_ATOMIZER, on IA-MELT-ATOM, which makes powder (S60).

The wire, sheet and powder go to the shop MFG_SHOP. Swarf and trim from the shop go to the hopper on stream S61 and to the leach on S16. The fume from wire drawing goes to the scrubber (IA-DRAW-FUME), and the fines lost in drawing go to the baghouse (IA-WIRE-LOSS).

The graph also keeps routes from the foundry that carry no flow at present: stock to the wire drawer (STOCK_TO_WIRE_DRAW), foundry melt to the atomiser (IND_TO_ATOM) and atomiser powder to stock (ATOM_TO_STOCK). The equipment list names the routes without flow on each regeneration.

## 3. Choices that fix the process

### 3.1 Electric induction melting

MET_MELT is a coreless induction furnace. Fuel firing is not used: it would need a fuel header and a flue for a small batch melt, and the induction furnace runs from the plant bus. The furnace takes only metal. No polymer, oil or printed circuit board enters it; organics go to the oil-line pyrolyser OIL_PYRO, which is a different unit with a different chemistry.

### 3.2 Bulk melting in the foundry

The foundry melts and casts the bulk of the metal in IND_MELT and the casting units. MET_MELT is kept for the small shop melt that feeds the forming tools, and it is not sized as the main melt.

### 3.3 Argon for atomising

The atomiser is a close-coupled design with the argon recirculated, as AQS-MFG-010 sizes it. The argon for a pour is held in a receiver charged above the nozzle supply pressure, and the compressor recovers and recharges it over the hours until the next heat. Argon is inert to the reactive metals that nitrogen would nitride. Shop air is never the atomising gas.

### 3.4 Tool design from the throughputs

The wire drawer, the cold mill and the atomiser are set from the throughputs on the graph rather than from fixed figures (A-M-416). The die series of the wire drawer runs from the copper rod down to the finest strand of the wire families, and each family leaves the line at the die that reaches its strand. The cold mill rolls a cast slab at constant width, so the slab mass sets the width of the strip and the strain sets its final gauge. The atomiser pours each heat through a nozzle whose flow sets the pour time and the argon drawn from the receiver. The resulting schedules are in Section 7 of the equipment list AQS-EQP-MFG-MET-001.

## 4. Air handling and heat recovery

The metal aisle has its own air handler, MET_AHU. It sends the aisle air to the scrubber MET_SCRUB (streams S62 and S71), which washes out fume and oil mist and returns the cleaned air to the air handler (IA-MET-AIR-RET). The scrubber liquor goes to the leach (S72) and the oil it collects to the oil line (S72B). The aisle air never shares a return with the habitation or the farm, and it is not discharged to outdoors without treatment.

Warm water from the foundry induction melt and the vacuum induction furnace is recovered in MET_HX_Q4 and sent to the Q4 header as heat (S63). Only water crosses to the Q4 header; no flue or melt gas does.

## 5. Hazards

1. Induction melting can cause burns and metal splash, and the coil carries a strong field. The coil supply is locked out before work on the furnace (29 CFR 1910.147 and 1910.333).
2. The wire drawer and the cold mill can trap and crush, and they are loud. They are guarded (29 CFR 1910.212), and hearing protection is used where the noise requires it (29 CFR 1910.95).
3. The atomiser holds gas under pressure and sprays hot metal. Its area is kept clear while it runs. Powder of reactive metals such as aluminium and titanium can burn or explode, so it is held under inert gas, the equipment is grounded, and open ignition sources are kept out.
4. Metal dust and fume are captured by the aisle air handler and the scrubber, not by the habitation air system.
5. Where inert gas is held in an enclosed volume, the oxygen level is monitored.

## 6. Related pages

- AQS-EQP-MFG-MET-001, the generated equipment list for these units, with streams, rates, balances and separation checks.
- AQS-EQP-MFG-001, the shop equipment list.
- AQS-MFG-010, the tool list that sizes the four metal tools.
- The process flow diagram is part of the plant view `flow_graph/views/pfd.svg`, drawn from the graph by the regenerator.
