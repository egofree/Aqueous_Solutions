# In-house MVR evaporators EVAP_ACID and EVAP_BASE

Document: AQS-DUTY-060 Rev A. Date 2026-10-15. Generated values from `flow_graph/param/evap_design.py` (X-MFG-30). Study. Not a PE stamp.

## 1. Basis
Owner decision 2026-10-15: no bought skid; evaporators are designed and built in-house to an open design. Single-effect mechanical vapour recompression, falling film inside vertical tubes, condensing compressed vapour on the shell side, at atmospheric body pressure.
- Boiling: 20 wt% HCl at the azeotrope temperature 108.6 C (PERRY9_HCL, bounding); 20 wt% NaOH at 108.0 C (BPE 8 K, McCabe Duhring lines, MCCABE7_DUHRING).
- Saturation pressures from IAPWS-IF97 region 4; latent heat 2257 kJ/kg (IAPWS_IF97).
- Blower: ideal-gas isentropic work, k 1.33, efficiency 0.70 (PERRY9_PUMP), motor 0.90 (A-M-106).
- Falling film U 1500 W/(m2 K) at 6 K driving difference (PERRY9_EVAP; A-M-106); minimum wetting rate 0.05 kg/(m s) sets the recirculation (PERRY9_EVAP).
- Interchanger: feed (35 C, A-M-106) against condensate and product, counter-current, 10 K approach, U 2000 W/(m2 K) (PERRY9_EVAP, INCROPERA7).
- Relief sized in-house: body fire case Q = 21000 F A^0.82 Btu/h (ISO 23251 / API 521) at 21 % overpressure; steam shell blocked outlet at 120 % of design blower flow, 10 % overpressure; areas by API 520 Part I gas equation (ISO 4126-1 valve). Body design 100 kPa g and full vacuum; shell 350 kPa g (A-M-107).

## 2. Results

| Quantity | EVAP_ACID | EVAP_BASE |
|---|---|---|
| T_boil_C | 108.6 | 108.0 |
| T_cond_C | 114.6 | 114.0 |
| p_body_kPa | 101.325 | 101.325 |
| p_shell_kPa | 166.98 | 163.73 |
| ratio | 1.648 | 1.616 |
| water_kg_h | 33.493 | 33.3 |
| duty_kW | 21.0 | 20.88 |
| w_kJ_kg | 93.7 | 89.6 |
| comp_shaft_kW | 1.245 | 1.185 |
| comp_elec_kW | 1.384 | 1.316 |
| pump_kW | 0.008 | 0.008 |
| trim_kW | 0.0 | 0.0 |
| total_kW | 1.391 | 1.324 |
| kWh_per_t | 41.5 | 39.8 |
| A_ff_m2 | 2.33 | 2.32 |
| tubes | 20 | 20 |
| tube_id_mm | 25.0 | 25.0 |
| tube_L_mm | 1500.0 | 1500.0 |
| recirc_kg_h | 282.7 | 282.7 |
| shell_D_mm | 350 | 350 |
| height_mm | 3100 | 3100 |
| ix_Q_kW | 3.52 | 3.67 |
| ix_A_m2 | 0.15 | 0.146 |
| T_feed_preheat_C | 98.6 | 98.0 |
| T_out_C | 48.7 | 50.6 |

Power is 41.5 and 39.8 kWh per tonne of water against the 72 kWh/t published upper bound previously used (VOGELBUSCH_MVR); the graph now carries the design values (1.391 and 1.324 kW). Compressor work exceeds the feed-to-boiling deficit, so no trim heater is needed in steady state; the surplus leaves as condensate subcooling and through SQ (start-up heat is a separate electric heater, not a continuous load).

## 3. Relief

| Case | Unit | W kg/h | P1 kPa abs | A required mm2 | Valve |
|---|---|---|---|---|---|
| Body fire | EVAP_ACID | 41.32 | 222.3 | 34.0 | API 526 D (71 mm2), adequate |
| Shell blocked outlet | EVAP_ACID | 40.19 | 486.3 | 15.465 | API 526 D, adequate |
| Body fire | EVAP_BASE | 41.32 | 222.3 | 33.98 | API 526 D, adequate |
| Shell blocked outlet | EVAP_BASE | 39.96 | 486.3 | 15.376 | API 526 D, adequate |

## 4. Outlet temperatures (X-MAT-20)
Product and condensate leave the interchanger at 48.7 C (acid) and 50.6 C (base), below the 60 C limit of line class P1 (AQS-STD-002). IA-EVAP_ACID-COND and IA-EVAP_BASE-COND stay P1; IA-ACID-01 stays P2 (hot leach liquor service into LEACH_CSTR_1); IA-BASE-01 and IA-BASE-PPT are P1 at 50.6 C. Edge params T_C carry these values.

## 5. Materials
Acid: impregnated graphite tubes, tubesheets and interchanger; PTFE-lined steel shell and separator; PVDF piping (PERRY9_MAT, ULLMANN_HCL). Base: nickel 200 tubes, shell and interchanger (PERRY9_MAT). Fasteners outside the wetted zone ISO 3506 A4-70 (acid) or ISO 898-1 8.8 (base).

## 6. Manufacturing
Model `models/mfg/evap_mvr.py` (CadQuery, reads params.design) exports `models/mfg/EVAP_*/export/*.step|stl` (watertight; three bodies: shell assembly, tube bundle bores, blower and interchanger frame). BOM `models/mfg/EVAP_*/bom.csv`, fasteners `fasteners.csv`. Production route `docs-authority/fab/EVAP_*.md` in MFG/FAB.

## 7. Open items
1. HCl in the acid vapour. At 20 wt% in a well-mixed recirculating film the vapour approaches the liquid composition near the azeotrope, so the condensate to BMED_ACID would carry HCl. Partial-pressure data (Perry sec. 2 HCl-water tables) are needed to quantify it; options are a short rectifying section on the vapour, or two-stage operation with the final stage once-through. Owner review.
2. Blower and pump are in-house designs (X-MFG-32); the efficiencies above are the design targets.
