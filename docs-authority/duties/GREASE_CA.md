# GREASE_CA

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.002659 kg/d. Mass out 0.002659 kg/d. Electrical duty 0.0001 kW. In: WAX_TO_GREASE_CA 0.002489 kg/d (wax cut); PCA_TO_GREASE 3.5e-05 kg/d (calcium hydroxide); IA-GREASE-AIR 0.000135 kg/d (oxygen of the process air for the wax oxidation). Out: GREASE_CA_TO_MFG 0.002392 kg/d (Ca grease); IA-GREASE-VENT 0.000267 kg/d (water, carbon dioxide and light acids of the wax oxidation and saponification).

2. Size.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. 316L jacketed soap kettle + 316L agitator; steel frame and insulation stays dry; steam - hot-water heads keep the jacket wetted side on the issued Q3/Q4 M1 water family. Basis: calcium soap saponification of the air-oxidised wax cut with Ca(OH)2 slaked from the acid-plant residue lime, in an electrically heated campaign kettle (rates and kettle sized in flow_graph/param/grease.py, A-M-429): grease manufacture practice selects 304/316L hot-soap contact (MANG2007 ch. 14.6); the alkaline soap concentrate is hot and basic, out of the PP-H class. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 304L kettle if the wax cut proves the only wetted face at a lower saponification temperature (cost down, first-article choice). allowance: corrosion is not the limit - cleaning and soap residue set the maintenance surface; no measured pit rate. (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/GREASE_CA.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Edges WAX_TO_GREASE_CA, PCA_TO_GREASE, GREASE_CA_TO_MFG carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them. Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
