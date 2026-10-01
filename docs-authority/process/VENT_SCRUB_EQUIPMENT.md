# Vent / scrub / regenerator equipment stubs

Document number: AQS-EQP-VENT-001  
Revision: A  
Date: 2026-09-28  
Authority: AQS-VENT-001, AQS-GAS-002 / AQS-GAS-003, AQS-CRY-002,
AQS-MFG-MET-001, FLOW_BATTERY.md, AQS-STR-001 S64–S72.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: scrub/regen + CRYO KO stubs for vent closure | 2026-09-28 |

Licence: CERN-OHL-S-2.0. Duties / Nm³/h / kW = **TBD**. Do not invent
nameplates. `SCALE_M = 1.0`.

## 1. Equipment tags

| Tag | Duty | Stream hooks | Status |
|---|---|---|---|
| ACID_POLISH_SCRUB | Post-ALK polish pack; lean BMED NaOH | S65 in; gas residual upset only | Stub |
| ACID_POLISH_REGEN | Blowdown / media regen → CRU | S66 / SCRUBBER_TO_CRU | Stub |
| ZNBR2_BR2_SCRUBBER | Existing Br₂ tower (FLOW_BATTERY) | Br₂ header | Issued massing |
| ZNBR2_BR2_REGEN | Hold + ORP + Br⁻ return to pos. tank | S69 | Stub |
| CRYO_AHU | CRYO room NFPA 2/55 AHU | S56 residual | Issued (AQS-EQP-CRY-001) |
| CRYO_AHU_COND | Condensate knockout / condensable return | S70 → COLD_BOX | Stub |
| MET_AHU | Dedicated MFG metal-aisle capture | S71 | Issued (AQS-EQP-MFG-MET-001) |
| MET_SCRUB | Fume / oil-mist scrub on MET_AHU train | S71 | Stub |
| MET_SCRUB_REGEN | Liquor / media regen toward returns | S72 | Stub |
| FLUE_CAP | AFTERBURNER → CRYO CO₂ / condensate KO | S67 / S18; S68 | Claimed |

## 2. Separation rules

1. Acid polish liquor → CRU only — no Br⁻, no organics, no NH₃.
2. Br₂ regen liquor → ZnBr2 positive tank only — never CRU.
3. CRYO_AHU_COND returns condensables to COLD_BOX — never HAB return.
4. MET_SCRUB fines → CSTR (S19 class); organic mist → OIL / HDR_ORG;
   do not tee metal fume into HDR_ACID_GAS as primary.
5. H₂ is not scrubbed wet (AQS-GAS-002 §5) — path is dryer → CRYO_H2.

## 3. FreeCAD

No new solids this pass. Optional later: attach stubs beside
`gas_handling.py` ALK_SCRUBBER, `cryo.py` CRYO_AHU, `mfg_shop.py`
MET_AHU, ZnBr2 scrubber. **plant.FCStd rebuild optional / note only.**

## 4. Regenerate related PFDs

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 mass_flow_pfd.py
python3 cryo_pfd.py
python3 metal_forming_pfd.py
python3 znbr2_flow_pfd.py
python3 oil_line_pfd.py
```
