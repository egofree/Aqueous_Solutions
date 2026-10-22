# GREASE_LI

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. 316L jacketed soap kettle + 316L agitator (same kettle class as GREASE_CA) for the lithium soap. Basis: lithium 12-hydroxystearate soap saponification, wax cut + Li source from LI_RECOVER (graph edges): Li soaps are the standard thickeners and their kettles run the same 95-120 C class (MANG2007 ch. 14). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 304L kettle at the same trade-off as GREASE_CA. Li-bearing residues drive the cleaning protocol, not corrosion. (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/GREASE_LI.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Edges WAX_TO_GREASE_LI, LI_TO_GREASE, GREASE_LI_TO_MFG carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them. Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
