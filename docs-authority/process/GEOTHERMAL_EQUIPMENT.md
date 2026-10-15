# Geothermal equipment list

Superseded copy. The current page is `docs-authority/GEOTHERMAL_EQUIPMENT.md`, C. This copy is history (AQS-REG-001).

Document number: AQS-EQP-GEO-001  
Revision: A  
Date: 2026-09-27  
PFD: AQS-PFD-GEO-001 (`geothermal_pfd.png`)  
Authority: AQS-PWR-001, `POWER/Power_System_overview.md`, AQS-SCALE-001,
`ELECTRICAL.md` (HVAC / Q4), AQS-STR-001 S43–S44 / S48.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with POWER gap close | 2026-09-27 |

Licence: CERN-OHL-S-2.0.

## 1. Locked unit tags

| Tag | Duty | Status |
|---|---|---|
| GEO_GHEX | Closed-loop vertical ground heat exchanger (bore field class) | Issued — site survey TBD |
| GEO_LOOP_PUMP | Circulation pump on S43 loop | Issued — rating TBD |
| GEO_HP | Water-source heat pump → Q4 (S44) | Issued — thermal path primary at M1 |
| GEO_ORC | Binary organic Rankine cycle electric stub | Stub — rating TBD |
| GEO_HDR | Yard stub header / keep-out to off-plate field | Massing |

## 2. Class and media

| Item | Spec intent |
|---|---|
| Loop fluid | Non-toxic inhibited water / glycol class; dedicated circuit |
| Bore field | Vertical closed-loop; count / depth TBD after conductivity test |
| Heat pump | Water-source; reject / absorb to Q4 only (< 80 °C into life air) |
| ORC working fluid | TBD (not Salria, not ZnBr2, not process Cl₂) |

## 3. Forbidden mixes

1. S43 loop fluid shall not enter HDR_UPW, CATCH, ROOF_TANK, or Salria.
2. GEO_ORC condenser heat may join Q4 only through a named HX — never
   raw ORC fluid into life headers.
3. Geothermal wells are not a process-water makeup source.

## 4. Ratings

| Quantity | Value | Source |
|---|---|---|
| Legacy campus electric claim | 100 kW baseload | `POWER/Power_System_overview.md` (narrative) |
| M1 electric claim this pass | **TBD** — ORC stub only | AQS-PWR-001 §2.1 |
| Heat-pump thermal | **TBD** | Do not invent kW |
| HVAC AC load context | 1.5 kW class | `ELECTRICAL.md` |


## Q4 peers (fuel cell + cryo)

`FC_HX_Q4` (AQS-EQP-FC-001 / S53) and `CRYO_HX_Q4` (AQS-EQP-CRY-001 /
S54) join the same Q4 water header as GEO_HP (S44) and S06. CRYO deep
reject stays on S55 (`CRYO_DED_COOL`) — not Q4. GEN exhaust (S46) never
enters Q4 or hab AHU.

## 5. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 geothermal_pfd.py
```
