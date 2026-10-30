# P_CA

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 4.8e-05 kg/d. Mass out 4.7e-05 kg/d. Electrical duty 0.0000 kW. In: IA-LIME-TO-PCA 3.9e-05 kg/d (cake-kiln lime residue to the slaker); IA-PCA-H2O 9e-06 kg/d (well water to slake the lime). Out: PCA_TO_GREASE 3.5e-05 kg/d (calcium hydroxide); IA-PCA-REJECT 1.2e-05 kg/d (slaker grit (anhydrite, fluorspar and inerts of the kiln residue)).

2. Size.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. PP-H precipitation vessel + PP agitator; PE slurry lines; steel frame and housing outside the wetted headspace. Basis: Ca(OH)2 slurry precipitation feeding the grease kettle: pH ~12.4 class liquor at ambient (the CA_POT duty line: the 0.055 kg/d Ca metal produces the slurry): PP-H is the house non-metal for the alkaline class (AQS-STD-002 M2/M5 spirit + P4 family; the Ca(OH)2 saturation behaviour per the duty basis). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 316L vessel + PP agitator as a mixed-build alternative if hot-work temperatures reach the PP limit. scale is knocked down mechanically at clean-out: a mechanical design note, not a material allowance. (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/P_CA.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Edges PCA_TO_GREASE carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them. Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
