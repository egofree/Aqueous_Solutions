# HF_GEN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 2.249 kg/d. Mass out 2.249 kg/d. Electrical duty 0.3083 kW. In: F_RECOVER_TO_HF_GEN 1.52 kg/d (fluoride concentrate); IA-CAF2-MU 0.3255 kg/d (fluorspar make-up, acid-spar class >= 97 % CaF2); IA-H2SO4-MU 0.4038 kg/d (98 wt% sulfuric acid make-up). Out: HF_GEN_TO_VDF 0.09374 kg/d (aqueous HF); HF_GEN_TO_TFE 0.08002 kg/d (aqueous HF); IA-GYPSUM-SHIP 0.5756 kg/d (fluorgypsum (anhydrite) cake byproduct); IA-HF-PROD 1.5 kg/d (aqueous HF to the fab reagent fork).

2. Size.
- Envelope 1200×700×1500 mm, 1.26 m³. That box over this flow would be 13444.1 h if it were full. It is not a residence time.
- Envelope basis (graph node): kiln-class study minimum at the 1.674 kg/d HF duty (ULLMANN_HF; A-M-283); tube 200 x 1200 mm, 2 deg slope, kiln gas absorbed into the recovered-F liquor at the dissolution tank.
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): machine indirectly heated rotary kiln, fluorspar + H2SO4 -> HF; tube_D_mm 200; tube_L_mm 1200; slope_deg 2; rpm 4; residence_min 30; T_C 250; spar_kg_d 0.3255; acid_kg_d 0.4038; hf_kg_d 1.674; cake_kg_d 0.5756; drive_kW 0.37; feed dock acid-spar 97 % CaF2 + 98 wt% H2SO4 + F_RECOVER concentrate; duty_kW 0.3083.

3. Material. carbon steel shell, dry HF service (PERRY9_MAT); Monel trunnion inserts (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/HF_GEN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/HF_GEN.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
