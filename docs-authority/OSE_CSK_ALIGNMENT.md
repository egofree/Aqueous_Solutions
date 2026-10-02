# OSE Civilization Starter Kit — Aqueous alignment map

Document number: AQS-REF-CSK-001  
Revision: A  
Date: 2026-10-01  
Authority: AQS-SEC-001 (`SECTOR_DEFINITIONS.md`); AQS-EQP-MFG-001;
AQS-EQP-MFG-MET-001; AQS-EQP-FRM-001; AQS-EQP-FAB-001; AQS-BOM-SC-001;
AQS-EQP-STUDY-001; `DEPENDENCIES.md`.  
Style: AQS-DOC-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Initial CSK / GVCS → Aqueous sector and unit mapping | 2026-10-01 |

Licence: CERN-OHL-S-2.0. This document is an Aqueous alignment study; it does
not redistribute OSE content and does not claim OSE endorsement.

---

## 1. Purpose

Record where Open Source Ecology (OSE) Global Village Construction Set
(GVCS) machines — documented via the Civilization Starter Kit (CSK)
repository — may fit Aqueous sectors, MFG/FAB shop roles, flow-graph
units, and equipment authority. Status values are inventory only:
**already covered**, **study**, or **candidate**. No rates, nameplates,
or MVS closure claims are invented here.

---

## 2. Scope

| In | Out |
|---|---|
| Factual CSK/GVCS identity and license as stated upstream | Bundling OSE files into this tree |
| Machine → candidate Aqueous sector / unit role | Declaring CSK machines Present CAD |
| Cross-links to existing Aqueous equipment docs | Invented kW, kg/h, or vendor nameplates |
| Status: already covered / study / candidate | Claiming loop or self-copy closure from OSE alone |

---

## 3. Upstream identity (verified)

| Item | Fact |
|---|---|
| Repository | [Civilization Starter Kit](https://github.com/OpenSourceEcology/Civilization-Starter-Kit) |
| What it is | OSE documentation tree for the Global Village Construction Set (GVCS): modular, DIY, low-cost blueprints intended to enable fabrication of **50 industrial machines** for a small sustainable civilization (repo README). |
| CSK v0.01 note | OSE wiki states the Civilization Starter Kit v0.01 holds training materials for **4 of 50** GVCS machines (beta); the full set is the GVCS catalogue. |
| Machine catalogue | [OSE GVCS List](https://wiki.opensourceecology.org/wiki/GVCS_List); [OSE machine index](https://www.opensourceecology.org/gvcs/gvcs-machine-index/) |
| License (repo README) | Dual-licensed: **code GPLv3**; **other content CC-BY-SA**. GitHub license metadata: GPL-3.0. |
| Distribution in Aqueous | **Not bundled — link only** (`DEPENDENCIES.md`). |

---

## 4. Status key

| Status | Meaning |
|---|---|
| **already covered** | Aqueous already names an equivalent or overlapping unit/role in issued equipment or flow-graph massing (overlap ≠ identical OSE design). |
| **study** | Relevant Aqueous study unit or open study path exists; CSK/GVCS may inform that study. Present CAD / rates remain open. |
| **candidate** | Plausible sector/unit role; no Aqueous Present unit and no issued study unit dedicated to this machine. Inventory only. |

---

## 5. Mapping — Habitat

| GVCS machine | Candidate Aqueous sector / role | Status | Notes / authority |
|---|---|---|---|
| CEB Press | HAB / building envelope materials | candidate | Aqueous building stack is AQS-BLD-001; no CEB Present unit. |
| Cement Mixer | HAB / construction support | candidate | Not in MFG shop equipment list. |
| Sawmill | MFG materials / external timber | candidate | Plant massing is metals + polymer; timber path not issued. |
| Bulldozer | Site / DOCK earthwork (outside process MVS) | candidate | Not a process sector unit. |
| Backhoe | Site / DOCK earthwork (outside process MVS) | candidate | Not a process sector unit. |

---

## 6. Mapping — Agriculture

Aqueous **FARM** is indoor aquaponics / hydroponics (AQS-EQP-FRM-001), not
field agriculture. Field implements are external/terrace candidates unless
noted.

| GVCS machine | Candidate Aqueous sector / role | Status | Notes / authority |
|---|---|---|---|
| Tractor / Microtractor | TRR / external farm (not L1 FARM plate) | candidate | No tractor unit in flow_graph. |
| Seeder / Spader / Soil Pulverizer / Rototiller | TRR / external soil prep | candidate | Indoor GROW_BED ≠ field tillage. |
| Hay Rake / Hay Cutter / Baler / Microcombine | TRR / external forage | candidate | Out of indoor FARM scope. |
| Trencher | Site utilities / TRR | candidate | — |
| Well-Drilling Rig | WTR source development | candidate | WTR authority is roof/catch/VCD/UPW (AQS-WTR-001); well path not issued. |
| Bakery Oven | HAB galley | candidate | HAB fit-out narrative; no bakery unit tag. |
| Dairy Milker | FARM livestock (optional) | candidate | Present FARM is fish + grow beds; dairy not issued. |

---

## 7. Mapping — Industry (MFG / FAB)

| GVCS machine | Candidate Aqueous sector / role | Status | Notes / authority |
|---|---|---|---|
| Welder | MFG `WELD / ASSY` | already covered | AQS-EQP-MFG-001 §3 massing. |
| 3D Printer | MFG `CNC / MILL` RepRap FDM/SLA note | already covered | AQS-EQP-MFG-001 §3; AQS-BOM-SC-001 Partial. |
| Metal Roller | MFG `COLD_MILL` | already covered | AQS-EQP-MFG-MET-001 issued. |
| Rod and Wire Mill | MFG `WIRE_DRAW` | already covered | AQS-EQP-MFG-MET-001 issued. |
| Induction Furnace | MFG `MET_MELT` (electric induction) | already covered | AQS-EQP-MFG-MET-001; ≠ INDUCTION_PYROLYZER. |
| Bioplastic Extruder | MFG polymer `EXTRUSION` | already covered | Overlaps Precious Plastic line (AQS-EQP-MFG-001 §2); link-only. |
| Multimachine / Drill Press | MFG `CNC / MILL` | candidate | Shop massing exists; OSE multimachine not adopted as a unit tag. |
| Ironworker | MFG shop metals | candidate | — |
| Laser Cutter / Plasma Cutter | MFG cut / fab | candidate | Not separately tagged in AQS-EQP-MFG-001. |
| CNC Torch Table | MFG cut table | candidate | — |
| Press Forge | MFG metal forming | candidate | Forming train is draw/mill/atomize; forge not issued. |
| Universal Rotor | MFG tool module | candidate | — |
| Industrial Robot | MFG / FAB handling | candidate | — |
| 3D Scanner | MFG / FAB metrology | candidate | — |
| CNC Circuit Mill | FAB PCB / electronics assist | candidate | Distinct from `WAFER_FAB` / `LITHO_STUB` (semiconductor path). |
| Chipper Hammermill | OIL / GLASS size reduction | candidate | Oil/glass have own mills; OSE chipper not mapped to a unit_id. |
| Aluminum Extractor | WET electrowin / PROD_METALS | already covered | Conceptual overlap with leach–EW metals path; not an OSE aluminum-from-clay Present unit. |

---

## 8. Mapping — Energy

| GVCS machine | Candidate Aqueous sector / role | Status | Notes / authority |
|---|---|---|---|
| Heat Exchanger | CRYO / GEO / MET_HX_Q4 / process HX pattern | already covered | Multiple issued HX roles; not one OSE HX design. |
| Power Cube | ELEC hydraulic power module | candidate | Aqueous electrical hub is Sol-Ark / MCC (AQS-ELC-001). |
| Electric Motor Generator | ELEC rotating machine | candidate | — |
| Hydraulic Motor | ELEC / MFG actuator peer | candidate | — |
| Universal Power Supply | ELEC distribution | candidate | Overlaps ELEC hub role conceptually only. |
| Solar Concentrator | ELEC_PV / thermal study | candidate | Campus PV is flat-plate class (ELEC_PV); concentrator not issued. |
| Wind Turbine | Energy Production (Electrical) peer | candidate | No wind sector_id; ELEC_PV is the Present generation primary. |
| Gasifier Burner | OIL pyro / thermal | study | Oil train exists; gasifier-as-OSE-machine not a named study unit. |
| Steam Engine / Steam Generator | BACKUP_GEN class peer | candidate | Present backup is H₂ genset (AQS-EQP-GEN-001), not steam. |
| Pelletizer | OIL / MFG densification | candidate | — |
| Nickel-Iron Battery | ESS peer (≠ ZNBR2 chemistry) | candidate | MVS ESS peers are ZNBR2 / MEOH / PUMPED_HYDRO — different chemistries. |

---

## 9. Mapping — Materials / Transportation

| GVCS machine | Candidate Aqueous sector / role | Status | Notes / authority |
|---|---|---|---|
| Aluminum Extractor | WET (see §7) | already covered | Conceptual metals path only. |
| Bioplastic Extruder | MFG (see §7) | already covered | — |
| Car / Truck | DOCK logistics / site mobility | candidate | Outside process mass–energy units. |

---

## 10. Flow-graph and equipment touchpoints

| Aqueous artifact | Relevance to CSK/GVCS |
|---|---|
| `flow_graph` nodes `MFG_SHOP`, `MET_MELT`, `COLD_MILL`, `WIRE_DRAW` (via MET), `BLOW_MOLD`, `WAFER_FAB` | Industry-class overlaps; CSK does not replace graph authority. |
| AQS-EQP-MFG-001 / AQS-EQP-MFG-MET-001 | Primary shop and metals forming lists for Industry-class candidates. |
| AQS-EQP-FRM-001 / AQS-EQP-NUT-001 | FARM is aquaponic; Agriculture-class GVCS mostly external. |
| AQS-EQP-FAB-001 / AQS-EQP-STUDY-001 (`LITHO_STUB`, `SOLAR_PV_CELL`) | Electronics/PV paths; CNC Circuit Mill remains candidate only. |
| AQS-BOM-SC-001 | Self-copy RepRap path cites MFG polymer + CNC massing; OSE is upstream reference, not BOM substitute. |
| AQS-SEC-001 sector table | MFG, FAB, FARM, HAB, WTR, ELEC, ELEC_PV, OIL, GLASS, WET, DOCK, BACKUP_GEN as above. |

---

## 11. Related documents

| Doc | Role |
|---|---|
| [`DEPENDENCIES.md`](../DEPENDENCIES.md) | Link-only upstream attribution |
| [`SECTOR_DEFINITIONS.md`](SECTOR_DEFINITIONS.md) | sector_id catalogue |
| [`MFG_SHOP_EQUIPMENT.md`](MFG_SHOP_EQUIPMENT.md) | AQS-EQP-MFG-001 |
| [`METAL_FORMING_EQUIPMENT.md`](METAL_FORMING_EQUIPMENT.md) | AQS-EQP-MFG-MET-001 |
| [`FARM_EQUIPMENT.md`](FARM_EQUIPMENT.md) | AQS-EQP-FRM-001 |
| [`SELF_COPY_BOM.md`](SELF_COPY_BOM.md) | AQS-BOM-SC-001 |
| [`STUDY_UNITS_STUB.md`](STUDY_UNITS_STUB.md) | AQS-EQP-STUDY-001 |
| [Civilization Starter Kit](https://github.com/OpenSourceEcology/Civilization-Starter-Kit) | Upstream repo |
| [GVCS List](https://wiki.opensourceecology.org/wiki/GVCS_List) | Machine catalogue |
