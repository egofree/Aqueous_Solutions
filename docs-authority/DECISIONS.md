# Decisions — foam-board EW cascade

Date: 2026-09-27  
Source: user request, this file.  
Licence: CERN-OHL-S-2.0 (same as the plant pack).

| Decision | Value | Why |
|---|---|---|
| What | Small-scale EW CASCADE, EW-1…EW-9, funnel bottoms, overflow +X, CEM slot, bund | Locked plant names. Not a second chemistry. |
| Scale | 1:3 on plant `params` cell | Nine cells at 250 mm pitch = 2250 mm. Fits a 2438 mm (8 ft) sheet with end-wall leftover. |
| Sheet | 4 ft × 8 ft = 1219 × 2438 mm | User. Grain long axis = 8 ft. |
| Wall | 6 mm expanded PVC foam board (Sintra / Komatex / Celtec class) | Knife-cut, rigid enough at this span. 3 mm oil-cans. 10 mm is an alt in `params.py`. |
| Joint | Walls sit on the bottom panel. Fillet both sides. Funnel panels have 12 mm glue tabs. | Foam-board shop joint. No mitre saw required. |
| CEM slot | 6 mm (one sheet) | Plant slot is 10 mm; 3 mm at scale is not a knife cut. A 3–4 mm card drops in. |
| Valve | 16 mm hole + tube stub | Not a GF 546. |
| Duty | Wet Salria coupon at bench temperature. Expanded PVC foam-core board. | User: rigid PVC already holds Salria in test. This model is that coupon at 1:3, not the 70–85 °C plant wall. Plant wet wall stays solid CPVC sheet. |
| Units | mm on drawings. Sheet called 4×8 in the cut list. | Dual only on the sheet callout. |

Change scale or thickness in `params.py` / `params.scad` only, then rerun `generate.py`.
