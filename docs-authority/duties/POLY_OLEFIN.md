# POLY_OLEFIN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.2941 kg/d. Mass out 0.2941 kg/d. Electrical duty 0.0000 kW. In: MEOH_TO_OLEFIN 0 kg/d (methanol co-feed); IA-C5-POLY 0.2941 kg/d (C5-C10 naphtha olefin feed). Out: OLEFIN_TO_PELLET 0.2941 kg/d (polyolefin resin); IA-MTO-H2O 0 kg/d (methanol-to-olefin reaction water).

2. Size.
- Envelope 600×600×1200 mm, 0.432 m³. That box over this flow would be 35250.1 h if it were full. It is not a residence time.
- Envelope basis (graph node): reactor-class study minimum; DN150 at 1 d hold-up of the naphtha feed at 750 kg/m3 melt density; wall by ASME VIII-1 UG-27 at 5 MPa.
- Sizing study AQS-DUTY-073 (study): feed_kg_d 0.2941; feed C5-C10 naphtha at the cut tank (IA-C5-POLY); T_C 150-250; P_MPa 1-5; heat_W 0.0013; basis AQS-SIZE-OIL-POLY POLY_OLEFIN reactor; feed heating 25->200 C at 2.1 kJ/kg K, exotherm neglected (study).
- Graph design (AQS-PAR-001 sizing): vessel vertical cylindrical oligomerization reactor; D_mm 150; H_mm 225; wall_mm 3.8; T_C 250; P_MPa 5; op_window 150-250 C at 1-5 MPa (AQS-SIZE-OIL-POLY); feed_kg_d 0.2941; heat_W 0.0013.

3. Material. SA-240 316L, welded (ASME IX) (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/POLY_OLEFIN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/POLY_OLEFIN.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
