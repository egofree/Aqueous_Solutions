# EVAP_ACID

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1243.3 kg/d. Mass out 1243.3 kg/d. Electrical duty 2.4115 kW. In: IA-EVAP_ACID-FEED 1243.3 kg/d (HCl 2 M from BMED). Out: IA-EVAP_ACID-COND 803.8 kg/d (evaporator condensate return (BMED water make-up)); IA-ACID-01 439.5 kg/d (regen HCl, 20 wt%).

2. Size.
- X-PAR acid-loop decision (AQS-PAR-001). Mechanical vapour recompression evaporator, HCl from 2 M (7.07 wt%) to 20 wt% (below the HCl-water azeotrope 20.2 wt%, PERRY9_HCL).
- Water off 803.8 kg/d, condensed and returned to BMED_ACID on IA-EVAP_ACID-COND as BMED water make-up.
- Power 0.8038 t/d × 72.0 kWh/t (VOGELBUSCH_MVR upper bound, A-M-089) / 24 h = 2.41 kW, 480 V feed SF-EVAP_ACID; heat leaves on SQ-EVAP_ACID (A-M-086).
- Study skid 1200 × 800 × 1800 mm (A-M-092). Values from `flow_graph/param/solver.py` evap().

3. Material. Wetted parts in hot HCl: impregnated graphite heat exchanger, fluoropolymer-lined shell, PVDF or PTFE piping (ULLMANN_HCL). No stainless or nickel in the HCl circuit. Above 60 °C no PVC-U or CPVC (AQS-STD-002).

4. Nozzles. Feed IA-EVAP_ACID-FEED, product IA-ACID-01, condensate IA-EVAP_ACID-COND. DN by AQS-PIP-004 at the next line-list run.

5. Instruments. Product density or conductivity controls the concentration and holds it below the azeotrope; level, temperature, compressor current. High level trips the feed.

6. Relief. Vendor relief on the vapour body (API 520 at vendor data). Vent to ACID_POLISH_SCRUB.

7. Code. Vendor skid. Not stamped. Placed in BMED_CRU (AQS-PLACE-STUDY-001).

8. Open items. Vendor MVR quote at about 0.8 t/d water (A-M-089); bench leach at 20 wt% (A-M-090).
