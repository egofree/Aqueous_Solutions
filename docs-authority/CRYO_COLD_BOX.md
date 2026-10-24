# Cryogenic cold-box internals

Document number: AQS-CRY-002  
Revision: B  
Date: 2026-09-28  
PFD: AQS-PFD-CRY-001 (`cryo_pfd.png`)  
Equipment: AQS-EQP-CRY-001  
Streams: AQS-STR-001 S02–S05 / S18 / S24 / S45 / S49–S50 / **S54–S56** / **S64** / **S67** / **S70**

Authority: root `09-air-liquefaction-cryogenic.md` (ALCRM narrative),
`GAS_SYSTEM/Gas_System_overview.md`, AQS-EQP-CRY-001, AQS-BLD-001
(L-1 east of CORE; FB_CRYO_PROCESS), AQS-HSE-001 (NFPA 2/55; MAQ),
AQS-PHF-001, AQS-PWR-002 / AQS-FC-001 (CRYO_H2 consumers), AQS-EQP-GEO-001
(Q4 peer), `freecad/cryo.py`, AQS-GAP-001 §7 item 5.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: cold-box internals + HVAC/geo heat-rejection split | 2026-09-28 |
| B | 1 | Vent closure: S64 H₂ normal; S67 flue-cap; S70 AHU condensable (AQS-VENT-001) | 2026-09-28 |

Licence: CERN-OHL-S-2.0.

---

## 1. Purpose

Lock ALCRM cold-box internals, heat-rejection split, and H₂ normal path consistent with vent closure.

## 2. Scope

Closes the GAS_SYSTEM / AQS-GAP-001 §7 item 5 gap: promote doc 09 /
AQS-EQP-CRY-001 hardware from a keep-out envelope into a **named
internals schedule** with HVAC / geothermal heat-rejection hooks and
CRYO_H2 consumer branches (GEN + FC + vent).

| In scope | Out of scope this pass |
|---|---|
| Stirling 77–90 K cold-head + distillation / PSA train tags | Invented M1 kW / kg/hr / L/d nameplates |
| Intake: centrifugal + demister, mol sieves, HEPA | Full plant.FCStd rebuild |
| Compressors / expanders / reboiler–condenser | ZnBr2 Br₂ tower (separate outdoor skid) |
| Vacuum-jacketed product lines (schedule note) | Acid-gas / oil vapor into cold box |
| Receivers CRYO_H2 / O2 / N2 / CO2 + consumer draws | SCALE_M change / git commit |
| HVAC / Q4 / dedicated cooling / vent split (named HX) | Quantitative MAQ holdup (still AQS-HSE-001 §5) |

**NOTE**

`SCALE_M` stays **1.0**. Doc 09 column / reboiler / COP figures are
**legacy study narrative only** — cite for topology, do not issue as
M1 nameplates. Duties = **TBD** pending heat/mass balance.

---

## 3. Decisions (locked this pass)

### 2.1 Placement — L-1 east of CORE

| Item | Lock |
|---|---|
| Level | L-1 process basement (`Z_Lm1`); replicas `_B2…` if `BASEMENT_LEVELS > 1` |
| XY | East of CORE (`CRYO_X/Y` in `params.py`); opposite wet aisle |
| Fire | `FB_CRYO` / `FB_CRYO_PROCESS` **2 h**; **no process-air duct** through (AQS-BLD-001 / AQS-HSE-001) |
| Envelope | Campus `CRYO` keep-out 6 × 6 × 4 m; internals sit inside |

### 2.2 Separation (unchanged, restated)

1. **CRYO_H2 ≠ HDR_H2** — product hold / fuel only; HDR_H2 is the
   aisle capture header to dryer / SHAFT_H2.
2. Acid-gas, oil vapor, and ZnBr2 Br₂ **never** enter COLD_BOX.
3. S18 / **S67** flue-cap CO₂ is **Claimed** capture (AQS-VENT-001) — not
   raw AFTERBURNER into HDR_CO2; flue dump is not the end state.
4. No shared HVAC **return** between HAB / FARM and CRYO / process
   (AQS-HSE-001 §8).

### 2.3 CRYO_H2 consumers (sizing interface)

Hold shall be sized for concurrent draws (MAQ design cap remains
AQS-HSE-001 §5 — do not invent holdup kg):

| Consumer | Stream | Authority |
|---|---|---|
| BACKUP_GEN | S45 | AQS-PWR-002 / AQS-EQP-GEN-001 |
| FUEL_CELL (PEM) | S49 | AQS-FC-001 / AQS-EQP-FC-001 |
| H₂ dryer normal feed | S64 | AQS-VENT-001 Partial (closes continuous roof dump) |
| Roof vent contingency | S24 | AQS-VENT-001 emergency only — not design dump |

Oxidizer to FC = CRYO_O2 (S50). Branches to GEN and FC shall be
**separately isolated** with flame arrestors (AQS-HSE-001 §11).

### 2.4 Heat rejection — three destinations (named only)

| Destination | Tag / stream | What goes there | What does **not** |
|---|---|---|---|
| **Q4** (life HVAC water) | `CRYO_HX_Q4` → **S54** | Recoverable **warm** reject after pinch: compressor intercooler residual and mol-sieve TSA cool-down that can meet **< 80 °C** water class (peer to S06 / S44 / S53) | Stirling deep reject; cryogenic condenser boil-off; flue gas; GEN exhaust |
| **Dedicated cryo cooling** | `CRYO_DED_COOL` → **S55** | Closed utility loop for Stirling cold-head reject, deep condenser / expander heat that **cannot** enter life air | HDR_UPW, CATCH, Salria, hab AHU |
| **Vent / room exhaust** | `CRYO_AHU` → `CRYO_AHU_COND` → **S70** / **S56** | NFPA 2 / 55 AHU; **condensables return to COLD_BOX (S70)**; S56 = non-condensable contingency only — not continuous outdoor dump | Shared return with HAB / FARM; process acid-gas header |

**WARNING**

Never route Q1 flue, AFTERBURNER, or BACKUP_GEN exhaust (S46) through
`CRYO_HX_Q4` or life AHU. Q4 remains water-only into FARM / HAB.

### 2.5 Process scheme (topology)

```
Ambient air → AIR_INTAKE → MOL_SIEVE → HEPA_BANK ─┐
H2_DRYER (S05) ──────────────────────────────────┤→ COLD_BOX
S18 CO₂ claim (optional) ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
         │
         ├─ STIRLING_COLD_HEAD (77–90 K)
         ├─ DIST_COL_PRI / SEC / TER (+ PSA where issued)
         ├─ REBOILER_COND (column heat integration)
         ├─ COMP_EXPAND (VFD compressors + expanders)
         └─ VJ_LINES → CRYO_O2 / N2 / CO2 / H2 receivers
```

PSA may share the cold-box envelope where distillation is not the
sole path; do not invent a second outdoor gas plant.

---

## 4. Internals schedule (tags)

See AQS-EQP-CRY-001 Rev C for the full equipment table. Summary:

| Tag | Role |
|---|---|
| COLD_BOX | Parent envelope (Stirling + distillation / PSA) |
| AIR_INTAKE | Centrifugal + demister |
| MOL_SIEVE | CO₂ / H₂O drying (5Å TSA class) |
| HEPA_BANK | Final particulate polish |
| STIRLING_COLD_HEAD | Cryocooler 77–90 K |
| DIST_COL_PRI / SEC / TER | Cryogenic distillation train |
| REBOILER_COND | Reboiler / condenser heat integration |
| COMP_EXPAND | Variable-speed compressors + expanders |
| VJ_LINES | Vacuum-jacketed transfer (schedule; CAD stub optional) |
| CRYO_HX_Q4 | Named HX → Q4 (S54) |
| CRYO_DED_COOL | Dedicated utility cooling loop (S55) |
| CRYO_AHU / CRYO_AHU_COND | Room AHU + condensate KO (S56 / S70) |
| CRYO_H2 / O2 / N2 / CO2 | Product receivers |

---

## 5. HVAC / geothermal integration

### 4.1 CRYO room ventilation (NFPA 2 / 55)

| Requirement | Design intent |
|---|---|
| Mechanical ventilation | Dedicated `CRYO_AHU` serving CRYO fire area only |
| Discharge | Condensables → S70 COLD_BOX; residual S56 contingency; **not** HAB / FARM return; not continuous dump (AQS-VENT-001) |
| Detection | H₂ at **25% LFL** trip → isolate H₂ trains + freeze cold-box feed (AQS-HSE-001 §8) |
| Fire barrier | No process-atmosphere duct through `FB_CRYO_PROCESS` |
| Makeup | Outdoor air or listed energy recovery on **Q4 water** only — never process-air ERV into life |

### 4.2 Building HVAC + geothermal Q4

| Source | Stream | Role vs CRYO |
|---|---|---|
| Building HVAC | S06 | Q4 water into FARM / HAB — peer header |
| GEO_HP | S44 | Same Q4 header (AQS-PWR-002) |
| FC_HX_Q4 | S53 | Same Q4 header (AQS-FC-001) |
| **CRYO_HX_Q4** | **S54** | CRYO warm-reject contribution — **named HX only** |
| CRYO_DED_COOL | S55 | **Not** on Q4 — dedicated loop |
| CRYO room exhaust | S70 / S56 | Condensable return / residual contingency — not Q4 |

Geothermal remains the primary **building** Q4 thermal path at M1;
CRYO contributes only the warm residual that meets the Q4 temperature
class. Deep cryo heat stays on S55.

---

## 6. FreeCAD

`freecad/cryo.py` issues parent `COLD_BOX` + receiver solids and
**internal envelope stubs** (children listed in AQS-EQP-CRY-001).

**NOTE:** `plant.FCStd` rebuild is **required** before new child
envelopes appear in the assembled plant. This pass does **not**
rebuild `plant.FCStd` (prefer docs + PFD + authority first).

---

## 7. Remaining gaps

1. Quantitative cold-box / Stirling / column duties (kW, kg/hr) — TBD;
   doc 09 numbers are narrative only.
2. CRYO_H2 holdup kg under MAQ — TBD (AQS-HSE-001 §5 cap remains).
3. `plant.FCStd` rebuild to show child envelopes + any `_Bn` replicas.
4. Detailed VJ isometric / nozzle schedule — later piping pass.
5. Mol-sieve regen heat balance (how much residual truly meets Q4) —
   after first heat/mass model.
6. CRYO_AHU_COND / S70 duty and S67 flue-cap condenser — TBD (AQS-VENT-001).

---

## 8. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 cryo_pfd.py
```

Share mirror: `share/aqueous-solutions/docs-authority/CRYO_COLD_BOX.md`,
`docs-authority/CRYO_EQUIPMENT.md`, `pfd/images/cryo_pfd.png`.
