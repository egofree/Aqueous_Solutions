# BEE_HIVE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.2 kg/d. Mass out 0.2 kg/d. Electrical duty 0.0000 kW. In: NECTAR_FORAGE 0.2 kg/d (nectar/pollen forage from the canopy and greenhouse crops). Out: HONEY 0.05 kg/d (honey to the food store (annual average)); BEE_VAP 0.15 kg/d (hive evaporation).

2. Size.
- Envelope 600×500×1100 mm, 0.33 m³. That box over this flow would be 39600.0 h if it were full. It is not a residence time.
- Envelope: 10-frame deep + medium + stand (A-M-424; TECHTREE beekeeping) (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service honey bee hive: pollination + honey; hives 1; honey_kg_yr 10-25; basis A-M-424 (X-FARM-08).

3. Material. Untreated solid-pine box bodies, SS316 screen bottom board, propolis-waxed interiors; no copper-bearing alloys and no treated lumber anywhere on the hive. Basis: Apis mellifera propolise rough untreated wood and are poisoned by lumber preservatives and copper salts (graph design; A-M-424): in the closed shell the hive may also not outgas into the habitable atmosphere, which is what excludes the polymer-hive class Alternative: none within the palette - the material is the biology interface here (a polymer hive is a process-change decision, not a materials trade). pollination service to the canopy is the primary output; honey and wax are secondary (A-M-424). (X-FARM-08)

4. Nozzles. Schedule at `nozzles/BEE_HIVE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops BEE_HIVEPT-01, BEE_HIVETE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/BEE_HIVE.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/BEE_HIVE/draw_bee_hive.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
