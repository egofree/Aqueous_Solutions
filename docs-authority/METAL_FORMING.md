# Metal forming path — wire draw / cold mill / gas atomizer

Document number: AQS-MFG-MET-001  
Revision: B  
Date: 2026-09-28  
PFD: AQS-PFD-MFG-MET-001 (`metal_forming_pfd.png`)  
Equipment: AQS-EQP-MFG-MET-001  
Streams: AQS-STR-001 **S57–S63** / **S71–S72** (AQS-VENT-001)

Authority: `MANUFACTURING/Manufacturing_Overview.md` (MetalFab Mermaid),
root `04-structural-metal-manufacturing.md` (thermal / powder narrative),
AQS-EQP-MFG-001 (shop envelope; metals massing), `freecad/mfg_shop.py`,
`freecad/wet_products.py` (`PROD_METALS`, `MELT` stub), AQS-STR-001 /
AQS-MF-001, AQS-HSE-001, AQS-GAP-001 §2 / §7 item 6, hub `ELECTRICAL.md`
(induction coil = electric Present), AQS-VENT-001 (MET_AHU scrub closure).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: wire-draw / cold-mill / atomizer path + HVAC/Q4 | 2026-09-28 |
| B | 1 | MET_SCRUB / S71–S72; no free outdoor dump (AQS-VENT-001) | 2026-09-28 |

Licence: CERN-OHL-S-2.0.

---

## 1. Scope

Closes AQS-GAP-001 §7 item 6 (**MFG metals forming kit**): promote the
legacy MetalFab nodes WireDraw / RollMill / PowderAtom from “out of M1
CAD massing” into a **named process path** with equipment list, PFD,
streams, and FreeCAD keep-out stubs inside `MFG_SHOP`.

| In scope | Out of scope this pass |
|---|---|
| Wire draw, 4HI cold mill, gas atomizer topology | Invented kW / kg/h / m/min nameplates |
| Feedstock from PROD_METALS / MET_MELT (induction electric) | Full plant.FCStd rebuild |
| Products: wire, sheet, powder; scrap → S16 / leach | Electrode coating line detail (RuO₂/IrO₂) |
| Dedicated process-aisle AHU; Q4 via named HX only | Textiles / melt-blown / HEPA media line |
| Distinction MET_MELT ≠ INDUCTION_PYROLYZER | SCALE_M change / git commit |
| Streams S57–S63 | Dock / yard geometry; compliance rewrite |

**NOTE**

`SCALE_M` stays **1.0**. Legacy Manufacturing_Overview figures (SuperbMelt
“35 kW”, Stanat/Fenn “5–8 kW”, “20–30 kW MFG allocation”) are **study
narrative only** — cite for topology, do not issue as M1 nameplates.
Duties = **TBD**.

---

## 2. Decisions (locked this pass)

### 2.1 Path topology

```
PROD_METALS / S08 crib
        │
        ▼
   MET_MELT  (induction electric metal melt — ≠ INDUCTION_PYROLYZER)
        │  S57 billet / melt / charge
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
   WIRE_DRAW      COLD_MILL     GAS_ATOMIZER
        │              │              │
     S58 wire       S59 sheet      S60 powder
        │              │              │
        └──────► MFG_CRIB / electrodes / RepRap / FAB charge
                      │
                   S61 swarf / trim → HOPPER (S16 class) / leach
```

Legacy Mermaid: `Smelt → WireDraw & RollMill & PowderAtom → Electrodes &
MetalProducts`. That topology is retained; equipment tags use locked
`_` names per AQS-SYS naming.

### 2.2 MET_MELT ≠ INDUCTION_PYROLYZER

| Tag | Duty | Energy | Feed | Location |
|---|---|---|---|---|
| **MET_MELT** | Structural / electrode metal melt → billet / charge for draw / roll / atomize | **Electric induction** (Present) | PROD_METALS / S08 metals | L0 `MFG_SHOP` |
| **INDUCTION_PYROLYZER** | Plastic / organics depolymerization on **oil line** | Electric induction coil (Present) | Sorted polymer (HDR_ORG) — **never FR-4** | L-1 oil aisle (`oil_line.py`) |

**CAUTION**

Do not route polymer scrap into MET_MELT. Do not treat MET_MELT as the
oil-line pyrolyzer. Combustion / oil-gas firing for metal melt is **not**
the M1 selection — electric induction only (matches `ELECTRICAL.md`
induction Present; avoids inventing a fuel header).

### 2.3 Units issued

| Tag | Role |
|---|---|
| `MET_MELT` | Induction metal melt pot / furnace envelope |
| `WIRE_DRAW` | Wire drawing (Cu / Al / Fe class 0.5–5 mm intent — size TBD) |
| `COLD_MILL` | 4HI reversing cold rolling mill (sheet 0.1–9 mm class intent — TBD) |
| `GAS_ATOMIZER` | Inert-gas atomizer → metal powder for RepRap / sinter / FAB charge |
| `MET_WIRE_BIN` | Wire product hold |
| `MET_SHEET_BIN` | Sheet / strip product hold |
| `MET_POWDER_CRIB` | Powder product hold (dry; N₂ blanketed) |
| `MET_N2_BLANKET` | Inert blanketing / atomizer gas from S03 (N₂); Ar = vendor option |
| `MET_AHU` / `MET_SCRUB` | **Dedicated** MFG metal-aisle capture → scrub/baghouse (AQS-VENT-001) |
| `MET_HX_Q4` | Low-grade coolant / quench residual → Q4 water only |
| `ELECTRODE_FAB` | Stub — 316L / Ti electrode prep (Partial; coating deferred) |

### 2.4 HVAC / heat rejection

| Destination | Tag / stream | What | Forbidden |
|---|---|---|---|
| **Dedicated process AHU** | `MET_AHU` → **S71** MET_SCRUB / BH | Metal-aisle capture (fume / oil mist / N₂ dilution) → scrub/baghouse; **S72** returns | Shared return with HAB / FARM; acid-gas header as primary; free outdoor dump |
| **Q4** (life HVAC water) | `MET_HX_Q4` → **S63** | Recoverable warm residual from mill / draw coolants or quench that can meet **< 80 °C** water class (peer to S06 / S44 / S53 / S54) | Atomizer hot gas as flue into life air; melt off-gas untreated |

**WARNING**

Never share `MET_AHU` return with HAB / FARM. Free outdoor dump is not the design end state (AQS-VENT-001). Never put melt / atomizer
hot gas into Q4 as flue. Q4 remains water-only into life air.

### 2.5 Feedstock and products (qualitative)

| Item | Source / sink |
|---|---|
| Feedstock | Electrowon / polished metals from `PROD_METALS` (S08 class); scrap remelt from S61 when chemistry allows |
| Wire | Cabling, fasteners, electrode wire stock (S58) |
| Sheet / strip | Structural panels, tank skins, electrode blanks (S59) |
| Powder | RepRap / sinter / FAB charge / powder-metallurgy (S60) |
| Scrap / swarf / trim | S61 → HOPPER (S16) or leach — **no FR-4**; no pyro |

### 2.6 Utilities

| Utility | Intent |
|---|---|
| Electric | Module AC / induction coil — load on S17 / S20; kW **TBD** |
| N₂ blanketing / atomize | S03 branch via `MET_N2_BLANKET`; Ar optional |
| Cooling water | Closed loop → `MET_HX_Q4` when residual qualifies for Q4; else dedicated cool (do not invent UPW dump) |
| Compressed air | Shop air for actuators only — not atomizer primary gas |

---

## 3. Placement — L0 MFG_SHOP

| Tag | Placement intent |
|---|---|
| Forming train | Inside `MFG_SHOP` / `MFG_FLOOR` cassette bay on L0 (`MFG_X/Y/Z`) |
| `MET_MELT` | Adjacent to crib / PROD_METALS handoff; keep-out from polymer line |
| `WIRE_DRAW` / `COLD_MILL` / `GAS_ATOMIZER` | Downstream of melt along floor +X |
| `MET_AHU` / `MET_SCRUB` | On metal aisle; scrub/BH before any residual vent — not through HAB |
| `MET_HX_Q4` | On Q4 water header with GEO_HP / FC_HX / CRYO_HX peers |

Full `plant.FCStd` rebuild is **required** before these envelopes appear
in the assembled plant model — stub only this pass.

---

## 4. Streams (qualitative)

| ID | From | To | Ph | Carries | Notes |
|---|---|---|---|---|---|
| S57 | PROD_METALS / MET_MELT | WIRE_DRAW / COLD_MILL / GAS_ATOMIZER | S/L | billet / melt / charge | Branch of S08; not polymer |
| S58 | WIRE_DRAW | MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB | S | wire product | Size class TBD |
| S59 | COLD_MILL | MET_SHEET_BIN / MFG_CRIB | S | sheet / strip | Gauge TBD |
| S60 | GAS_ATOMIZER | MET_POWDER_CRIB / FAB / RepRap | S | metal powder | N₂/Ar atomize; dry hold |
| S61 | Forming train swarf / trim | HOPPER / leach | S | metal scrap | S16 class; no FR-4; no pyro |
| S62 / S71 | MET_AHU → MET_SCRUB / BH | scrub train | G | aisle capture | Never HAB return; not free dump |
| S72 | MET_SCRUB / BH | CSTR / OIL / ORG | L/S | fines + liquor returns | sewer-as-primary |
| S63 | MET_HX_Q4 | Q4 / FARM / HAB | E | heat < 80 °C | Same Q4 rule as S06 / S44 / S53 / S54 |

---

## 5. Hazards (summary)

1. Induction melt: burn / splash / EMF; LOTO on coil supply
   (29 CFR 1910.147 / 1910.333).
2. Wire draw / cold mill: pinch / crush / noise — machine guarding
   (1910.212 / 1910.95); same family as shredder discipline.
3. Gas atomizer: pressurized inert gas + hot metal spray — keep-out;
   powder explosion / fire risk for reactive metals (Al / Ti class) —
   inert hold, grounding, no open ignition sources.
4. Metal dust / fume → `MET_AHU` → `MET_SCRUB` / baghouse (S71–S72); do not rely on hab AHU; no free outdoor dump (AQS-VENT-001).
5. FR-4 and polymer never enter MET_MELT or the forming train
   (same FR-4 rule as pyro).
6. N₂ asphyxiation in blanketed bins — O₂ deficiency monitors where
   hold volumes warrant (shop practice).

---

## 6. Relationship to existing MFG / wet path

| Existing | Relationship |
|---|---|
| AQS-EQP-MFG-001 / AQS-PFD-MFG-001 | Shop envelope + polymer + CNC massing; this doc is the **metals forming detail sheet** |
| `PROD_METALS` / `MELT` (`wet_products.py`) | Upstream crib / melt stub — MET_MELT is the issued shop-side melt tag |
| Oil-line `INDUCTION_PYROLYZER` | Separate chemistry; electric but organics only |
| Glass line MILL | Silicate mill — not COLD_MILL |
| Electrode fab (legacy) | `ELECTRODE_FAB` stub only; coating chemistry deferred |

---

## 7. Rebuild / sync

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 metal_forming_pfd.py
python3 mfg_shop_pfd.py          # pointer callout if regenerated
```

Optional FreeCAD envelope only (no full plant rebuild this pass):

```bash
# edit cad/freecad/mfg_shop.py stubs (MET_*), then:
# /usr/bin/freecadcmd cad/freecad/mfg_shop.py
# Full plant.FCStd rebuild REQUIRED before stubs appear in plant.
```

Share mirror: `share/aqueous-solutions/docs-authority/`,
`docs-authority/process/`, `pfd/scripts/`, `pfd/images/`,
`models/freecad/mfg_shop.py`.
