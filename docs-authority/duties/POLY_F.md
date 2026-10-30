# POLY_F

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.25 kg/d. Mass out 0.25 kg/d. Electrical duty 0.0449 kW. In: VDF_TO_POLY_F 0.15 kg/d (VDF monomer); TFE_TO_POLY_F 0.1 kg/d (TFE monomer). Out: POLYF_TO_PELLET 0 kg/d (PVDF/PTFE resin); POLYF_TO_POWDER 0.09 kg/d (fluoropolymer powder); POLYF_TO_FILM 0.14 kg/d (PVDF resin to the film/sheet line); POLYF_RECLAIM 0.02 kg/d (off-spec fluoropolymer scrap/rework).

2. Size.
- Envelope 600×600×1200 mm, 0.432 m³. That box over this flow would be 41472.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): reactor-class study minimum; jacketed kettle at the 0.25 kg/d monomer duty, reclaim loop to F_RECOVER (A-M-283).
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): vessel PVDF/PTFE emulsion polymerization kettle; D_mm 150; H_mm 225; T_C 60; vdf_kg_d 0.15; tfe_kg_d 0.1; pvdf_kg_d 0.14; ptfe_kg_d 0.09; reclaim_kg_d 0.02; initiator persulfate class, emulsion/suspension (ULLMANN_FLUOROPOLY); duty_kW 0.0449.

3. Material. Hastelloy C-276 wetted, PTFE gasketed (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/POLY_F.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/POLY_F.stl`. Manufacturing model `models/mfg/POLY_F/draw_poly_f.py` (AQS-PLAN-006).

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
