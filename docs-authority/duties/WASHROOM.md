# WASHROOM

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: IA-WASH-FEED 0 kg/d (wash-water feed to the washroom fixtures). Out: WASH_GREY 0 kg/d (wash grey water to the treatment train).

2. Size.
- Envelope 3000×2000×2400 mm, 14.4 m³.
- Envelope: 8 m2 fitout shell (A-M-419; AQS-HAB-001) (X-HAB sec3).
- Graph design (AQS-PAR-001 sizing): service washroom / hygiene, 6 m2; area_m2 6; basis A-M-419; AQS-HAB-001.

3. Material. FRP wet-wall panels, SS304 fixtures, ceramic tile wet zones, SS drainage. Basis: continuous wet zone at habitable temperature (AQS-HAB-001; A-M-419): FRP and ceramic carry the standing condensate; 304 is the fixture class at the chloride-light service Alternative: SS316 fixtures where sanitiser chemistry concentrates. grey water to the WTR loop; the washroom is the largest hab water consumer. (X-HAB-01)

4. Nozzles. Schedule at `nozzles/WASHROOM.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops WASHROOMPT-01, WASHROOMTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/WASHROOM.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/WASHROOM/draw_washroom.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
