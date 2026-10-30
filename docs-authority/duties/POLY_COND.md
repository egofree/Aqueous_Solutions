# POLY_COND

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Envelope 600×600×1200 mm, 0.432 m³.
- Envelope basis (graph node): real kettle design at the 0.5 kg/d design case; standby envelope (recipe waits on the digester organic assay, AQS-DES-POLY; geometry issued A-M-283).
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): vessel condensation resin kettle; D_mm 200; H_mm 300; design_case_kg_d 0.5; jacket_C 160; agitator_kW 0.18; note installed standby: DIGEST_TO_POLY stays 0 until the digester organic assay issues the recipe.

3. Material. 316L, Hastelloy option (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/POLY_COND.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/POLY_COND.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
