# EVAP_BASE

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1307 kg/d. Mass out 1307 kg/d. Electrical duty 1.3240 kW. In: IA-EVAP_BASE-FEED 1302 kg/d (NaOH 2 M from BMED); IA-NAOH-MU 5.059 kg/d (purchased NaOH flake make-up). Out: IA-BASE-01 25.3 kg/d (digest NaOH, 20 wt%); IA-BASE-PPT 482.3 kg/d (NaOH 20 wt% to hydroxide precipitation of leached Al, Ca, Mg, Fe (class A)); IA-EVAP_BASE-COND 799.2 kg/d (evaporator condensate return (BMED water make-up)).

2. Size.
- X-PAR acid-loop decision (AQS-PAR-001). Mechanical vapour recompression evaporator, NaOH from 2 M (7.41 wt%) to 20 wt%.
- Water off 799.2 kg/d, condensed and returned to BMED_BASE on IA-EVAP_BASE-COND as BMED water make-up. NaOH flake make-up IA-NAOH-MU enters here (NaOH balance, owner decision 2026-10-15).
- Power 0.7992 t/d × 72.0 kWh/t (VOGELBUSCH_MVR upper bound, A-M-089) / 24 h = 2.40 kW, 480 V feed SF-EVAP_BASE; heat leaves on SQ-EVAP_BASE (A-M-086).
- Study skid 1200 × 800 × 1800 mm (A-M-092). Values from `flow_graph/param/solver.py` evap().

3. Material. Wetted parts in hot NaOH: nickel 200 or fluoropolymer-lined. No aluminium, zinc or PVC above 60 °C (AQS-STD-002).

4. Nozzles. Feed IA-EVAP_BASE-FEED, product IA-BASE-01 and IA-BASE-PPT, condensate IA-EVAP_BASE-COND. DN by AQS-PIP-004 at the next line-list run.

5. Instruments. Product density or conductivity controls the concentration; level, temperature, compressor current. High level trips the feed.

6. Relief. Sized in-house (AQS-DUTY-060 section 3). Body: fire case ISO 23251 / API 521, 41.32 kg/h at 222.3 kPa abs, 33.98 mm2 required, API 526 D orifice, set 100 kPa g. Shell: blocked outlet 39.96 kg/h, 15.376 mm2, D orifice, set 350 kPa g. API 520 Part I / ISO 4126-1. Vent to ACID_POLISH_SCRUB.

7. Code. Built in-house to an open design (X-MFG-30); no bought skid. Not stamped. Placed in BMED_CRU (AQS-PLACE-STUDY-001). Model `models/mfg/EVAP_BASE/export/evap_base.step`; envelope `cad/stl/EVAP_BASE.stl`. Production route `docs-authority/fab/EVAP_BASE.md`.

8. Open items. bench leach at 20 wt% (A-M-090); pilot U and blower efficiency (A-M-106).
