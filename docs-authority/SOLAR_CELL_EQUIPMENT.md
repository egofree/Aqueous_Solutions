# Solar-cell branch — equipment schedule (architecture Partial)

Document number: AQS-EQP-FAB-PV-001  
Revision: B  
Date: 2026-10-01  
PFD: AQS-PFD-FAB-PV-001 (`solar_cell_pfd.png`); parent pointer on AQS-PFD-FAB-001.  
Authority: AQS-EQP-FAB-001 §4, root `03-silicon-wafer-fabrication.md`,
AQS-EQP-FAB-RGN-001 (`WS_KOH`), AQS-WTR-001 / FAB UPW, AQS-ELC-001
(campus PV narrative only).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Close open solar-cell path with named train; no invented kW / belt solids | 2026-10-01 |
| B | Wave 4 | Dedicated PFD + FreeCAD PV_* east-strip envelopes; kW still TBD | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-002. `SCALE_M = 1.0`.

---

## 1. Purpose

Replace the **empty** solar-cell open stub with a **Partial** architecture
schedule: texture → emitter → ARC → contact → fire → test. Keeps the
branch visible on the fab path without inventing FreeCAD solids or
vendor nameplates.

## 2. Scope

| In | Out this pass |
|---|---|
| Named unit tags and sequence | Invented belt-furnace kW or PECVD power |
| KOH / POCl₃ / SiNₓ / Ag-Al / fire hooks | Electrical yard resize for cell offtake |
| FreeCAD PV_* envelope stubs | Detailed solids / STL / in-house tool designs (X-MFG-38) |
| Dedicated PFD AQS-PFD-FAB-PV-001 | Claiming Present/Complete CAD |
| Status = Partial architecture + CAD envelopes | |

---

## 3. Process train (polished wafer → cell)

Upstream wafer from AQS-EQP-FAB-001 (CZ → cut → lap/CMP → clean).
Solar branch begins on **polished / textured-ready** wafers:

| Step | Tag | Duty | Reagent / utility | Status |
|---|---|---|---|---|
| 1 | PV_TEXTURE | Alkaline texture (random pyramid) | **WS_KOH** (AQS-EQP-FAB-RGN-001); UPW rinse S27 | Partial — envelope |
| 2 | PV_EMITTER | POCl₃ emitter diffusion / furnace | POCl₃ source; N₂ / O₂ (S03 / S02); exhaust to scrub | Partial — envelope |
| 3 | PV_PSG_ETCH | PSG / edge isolation etch | Dilute HF / acid class → S10 etch return | Partial — envelope |
| 4 | PV_ARC | SiNₓ ARC (PECVD class) | SiH₄ / NH₃ class **vendor gas TBD**; N₂ purge | Partial — **REQ-PECVD** 0.5–2 avg / 5–15 peak kW_e (SI-PECVD-01) |
| 5 | PV_CONTACT | Ag front / Al rear screen print | Ag/Al pastes; solvent wipe → WS_SOLV path | Partial — envelope |
| 6 | PV_FIRE | Belt / continuous fire furnace | Air / N₂; heat → Q4 via PV_HX_Q4 stub | Partial — **REQ-BELT** 0.5–2 avg / 10–25 peak kW_e (SI-BELT-01) |
| 7 | PV_IV | IV / flash test + sorting | Electrical only | Partial — envelope |
| 8 | PV_MODULE_OFFTAKE | Cells → campus PV string (narrative) | AQS-ELC-001 PV_COUNT sizing **unchanged** this pass | Narrative only |

**NOTE**

Photolithography / implant for **IC** fab remain inside `FAB_TOOL`
(AQS-EQP-FAB-001). Solar branch is a **separate** train sharing UPW,
KOH, etch return, and N₂ — not a silent drop of root-03 requirements.

---

## 4. Utilities & returns

| Utility | Source | Notes |
|---|---|---|
| UPW | S27 FAB_UPW | Same wet-bench class quality |
| KOH | WS_KOH | Already mapped on reagent forks |
| Etch return | S10 → REGEN LEACH | Closed |
| Exhaust | LEV → scrub / acid-gas rules | No free outdoor dump (AQS-VENT-001) |
| Heat reject | PV_HX_Q4 stub | Q4 water; not Q1 flue |
| Power | Module bus | **Nameplate kW TBD** — do not invent |

---

## 5. Layout intent (L0 FAB bay)

Place PV_* as a **south or east strip inside FAB envelope**
(12 × 10 m at M1) without relocating CZ train. FreeCAD child stubs =
follow-up (same class as CZ_PULLER solids still open on FAB-001).

Clash rules: no Salria in PV wet benches; no HDR_H2 dwell in FAB;
Br₂ / ZnBr2 stay outdoor.

---

## 6. Open → next solar pass

1. ~~Dedicated PFD sheet AQS-PFD-FAB-PV-001~~ **Done** Wave 4 (`solar_cell_pfd.py`).
2. ~~FreeCAD envelope stubs for PV_TEXTURE … PV_FIRE / PV_IV / PV_HX_Q4~~ **Done** Wave 4 (`freecad/wafer_fab.py` east strip).
3. Vendor PECVD / belt-furnace purchase datasheets — **open**; study reqs in AQS-REQ-KW-001.
4. Decide whether cell offtake resizes PV_COUNT (electrical cassette) — **open**.

---

## 7. Sync

Canonical in this tree: `docs-authority/SOLAR_CELL_EQUIPMENT.md`  
