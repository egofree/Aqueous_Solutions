# Electrode fabrication / coating — architecture (in scope)

Document number: AQS-MFG-ELC-001  
Revision: B  
Date: 2026-10-01  
Authority: AQS-GAP-001; AQS-MFG-MET-001 / AQS-EQP-MFG-MET-001; AQS-BOM-SC-001 Rev C;
AQS-EQP-STUDY-001; AQS-AUTH-001; Project decision 2026-10-01 (coating IN SCOPE).  
Status: **Study duty issued** (ST-ELC-01); Present booth CAD + lab formula = external — not accepted gap.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Wave 2 stub: coating Remaining to Partial architecture | 2026-10-01 |
| B | 1 | Project decision: coating **IN SCOPE**; seed `ELECTRODE_COAT`; MFG primary; sector cross-use OK | 2026-10-01 |
| C | 2 | ST-ELC-01: 0.3 kW_e avg; non-precious M1 formulation class; RuO₂–IrO₂ deferred | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-002. SCALE_M = 1.0.

## 1. Purpose

Describe where DSA / powder electrode coating lives relative to the
metal-forming aisle, and keep it on the **path to MVS** (required capability)
without inventing formulation nameplates. Present booth = **ST-ELC-01** open study.

## 2. Scope

| In | Out this pass |
|---|---|
| Substrate path from MET wire / sheet / powder (AQS-MFG-MET-001) | Vendor RuO₂–IrO₂ duty / slurry recipes |
| Seed unit `ELECTRODE_COAT` (MFG) | Present FreeCAD booth solids |
| HSE: coating fumes → MET_AHU → MET_SCRUB (S71–S72) | MeOH / DMFC electrodes (AQS-FC-001 / MEOH path) |
| Sector cross-use: MFG may borrow FAB wet-bench practice | Claiming `electrode_coating_on_site=true` |

## 3. Architecture (in-scope study)

1. Substrates — 316L / Ti mesh or plate from MET cold-mill / mesh path (AQS-EQP-MFG-MET-001).
2. Coating — booth in MFG metal aisle, exhausted to MET_AHU then MET_SCRUB per AQS-VENT-001 / AQS-HSE-001; not afterburner as primary.
3. Product — EW / BMED anodes-cathodes as replaceable articles; no claim of on-site precious-metal coat at M1 rates.
4. Seed flag `electrode_coating_on_site=false` until Present CAD + formulation study closes.

## 4. ST-ELC-01 results + next pass

| Item | Study result |
|---|---|
| Continuous kW_e | **~0.3** avg; peak **1–2** (exhaust + cure campaign) |
| Formulation class | Non-precious carbon / Ni / passivation for M1 EW |
| RuO₂–IrO₂ DSA | **Deferred** — no invented slurry |
| Next (external) | Booth FreeCAD + lab formulation trial — **owner/date TBD** |

Also: AQS-EQP-MFG-ELC-001 equipment list when MET nameplates exist.
Detail: AQS-EQP-STUDY-001 Rev E §10.

## 5. Sync

Canonical: docs-authority/ELECTRODE_FAB.md  
Share: docs-authority/ELECTRODE_FAB.md
