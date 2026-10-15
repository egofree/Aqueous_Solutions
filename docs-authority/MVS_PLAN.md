# MVS completion plan

Superseded by `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). This page is kept as history; open work is tracked there only.

Document: AQS-MVS-PLAN-001
Date: 2026-10-02
Graph on main is the topology. This plan finishes the equipment set. Not a PE stamp.

## 1. Issue the missing node

Add WS_PHOS. Phosphoric acid etch. Separate bund from HF. Stream S34 already names it. No new chemistry.

## 2. Build the EW aisle solids

Run models/freecad/ew_cascade_present.py on the operator box. It writes ew_cascade.FCStd. Do not open plant.FCStd. Confirm EW-1 through EW-9 at 750 mm pitch, then stop.

## 3. Close the seven machine studies, one at a time

Each pass issues a solid, a nozzle list, and a power number from the study band. No vendor line that exceeds the band.

| Order | Unit | Pass |
|---|---|---|
| 1 | GLASS_RINSE, GLASS_MILL, GLASS_BURNOUT | Rinse, drain, mill, burnout, then the existing digest. Burnout off-gas to the oil-vapor header. |
| 2 | VCD_TRAIN | Pick a compressor inside 14–20 kWh/m³ at 0.11 m³/d. Issue the equipment ID. |
| 3 | REMIN | Dose from the hydroxide crib. 10 L/d, 25 mg/L Ca, 10 mg/L Mg. UV after dose. |
| 4 | LITHO_STUB | Three children: coat, align, develop. Lock starts/day in the 1–5 band. Pick the UV lamp class. |
| 5 | ELECTRODE_COAT | Carbon or nickel booth. Exhaust to MET_AHU. DSA stays out. |
| 6 | BLOW_MOLD | Clamp and air on the polymer line. Peak 2–4 kW. Scrap to the oil line. |
| 7 | SOLAR_PV_CELL | Texture, emitter, PSG etch, ARC, contact, fire, IV. KOH from WS_KOH. Not the yard array. |

GEO_ORC stays a reserved pad. No skid until the borehole survey shows surplus after Q4.

## 4. Size the ladder stores

One thermosyphon per step. Q1 oil or ceramic. Q4 water only.

For each of Q1_A…Q4_B issue volume, fluid, design temperature, and the relief device. Relief orifices get a calculation, not a placeholder. Q4 relief is water. Q1 relief is not a hab vent.

## 5. Assign the fab room

Pick an ISO 14644 class for the wet bench and the tool row. Write it on WAFER_FAB. Do not leave the family unnamed.

## 6. Placement pass

After the solids exist, run flow_to_cad.py. Apply only to a copy. plant.FCStd stays untouched. Study envelopes for the generator, fuel cell, and methanol skids get replaced by the issued sizes before that run.

## 7. Done test

MVS design is complete when every present node has a solid or a stated reason it is a header, WS_PHOS exists, the seven machines above are present, ladder relief is sized, and the fab class is written. loops_closed stays false until those solids are on the copy.
