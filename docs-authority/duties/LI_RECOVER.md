# LI_RECOVER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0500 kW. In: none. Out: none.

2. Size.
- Envelope 200×200×800 mm, 0.032 m³.
- Envelope basis (graph node): the carbonation contactor at the 0.5 kg/d slipstream.
- Sizing study pending (study): slipstream_kgd 0.5.
- Graph design (AQS-PAR-001 sizing): duty carbonate the POLISH_BANK LiOH slipstream -> the lithium thickener (feeds GREASE_LI); slipstream_kgd 0.5.

3. Material. PP-H settling/carbonation vessel + PP agitator; PE slurry lines; 316L frame metal outside the wetted zone. Basis: LiOH/Li2CO3-class polish liquor from POLISH_BANK, held at ambient for the carbonation step (graph edges): matches the issued alkaline P4 PP-H family behaviour at the pH class the LiOH carbonation produces (AQS-STD-002 section 12.1 alk; GREENWOOD basic-oxide chemistry behind the route). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 316L vessel where the liquor pH crosses neutral during the batch cycle. the rate is unsized (unit task 02 pending) - the selection is issued on the construction level; level control over internals. (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/LI_RECOVER.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops LI_RECOVERLSH-01, LI_RECOVERLT-01, LI_RECOVERPT-01, LI_RECOVERTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Edges POLISH_TO_LI, LI_TO_GREASE carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them. Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
