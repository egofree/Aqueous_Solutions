# GW_INTAKE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.3700 kW. In: none. Out: IA-GW-MAKEUP 0 kg/d (groundwater make-up, reverse-osmosis treated).

2. Size.
- Envelope 800×800×600 mm, 0.384 m³.
- Envelope basis (graph node): the wellhead hatch + pump discharge set (X-LOC-13 well head).
- Sizing study pending (study): pump_kw 0.37.
- Graph design (AQS-PAR-001 sizing): duty standby well head: the make-up on loss of atmospheric harvest; pump_kw 0.37.
- Node params (AQS-PAR-001): equipment_id GW_INTAKE-01; design_note RO reject leaves as a defined plant stream; the well source and quality basis is USGS_DV_GW for the Death Valley variant and the local well record at any other dry site.

3. Material. SS304 wellhead plate and discharge head, HDPE potable discharge line, submersible pump SS304/stainless stages. Basis: potable groundwater contact (X-LOC-13 well head): 304 wetted at the chloride-light aquifer class, HDPE for the discharge run; the pump stages are the well-class stainless Alternative: 316L wetted where the aquifer mineralisation ever shows pitting. standby-zero at the baseline: the atmospheric harvest covers the water cycle (the T4 by-design ruling). (X-LOC-13)

4. Nozzles. Schedule at `nozzles/GW_INTAKE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops GW_INTAKECT-01, GW_INTAKEFT-01, GW_INTAKEPT-01, GW_INTAKETE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/GW_INTAKE.stl` (a thick-walled tray at the claimed envelope; X-PAR-04).

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
