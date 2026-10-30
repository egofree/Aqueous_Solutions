# IND_MELT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 37.6 kg/d. Mass out 37.6 kg/d. Electrical duty 0.8934 kW. In: CAST_SCRAP_TO_IND 0.5294 kg/d (foundry scrap); METALS_TO_IND_MELT 0.5 kg/d (Ti and other metal powders/sponge); FLUX_TO_IND 0.03978 kg/d (flux); MO_TO_IND 0.0625 kg/d (Mo metal); 5 more. Out: IND_MELT_TO_CAST 3.529 kg/d (molten metal); IND_TO_CONT 31.71 kg/d (melt to continuous caster); FOUNDRY_SLAG_TO_LEACH 0.3302 kg/d (slag return); IND_TO_ATOM 0 kg/d (melt to atomizer when powder required); 2 more.

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³. That box over this flow would be 957.3 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 melt class: crucible melt_charge_kg at 7000 kg/m3, H/D atm_HD, +300/+500 allowances; box furnace at the connected load.
- Sizing study AQS-DUTY-072 (study): charge_kg_d 37.01; stock_out_kg_d 25.9; slag_kg_d 0.3565; crucible_kg 10; heats_d 4; melt_kWh_d 21.25; avg_kW 0.8854; peak_kW 15; connected_kW 25; basis scrap remelt + pot metal; class energies (cp_s dT + L + cp_l superheat)/eta per A-M-177 method, CRC_CU/CRC_FE/CRC_ZN/CRC_AL/CRC_TI (reactive/addition class bounding at Ti).
- Graph design (AQS-PAR-001 sizing): service Cu/Fe/Zn/Al scrap + pot-metal remelt; medium-frequency coreless induction, tilt pour; crucible_kg 10; crucible_D_mm 110; crucible_H_mm 165; heats_d 4; connected_kW 25; peak_kW 15; melt_kWh_d 21.25; lining ceramic-fibre hot face 150 mm + 4 mm CS casing (study).

3. Material. Clay-graphite crucibles assigned per melt family (Cu/Zn/Fe/Al one each), ceramic-fibre hot face 150 mm + 4 mm CS casing; alumina castable hearth under the pour lip. Basis: coreless medium-frequency induction remelt of Cu/Fe/Zn/Al scrap + pot metal at the 10 kg class (graph design, A-M-282 energies): melting points bound the refractory class (CRC_CU/CRC_FE/CRC_ZN/CRC_AL); crucible and lining class per SCHACHT2004 ch. 8/10; coil hardware per INDUCT_SOCX. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: SiC crucibles for the Al family if attack is measured (cost up, better wetting resistance); alumina-liner swap when the charge is ferrous-only. crucible life is a unit task 12 first-article measurement (crucible_kg 10, heats_d 4 in graph design); no rate claimed. Slag tap is basic-oxide wetted: alumina hot face. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/IND_MELT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/IND_MELT.stl`. Manufacturing model `models/mfg/IND_MELT/draw_ind_melt.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
