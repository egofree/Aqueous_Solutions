# GROWBED_A

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 202.8 kg/d. Mass out 202.8 kg/d. Electrical duty 0.0000 kW. In: VERMICOMPOST 1.9 kg/d (vermicompost to the growbed soil); WORM_TEA 0.85 kg/d (worm tea to the growbed soil); AQUA_SAN 0 kg/d (sanitized loop water to the growbeds (food-safety/contingency mode)); AQUA_BYPASS 200 kg/d (normal-mode loop bypass around AQUA_UV). Out: AQUA_LOOP3 202.8 kg/d (nitrate water through the aerobic root zone (plant uptake + anaerobic mineralisation layer)).

2. Size.
- Envelope 3600×2100×500 mm, 3.78 m³. That box over this flow would be 447.4 h if it were full. It is not a residence time.
- Envelope: media bed 7 m2 of the 14 m2 dual-root-zone duty at the 0.9 kg/d feed class, 300 mm media + freeboard (A-M-415; A-M-229) (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service aquaponic root zone A (aerobic plant roots); area_m2 14.56; zones aerobic top / anaerobic mineralisation bottom (dual root zone); basis A-M-229 area; A-M-415 loop.

3. Material. HDPE tray with EPDM liner at the ponded inlet zone, expanded-clay (LECA) media on a geotextile separation cloth, CPVC loop piping. Basis: aerobic mineralisation front half of the dual root zone (A-M-229; A-M-415): oxygenated trickling water, so the sulfide exclusion of the anaerobic half does not bind - but the water returns to the fish stock, and Cu/Zn/brass stay out of every wetted face regardless (ichthyotoxicity, AQS-STD-002 with the duty section 2 environment). Alternative: PP tray if media abrasion ever shows on the HDPE floor (same polymer family, higher cost). pairs with GROWBED_B (the anaerobic half); the bed passes 202.8 kg/d loop water and 1.9 kg/d vermicompost to the beds. (X-FARM-11)

4. Nozzles. Schedule at `nozzles/GROWBED_A.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops GROWBED_ALT-01, GROWBED_APT-01, GROWBED_ATE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/GROWBED_A.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/GROWBED_A/draw_growbed_a.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
