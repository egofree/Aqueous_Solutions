# FLUX_PREP

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.03978 kg/d. Mass out 0.03978 kg/d. Electrical duty 0.1000 kW. In: IA-KROLL-FLUX 0.03978 kg/d (MgCl2-class salt drag-out (flux cover source)). Out: FLUX_TO_IND 0.03978 kg/d (flux).

2. Size.
- Envelope 800×600×1200 mm, 0.576 m³. That box over this flow would be 347502.6 h if it were full. It is not a residence time.
- Envelope basis (graph node): prep-class study minimum; live on the Kroll drag-out (A-M-280).
- Sizing study AQS-DUTY-072 (study): salt_kg_d 0.0398; basis Kroll MgCl2-class drag-out (A-M-280); salt-flux cover for the Al-charged melt.
- Graph design (AQS-PAR-001 sizing): bench salt flux cover preparation bench; salt_kg_d 0.0398; hopper_L 20; mixer_kW 0.1.

3. Material. PP-H day-drum metering + 304L mixing bench kept dry; sealed anhydrous handling of the MgCl2-class drag-out. Basis: salt-flux cover preparation, 0.0398 kg/d dry Kroll/MgCl2-class drag-out (graph design; A-M-280): MgCl2 hygroscopicity drives the anhydrous handling class (ULLMANN_MAGNESIUM, GREENWOOD). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 316L drum if the salt arrives as a concentrated solution slurry (different duty class). the 0.1 kW mixer is the only powered part; dry salt contact throughout. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/FLUX_PREP.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/FLUX_PREP.stl`. Manufacturing model `models/mfg/FLUX_PREP/draw_flux_prep.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
