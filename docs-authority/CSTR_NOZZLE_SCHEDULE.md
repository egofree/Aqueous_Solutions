# LEACH CSTR 1 nozzle schedule

Document number: AQS-NZ-001  
Revision: B  
Date: 2026-09-27  
Measurement: metric

| Rev | Change | Date |
|---|---|---|
| — | Basic issue | 2026-09-27 |
| A | GF Type 546 / 546 Pro article numbers (family only) | 2026-09-27 |
| B | N1–N12 locked. Vented PVC-C FKM SKUs from GF 546 Pro V ASTM list | 2026-09-27 |

Wall: PVC-U sheet 12 mm, floor 16 mm, per AQS-STD-002 M2 (2026-10-15; was CPVC; the 316L on the duty is withdrawn). Above 60 °C: CPVC. The HX-5 Q3 ports at 95 °C are PVDF per AQS-STD-002 section 3.2.
Not PP, not 316L, not Ti. Cement: Weld-On 724 family on CPVC.

Oxidizer isolation valves are **vented-ball PVC-C FKM** (hypochlorite /
Salria out-gassing). Non-vented balls are forbidden on N4, N5, N8, N9,
N12.

## Article-number lock

Generation used on the MTO: **Type 546 Pro V**, PVC-C body, PTFE seats,
FKM O-rings, ASTM solvent-cement sockets + two NPT union ends, vented
ball. Codes from GF datasheet 2126007 (2026-06).

| DN | Inch | d (mm) | 546 Pro V PVC-C ASTM FKM | Legacy 546 CPVC FPM vented |
|---|---|---|---|---|
| 15 | 1/2 | 20 | 163 546 352V | V163 546 352 |
| 20 | 3/4 | 25 | 163 546 353V | V163 546 353 |
| 25 | 1 | 32 | 163 546 354V | V163 546 354 |
| 32 | 1-1/4 | 40 | 163 546 355V | V163 546 355 |
| 40 | 1-1/2 | 50 | 163 546 356V | V163 546 356 |
| 50 | 2 | 63 | 163 546 357V | V163 546 357 |
| 80 | 3 | 90 | 163 546 359V | V163 546 359 |

546 Pro non-vented PVC-C ASTM FKM (utility water / HX only, never
Salria): 163 546 353 … 163 546 359, same size column.

Codes move between 546 and 546 Pro. Confirm the current GF list against
this table before a PO. Alternate harvest valve if GF lead time is
bad: Spears TU 2000 2 in CPVC FKM, vented ball.

## N1–N12

Origin: leach outer SW bottom corner. Z is above inner floor unless
noted. Valve column is empty when the nozzle is a flanged stub only.

| Tag | Service | DN | Face | X mm | Y mm | Z mm | Valve article | Notes |
|---|---|---|---|---|---|---|---|---|
| N1 | Feed drop coaming | 400×250 slot | lid | WALL+DROP_X | WALL+(W−DROP_W)/2 | CSTR_H | — | No valve. Shredder dumps here. No screen. |
| N2 | Mixer stuffing box | 50 | lid | WALL+0.55 L | WALL+0.55 W | CSTR_H | 163 546 357V | Shaft seal, not a process isolator. |
| N3 | HDR_ACID_GAS | 80 | lid | WALL+0.80 L | WALL+0.20 W | CSTR_H | — | CPVC flange to demister. Induced draft. |
| N4 | LEACHATE PUMP / strainer | 80 | −X | 0 | WALL+PUMP_Y | PUMP_Z | 163 546 359V | Mag-drive PVDF. Basket 3–6 mm. To EW-1 only. |
| N5 | REGEN LEACH in | 40 | +Y | WALL+0.20 L | W+2 WALL | 900 | 163 546 356V | From REGEN LEACH / BMED salt side. |
| N6a | HX-5 supply (Q3) | 25 | −Y | WALL+0.70 L | 0 | 300 | 163 546 354 | Non-vented. Jacket water, not Salria. |
| N6b | HX-5 return | 25 | −Y | WALL+0.70 L | 0 | 1100 | 163 546 354 | Pair with N6a. |
| N7 | Weir spout | 450 wide | +X | L+2 WALL | WALL+(W−WEIR_W)/2 | WEIR_CREST | — | CSTR 2. Not a valved nozzle. |
| N8a | FLOAT DEWATER return | 40 | +X | L+2 WALL | WALL+(W−WEIR_W)/2 | 200 | 163 546 356V | Liquor only, back to CSTR 1. |
| N8b | SINK DEWATER return | 40 | +X | L+2 WALL | WALL+AUGER_OFFSET_Y | 200 | 163 546 356V | Pair with N8a. |
| N9 | Drain | 50 | floor | WALL+80 | WALL+80 | 0 | 163 546 357V | To CRU / REGEN LEACH. Not sewer. |
| N10 | ORP / T thermowell | 20 | +Y | WALL+0.40 L | W+2 WALL | 700 | — | PVDF well. No ball valve. |
| N11 | Level well | 20 | +Y | WALL+0.40 L | W+2 WALL | 200 | — | PVDF well. |
| N12 | Spare / sample | 40 | −Y | WALL+0.15 L | 0 | 700 | 163 546 356V | Capped. Vented ball on the cap spool. |

N7 is the weir. It stays on this sheet so the twelve-tag list matches
the tank faces. EW harvest valves are not CSTR nozzles; they are
163 546 357V × 9 on the funnel cells (see `mfg_ew_fitout.scad`).
