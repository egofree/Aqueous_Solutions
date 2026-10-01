# MFG shop equipment list

Document number: AQS-EQP-MFG-001  
Revision: C  
Date: 2026-09-28  
PFD: AQS-PFD-MFG-001 (`mfg_shop_pfd.png`)

Authority: `MANUFACTURING/Manufacturing_Overview.md`, Precious Plastic kit
(link-only — `DEPENDENCIES.md`), `freecad/mfg_shop.py`, AQS-STR-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Massing-level named machines | 2026-09-27 |
| B | 1 | Point metals forming to AQS-MFG-MET-001 / S57–S63 | 2026-09-28 |
| C | 2 | Blow mold **in MFG / in MVS** (Project decision 2026-10-01); electrode coat pointer | 2026-10-01 |
| D | 3 | ST-BLOW-01 duty 0.5 kW_e avg / 2–4 peak; industrial 14–28 kW avg forbidden as M1 continuous | 2026-10-01 |

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
(`metal_forming_pfd.png`); streams S57–S63. Twin-screw extruder remains out of M1 CAD massing unless issued later.
**Blow mold / shoe mold:** **required for MVS** (Project decision 2026-10-01) — seed
`BLOW_MOLD` + AQS-BOM-SC-001 Rev D; Present FreeCAD open → **ST-BLOW-01**.
Electrode coating: AQS-MFG-ELC-001 / `ELECTRODE_COAT` → **ST-ELC-01**.
Sandbox tracks progress; gaps are open studies, not accepted endpoints.

## 3.1 Blow mold (Rev C — in MVS)

| Tag | Duty | Status |
|---|---|---|
| BLOW_MOLD | Extrusion-blow / shoe-mold class articles from polymer melt | Study duty **0.5 kW_e** avg (ST-BLOW-01); Present CAD external |
| Upstream | EXTRUSION / oil-cut polymer | AQS-EQP-MFG-001 polymer line |
| If sandbox-off | Solver flags **open study** ST-BLOW-01 (not accepted unreclaimed endpoint) | AQS-BOM-SC-001 Rev D; AQS-EQP-STUDY-001 §7.1 |

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
