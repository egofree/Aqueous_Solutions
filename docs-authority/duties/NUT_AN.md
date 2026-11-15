# NUT_AN

Standard: AQS-STD-001 Rev A. Graph Rev AD. Study. Not a PE stamp.

1. Basis. Mass in 4.107 kg/d. Mass out 4.107 kg/d. Electrical duty 0.0600 kW. In: IA-NUT-NH3 0.2305 kg/d (ammonia liquor to the nitrate skid (Ostwald feed and the neutralization base)); IA-NUT-O2 0.4331 kg/d (plant oxygen for the ammonia oxidation); IA-NUT-H2O 3.443 kg/d (dilution water to the dosing strength). Out: NUT_AQUA 4.087 kg/d (ammonium-nitrate nutrient solution to the raceway (on-site skid, X-QA-11)); IA-NUT-VENT 0.01991 kg/d (unconverted slip to the NOx scrubber (its nitrate liquor feeds NUTRIENT_DOSE)).

2. Size.
- Graph design (AQS-PAR-001 sizing): gap_N_kg_d 0.1839; an_kg_d 0.5255; dose_kg_d 4.087; nh3_kg_d 0.2305; o2_kg_d 0.4331; rxn_h2o_kg_d 0.1183; dil_kg_d 3.443; vent_kg_d 0.01991; kw 0.06.
- Node note: Ammonium-nitrate nutrient skid (A-M-497).

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/NUT_AN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-NUT-VENT on the graph (to NOX_SCRUB). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
