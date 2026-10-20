# TI_CELL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 3.074 kg/d. Mass out 3.074 kg/d. Electrical duty 0.5000 kW. In: FLOAT_SINK_GRIT_TO_TI 0 kg/d (dense grit (ilmenite/rutile fraction)); IA-MG-TI 0.5078 kg/d (Mg reductant to the Kroll retort); IA-CL2-MG-TI 1.481 kg/d (chlorine to the Kroll chlorinator); IA-TIO2-MU 0.8342 kg/d (TiO2-equivalent rutile concentrate (dock import class)); 1 more. Out: TI_CELL_SLAG_RETURN 0 kg/d (slag / residual grit); TI_CELL_CL2_TO_CRU 0 kg/d (chlorine from Kroll chlorinator / Mg recycle); METALS_TO_IND_MELT 0.5 kg/d (Ti and other metal powders/sponge); VAC_IND_TI 0 kg/d (Ti sponge/powder to vacuum melt); 3 more.

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 7994.2 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK rutile + carbon imports with the Mg-pot loop (A-M-280).
- Sizing study AQS-DUTY-072 (study): ti_kg_d 0.5; tio2_kg_d 0.8342; c_kg_d 0.2509; cl2_kg_d 1.481; mg_kg_d 0.5078; mgcl2_gross_kg_d 1.989; co_kg_d 0.5852; chemistry TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL); I_A 0; V 0; dc_kW 0; hold_kW 0.5; kW 0.5; basis dock rutile-equivalent + carbon + Mg-pot loop; A-M-280 (assay envelope on the concentrate).
- Graph design (AQS-PAR-001 sizing): service Kroll chlorinator + Mg-reduction retort train; chemistry TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL); tio2_kg_d 0.8342; c_kg_d 0.2509; ti_kg_d 0.5; mg_kg_d 0.5078; cl2_kg_d 1.481; mgcl2_gross_kg_d 1.989; co_kg_d 0.5852; retort_T_C 900; chlorinator_T_C 800; hold_kW 0.5; batch_kg 1; basis batch retort campaigns at the 0.5 kg/d Ti scale.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/TI_CELL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/TI_CELL.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
