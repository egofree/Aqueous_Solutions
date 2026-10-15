# EVAP_ACID

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1305 kg/d. Mass out 1305 kg/d. Electrical duty 1.4970 kW. In: IA-EVAP_ACID-FEED 1305 kg/d (HCl 2 M from BMED). Out: IA-ACID-01 439.5 kg/d (regen HCl, 20 wt%); IA-EVAP_ACID-COND 865 kg/d (evaporator condensate return (BMED water make-up)); IA-EVAP_ACID-VENT 0.0292 kg/d (column vent: non-condensables, water vapour, trace HCl).

2. Size.
- X-PAR acid-loop decision (AQS-PAR-001). Mechanical vapour recompression evaporator, HCl from 2 M (7.07 wt%) to 20 wt% (below the HCl-water azeotrope 20.2 wt%, PERRY9_HCL).
- Water off 803.8 kg/d, condensed and returned to BMED_ACID on IA-EVAP_ACID-COND as BMED water make-up.
- In-house MVR design (X-MFG-30, AQS-DUTY-060 Rev B): body 101.325 kPa, boiling 108.6 C, condensing 114.6 C at 166.98 kPa (ratio 1.648); 22 tubes ID 25.0 x 1500 mm, 2.51 m2; shell DN350.
- Counter-current HCl column on the frame, feed at the top: DN150, packed 3000 mm, 4 ideal stages from the Perry Tables 2-9/2-10 VLE; condensate 0.5 wt% HCl (4.32 kg/d recycled to BMED_ACID).
- Power 1.497 kW (41.5 kWh/t: blower 1.489 kW, recirculation 0.008 kW), 480 V feed SF-EVAP_ACID.
- Interchanger 0.155 m2, 3.7 kW; feed preheated to 98.6 C; product and condensate out at 49.1 C.

3. Material. Wetted parts in hot HCl: impregnated graphite heat exchanger, fluoropolymer-lined shell, PVDF or PTFE piping (ULLMANN_HCL). No stainless or nickel in the HCl circuit. Above 60 °C no PVC-U or CPVC (AQS-STD-002).

4. Nozzles. Feed IA-EVAP_ACID-FEED, product IA-ACID-01, condensate IA-EVAP_ACID-COND. DN by AQS-PIP-004 at the next line-list run.

5. Instruments. Product density or conductivity controls the concentration and holds it below the azeotrope; level, temperature, compressor current. High level trips the feed.

6. Relief. Sized in-house (AQS-DUTY-060 section 3). Body: fire case ISO 23251 / API 521, 41.32 kg/h at 222.3 kPa abs, 34.0 mm2 required, API 526 D orifice, set 100 kPa g. Shell: blocked outlet 43.25 kg/h, 16.642 mm2, D orifice, set 350 kPa g. API 520 Part I / ISO 4126-1. Relief discharge to ACID_POLISH_SCRUB. Process vent (non-condensables, 29 g/d) through the vent condenser to EVAP_ACID_VS (AQS-DUTY-061, X-PAR-10).

7. Code. Built in-house to an open design (X-MFG-30); no bought skid. Not stamped. Placed in BMED_CRU (AQS-PLACE-STUDY-001). Model `models/mfg/EVAP_ACID/export/evap_acid.step`; envelope `cad/stl/EVAP_ACID.stl`. Production route `docs-authority/fab/EVAP_ACID.md`.

8. Open items. Pilot check of the column (condensate titration, A-M-108); bench leach at 20 wt% (A-M-090); pilot U and blower efficiency (A-M-106).
