# Sector Definitions catalogue — plant sector_id map

Document number: AQS-SEC-001  
Revision: H  
Date: 2026-10-24  
Authority: generated from AQS-FLOW-GRAPH-001 `mvs.sectors` (graph Rev AC, 2026-10-17) and AQS-SYS-TREE-001 by `docs-authority/_sector_definitions.py`. Do not edit this page; change the graph, the system tree or `design_tool/aqs_design_tool/sector_definitions.py`, then run the pipeline. The Sector Definition class list is owned by AQS-UI-001 §3.1. Not a PE stamp.

| Rev | Change | Date |
|---|---|---|
| A–G | Hand-written catalogue and its ambiguity locks (A1–A9). Text in git history. | 2026-10-01 |
| H | Generated from the graph after the Rev AC sector pivot: WET renamed DIGESTER; ELEC_PV, ZNBR2, BACKUP_GEN and FUEL_CELL became units in ELEC; TRR retired; FOUNDRY, POLYMERS and HEAT added. | 2026-10-24 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose

Map every plant `sector_id` to exactly one Sector Definition, with its MVS-closure flag, so that the design tool, the solver and the documents use one sector list. The list is the graph's; this page only presents it. `flow_graph/test_doc_consistency.py` fails when the design-tool catalogue or the README sector table drifts from the graph.

## 2. Sector Definition classes

Owned by AQS-UI-001 §3.1; do not add a class without a project decision. "In use" lists the sectors that currently carry the class.

| Class | In use by |
|---|---|
| Energy Storage System (Gravity) | PUMPED_HYDRO |
| Energy Storage System (Electrochemical) | MEOH |
| Energy Production (Electrical) | — |
| Energy Production (Combustion Engine) | — |
| Energy Production (Electrochemical) | — |
| Process (Mass transform) | DIGESTER, OIL, GLASS, POLYMERS, GAS, FAB, MFG, FOUNDRY, NUT |
| Life support / habitat | FARM, HAB |
| Utility / header | CRYO, WTR, ELEC, HEAT, GEO |
| Export / dock | DOCK |

## 3. Catalogue

One row per graph sector, in graph order. `required` is `required_for_mvs_closure`. Units are counted from the graph nodes; trains are the first level of the system tree.

| sector_id | Sector Definition | required | enabled | units | trains | notes (graph) |
|---|---|---|---|---|---|---|
| DIGESTER | Process (Mass transform) | true | true | 25 | ew-cascade-train, metals-leach-train | Leach / EW / BMED / polish; renamed from WET at the Rev AC sector pivot (AQS-SEC-001 lineage; first_principles_audit_2026-10-17 §sector definitions). 150 kg/d wet feed basis carried. |
| OIL | Process (Mass transform) | true | true | 13 | pyro-fractionation-train | Organics / oil loop; AFTERBURNER → CRYO |
| GLASS | Process (Mass transform) | true | true | 5 | glass-recycle-train | Silicate / ceramic; materials surplus path (AQS-SEC-001) |
| POLYMERS | Process (Mass transform) | true | true | 10 | fluoropolymer-train, forming-train, polyolefin-train | Fluoropolymer synthesis, film, resins — Rev AC scope (HF_GEN/VDF_SYN/TFE_SYN/POLY_F/FILM_CAST/...). |
| GAS | Process (Mass transform) | true | true | 10 | scrubbing-headers-train | Scrub / vent closure (AQS-VENT-001); secondary Utility |
| FAB | Process (Mass transform) | true | true | 17 | litho-train, wafer-line-train, wet-reagent-train | Wafer / solar-cell fab + LITHO required for MVS (ST-LITHO-01/ST-SOLAR-01 until Present). Sandbox tracks progress toward MVS. |
| MFG | Process (Mass transform) | true | true | 10 | tools-metal-forming-train | Shop + metal forming + BLOW_MOLD + ELECTRODE_COAT required for MVS (open studies ST-BLOW-01/ST-ELC-01 until Present). Sandbox tracks progress; not accepted sub-MVS. Cross-use OK (AQS-SEC-001 §3.1). |
| FOUNDRY | Process (Mass transform) | true | true | 27 | form-train, investment-casting-train, melt-and-cast-train, pot-cell-train | Smelting pots, casting, forging, rolling — Rev AC scope (notes/FOUNDRY_SIZING.md); goods-surplus train with MFG/FAB (A2 lineage). |
| NUT | Process (Mass transform) | true | true | 1 | dosing-train | Nutrient dose; [catalogue-proposed] sector (AQS-SEC-001) |
| FARM | Life support / habitat | true | true | 2 | grow-bed-train | Grow beds; food surplus (CAD name FARM not FRM) |
| HAB | Life support / habitat | true | true | 3 | life-support-train | Habitation / life support |
| CRYO | Utility / header | true | true | 14 | cold-box-asu-recovery-train | Cold-box O2/N2/CO2/H2; not a generation class |
| WTR | Utility / header | true | true | 8 | grey-black-train, potable-upw-train | Roof/catch/VCD/UPW (AQS-WTR-001); was WATER in early seed |
| ELEC | Utility / header | true | true | 9 | distribution-train, generation-train, storage-train | Sol-Ark / ATS / RECT / MCC hub; PV_ARRAY, ZNBR2, BACKUP_GEN and FUEL_CELL are units here since the Rev AC sector pivot |
| HEAT | Utility / header | false | true | 12 | ladder-train | Heat ladder batteries Q1-Q4 (AQS-HEAT-LADDER-001), Q4_BUS header, Q4 branches (HX-9/HX-10, ADS_CHILL, MAU_HX, DRY_COOLER per AQS-HEAT-STUDY-002). |
| MEOH | Energy Storage System (Electrochemical) | true | true | 5 | synthesis-train | MeOH — required ESS peer in MVS; also feeds other processes (AQS-SEC-001 A1 secondary). Sandbox off → unreclaimed_resource. |
| PUMPED_HYDRO | Energy Storage System (Gravity) | true | true | 1 | hydro-train | Roof–catch penstock — required ESS peer in MVS (redundancy). Sandbox off → unreclaimed_resource gap (AQS-SEC-001 Rev D). |
| GEO | Utility / header | false | true | 4 | ground-loop-train | GEO HP→Q4; GEO_ORC heat→electric. Carnot study band issued; ST-ORC-01 survey queued before kW freeze. required_for_mvs_closure false until evidence (AQS-SEC-001 A7). |
| DOCK | Export / dock | true | true | 2 | boundary-train | North dock / freight; surplus export boundary |

### 3.1 System tree descriptions

| sector_id | Description (AQS-SYS-TREE-001) |
|---|---|
| DIGESTER | Process (Mass transform) — leach / EW / BMED / polish; 150 kg/d wet feed basis. |
| OIL | Process (Mass transform) — organics / oil loop; afterburner to CRYO. |
| GLASS | Process (Mass transform) — silicate / ceramic; materials surplus path. |
| POLYMERS | Process (Mass transform) — fluoropolymer synthesis, polyolefin, form factors. |
| GAS | Process (Mass transform) — scrub / vent closure; secondary Utility. |
| FAB | Process (Mass transform) — wafer / solar-cell fab; litho required for MVS. |
| MFG | Process (Mass transform) — shop, metal forming, blow mold, electrode coat. |
| FOUNDRY | Process (Mass transform) — smelting pots, casting, forging, rolling (goods-surplus train with MFG/FAB). |
| NUT | Process (Mass transform) — nutrient dose. |
| FARM | Life support / habitat — grow beds; food surplus. |
| HAB | Life support / habitat — habitation and life support. |
| CRYO | Utility / header — cold-box O2/N2/CO2/H2; not a generation class. |
| WTR | Utility / header — roof / catch / VCD / UPW / grey / black water. |
| ELEC | Utility / header — Sol-Ark / ATS / RECT / MCC hub. |
| HEAT | Utility / header — heat ladder batteries Q1-Q4, Q4_BUS, Q4 services. |
| MEOH | Energy Storage System (Electrochemical) — MeOH ESS peer; also feeds processes. |
| PUMPED_HYDRO | Energy Storage System (Gravity) — roof-catch penstock ESS peer. |
| GEO | Utility / header — ground loop HP to Q4; ORC study. |
| DOCK | Export / dock — north dock / freight; surplus export boundary. |

## 4. Energy storage peers

MVS requires every ESS peer. Peers that are sectors: MEOH, PUMPED_HYDRO. Peers that are units inside a sector: ZNBR2 (ELEC). A sandbox may disable a peer; the solver then reports `unreclaimed_resource` for it and does not claim closure.

## 5. Retired sector ids

Older documents and dated notes may use these names. Read them as the current sector shown.

| Former id | Now | Since | Note |
|---|---|---|---|
| BACKUP_GEN | ELEC | graph Rev AC (2026-10-17) | the standby H2 genset is a unit in ELEC |
| ELEC_PV | ELEC | graph Rev AC (2026-10-17) | PV_ARRAY is a unit in ELEC |
| FUEL_CELL | ELEC | graph Rev AC (2026-10-17) | the PEM fuel cell is a unit in ELEC |
| TRR | retired | 2026-10-18 | terrace irrigation retired with the TERRACE_IRRIG unit |
| WET | DIGESTER | graph Rev AC (2026-10-17) | renamed; the same leach / EW / BMED / polish line |
| ZNBR2 | ELEC | graph Rev AC (2026-10-17) | the flow battery is a unit in ELEC; still an ESS peer by unit (ESS_PEER_UNIT_IDS) |

## 6. Aliases and non-sector names

Not sector ids. Reject them as `sector_id`; map them as shown.

| Name | Meaning |
|---|---|
| CORE | building shafts — not a sector toggle |
| CRY | alias → CRYO |
| FRM | alias → FARM |
| LIFE | composite → FARM + HAB (+ WTR) |
| MET | folded under MFG |
| OIL_GLASS | FreeCAD group → OIL + GLASS |
| POWER | composite → ELEC (PV / ZNBR2 / FC / genset units) + GEO, MEOH |
| SLINGSHOT | non-sector interface |
| WATER | legacy seed id → WTR (AQS-SEC-001) |

## 7. Related documents

| Doc | ID | Role |
|---|---|---|
| `flow_graph/plant_flow_graph.json` | AQS-FLOW-GRAPH-001 | Sole topology authority; `mvs.sectors` is the sector list |
| `flow_graph/system_tree.yaml` | AQS-SYS-TREE-001 | Sector → train → unit decomposition |
| [DESIGN_TOOL_ARCHITECTURE.md](DESIGN_TOOL_ARCHITECTURE.md) | AQS-UI-001 | Owns the Sector Definition class list (§3.1) |
| [GLOSSARY.md](GLOSSARY.md) | — | Sector and unit terms |
