# Phase F — farm / wafer fab / habitation / cryo envelopes

Document number: AQS-PHF-001  
Revision: A  
Date: 2026-09-27

These four blocks are **out of the recycling-line model set**. They
exist so the plant document has keep-outs and utility stubs. They are
not shop models.

**Subordinate to AQS-BLD-001** (`BUILDING_STACK.md`). Keep-out *sizes*
and utility columns in this table remain valid. Flat Z=0 origins below
are **interim** — CAD placements follow building levels (life L1,
process L-1, dock/fab/cryo/mfg/power L0, water L2, catch L-2).
See `cad/AUTHORITY.md`.

Locked names only. Do not invent unit ops inside the boxes.

| Object | Envelope mm (L × W × H) | Origin (plant) | Utilities from core | Returns to core |
|---|---|---|---|---|
| FARM | 12 000 × 8 000 × 4 500 | X=12 000, Y=8 000, Z=0 | UPW, CO2, N2, Q4 heat, struvite / NH4, chelates, LED DC | condensate, plant waste, O2 |
| WAFER_FAB | 8 000 × 6 000 × 4 000 | X=12 000, Y=−6 000, Z=0 | UPW (ED), Si, Al, Cu, Fe, HCl, NaOH, N2 | etchants + metals to leach |
| HABITATION | 8 000 × 6 000 × 3 200 | X=−8 000, Y=8 000, Z=0 | UPW, O2, food, HVAC | CO2, heat, human waste to core |
| CRYO | 4 000 × 3 000 × 3 000 | X=−6 000, Y=−4 000, Z=0 | Q1 reject + electric | H2, O2, N2, CO2 product |
| MFG_SHOP | 6 000 × 4 000 × 3 500 | X=2 000, Y=9 000, Z=0 | metals crib S08 | scrap S16 → HOPPER |

Rules:

1. No process header from the wet line enters these boxes except the
   named utilities.
2. HDR_ACID_GAS, HDR_H2, HDR_OIL_VAPOR, HDR_DUST stay on the recycle
   aisle.
3. Wafer-fab etchant return is a closed tote / pipe to REGEN LEACH,
   not a floor drain.
4. Cryo is the Stirling + distillation / PSA skid from the system
   summary. It does not share a cold box with the ZnBr2 Br2 tower.
5. Shop-level internals follow `cad/CAMPUS_PLAN.md` (AQS-CMP-001).
   Streams: `cad/STREAM_REGISTER.md`. Overview PFD: `campus_pfd.png`.
6. Fire areas and ratings: `cad/HAZARD_SEPARATION.md` (AQS-HSE-001).
   One roof is not one fire area. HABITATION does not share HVAC return
   with the recycle aisle.

Generator: `cad/freecad/campus.py`.
