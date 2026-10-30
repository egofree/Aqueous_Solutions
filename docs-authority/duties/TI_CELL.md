# TI_CELL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 3.119 kg/d. Mass out 3.119 kg/d. Electrical duty 0.5000 kW. In: FLOAT_SINK_GRIT_TO_TI 0 kg/d (dense grit (ilmenite/rutile fraction)); IA-MG-TI 0.5078 kg/d (Mg reductant to the Kroll retort); IA-CL2-MG-TI 1.481 kg/d (chlorine to the Kroll chlorinator); IA-TIO2-MU 0.8342 kg/d (TiO2-equivalent rutile concentrate (dock import class)); 1 more. Out: TI_CELL_SLAG_RETURN 0 kg/d (slag / residual grit); TI_CELL_CL2_TO_CRU 0 kg/d (chlorine from Kroll chlorinator / Mg recycle); METALS_TO_IND_MELT 0.5 kg/d (Ti and other metal powders/sponge); VAC_IND_TI 0 kg/d (Ti sponge/powder to vacuum melt); 4 more.

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 7880.6 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK rutile + carbon imports with the Mg-pot loop (A-M-280).
- Sizing study AQS-DUTY-072 (study): ti_kg_d 0.5; tio2_kg_d 0.8342; c_kg_d 0.2509; cl2_kg_d 1.481; mg_kg_d 0.5078; mgcl2_gross_kg_d 1.989; co_kg_d 0.5852; chemistry TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL); I_A 0; V 0; dc_kW 0; hold_kW 0.5; kW 0.5; basis dock rutile-equivalent + carbon + Mg-pot loop; A-M-280 (assay envelope on the concentrate).
- Graph design (AQS-PAR-001 sizing): service Kroll chlorinator + Mg-reduction retort train; chemistry TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL); tio2_kg_d 0.8342; c_kg_d 0.2509; ti_kg_d 0.5; mg_kg_d 0.5078; cl2_kg_d 1.481; mgcl2_gross_kg_d 1.989; co_kg_d 0.5852; retort_T_C 900; chlorinator_T_C 800; hold_kW 0.5; batch_kg 1; basis batch retort campaigns at the 0.5 kg/d Ti scale.

3. Material. Alumina-brick-lined carbochlorinator at 800 C with graphite hot face; TiCl4 take-off cooled through a 316L condensation train; Kroll reduction retort 310S (25Cr-20Ni) with a graphite crucible insert at 900 C; molten MgCl2 return through graphite/Ni-200 launder. Basis: TiO2 + 2C + 2Cl2 at 800 C and TiCl4 + 2Mg at 900 C (AQS-BAL-KROLL closure, graph design): the chlorinator bed is a dry hot face; the retort is the Kroll steel-retort class (KROLL1940, ULLMANN_TITANIUM); chloride-melt metallurgy for the launder (DING2018_CL_REVIEW). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Mo-clad retort (Kroll shipped his demonstration retort Mo-clad) if service pushes above 950 C; Hastelloy C-276 condensation if TiCl4 hydrolysis is ever traced. batch 1 kg sponge class retort (graph design); the Mg recycles from MG_POT and the MgCl2 returns through the issued section 12.2 last-row launder. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/TI_CELL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/TI_CELL.stl`. Manufacturing model `models/mfg/TI_CELL/draw_ti_cell.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
