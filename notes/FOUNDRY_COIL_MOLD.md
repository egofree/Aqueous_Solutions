# Coil turns and mold water flow

Document number: AQS-SIZE-FOUNDRY-DTL  
Revision: A  
Date: 2026-10-16  
Authority: notes/FOUNDRY_SIZING.md. Design assumptions. Not measured. Not a PE stamp.

## IND_MELT coil (25 kW, 2–3 kHz, 10 kg)

| Parameter | Value | Basis |
|-----------|-------|-------|
| Crucible ID | 110 mm | 10 kg steel, H/D ≈ 1.5 |
| Coil ID | 160 mm | Clearance for refractory |
| Coil height | 180 mm | Matches melt height |
| Tube | 10 mm OD copper, 1 mm wall, water passage | Standard small-furnace |
| Turns | 14 | Pitch ≈ 12 mm over 180 mm |
| Coil voltage | 400–600 V | Matched inverter |
| Coil current | 40–60 A | At 25 kW |
| Cooling water | 8–12 L/min | ΔT ≤ 15 °C on coil; ~2–3 kW coil loss |
| Insulation | Between turns + outer wrap | Standard |

Turns are series. Tap at turn 10 optional for lower-power hold. Exact turns confirmed when inverter voltage is fixed.

## VAC_IND coil (15 kW, 5–10 kHz, 2 kg ISM)

| Parameter | Value | Basis |
|-----------|-------|-------|
| Copper segment crucible ID | 60 mm | 2 kg Ti skull |
| Coil ID | 100 mm | Around segmented crucible |
| Coil height | 80 mm | Small pool |
| Tube | 8 mm OD copper | |
| Turns | 8 | Higher frequency, shorter coil |
| Cooling water | 6–10 L/min | Coil + segment cooling separate |
| Segment cooling | 10–15 L/min total | Skull heat to copper wall |

## CONT_CAST mold water (50–80 mm billet, 10 kg batch)

Heat to extract: ~0.3–0.4 kWh/kg in the mold (balance leaves in the strand).  
10 kg → 3–4 kWh → 11–14 MJ. Cast time ~8–12 min → average 15–30 kW into the mold.

| Parameter | Value | Basis |
|-----------|-------|-------|
| Mold | Water-cooled copper, horizontal, 60 mm nominal | Mid of 50–80 mm |
| Water passages | 4–6 longitudinal channels | |
| Design flow | 25 L/min | |
| ΔT design | 8–12 °C | |
| Heat capacity at 25 L/min, 10 °C | ~17 kW | Matches average extraction |
| Peak flow | 40 L/min | Short superheat spike |
| Inlet temperature | 20–30 °C | Closed loop to MET_HX or plant cooling |
| Outlet limit | ≤ 45 °C | Avoid boiling in channels |

Vacuum Ti variant: same mold principle, flow 15 L/min (smaller section, lower rate).

## Summary

- IND_MELT: 14 turns, 8–12 L/min coil water.  
- VAC_IND: 8 turns, 6–10 L/min coil + 10–15 L/min segment.  
- CONT_CAST mold: 25 L/min design, 40 L/min peak, ΔT 8–12 °C.

All assumptions. Confirm against inverter nameplate and a heat-balance test on the first article.
