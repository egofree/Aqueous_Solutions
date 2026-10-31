# DRY_COOLER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.1500 kW. In: IA-DC-SPRAY 0 kg/d (evaporative spray make-up). Out: IA-DC-EVAP 0 kg/d (evaporated spray water to air).

2. Size.
- Envelope 1200×600×1200 mm, 0.864 m³.
- Envelope basis (graph node): the dry coil + fan at the 7.25 kW rejection duty.
- Sizing study pending (study): airflow_m3_s 0.61.
- Graph design (AQS-PAR-001 sizing): duty dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share; airflow_m3_s 0.61; fan_kw 0.15.
- Node params (AQS-PAR-001): rated_kW 12; design_C 37.8; design_basis 0.4 % summer design temp (AQS-SITE-002 via AQS-THM-002); LMTD_K 15; fan_kW 0.6.
- Basis (graph node): AQS-HEAT-STUDY-002 Rev A 2026-10-18 §10.8 (A-M-244): 0.05 kW_fan/kW_th class; rated 12 kW to pass the 10.16 kW no-preheat upset with margin.

3. Material. Copper-tube, aluminium-fin air coil with galvanized-steel casing; epoxy-coated headers; the rejection loop is the house HDPE-class closed water loop. Basis: 12 kW dry rejection at the 37.8 C design bulb (graph params; A-M-244): air-sided fin-coil construction is the air-cooled exchanger class (PERRY9_HEAT); the loop side follows the issued water-loop families (AQS-STD-002 section 12.1). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: micro-channel all-aluminium coil (cost down) if galvanic behaviour in the dry service proves neutral. no wetted stream; the fan is the only moving part. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/DRY_COOLER.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops DRY_COOLERPT-01, DRY_COOLERTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
