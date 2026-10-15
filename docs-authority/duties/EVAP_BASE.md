# EVAP_BASE

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1306.8 kg/d. Mass out 1306.8 kg/d. Electrical duty 2.3976 kW. In: IA-EVAP_BASE-FEED 1301.7 kg/d (NaOH 2 M from BMED); IA-NAOH-MU 5.059 kg/d (purchased NaOH flake make-up). Out: IA-EVAP_BASE-COND 799.2 kg/d (evaporator condensate return (BMED water make-up)); IA-BASE-PPT 482.3 kg/d (NaOH 20 wt% to hydroxide precipitation of leached Al, Ca, Mg, Fe (class A)); IA-BASE-01 25.3 kg/d (digest NaOH, 20 wt%).

2. Size.
- X-PAR acid-loop decision (AQS-PAR-001). Mechanical vapour recompression evaporator, NaOH from 2 M (7.41 wt%) to 20 wt%.
- Water off 799.2 kg/d, condensed and returned to BMED_BASE on IA-EVAP_BASE-COND as BMED water make-up. NaOH flake make-up IA-NAOH-MU enters here (NaOH balance, owner decision 2026-10-15).
- Power 0.7992 t/d × 72.0 kWh/t (VOGELBUSCH_MVR upper bound, A-M-089) / 24 h = 2.40 kW, 480 V feed SF-EVAP_BASE; heat leaves on SQ-EVAP_BASE (A-M-086).
- Study skid 1200 × 800 × 1800 mm (A-M-092). Values from `flow_graph/param/solver.py` evap().

3. Material. Wetted parts in hot NaOH: nickel 200 or fluoropolymer-lined. No aluminium, zinc or PVC above 60 °C (AQS-STD-002).

4. Nozzles. Feed IA-EVAP_BASE-FEED, product IA-BASE-01 and IA-BASE-PPT, condensate IA-EVAP_BASE-COND. DN by AQS-PIP-004 at the next line-list run.

5. Instruments. Product density or conductivity controls the concentration; level, temperature, compressor current. High level trips the feed.

6. Pressure relief open. To be sized in-house under X-MFG-30 (API 520 Part I / ISO 4126-1, blocked-outlet and fire cases on the custom vapour body); the vendor-data basis is withdrawn (owner decision 2026-10-15). Vent to ACID_POLISH_SCRUB (alkaline mist).

7. Code. Built in-house to an open design (X-MFG-30); no bought skid. Not stamped. Placed in BMED_CRU (AQS-PLACE-STUDY-001). The envelope is `cad/stl/EVAP_BASE.stl` (flow_graph/param/envelopes.py).

8. Open items. Outlet temperatures and line classes (X-MAT-20). Vendor MVR quote at about 0.8 t/d water (A-M-089); bench leach at 20 wt% (A-M-090).
