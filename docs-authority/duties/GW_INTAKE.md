# GW_INTAKE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 11.4 kg/d. Electrical duty 0.0000 kW. In: none. Out: IA-GW-MAKEUP 0 kg/d (groundwater make-up, reverse-osmosis treated); IA-ACID-H2O 0.08076 kg/d (well water for SO3 absorption and dilution to 98 wt%); IA-NAOH-H2O 11.32 kg/d (well water for the liquor, the slaker or the cell); IA-PCA-H2O 8e-06 kg/d (well water to slake the lime).

2. Size.
- Envelope 900×700×1800 mm, 1.134 m³.
- Envelope: L x W x H mm study envelope for the well pump, sand separator and RO rack; unit task 02 sizing pending.
- Node params (AQS-PAR-001): equipment_id GW_INTAKE-01; design_note RO reject leaves as a defined plant stream; the well source and quality basis is USGS_DV_GW for the Death Valley variant and the local well record at any other dry site.

3. Material. Selections issued (unit task 09 pattern; checked across the AQS-ASSAY-001 Rev C bounding cases, AQS-STD-002). The raw well side, from the well pump suction through the sand separator, is PVC-U Sch 80 (class P1): mineralised water at about 30 C with silica, fluoride and arsenic (USGS_DV_GW) and no hydrocarbon or aromatic exposure in the bounding cases. The reverse-osmosis stage uses FRP membrane housings with 316L wetted pump and valve internals; the permeate is aggressive to plain carbon steel at low dissolved solids (AQS-STD-002 section 12 family classes). The permeate and reject lines, including IA-GW-MAKEUP to ROOF_TANK, are PVC-U Sch 80 (class P1); the reject is the concentrated-salt stream at or below 60 C. The RO reject leaves as a defined plant stream whose outlet destination is named before first water (unit task 12 traveller item; the AQS-END-002 EOL matrix carries the construction rows). The unit internals are the replaceable RO membrane elements and the sand-separator media, both consumable-change items (unit task 12).

4. Nozzles. Schedule at `nozzles/GW_INTAKE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops authored in AQS-CTL-001 (2026-10-25 extension): FT on IA-GW-MAKEUP (2 x normal range rule), PT on the membrane feed (0-10 bar g), CT on the permeate (0-2000 uS/cm quality watch). No trip is specified; the tank-level demand modulates the recovery valve at control level (PLC-WTR).

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). Envelope registry STL issued at `cad/stl/GW_INTAKE.stl` (metres, ASCII; the study envelope of section 2).

8. Open items. Sizing calculation pending (unit task 02). Nozzle schedule and elevations are placeholders (unit tasks 04/06). Relief case pending (unit task 07). The RO reject outlet destination is a first-water traveller item (unit task 12). The unit duty solves to zero at the baseline site; the Death Valley variant carries the make-up flow (AQS-SITE-006).
