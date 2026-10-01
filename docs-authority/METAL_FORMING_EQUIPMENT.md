# Metal-forming equipment list

Document number: AQS-EQP-MFG-MET-001  
Revision: D  
Date: 2026-10-01  
PFD: AQS-PFD-MFG-MET-001 (`metal_forming_pfd.png`)  
Authority: AQS-MFG-MET-001, AQS-EQP-MFG-001 (shop envelope),
`MANUFACTURING/Manufacturing_Overview.md` (MetalFab Mermaid — narrative
kW only), root `04-…` (powder / thermal), `freecad/mfg_shop.py`,
`wet_products.py` (PROD_METALS / MELT), AQS-STR-001 S57–S63,
AQS-HSE-001 / AQS-MF-001, hub `ELECTRICAL.md` (induction electric Present).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: wire-draw / cold-mill / atomizer + HVAC/Q4 tags | 2026-09-28 |

Licence: CERN-OHL-S-2.0.

## 1. Locked unit tags

| Tag | Duty | Status |
|---|---|---|
| MET_MELT | Induction electric metal melt → billet / charge (≠ INDUCTION_PYROLYZER) | Issued — **REQ-MET-MELT-CONT 5–15 kW_e** (AQS-REQ-KW-001) |
| WIRE_DRAW | Wire drawing Cu/Al/Fe class | Issued — speed / die schedule TBD |
| COLD_MILL | 4HI reversing cold rolling mill | Issued — gauge / width TBD |
| GAS_ATOMIZER | Inert-gas atomizer → metal powder | Issued — kg/h TBD |
| MET_WIRE_BIN | Wire product hold | Issued |
| MET_SHEET_BIN | Sheet / strip product hold | Issued |
| MET_POWDER_CRIB | Dry powder hold; N₂ blanketed | Issued |
| MET_N2_BLANKET | S03 N₂ branch for blanketing / atomize (Ar = option) | Issued |
| MET_AHU | Dedicated MFG metal-aisle capture AHU (S62 → S71) | Issued |
| MET_SCRUB | Fume / oil-mist scrub on MET_AHU train | Stub — AQS-EQP-VENT-001 |
| MET_SCRUB_REGEN | Liquor / media regen → S72 returns | Stub |
| MET_HX_Q4 | Low-grade residual → Q4 water (S63); peer GEO/FC/CRYO HX | Issued |
| MET_SWARF | Swarf / trim collection → S61 / HOPPER | Issued |
| ELECTRODE_FAB | Electrode blank prep (316L / Ti intent) | Stub — coating deferred |
| MET_COMP_AIR | Shop air for actuators only (not atomizer primary) | Stub |

## 2. Chemistry and media

| Item | Spec intent |
|---|---|
| Melt energy | **Electric induction** — not oil-gas / afterburner fuel |
| Feedstock | PROD_METALS / S08 electrowon metals; remelt of clean S61 when allowed |
| Atomizer gas | N₂ (S03) primary; Ar vendor option — not compressed air as primary |
| Coolant | Closed loop; residual to MET_HX_Q4 only if < 80 °C Q4 class |
| Products | Wire (S58), sheet (S59), powder (S60) |
| Scrap | S61 → HOPPER (S16 class) or leach; **never** FR-4; **never** pyro |

**NOTE**

Legacy SuperbMelt “35 kW”, Stanat/Fenn “5–8 kW”, and “20–30 kW MFG”
figures in Manufacturing_Overview are **study narrative only**. M1
continuous ratings = **TBD**. Do not invent nameplates.

## 3. Separation rules

1. MET_MELT ≠ INDUCTION_PYROLYZER (oil-line organics).
2. Polymer / FR-4 never enter MET_MELT or the forming train.
3. MET_AHU → MET_SCRUB / baghouse (S71–S72); **no shared HAB / FARM return**; no free outdoor dump (AQS-VENT-001).
4. Hot atomizer / melt gas shall not enter Q4 as flue — only named
   water residual via MET_HX_Q4 (S63).
5. Powder crib grounded / inert for reactive metals; keep ignition sources out.
6. Glass-line MILL ≠ COLD_MILL.

## 4. Interfaces

| Interface | Stream / note |
|---|---|
| Upstream crib | S08 / PROD_METALS → MET_MELT |
| Forming feed | S57 |
| Products | S58 / S59 / S60 |
| Scrap | S61 → HOPPER / leach |
| Electric | S17 / S20 module load |
| N₂ | S03 → MET_N2_BLANKET |
| HVAC / scrub | S62 → S71–S72 (scrub/BH returns) |
| Heat | S63 → Q4 |

## 5. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 metal_forming_pfd.py
```


## Study throughput / kW bounds (2026-10-01)

**Study estimates** (AQS-AUD-001 §10.6) — not vendor nameplates:

| Item | Study | Basis |
|---|---|---|
| Wire / sheet / powder | **~0.2–2 kg/h** continuous equiv. | Plated metals 4.5–42 kg/d at 150 kg/d feed (ELECTRICAL yields × 0.15 t) |
| MET_MELT electric | **~5–15 kW** class | Share of induction 0–25 kW; ≠ INDUCTION_PYROLYZER |
| MET_SCRUB capture | **540–900 m³/h** | AQS-EQP-VENT-001 §2.4 |
| Vendor kg/h / kW | **TBD** | — |
