# Solar-cell line equipment

Document number: AQS-EQP-FAB-PV-001  
Revision: D  
Date: 2026-10-29  
Process flow diagram: AQS-PFD-FAB-PV-001 (`solar_cell_pfd.png`); the parent fab diagram AQS-PFD-FAB-001 points to it.  
Basis: AQS-EQP-FAB-001 §4; AQS-EQP-FAB-RGN-001 (`WS_KOH`); AQS-WTR-001 (fab ultrapure water); AQS-ELC-001 (campus PV narrative only).  
Licence: CERN-OHL-S-2.0. Style: AQS-DOC-002. `SCALE_M = 1.0`.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Close open solar-cell path with named train; no invented kW / belt solids | 2026-10-01 |
| B | 1 | Dedicated PFD + FreeCAD PV_* east-strip envelopes; kW still TBD | 2026-10-01 |
| C | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope merged into §1, terms in §2, captions; layout section brought in line with the issued FreeCAD stubs. Tags, requirements and status unchanged. | 2026-10-24 |
| D | 1 | References to documents outside this repository removed; the FreeCAD script cited by its path in the repository. Tags, requirements and status unchanged. | 2026-10-29 |

## 1. Purpose and scope

The plant's wafer fab can also make solar cells. This page names the units of that line, in order from a polished wafer to a tested cell: texture, emitter, anti-reflection coating, contacts, firing and test. Its status is Partial: the units are named and have FreeCAD envelopes, but there are no detailed solids and no vendor nameplates.

Table 1.1. Scope

| In | Out |
|---|---|
| Named unit tags and sequence | Invented belt-furnace kW or PECVD power |
| KOH / POCl₃ / SiNₓ / Ag-Al / fire hooks | Electrical yard resize for cell offtake |
| FreeCAD PV_* envelope stubs | Detailed solids / STL / in-house tool designs (X-MFG-38) |
| Dedicated PFD AQS-PFD-FAB-PV-001 | Claiming Present/Complete CAD |
| Status = Partial architecture + CAD envelopes | |

## 2. Terms

- Texture: an alkaline etch that forms small pyramids on the wafer surface to trap light.
- Emitter: the thin doped layer, here diffused from phosphoryl chloride (POCl₃), that forms the cell junction.
- PSG: phosphosilicate glass, left on the wafer by the emitter diffusion and etched off.
- ARC: anti-reflection coating, here silicon nitride (SiNₓ) deposited by PECVD.
- Firing: a short high-temperature pass in a belt furnace that sinters the printed contacts.
- IV test: measuring the current–voltage curve of a finished cell under a flash.
- M1: the first module of the plant at the baseline size.

Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Process train, polished wafer to cell

The wafer comes from the main fab line (AQS-EQP-FAB-001: CZ pulling, cutting, lapping and chemical-mechanical polishing, cleaning). The solar line starts on polished wafers ready for texturing (Table 3.1).

Table 3.1. Solar-cell process train

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

Photolithography and implantation for integrated circuits stay inside `FAB_TOOL` (AQS-EQP-FAB-001). The solar line is a separate train that shares ultrapure water, potassium hydroxide, the etch return and nitrogen with it; it does not drop any requirement of root document 03.

## 4. Utilities and returns

Table 4.1. Utilities and returns

| Utility | Source | Notes |
|---|---|---|
| UPW | S27 FAB_UPW | Same wet-bench class quality |
| KOH | WS_KOH | Already mapped on reagent forks |
| Etch return | S10 → REGEN LEACH | Closed |
| Exhaust | LEV → scrub / acid-gas rules | No free outdoor dump (AQS-VENT-001) |
| Heat reject | PV_HX_Q4 stub | Q4 water; not Q1 flue |
| Power | Module bus | **Nameplate kW TBD** — do not invent |

## 5. Layout (level 0 fab bay)

The `PV_*` units sit as a strip inside the fab envelope (12 × 10 m at M1) without moving the CZ train. Their FreeCAD envelope stubs are on the east strip in `models/freecad/wafer_fab.py`; detailed solids remain open, as do the `CZ_PULLER` solids in AQS-EQP-FAB-001.

Clash rules: no Salria in the PV wet benches; no `HDR_H2` dwell in the fab; bromine and the zinc-bromide battery stay outdoors.

## 6. Status of follow-up items

1. Dedicated process flow diagram AQS-PFD-FAB-PV-001: done (`solar_cell_pfd.py`).
2. FreeCAD envelope stubs for `PV_TEXTURE` to `PV_FIRE`, `PV_IV` and `PV_HX_Q4`: done (`models/freecad/wafer_fab.py`, east strip).
3. Purchase datasheets for the PECVD tool and the belt furnace: open. The study requirements are in AQS-REQ-KW-001.
4. Whether the cell output changes `PV_COUNT` (the electrical cassette): open.

## 7. Canonical copy

The canonical copy of this page is `docs-authority/SOLAR_CELL_EQUIPMENT.md`.
