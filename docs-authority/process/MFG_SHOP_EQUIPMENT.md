# MFG shop equipment list

Superseded copy. The current page is `docs-authority/MFG_SHOP_EQUIPMENT.md`, C. This copy is history (AQS-REG-001).

Document number: AQS-EQP-MFG-001  
Revision: B  
Date: 2026-09-28  
PFD: AQS-PFD-MFG-001 (`mfg_shop_pfd.png`)

Authority: `MANUFACTURING/Manufacturing_Overview.md`, Precious Plastic kit
(link-only — `DEPENDENCIES.md`), `freecad/mfg_shop.py`, AQS-STR-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Massing-level named machines | 2026-09-27 |
| B | 1 | Point metals forming to AQS-MFG-MET-001 / S57–S63 | 2026-09-28 |

## 1. Locked CAD units

| Tag | Duty |
|---|---|
| MFG_SHOP | Envelope on L0 |
| MFG_CRIB | S08 stock / fasteners |
| MFG_FLOOR | Cassette work floor |

## 2. Precious Plastic–class polymer line (named massing)

| Machine | Role |
|---|---|
| SHREDDER | Flake sorted plastic |
| WASH / DRY | Rinse; grey to HDR_GREY |
| EXTRUSION | Beam / sheet / filament option |
| INJECTION | Clamp-press parts |
| SHEETPRESS / COMPRESSION | Panels |

Upstream reference: [Precious Plastic](https://preciousplastic.com/) /
[ONEARMY/precious-plastic-kit](https://github.com/ONEARMY/precious-plastic-kit)
— **not bundled**.

## 3. Metals / precision (massing)

| Machine | Role |
|---|---|
| CNC / MILL | Lab-scale machining + RepRap FDM/SLA |
| WELD / ASSY | Join / fixture / pump housings |

**Metal forming (issued detail):** wire draw / cold mill / gas atomizer
path is now AQS-MFG-MET-001 / AQS-EQP-MFG-MET-001 / AQS-PFD-MFG-MET-001
(`metal_forming_pfd.png`); streams S57–S63. Twin-screw extruder and
blow mold remain out of M1 CAD massing unless issued later.

## 4. Streams

| ID | Role |
|---|---|
| S08 | Metals / silicate in |
| S16 | Scrap to HOPPER |
| S57–S63 | Metal forming (AQS-MFG-MET-001) |
| — | FR-4 never to INDUCTION PYROLYZER or MET_MELT |

## 5. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 mfg_shop_pfd.py
python3 metal_forming_pfd.py
```

## 6. Continuous kW requirements

See **AQS-REQ-KW-001**: polymer **1–3 kW_e** avg (SI-MFG-01); total MFG **8–20 kW_e** continuous class.
