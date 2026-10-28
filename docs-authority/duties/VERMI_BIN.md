# VERMI_BIN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 2.75 kg/d. Mass out 2.75 kg/d. Electrical duty 0.0000 kW. In: QUAIL_DROP 1.75 kg/d (quail droppings to the vermi bin); VERMI_FEED 1 kg/d (soft canopy residue to the vermi bin). Out: VERMICOMPOST 1.9 kg/d (vermicompost to the growbed soil); WORM_TEA 0.85 kg/d (worm tea to the growbed soil).

2. Size.
- Envelope 2100×1100×600 mm, 1.386 m³. That box over this flow would be 12096.0 h if it were full. It is not a residence time.
- Envelope: 2 m2 bin at 300 mm bedding depth (A-M-425) (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service vermiculture bin, Eisenia fetida; bin_m2 2; basis A-M-425 (X-FARM-09); organisms Eisenia fetida (red wiggler): surface-dwelling, no O2 requirement edge (the bin is aerobic through diffusion); castings_quality vermicompost 1.5-2.5 % N, 1.0-1.5 % P, 1.0-1.5 % K in plant-available form + humic acids + growth hormones (TECHTREE vermiculture).

3. Material. HDPE bin with coco-coir and shredded-paper bedding, PP working fork, SS316 harvest screen. Basis: bedding held at 70-80 % moisture near neutral pH for Eisenia fetida (graph design; A-M-425): the wet near-neutral bedding is benign to HDPE/PP and hostile to unprotected steel; no metal contact with the casting harvest Alternative: FRP bin at larger areas (same polymer-class logic as the BSFL bin). castings 1.5-2.5 % N to the soil root zones (A-M-425). (X-FARM-09)

4. Nozzles. Schedule at `nozzles/VERMI_BIN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops VERMI_BINPT-01, VERMI_BINTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/VERMI_BIN.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/VERMI_BIN/draw_vermi_bin.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
