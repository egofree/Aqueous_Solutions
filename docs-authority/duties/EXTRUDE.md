# EXTRUDE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: CAST_TO_EXTRUDE 0 kg/d (billet to extrude). Out: EXTRUDE_TO_STOCK 0 kg/d (rod/profile).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³.
- Envelope basis (graph node): A-M-199 forming class; N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 15; backup_of ROLL (profile press at the Al/Cu profile class); outage_basis roll-stand outage on profile-class lots (A-M-282).
- Graph design (AQS-PAR-001 sizing): machine horizontal profile press, N+1 former of ROLL; connected_kW 15; backup_of ROLL; outage_d 2; press_t 50; container_mm 60.

3. Material. H13 extrusion die + tool-steel container liner on a 50 t press (graph design press_t). Basis: horizontal profile press N+1 of ROLL (graph design): hot-work die steel class per ASM_V1 / DIETER1988. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: billet preheater induction sleeve if the profile class moves hot (a separate duty entry). Nitrided die land where galling is measured (first-article item). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/EXTRUDE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/EXTRUDE.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
