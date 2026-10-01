# Life-header racks

Document number: AQS-PIP-002  
Revision: A  
Date: 2026-09-27

Wave 5. Process gas racks stay in `pipe_services.py` on the wet aisle
(Z = 2000 liquor / 2200 acid / 2400 H2 / 2600 dust). Life headers are
separate objects and separate elevations.

## Tiers (mm above grade)

| Z | Header | OD | Material | Forbidden tee |
|---|---|---|---|---|
| 900 | HDR_GREY | 50 | PP | Salria, etch |
| 1100 | HDR_UPW | 40 | PP-R / PVDF | leach, grey, etch |
| 1300 | HDR_ETCH | 32 | PVDF | sewer, HDR_GREY, farm beds |
| 2800 | HDR_O2 | 25 | 316 | HDR_H2, acid gas |
| 3000 | HDR_N2 | 25 | 316 | process headers |
| 3200 | HDR_CO2 | 40 | 316 | raw AFTERBURNER flue |

HDR_ORG is a tote / conveyor path, not a pipe on this rack.

## Spines

| Object | Run |
|---|---|
| RACK_LIFE_N | Y = 7800, X = −8000 → 24000 (HAB — MFG — FARM) |
| RACK_LIFE_S | Y = −2500, X = −6000 → 20000 (CRYO — FAB) |
| RACK_LIFE_W | X = −2000, Y = −4000 → 16000 |
| RACK_LIFE_E | X = 11800, Y = −6000 → 16000 (FAB — FARM) |

Generators: `cad/detail/mfg_life_rack.scad`, `freecad/pipe_services.py`.
Sheet: `life_headers_pfd.png`.
