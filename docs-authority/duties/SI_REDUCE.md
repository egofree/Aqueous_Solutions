# SI_REDUCE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 5.0000 kW. In: none. Out: none.

2. Size.
- Envelope 1200×1000×1600 mm, 1.92 m³.
- Envelope basis (graph node): graphite hot-face furnace (the issued sec3 selection) at the batch class.
- Sizing study pending (study): si_kgd 1.8.
- Graph design (AQS-PAR-001 sizing): duty carbothermic silicon reduction for the PV cell line (SOLAR_PV_CELL draws 1.8 kg/d Si); si_kgd 1.8; sio2_kgd 3.85; char_kgd 1.924.

3. Material. Graphite hot-face carbothermic-reduction furnace with alumina brick backup and a mild-steel casing; dry char and silica-class feed handling; the hot face stays dry (M7). Basis: GLASS-sector furnace unit with solids-only edges (CHAR_TO_SI on the graph design day at zero): the construction material is issued here at the lining level (SCHACHT2004 ch. 8 carbonaceous hot faces; CRC_SI is the element benchmark for the reduction duty class); process duty and its rates stay a unit task 02 pending item. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Silicon-carbide hot face when batch chemistry reaches beyond the graphite class (a process-change decision, not a materials trade). no wetted stream on the graph; the selection is the construction class only. (X-MAT-22)

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. Loops SI_REDUCETE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Edges CHAR_TO_SI carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them.
