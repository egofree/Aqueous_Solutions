# VAC_IND

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: VAC_IND_TI 0 kg/d (Ti sponge/powder to vacuum melt). Out: VAC_TO_INV 0 kg/d (reactive melt for investment pour).

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³.
- Envelope basis (graph node): A-M-199 melt class; N+1 rated envelope (A-M-282): real machine, standby-zero design-day rate.
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 15; backup_of IND_MELT (diverse: vacuum induction skull melt); outage_basis IND_MELT relining/repair outage 2 d (crucible life 20-50 heats, AQS-SIZE-FOUNDRY sec. Crucibles; AGENTS.md redundancy rule); design_case 2 kg ISM skull melt (AQS-SIZE-FOUNDRY).
- Graph design (AQS-PAR-001 sizing): service vacuum induction skull melt (ISM), N+1 diverse of IND_MELT; design_case_kg 2; connected_kW 15; backup_of IND_MELT; outage_d 2; duty_note equal-duty backup of the 25 kW melt at the 2 kg ISM batch class (A-M-282).

3. Material. Water-cooled copper induction crucible (no wetted-refractory interface) + 304L vacuum chamber; ceramic-fibre insulation on the shell. Basis: vacuum induction skull/ISM melt of Ti sponge, N+1 diverse of IND_MELT, 2 kg batch class (graph design, A-M-282): the water-cooled copper face keeps the Ti melt out of contact with any refractory (CRC_TI melting point 1668 C; INDUCT_SOCX power class). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: graphite crucible inside the vacuum chamber if skull-melt power runs above the design (a different metal-contact duty class). no oxides, no salt: M7 vacuum-dry service; Ti sponge line is zero-rate at the design day. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/VAC_IND.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/VAC_IND.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
