# EVAP_ACID

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1243.3 kg/d. Mass out 1243.3 kg/d. Electrical duty 2.4115 kW. In: IA-EVAP_ACID-FEED 1243.3 kg/d (HCl 2 M from BMED). Out: IA-EVAP_ACID-COND 803.8 kg/d (evaporator condensate return (BMED water make-up)); IA-ACID-01 439.5 kg/d (regen HCl, 20 wt%).

2. Size.
- X-PAR acid-loop decision (AQS-PAR-001). Mechanical vapour recompression evaporator, HCl from 2 M (7.07 wt%) to 20 wt% (below the HCl-water azeotrope 20.2 wt%, PERRY9_HCL).
- Water off 803.8 kg/d, condensed and returned to BMED_ACID on IA-EVAP_ACID-COND as BMED water make-up.
- In-house MVR design (X-MFG-30, AQS-DUTY-060): body 101.325 kPa, boiling 108.6 C, condensing 114.6 C at 166.98 kPa (ratio 1.648); 20 tubes ID 25.0 x 1500 mm, 2.33 m2; shell DN350, height 3100 mm.
- Power 1.391 kW (41.5 kWh/t: blower 1.384 kW, recirculation 0.008 kW), 480 V feed SF-EVAP_ACID.
- Interchanger 0.15 m2, 3.52 kW; feed preheated to 98.6 C; product and condensate out at 48.7 C.

3. Material. Wetted parts in hot HCl: impregnated graphite heat exchanger, fluoropolymer-lined shell, PVDF or PTFE piping (ULLMANN_HCL). No stainless or nickel in the HCl circuit. Above 60 °C no PVC-U or CPVC (AQS-STD-002).

4. Nozzles. Feed IA-EVAP_ACID-FEED, product IA-ACID-01, condensate IA-EVAP_ACID-COND. DN by AQS-PIP-004 at the next line-list run.

5. Instruments. Product density or conductivity controls the concentration and holds it below the azeotrope; level, temperature, compressor current. High level trips the feed.

6. Relief. Sized in-house (AQS-DUTY-060 section 3). Body: fire case ISO 23251 / API 521, 41.32 kg/h at 222.3 kPa abs, 34.0 mm2 required, API 526 D orifice, set 100 kPa g. Shell: blocked outlet 40.19 kg/h, 15.465 mm2, D orifice, set 350 kPa g. API 520 Part I / ISO 4126-1. Vent to ACID_POLISH_SCRUB.

7. Code. Built in-house to an open design (X-MFG-30); no bought skid. Not stamped. Placed in BMED_CRU (AQS-PLACE-STUDY-001). Model `models/mfg/EVAP_ACID/export/evap_acid.step`; envelope `cad/stl/EVAP_ACID.stl`. Production route `docs-authority/fab/EVAP_ACID.md`.

8. Open items. HCl carry-over in the vapour near the azeotrope (AQS-DUTY-060 section 7 item 1, owner review); bench leach at 20 wt% (A-M-090); pilot U and blower efficiency (A-M-106).
