# CONT_CAST

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 31.71 kg/d. Mass out 31.71 kg/d. Electrical duty 0.0000 kW. In: IND_TO_CONT 31.71 kg/d (melt to continuous caster). Out: CONT_TO_ROLL 10 kg/d (continuous billet/slab); CONT_TO_STOCK 21.71 kg/d (as-cast stock).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 1362.2 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; hold-up of the cont feed is below the class minimum.
- Sizing study AQS-DUTY-072 (study): feed_kg_d 31.71; billet_kg_d 10; ingot_kg_d 21.71; mold water-cooled copper, horizontal (AQS-SIZE-FOUNDRY); basis pot metal + Zn + stainless base to the ingot line; Fe 10 rolled.
- Graph design (AQS-PAR-001 sizing): machine two-strand horizontal semi-continuous caster; feed_kg_d 31.71; billet_kg_d 13.24; ingot_kg_d 21.71; strands 2; mould water-cooled copper (AQS-SIZE-FOUNDRY).

3. Material. Water-cooled copper mould (the graph-design primary), demineralized-water jacket on the issued Q3/Q4 M1 loop family; graphite feed launder; steel jacket casing. Basis: two-strand horizontal semi-continuous caster (graph design): the water-cooled copper mould is the caster hot face; the water side is already the issued M1 family (AQS-STD-002 section 12.1; A-M-199). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Cu-Cr or Cu-Zr mould alloy if mould heat-cracking shows at the 31.7 kg/d feed (cost up). slab/billet leaves on conveyors; solids only thereafter. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/CONT_CAST.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/CONT_CAST.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
