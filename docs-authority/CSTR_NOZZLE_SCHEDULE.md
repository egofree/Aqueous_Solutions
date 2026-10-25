# Nozzle schedule for leach tank CSTR 1

Document number: AQS-NZ-001  
Revision: C  
Date: 2026-10-24  
Measurement: metric

| Rev | Change | Date |
|---|---|---|
| — | Basic issue | 2026-09-27 |
| A | GF Type 546 / 546 Pro article numbers (family only) | 2026-09-27 |
| B | N1–N12 locked. Vented PVC-C FKM article numbers from GF 546 Pro V ASTM list | 2026-09-27 |
| C | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions. Nozzles, positions and article numbers unchanged. | 2026-10-24 |

## 1. Purpose and scope

`LEACH_CSTR_1` is the first stirred leach tank of the wet line. This page fixes each of its nozzles, N1 to N12: service, size, face, position and the isolation valve fitted. It also fixes the valve article numbers used on the material take-off. Valves on other equipment are out of scope, apart from a note on the electrowinning harvest valves.

## 2. Terms

- Nozzle: a connection through the tank wall, floor or lid.
- DN: nominal diameter in millimetres; "Inch" is the matching nominal pipe size and d the outside diameter of the pipe.
- Vented ball valve: a ball valve whose ball is drilled to relieve gas trapped in the closed cavity, needed where hypochlorite or Salria liquor gives off gas.
- FKM: fluoroelastomer seal material; older GF lists use the ISO 1629 code for it.
- NPT: American taper pipe thread (ASME B1.20.1).
- Material take-off (MTO): the list of parts and quantities taken from the drawings for purchase.
- `WALL`, `L`, `W`, `CSTR_H`, `DROP_X` and the other capitals in the position columns are parameters in `models/freecad/params.py`.

Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Materials

Wall: CPVC sheet 16 mm with three FRP belts (AQS-DUTY-050; 12 mm superseded), floor 16 mm, per AQS-STD-002 Rev F (liquor 70–85 °C exceeds PVC-U; the 316L on the duty is withdrawn). HX-5 is a borosilicate glass 3.3 coil, 4.22 m² (AQS-DUTY-049 natural-convection case, 7.941 kW rated), two concentric helices of 25 × 3 mm tube, 53.7 m, on PTFE pads, entering through CPVC stubs at N6a/N6b with FKM gaskets (AQS-STD-002 section 3.3); the Q3 metal piping ends at a dielectric isolating flange outside the tank.
Not PP, not 316L, not Ti. Cement: Weld-On 724 family on CPVC.

Oxidiser isolation valves are vented-ball PVC-C with FKM seals, because hypochlorite and Salria liquor give off gas. Non-vented balls are not allowed on N4, N5, N8, N9 or N12.

## 4. Valve article numbers

The material take-off uses GF Type 546 Pro V: PVC-C body, PTFE seats, FKM O-rings, ASTM solvent-cement sockets with two NPT union ends, vented ball. The codes are from GF datasheet 2126007 (2026-06) (Table 4.1).

Table 4.1. Valve article numbers

| DN | Inch | d (mm) | 546 Pro V PVC-C ASTM FKM | Earlier 546 CPVC FKM vented |
|---|---|---|---|---|
| 15 | 1/2 | 20 | 163 546 352V | V163 546 352 |
| 20 | 3/4 | 25 | 163 546 353V | V163 546 353 |
| 25 | 1 | 32 | 163 546 354V | V163 546 354 |
| 32 | 1-1/4 | 40 | 163 546 355V | V163 546 355 |
| 40 | 1-1/2 | 50 | 163 546 356V | V163 546 356 |
| 50 | 2 | 63 | 163 546 357V | V163 546 357 |
| 80 | 3 | 90 | 163 546 359V | V163 546 359 |

The 546 Pro non-vented PVC-C ASTM FKM valves, 163 546 353 to 163 546 359 in the same size order, are for utility water and the heat exchanger only, never Salria.

Codes move between the 546 and 546 Pro ranges. Check the current GF list against Table 4.1 before ordering. If the GF lead time is too long, the alternative harvest valve is the Spears true-union valve model "TU 2000", 2 in, CPVC with FKM seals and a vented ball.

## 5. Nozzles N1 to N12

The origin is the bottom corner of the leach tank on its outer south-west side. Z is measured above the inner floor unless noted. The valve column is empty when the nozzle is a flanged stub only (Table 5.1).

Table 5.1. Nozzles

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

N7 is the weir. It stays in this table so that the tag list N1 to N12 matches the tank faces. The electrowinning harvest valves are not tank nozzles: they are 163 546 357V × 9 on the funnel cells (see `mfg_ew_fitout.scad`).
