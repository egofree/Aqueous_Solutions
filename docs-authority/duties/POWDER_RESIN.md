# POWDER_RESIN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.09 kg/d. Mass out 0.09 kg/d. Electrical duty 0.0152 kW. In: POLYF_TO_POWDER 0.09 kg/d (fluoropolymer powder). Out: POWDER_TO_STOCK 0.09 kg/d (powder stock).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 480000.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): forming-class minimum (A-M-199); mill + classifier at the 0.09 kg/d powder duty (A-M-283).
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): machine PTFE powder line: pin mill + cyclone classifier + collector; ptfe_kg_d 0.09; mill_kWh_kg 0.05; duty_kW 0.0152; product fine powder for compression sintering (PTFE is not melt-processable; ULLMANN_FLUOROPOLY).

3. Material. 316L mill, PE-lined collector (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/POWDER_RESIN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/POWDER_RESIN.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
