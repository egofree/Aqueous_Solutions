# CAD authority lock

Document number: AQS-AUTH-001  
Revision: Y  
Date: 2026-10-24

## 1. Purpose and scope

The repository holds several documents that describe where things are in the plant. This page says which one wins when they disagree, so that every three-dimensional (CAD) model is built from one consistent source. It also points to the controlling document for each related topic: venting, scale, energy storage, compliance and so on.

The page covers the FreeCAD solids, campus placements, fire assemblies and shafts. Plant topology (which units exist and how streams connect them) is not decided here. It is held by the typed plant flow graph in `flow_graph/` (AQS-FLOW-GRAPH-001), as AQS-UI-001 sets out.

## 2. Terms

Active authority: the document that controls a subject. Where another document disagrees, the active authority wins.

Subordinate document: a document that adds detail within the limits set by an active authority. It cannot override that authority.

Cassette: a group of equipment modelled in its own local coordinates and then moved into place as one block. The process wet line is a cassette.

World coordinates: plant coordinates in millimetres. World Z = 0 is the finished-floor level (FFL) of L0 at grade. Levels L-2 to L2 are defined in AQS-BLD-001.

Other abbreviations (MVS, ESS, PFD, MFD, EFD, SLD, BOM, VJ, MAWP, WPS) are defined in `docs-authority/GLOSSARY.md`.

## 3. Active CAD authority

CAD placement follows AQS-BLD-001 Rev F (`docs-authority/BUILDING_STACK.md`). All FreeCAD solids, campus placements, fire assemblies and shafts follow the stacked building levels in that document. The level datums are in `models/freecad/params.py` (`Z_Lm2` to `Z_L2`). Site access, the north dock and service egress follow AQS-SITE-001 (`docs-authority/SITE_ACCESS.md`). The controlling-code annex for egress is AQS-EGR-001 Rev B.

Table 3.1 gives the role of each placement source.

Table 3.1. Placement sources and their roles

| Source | Role |
|---|---|
| `BUILDING_STACK.md` (AQS-BLD-001) | Active: levels, cores, shafts, masses, fire ratings |
| `HAZARD_SEPARATION.md` (AQS-HSE-001) | Active: the names and ratings of fire barriers `FB_*`, hazard areas `HA_*`, shafts `SHAFT_*` and cores `CORE_*` |
| `PHASE_F_ENVELOPES.md` (AQS-PHF-001) | Subordinate: keep-out sizes and utility lists only. Its flat placements at Z = 0 are interim and are not placement authority |
| Wet-line `*.FCStd` files | Cassette: local Z = 0 is the FFL of L-1. `build_plant.py` shifts the process cassette by `Z_Lm1` into world coordinates |

There is only one campus model, the stacked building. Do not keep a second campus at Z = 0 beside it. Where a size in PHASE_F_ENVELOPES differs from BUILDING_STACK §9, the building stack controls the CAD envelope; PHASE_F_ENVELOPES remains the note on utilities and return paths.

## 4. Process wet-line transform

The files `wet_line.FCStd` and `leach_cstr.FCStd`, and the attachments along the aisle (product, oil, glass and gas equipment and the process pipe racks), are drawn in L-1 local millimetres. The plant assembly moves them into world coordinates as follows.

```
world_x = local_x + PROCESS_DX   # 5000 mm
world_y = local_y + PROCESS_DY   # 4000 mm
world_z = local_z + Z_Lm1        # Z_Lm1 = -6000 mm
```

The horizontal offset places the M1 cassette wholly inside the L-1 slab `SLAB_Lm1`, on the bay grid. Move the line with this transform; do not add a second leach tank to relocate it. The cryogenic plant (CRYO) is on L-1 at (18 000, 6 000) mm, east of the core and across from the wet aisle, behind fire barrier `FB_CRYO_PROCESS` (2 h rating; no process-air duct passes through it).

## 5. Hydrogen path

The aisle header `HDR_H2` is the horizontal hydrogen capture header. `SHAFT_H2` is the vertical riser, with no traps, from L-1 to `CRYO_H2` (stream S64 in normal operation), with a roof contingency outlet (S24). The CAD model must show both. Continuous free release at the roof is not design intent (AQS-VENT-001).

## 6. Controlling documents for related topics

Table 6.1 lists the document that controls each related topic, with its relationship to other documents. Two entries are planning notes that are not published in this repository; they are named so that references to them can be traced.

Table 6.1. Controlling documents by topic

| Topic | Document | Notes |
|---|---|---|
| Mass-flow claim status | `docs-authority/MASS_FLOW.md` (AQS-MF-001 Rev I) | |
| Vent and stack closure | `docs-authority/VENT_CLOSURE.md` (AQS-VENT-001) | Former outdoor releases go to scrubbing and regeneration or to CRYO. Equipment stubs in `docs-authority/VENT_SCRUB_EQUIPMENT.md` (AQS-EQP-VENT-001) |
| Parametric scale | `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001 Rev C) | Subordinate growth rules for bays, cassettes, life plates, tanks, electrical modules and overflow terraces. The plant baseline on disk is `SCALE_M = 1.0` (M1) |
| Scale-down to unreclaimed resources | `docs-authority/SCALE_DOWN_UNRECLAIMED.md` (AQS-SCALE-UR-001 Rev C) | Maps `SCALE_M` and sectors or modules switched off to `stream_id` and the Sector Definition `unreclaimed_resource` gaps. Solver: `design_tool/.../solver/scale_down_map.py`. Subordinate to AQS-SCALE-001 and AQS-UI-001 §3.2 |
| Surplus pass thresholds | `docs-authority/SURPLUS_PASS_THRESHOLDS.md` (AQS-SUR-001 Rev B) | Numeric study thresholds for food, water, goods and energy; solver function `pass_study` |
| Energy storage duties | `docs-authority/ESS_DUTY_MATRIX.md` (AQS-ESS-001 Rev B) | Study duties for zinc-bromide (ZnBr₂), methanol and pumped hydro storage, and hydrogen contention. Records that hydro energy is far below ZnBr₂ energy |
| Self-copy critical-path BOM | `docs-authority/SELF_COPY_BOM.md` (AQS-BOM-SC-001 Rev D) | Partial. Lithography, blow moulding and electrodes are required for the MVS; open studies ST-* are queued, not accepted as unreclaimed |
| Study and deferred units | `docs-authority/STUDY_UNITS_STUB.md` (AQS-EQP-STUDY-001 Rev F) | First-principles study queue towards the MVS; the design-tool sandbox tracks progress |
| Equipment maker and model gaps | Unpublished planning note UNIT_EQUIPMENT_SPEC_GAP (AQS-EQ-GAP-001) | Includes the policy of moving from commercial interim equipment to open-source equipment. Planning only |
| Terrace landscape and irrigation | `docs-authority/TERRACE_LANDSCAPE.md` (AQS-TRR-001) | Subordinate to AQS-SCALE-001 massing and AQS-WTR-001 clean-water rules |
| Cryogenic cold box | `docs-authority/CRYO_COLD_BOX.md` (AQS-CRY-002) | Subordinate to AQS-BLD-001 placement and AQS-HSE-001 ventilation. Equipment list AQS-EQP-CRY-001 Rev D; heat split S54 to S56; condensable return S70; hydrogen normal S64 |
| Metal forming | `docs-authority/METAL_FORMING.md` (AQS-MFG-MET-001) | Subordinate to the AQS-EQP-MFG-001 shop envelope. Equipment AQS-EQP-MFG-MET-001; streams S57 to S63 and S71 to S72. The metal melt `MET_MELT` is not the pyrolysis unit |
| Planning capacity audit | AQS-AUD-001 (unpublished planning record) | Not CAD authority. A subordinate study checked against the AQS-BLD-001 envelopes, the AQS-STR-001 and AQS-MF-001 loops and the AQS-EQP-* lists at `SCALE_M = 1.0`. Study estimates are not nameplate ratings |
| Compliance themes | `docs-authority/COMPLIANCE_MATRIX.md` (AQS-COMPL-001) | |
| Documentation style | `docs-authority/DOC_STYLE.md` (AQS-DOC-002) | |
| Electrical hub | `docs-authority/ELECTRICAL.md` (AQS-ELC-001) | |
| Methanol fuel cell | AQS-FC-001 | The direct methanol fuel cell remains deferred |
| Design-tool architecture | `docs-authority/DESIGN_TOOL_ARCHITECTURE.md` (AQS-UI-001 Rev D) | Sector Definitions; the MVS is a self-sustaining colony with closed loops and surplus export; all three energy storage peers are required; unreclaimed-resource gaps; the typed plant graph is the only topology authority; `candidate_mvs` is folded in or projected from the graph (decision unify_then_reshape). The interface is schematic first, as graph layers drawn with React and SVG; matplotlib is an optional exporter only; exports are modular and licensed CERN-OHL-S; Odysseus (AQS-ORG-001), a separate local planning and research source whose AGPL-licensed data is kept out of the model and interface tree, is not a runtime dependency (what it is: open question Q-016); Phase D favours rebuilding in FreeCAD (Three.js only with a written decision). It does not overwrite the MVS. Scaffold code for phases P0 and P1 is in `design_tool/` and `design_tool/web/`. Topology comes through `flow_graph_adapter`; sandboxes merge graph units and streams; `mvs_equivalent` is never set from topology alone. Completion plan AQS-PLAN-UI-001 Rev N (A′ unify, B′ layer interface, C export from the graph to GitHub, then D and E) and the stack re-evaluation in the unpublished planning note STACK_REEVAL_2026-10-01. WP-Ap1 to Ap3, WP-Bp1 to Bp4 and WP-C1 (local PFD, SLD and BOM from the graph) are done; A′ and B′ exits met; C2 and C3 waited on authorisation to publish to GitHub (C2 not started). Plan Rev R |
| Sector Definitions | `docs-authority/SECTOR_DEFINITIONS.md` (AQS-SEC-001) | Generated from the graph's `mvs.sectors` by `docs-authority/_sector_definitions.py`. Maps every plant `sector_id` to one AQS-UI-001 §3.1 class, with its MVS-closure flag, storage peers, retired ids and aliases. AQS-UI-001 §3.1 owns the class list |
| Egress study | `docs-authority/EGRESS_CALC.md` (AQS-EGR-001) | |
| Pressure vessels and piping classes | `docs-authority/ASME_CLASS_SHEETS.md` (AQS-ASM-001) | Vessel inventory and ASME B31.3 class sheets |
| Living-area mechanical, electrical and plumbing | `docs-authority/LIFE_MEP.md` (AQS-MEP-001) | |
| Solar-cell schedule | `docs-authority/SOLAR_CELL_EQUIPMENT.md` (AQS-EQP-FAB-PV-001 Rev B) | PFD AQS-PFD-FAB-PV-001; FreeCAD `PV_*` envelopes on the east strip |
| Optional greenhouse envelopes | `docs-authority/GREENHOUSE_ENVELOPE.md` (AQS-TRR-GH-001 Rev B) | `GH_ENV_*`, `GH_AHU`, `GH_IRRIG_HDR` and `GH_DOOR_AIRLOCK` in `building_stack.py` |
| Cryogenic vacuum-jacketed line envelopes | AQS-ASM-001 §8 | Tags `VJ_001` to `VJ_005` in `freecad/cryo.py`. These are not fabricator isometrics; MAWP and WPS are still open |

Planning gap audits and other planning-only documents are kept outside this repository.

## 7. Rebuilding the models

Run `python3 -m flow_graph.param.regen`, adding `--cad` to rebuild the three-dimensional models. `docs-authority/REBUILD.md` (AQS-REB-001) describes the procedure, including `SCALE_M`, the actual building size set in `models/freecad/params.py`: 1.0 for manufacturing, 2.0 for review only.

## 8. Revision history

Earlier revisions recorded each change as a lettered entry. Table 8.1 keeps entries K to X; work packages (WP-*) are planning tranches of AQS-PLAN-UI-001.

Table 8.1. Revision history

| Rev | Change | Date |
|---|---|---|
| K | Pointers to the surplus, storage, equipment-study, scale-down and BOM documents at their new revisions; design-tool Phase A note (AQS-PLAN-UI-001). The planning freeze checklist stays unpublished | 2026-10-01 |
| L | WP-A3 and WP-A5: BOM-SC Rev C; EQP-STUDY Rev C (vapour-compression distillation, remineralisation and organic Rankine cycle from first principles); SEC Rev F cross-use; seed C candidate | 2026-10-01 |
| M | Framing: the MVS is pursued as the ideal; live progress in the sandbox; gaps are open studies (BOM-SC and EQP-STUDY Rev D; SEC Rev G; seed D candidate) | 2026-10-01 |
| N | Pointer to the equipment specification gap register, UNIT_EQUIPMENT_SPEC_GAP (AQS-EQ-GAP-001, unpublished); STUDY stub Rev F | 2026-10-01 |
| O | Typed plant flow graph made the only authority, `flow_graph/` (AQS-FLOW-GRAPH-001); locks include present items plus placeholders; STREAM_REGISTER and MASS_FLOW become derived or synchronised targets | 2026-10-01 |
| P | Flow-graph adapter for the design tool and SVG layer views: FastAPI `flow_graph_adapter`, `/api/v1/flow-graph*` and sandbox topology merge; `render_layer_views.py` emits SVG (MFD and EFD); S17 on the electrical EFD; methanol on the MFD; dock and hydro campus placeholders; earlier PFD and SLD scripts documented | 2026-10-01 |
| Q | Matplotlib bridge from the graph to the SLD and mass-flow drawings, `flow_graph/pfd_bridge.py`: `electrical_sld.png` shows S17 and the storage peers (ZNBR2, MEOH, HYDRO); `mass_flow_pfd.png` shows methanol streams S73 to S82 and `DOCK_EXPORT_TBD`; other PFD scripts remain as before | 2026-10-01 |
| R | Line PFD bridges for the electrowinning, continuous, glass, BMED and polish lines, and a dedicated `hydro_dock_pfd` for PUMPED_HYDRO and DOCK; ZnBr₂ and methanol storage overlays; `DOCK_EXPORT_TBD` still to be determined | 2026-10-01 |
| S | Remaining process line PFDs bridged to the graph (oil, wet, metal, manufacturing, habitat, fab, power, farm, cryogenic, vent); campus, building and container layout overlays; no process lines left on the earlier scripts; WP-A10 bridge tranche closed. Remaining: `DOCK_EXPORT_TBD`, null rates and an optional matplotlib rewrite | 2026-10-01 |
| T | Project decision unify_then_reshape (2026-10-01). AQS-UI-001 Rev D: the typed plant graph is the only topology authority; `candidate_mvs` is folded in or projected; matplotlib becomes an optional exporter; roadmap A′, B′, C, D, E with a FreeCAD three-dimensional emphasis; Phase C blocked until unification. Planning: AQS-PLAN-UI-001 Rev N and the unpublished planning note STACK_REEVAL_2026-10-01 (planning only) | 2026-10-01 |
| U | WP-Ap1 done: `plant_flow_graph.json` Rev B is the only write path (nodes, edges, `mvs` sectors, site, crew, `SITE_LAT`, surplus, unit kW and parameters); `candidate_mvs.json` is generated only by `flow_graph/export_candidate_mvs.py`; FastAPI and `mvs_from_graph` load the graph; never a silent dual write; `mvs_equivalent` stays false; `DOCK_EXPORT_TBD` still to be determined. Plan Rev O | 2026-10-01 |
| V | WP-Ap2 and WP-Ap3 done: authority contract tests (`flow_graph/check_authority_contract.py`, `test_authority_contract.py`); FastAPI projection check (HTTP 409 on drift); solve, MVS and sandbox read only the graph; derived stream and mass pages via `export_authority_md.py` into `flow_graph/derived/` with CAD synchronisation pointers; layer stubs still from `render_layer_views.py`; A′ exit met (Ap1 and Ap2); Phase C still needs B′. Plan Rev P. No dock streams or rates invented | 2026-10-01 |
| W | WP-Bp1 to Bp4 done: React and SVG graph-layer interface (`design_tool/web/`) loads `/api/v1/flow-graph` and its views (PFD, MFD, electrical EFD, thermal, storage); placeholders shown; sandbox patches the graph-backed model; export packs include `flow_graph_snapshot.json`; MVS reference unchanged; `npm run build` passes; B′ exit met; Phase C planned and unblocked, starting only on explicit authorisation. Plan AQS-PLAN-UI-001 Rev Q. Nothing published to GitHub; no rates, streams or nameplates invented | 2026-10-01 |
| X | WP-C1 done locally: modular export packs emit graph-driven `pfd/` (PFD and MFD views as SVG and JSON), `sld.svg` and `sld.json` (electrical EFD), and `bom.csv` and `bom_self_copy.json` from graph nodes and flags; the optional `matplotlib` module copies bridged hub PNG files only (not authority); unused modules off; MVS reference unchanged. WP-C2 and C3 waited on authorisation to publish to GitHub; C2 not started. Plan AQS-PLAN-UI-001 Rev R. No rates, streams or nameplates invented | 2026-10-01 |
| Y | Rewritten to DOC_STYLE (AQS-DOC-002): purpose, terms, tables and revision history; pointer list made a table; VJ reference updated to AQS-ASM-001 §8; values unchanged | 2026-10-24 |
