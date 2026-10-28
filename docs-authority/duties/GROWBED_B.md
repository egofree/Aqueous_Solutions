# GROWBED_B

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 229.7 kg/d. Mass out 229.7 kg/d. Electrical duty 0.0000 kW. In: AQUA_LOOP3 202.8 kg/d (nitrate water through the aerobic root zone (plant uptake + anaerobic mineralisation layer)); RABBIT_MANURE 0.3 kg/d (cold rabbit manure direct to the mineralisation zone); FORM_PRESS 25.69 kg/d (press water back to the loop); NUT_AQUA_BED 1 kg/d (mineral nitrate solution to the media beds). Out: AQUA_LOOP4 220.7 kg/d (loop water to the duckweed raceway (polisher + feed crop)); BED_GREENS 4 kg/d (media-bed greens to the reserve); BED_ET 5 kg/d (growbed evapotranspiration).

2. Size.
- Envelope 3600×2100×500 mm, 3.78 m³. That box over this flow would be 394.9 h if it were full. It is not a residence time.
- Envelope: media bed 7 m2, the anaerobic mineralisation half (A-M-415; A-M-229) (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service aquaponic root zone B (anaerobic mineralisation); area_m2 14.56; zones aerobic top / anaerobic mineralisation bottom (dual root zone); basis A-M-229 area; A-M-415 loop.

3. Material. HDPE tray with EPDM liner, expanded-clay (LECA) media on a geotextile separation cloth, CPVC loop piping. Basis: anaerobic mineralisation root zone (A-M-229; A-M-415): the bed runs sulfidic under the ponded tail, and sulfide plus loop-water contact excludes Cu/Zn/brass outright (ichthyotoxic to the fish stock the loop serves); LECA is the aquaponic media class (graph design). Selection per AQS-STD-002 with the duty section 2 environment. Alternative: PP tray if media abrasion ever shows on the HDPE floor (same polymer family, higher cost). the anaerobic half of the dual root zone; the aerobic half (GROWBED_A) carries its own issued selection. (X-FARM-01)

4. Nozzles. Schedule at `nozzles/GROWBED_B.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops GROWBED_BLT-01, GROWBED_BPT-01, GROWBED_BTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/GROWBED_B.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/GROWBED_B/draw_growbed_b.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
