# SI_REDUCE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 6.749 kg/d. Mass out 6.749 kg/d. Electrical duty 0.7955 kW. In: CHAR_TO_SI 1.231 kg/d (pyrolysis char reductant); IA-QUARTZ-MU 3.878 kg/d (quartz ore for the silicon furnace (raw ore)); IA-SI-HOOD-O2 1.64 kg/d (oxygen of the hood air that burns the furnace carbon monoxide). Out: IA-SI-CO2 4.511 kg/d (carbon dioxide of the burned furnace gas); IA-SI-FUME 0.7698 kg/d (silica fume from the furnace baghouse); IA-SI-MG 1.469 kg/d (metallurgical-grade silicon).

2. Size.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. Graphite hot-face carbothermic-reduction furnace with alumina brick backup and a mild-steel casing; dry char and silica-class feed handling; the hot face stays dry (M7). Basis: GLASS-sector arc furnace reducing quartz ore with char (IA-QUARTZ-MU, CHAR_TO_SI, sized by flow_graph/param/si_refine.py, A-M-419): the construction material is issued at the lining level (SCHACHT2004 ch. 8 carbonaceous hot faces; CRC_SI is the element benchmark for the reduction duty class); the CO burns in the hood and the silica fume goes to the baghouse. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Silicon-carbide hot face when batch chemistry reaches beyond the graphite class (a process-change decision, not a materials trade). no wetted stream on the graph; the selection is the construction class only. (X-MAT-22)

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Edges CHAR_TO_SI carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them.
