# Textiles / HEPA media — architecture stub

Document number: AQS-MFG-TEX-001  
Revision: A  
Date: 2026-10-01  
Authority: AQS-GAP-001 (was **Missing**); AQS-EQP-MFG-001 shop envelope;
AQS-CRY-002 / AQS-EQP-CRY-001 (HEPA on cryo intake only); AQS-AUTH-001.  
Status: **Partial** (architecture only — no CAD bay, no PFD, no duties).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Wave 2 stub: Missing to Partial architecture | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001. SCALE_M = 1.0.

## 1. Purpose

Record how a future melt-blown / knit HEPA media line would sit in the
MFG story without inventing equipment IDs or rates.

## 2. Scope

| In | Out |
|---|---|
| Architecture decision: media for life/farm HVAC filters and cryo intake spares | FreeCAD solids / PFD sheet |
| Link to existing CRYO intake HEPA tag | Process acid-train HEPA as primary (acid uses demister + pack) |
| Shop adjacency note under MFG L0 | Vendor nameplates; polymer resin grades |

## 3. Architecture (Partial)

1. Cryo intake HEPA remains on AQS-EQP-CRY-001 (Present/Partial) — not this line.
2. Life / farm filter media — if produced on site, occupy a future MFG cassette bay east-south (AQS-BLD-001 MFG envelope), downstream of polymer handling, upstream of scrap return to leach only as clean offcuts (no Salria contact).
3. Process acid gas continues demister + alkali pack (AQS-VENT-001 / AQS-GAS-002) — do not substitute HEPA as the primary acid scrub.
4. No incinerator path for textile scrap (AQS-GAP-001 superseded intent).

## 4. Next pass (not Wave 2)

- Equipment list AQS-EQP-MFG-TEX-001 + streams if farm/hab filter demand is quantified.
- CAD bay only after AQS-AUD-001 shows filter mass justifies on-site make.

## 5. Sync

Canonical: cad/TEXTILES_HEPA.md  
Share: docs-authority/TEXTILES_HEPA.md
