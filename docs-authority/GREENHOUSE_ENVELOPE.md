# Enclosed greenhouse envelope — schedule stub (optional FreeCAD)

Document number: AQS-TRR-GH-001  
Revision: B  
Date: 2026-10-01  
Authority: AQS-TRR-001 (climate decision rule), AQS-SCALE-001 terrace
massing, AQS-EQP-FRM-001, `params.py` TERRACE_* / OVERFLOW_*.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Doc schedule for optional GH solids; no FreeCAD this pass | 2026-10-01 |
| B | Wave 4 | FreeCAD GH_ENV_* / GH_AHU / GH_IRRIG_HDR / GH_DOOR_AIRLOCK envelopes | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Envelope solids in `building_stack.py` (Wave 4).

## 1. Intent

When AQS-TRR-001 §3.1 selects **enclosed greenhouse** on the
equator-facing terrace band, the following tags are reserved for a
future FreeCAD pass. Open-terrace sites skip this file’s solids.

| Tag | Plan intent | Notes |
|---|---|---|
| GH_ENV_S | Equator-facing primary band enclosure | Over OVERFLOW_TERRACE_S_B* |
| GH_ENV_E / GH_ENV_W | Optional wrap enclosures | Only if mixed mode requires |
| GH_AHU | Dedicated greenhouse AHU | ≠ HAB return; Q4 optional |
| GH_IRRIG_HDR | Drip header | S40 clean or dilute fertigation → S42 grey return |
| GH_DOOR_AIRLOCK | Vestibule to terrace apron | Keep fertigation off CATCH |

## 2. Status

| Deliverable | Status |
|---|---|
| Decision rule | Done — AQS-TRR-001 |
| Doc schedule (this file) | **Done** |
| FreeCAD GH_ENV_* solids | **Done** Wave 4 — envelopes on plant rebuild; open-terrace sites may hide |

## 3. Sync

Canonical: `cad/GREENHOUSE_ENVELOPE.md`  
Share: `docs-authority/GREENHOUSE_ENVELOPE.md`
