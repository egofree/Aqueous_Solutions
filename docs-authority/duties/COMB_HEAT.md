# COMB_HEAT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0500 kW. In: none. Out: COMB_OFFGAS 0 kg/d (combustion off-gas when alternate used).

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³.
- Envelope basis (graph node): A-M-199 melt class; N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 30; backup_of IND_MELT (tertiary, fuel-fired C5-C10 class); outage_basis long IND_MELT outage with both electric alternates unavailable (A-M-282); off-gas to MET_SCRUB when energized.
- Graph design (AQS-PAR-001 sizing): service combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT; connected_kW 0.05; thermal_kW 30; backup_of IND_MELT; outage_d 2; offgas to MET_SCRUB when energized (COMB_OFFGAS).

3. Material. Alumina-silica brick + castable crown hot face on a mild-steel shell; 310S burner tube; flue path dry above the acid dew point into MET_SCRUB. Basis: tertiary N+1 fuel-fired melt heat (graph design): combustion hot-face class per SCHACHT2004 ch. 10; the fuel class is the plant C5-C10 product (duty section 1); combustion stoichiometry per TURNS2012. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: precast refractory module kit if relining downtime dominates the outage plan. energized only on IND_MELT outage (outage_d 2); off-gas books to MET_SCRUB when hot (M7). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/COMB_HEAT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/COMB_HEAT.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
