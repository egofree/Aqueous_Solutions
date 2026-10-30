# NAOH_PLANT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 20.96 kg/d. Mass out 20.96 kg/d. Electrical duty 1.1929 kW. In: IA-TRONA-MU 0.9196 kg/d (trona ore (raw ore) for soda ash); IA-NA-RECYCLE 5.778 kg/d (sodium chloride of the leach purge recovered to the cell brine); IA-NAOH-H2O 14.24 kg/d (well water for the liquor, the slaker or the cell); IA-LIME-TO-NAOH 0.02237 kg/d (cake-kiln lime residue as the lime-cycle make-up). Out: IA-NAOH-VENT 0.4751 kg/d (carbon dioxide and water vapour of the trona calciner and lime kiln); IA-NAOH-CL2-SHIP 3.505 kg/d (chlor-alkali chlorine, shipped with the chlorine export); IA-NAOH-H2 0.09965 kg/d (chlor-alkali cathode hydrogen to the H2 header); IA-NAOH-RESIDUE 0.1264 kg/d (ore insolubles and the lime-mud purge); 1 more.

2. Size.
- Node note: Sodium hydroxide plant (A-M-422).
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. Lime kiln and trona calciner tubes of Inconel 600 with alumina lining and mineral-wool insulation; slaker, causticiser and white-liquor tank of carbon steel; on the chlor-alkali route, titanium anode pans, nickel cathode pans and perfluorinated membranes, with nickel catholyte piping and PVC-lined brine piping. Basis: Sodium hydroxide liquor at about 10 wt% and 90 C from the causticiser, or 32 wt% catholyte with wet chlorine and brine on the chlor-alkali route (A-M-422, flow_graph/param/caustic.py): carbon steel serves dilute caustic below the caustic-cracking range, nickel serves hot strong caustic, and wet chlorine and acid brine need titanium or lined steel (ULLMANN_NAOH; PERRY9_MAT). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Nickel 200 for the liquor lines if the caustic runs hot and strong in service. wetted by caustic liquor (and wet chlorine on the chlor-alkali route); caustic cracking of stressed carbon steel is the corrosion load. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/NAOH_PLANT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-NAOH-VENT on the graph (to ATMOS). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
