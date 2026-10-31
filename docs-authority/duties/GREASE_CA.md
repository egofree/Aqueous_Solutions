# GREASE_CA

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.2000 kW. In: none. Out: none.

2. Size.
- Envelope 500×400×600 mm, 0.12 m³.
- Envelope basis (graph node): the 0.2 kg/d batch kettle: heated soap-precipitation class.
- Sizing study pending (study): batch_kgd 0.2.
- Graph design (AQS-PAR-001 sizing): duty calcium grease kettle: the C19-C28 wax base + the P_CA thickener -> the general lubrication grease; batch_kgd 0.2; heat_class soap precipitation, jacket heated.

3. Material. 316L jacketed soap kettle + 316L agitator; steel frame and insulation stays dry; steam - hot-water heads keep the jacket wetted side on the issued Q3/Q4 M1 water family. Basis: calcium soap saponification at the 95-120 C kettle class, wax cut + Ca(OH)2 (graph edges/duty AQS-DUTY-GREASE 0.1 kg/d Ca(OH)2): grease manufacture practice selects 304/316L hot-soap contact (MANG2007 ch. 14.6); the alkaline soap concentrate is hot and basic, out of the PP-H class. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 304L kettle if the wax cut proves the only wetted face at a lower saponification temperature (cost down, first-article choice). allowance: corrosion is not the limit - cleaning and soap residue set the maintenance surface; no measured pit rate. (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/GREASE_CA.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops GREASE_CALT-01, GREASE_CAPT-01, GREASE_CATE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Edges WAX_TO_GREASE_CA, PCA_TO_GREASE, GREASE_CA_TO_MFG carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them. Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
