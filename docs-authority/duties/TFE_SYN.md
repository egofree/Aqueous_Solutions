# TFE_SYN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.4353 kg/d. Mass out 0.4353 kg/d. Electrical duty 0.3989 kW. In: HF_GEN_TO_TFE 0.07984 kg/d (aqueous HF); CRU_TO_TFE 0.2913 kg/d (chlorine); MEOH_TO_TFE 0.06407 kg/d (methanol carbon source to TFE). Out: TFE_TO_POLY_F 0.1076 kg/d (TFE monomer); TFE_HCL_TO_CRU 0.3277 kg/d (dilute HCl return (HCl + reaction water)).

2. Size.
- Envelope 600×600×1200 mm, 0.432 m³. That box over this flow would be 23820.7 h if it were full. It is not a residence time.
- Envelope basis (graph node): reactor-class study minimum; pyrolysis tube + quench at the 0.10 kg/d duty (A-M-283).
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): machine TFE train: R-22 pyrolysis furnace, quench, scrub; pyrolysis_C 750; quenched immediate quench (TFE autopolymerisation hazard; ULLMANN_FLUOROPOLY); tfe_kg_d 0.1; meoh_kg_d 0.06407; cl2_kg_d 0.2836; hf_kg_d 0.08002; hcl_return_kg_d 0.3277; duty_kW 0.3989.

3. Material. Inconel 600 pyrolysis tube, Hastelloy C-276 coolers, PTFE-lined scrubber (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/TFE_SYN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/TFE_SYN.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
