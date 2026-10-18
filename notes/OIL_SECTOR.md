# OIL sector — finished design

Document number: AQS-DES-OIL  
Revision: A  
Date: 2026-10-16  
Authority: notes/oil_cuts.md, graph Rev V. Not a PE stamp.  
Rates are design assumptions for a 500 kg/day plant. Not measured.

## Purpose

Pyrolyze organic float and solvent waste. Fractionate. Send cuts to their consumers. No external solvent or grease. Char to the silicon line. Bottoms recycle.

## Units (sector OIL)

| Unit | Duty |
|------|------|
| HOPPER | Organic/scrap feed |
| OIL_DRYER | Dry feed before pyro |
| OIL_PYRO | Induction pyrolyzer, 400–600 °C. Oil vapor + NCG + char |
| OIL_FRAC | Atmospheric column. Side draws + bottoms |
| NCG_HEADER | C1–C4 non-condensables |
| AFTERBURNER | Burn NCG. CO₂ to cryo. Heat to Q1 |
| PROD_C5_C10 | Light cut tank |
| PROD_C11_C18 | Mid cut tank |
| PROD_C19_C28 | Heavy-mid / wax cut tank |
| PROD_C29 | Bottoms tank |
| C29_RECYCLE | Bottoms return to OIL_PYRO |

## Cut duties (from oil_cuts.md, confirmed)

| Cut | Consumer | Notes |
|-----|----------|-------|
| NCG (C1–C4) | AFTERBURNER, Q2 pilot | Not genset fuel |
| C5–C10 | POLY_OLEFIN (POLYMERS), fab solvent, shop washer | Aliphatic. Also the light-cut feed already edged to POLY_OLEFIN |
| C11–C18 | Afterburner pilot, Q2 oil burner, quench makeup | Liquid fuel |
| C19–C28 | Grease kettle (Ca soap from P-Ca). Shop grease | Not a second column |
| C29+ | Recycle to OIL_PYRO | |
| Char | Silicon arc / Si reduce | Not a column cut |
| Unrecovered wax | From FOUNDRY SHELL_BURNOUT | Already edged to OIL_FRAC |

## Rates (assumptions)

Basis: organic float and solvent waste from a 500 kg/day plant, plus fab/MFG solvent returns.

| Stream | Rate | Notes |
|--------|------|-------|
| Feed to OIL_DRYER | 15 kg/d | Mixed polyolefin float + solvent waste |
| Oil vapor to OIL_FRAC | 10 kg/d | ~65 % liquid yield |
| NCG | 2 kg/d | To AFTERBURNER |
| Char | 3 kg/d | To Si reduce |
| C5–C10 | 3 kg/d | 2 kg/d to POLY_OLEFIN; remainder solvent |
| C11–C18 | 3 kg/d | Fuel / quench |
| C19–C28 | 2 kg/d | Grease stock |
| C29+ recycle | 2 kg/d | Internal |

Yields are typical for mixed-plastic pyrolysis and are assumptions.

## Heat

- OIL_PYRO: induction primary (consistent with foundry heat policy).  
- AFTERBURNER flue → Q1 (edges present).  
- Column reboiler: existing HX-3 concept from oil_cuts.md.

## Interfaces

- In: GROW_BED organics, WET_BENCH / WAFER_FAB solvent, MET_SCRUB organic mist, FOUNDRY wax, MFG scrap to HOPPER.  
- Out: POLY_OLEFIN (light cut), AFTERBURNER, grease use, char to Si, CO₂ to cryo.

## Detail

Fatty-acid split, pyro profile, and column stages: notes/OIL_POLY_SIZE.md.  
Grease saponifiable fraction 40 % of C19–C28 (assumption).

- Exact pyro temperature profile and residence time.  
- Column stage count and reboiler duty.  
- Grease: both Ca and Li lines are baseline (graph Rev W). See notes/GREASE_LINES.md. Kettles GREASE_CA and GREASE_LI are on the graph.

## Graph

Rev V. Design rates above are the basis. Existing edges retained.

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
