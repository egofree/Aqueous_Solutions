# POLY_FIBER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.09219 kg/d. Mass out 0.09219 kg/d. Electrical duty 0.3000 kW. In: STOCK_TO_FIBER 0.09048 kg/d (PP pellet draw to the melt-spin line); FR_FINISH 0.001719 kg/d (phosphorus-FR finish (reagent manifest)). Out: FIBER_SCRAP 0.004524 kg/d (spin scrap to the solids line); FLEECE_TO_MFG 0.08767 kg/d (FR-finished fleece to the shop for conversion).

2. Size.
- Sizing study pending (study): throughput_kg_d 0.0905; basis POLYMERS.textile drivers.
- Graph design (AQS-PAR-001 sizing): service PP melt-spin staple-fiber line: pellet -> spun fiber -> needle-punched nonwoven fleece for the crew textile issue; basis A-M-429; A-M-225 (the FR finish rides the D-DOCK reagent manifest, the WS_SOLV reagent-import class); fr_finish phosphorus-FR finish at the ~2 % pick-up class: PP is inherently flammable, the FR finish is the wool-flammability replacement carrier; product fleece to MFG_SHOP for conversion (cutting/sewing/knitting) - the shop issues finished textiles to the hab; feed draws the C5-C10 export surplus: IA-C5-SHIP gives up the 0.09 kg/d polymer share (the export carried 7.13 kg/d); waste spin scrap returns to the solids/leach line (POLY_TO_WET class: PP is leach-inert).

3. Material. SS304 melt vessel and spin pump with heater bands, brass-free spinnerette (stainless die plate), PP quench ducting. Basis: PP melts at 160-220 C and is non-wetting to the 304 class at the bench throughput (A-M-429): the die plate is the precision item; no copper alloys touch the melt (PP degrades against copper at melt temperature) Alternative: a 316L die plate if the FR-finish chemistry ever shows die corrosion. the FR finish dosing skid is PP/PTFE-contact throughout. (X-POLY-01)

4. Nozzles. Schedule at `nozzles/POLY_FIBER.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops POLY_FIBERFIT-01, POLY_FIBERPT-01, POLY_FIBERTE-01, POLY_FIBERTIR-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet. Manufacturing model `models/mfg/POLY_FIBER/draw_poly_fiber.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
