# Status board

Document number: AQS-PLAN-004
Revision: A
Date: 2026-10-12
Authority: graph Rev BH. Not a PE stamp. Line C6 closed in this revision. No rate change.

This is the work order for AQS-PLAN-005. A line closes only when the cited file holds the result, the check on that line passes, the present kilogram-per-day nodes still close, and this page is updated in the same commit.

## Closed at Rev BH

| Item | Where |
| --- | --- |
| Present kg/d nodes, \|in − out\| ≤ 1e-4 | `flow_graph/plant_flow_graph.json`, 169 nodes, 0 off |
| Synthesis reactions | `docs-authority/SOLVENT_ROUTE.md`, commit 682b64e |
| Both air returns | commit c8eb942 |
| Copper-equivalent electrowinning. Assay left open. | `docs-authority/CHECKS.md` |
| Frame parameter set | `docs-authority/PATH_MODULES.md` |
| One duty page per present unit | `docs-authority/duties/` |
| MVS loops flag | hold. `mvs.mvs_criteria.loops_closed` is false |

## Open

Active: C7

AQS-PLAN-005 Rev C is the completion sequence. Line 2.2 is closed by C2 and C3.

| Line | Phase | Work | Check | Status |
| --- | --- | --- | --- | --- |
| 0.1 | 0 | Revision notes Q through BH. Mark drawings that still say Rev N. | Each issued letter Q–BH has `notes_rev_*`. AQ is recorded as not issued. Derived pages and view files say they are not current, or they name BH. No edge rate changes. | closed. 44 notes on the graph. 531 edge rates unchanged. 169 kg/d nodes, 0 off. View json, dot, and svg, and the derived pages other than `LOOP_CLOSURE.md`, are marked not current. |
| 0.2 | 0 | Cut test | `python3 flow_graph/loop_closure.py` is run. The report names the graph revision and says the result is not the MVS flag. `mvs.mvs_criteria.loops_closed` stays false. The root `loops_closed` key is reconciled with that report in the same commit. | closed. Report `flow_graph/derived/LOOP_CLOSURE.md` names Rev BH, all eight components pass within 1%, and the last line says the result is not the MVS flag. Root `loops_closed` left true. `mvs.mvs_criteria.loops_closed` left false. Mass-layer kg/d nodes 169, 0 off at 1e-4. No rate change. |
| 0.3 | 0 | Electrical and thermal book | `ONE_LINE.md`, `POWER.md`, and `HEAT_LADDER.md` name the graph revision they were checked against, or the page is stamped not current. No rate change. | closed. `ONE_LINE.md` names Rev BH. IA-PV-01 is 27.88 kW on the edge. `POWER.md` names Rev BH and is not current for the EW-1 current: the page says 5.3 kW, the node is 6.0 kW study. `HEAT_LADDER.md` names Rev BH. HX-8 and the Q3 draws are present. No present edge from Q1, Q2, or Q3 lands on Q4_BUS. `HEAT_LADDER_DUTIES.md` stays the Rev K note. No rate change. |
| 1.1 | 1 | Feed assay and the sheet split | The assay is a measured composition on the edge, or the line names the missing measurement. No resize before that composition is on the edge. | closed by the missing measurement. IA-FEED-01, S08, and S16 still carry the placeholder water 0.90, HCl 0.05, Fe 0.02, other_metals 0.03. IA-EW-SHEET is metal 1.0. ELECTRICAL.md working averages were not copied onto the edge. No resize. No rate change. |
| 1.2 | 1 | Digester | `DIGESTER.md` section 8. Biological feeds do not leave entirely as one gas edge, or the line names the missing volatile-solids measurement. | closed by the missing measurement. IA-FERM-RES, IA-STILL, and IA-ABE-STILL sum to IA-DIG-GAS, 0.6254 kg/d. Section 8 names the missing volatile-solids measurement. No digestate was added. No rate change. |
| 1.3 | 1 | Other streams that already have a composition object | No unit is resized. The line names any inlet that is still not a measurement. | closed by the missing measurement. 450 present kg/d edges, 14 composition objects, none measured. No resize. No rate change. |
| 2.1 | 2 | Four units with no class | Each of the four has a class taken from its edges and its duty. No rate change. | closed. AFTERBURNER_FLUE header. CRYO_AHU_COND_CONDENSABLE separator. GEO_HP_CLOSED_LOOP thermal. S13_CLASS_TREAT treat. No rate change. |
| 2.2 | 2 | Nozzles and a line list | A present connection has a nozzle location and a flange rating, or the line names what is missing. Phase 2 is not accepted until a connection can be built. | closed by C2 and C3. Placed units have a face, a height, and a rating. Atmospheric rating is hose, not a flange class. TERRACE_IRRIG has no height on the seed. No rate change. |
| 4.1 | 4 | Relief on pressurized nodes | Each pressurized node has a case and a destination. Each atmospheric node says so. | waits. Phase 2 is not accepted. One case is already on EXPANDER: 550 kPa to CRYO_ASU. The other stored design_kPa values are the old head-plus-10 figures. |
| 5.1 | 5 | Solids | Operator box. Meshes match the duties at the revision that enters the phase. | waits. Phase 2 is not accepted. Meshes are not in this repo session. |
| R1 | — | Three hydrogen edges with no layer | The edges say they are outside the mass cut. Rates unchanged. Mass-layer nodes still close. | closed. IA-HDR-H2-01, IA-HDR-H2-03, and IA-HDR-H2-04 remain 2.1333 kg/d with an empty layer list. Mass-layer kg/d nodes 169, 0 off at 1e-4. |
| R2 | — | Expander stored pressure | The node matches the written set point. The orifice is not resized. | closed. EXPANDER design_kPa is 550. Destination CRYO_ASU on IA-EXP-OUT. relief_mm left at 3.6. No edge rate change. |
| C1 | C | Nozzle rule, holds, counts | The rule is on AQS-PLAN-005. No rate change. | closed. Rev C of `docs-authority/PROJECT_PLAN.md`. Atmospheric joints are hose. 72 placed, 43 in a block without an origin, 84 in no block. |
| C2 | C | HX8 nozzles | The duty matches the two 2.286 kW edges. Two nozzles follow the rule. No rate change. | closed. Heat in 4.572 kW on IA-HX8. Out 2.286 kW on HL-HX8-Q4-A and HL-HX8-Q4-B. N2 and N3 on the +Y face, DN25 from the edge, hose. N1 on the −Y face, bore not calculated. No rate change. |
| C3 | C | Nozzles on the other placed units | Face, height, and rating, or the bore is named as not calculated. | closed. 71 duties. Every present edge on those units is named. DN only where the edge already had line_DN. Conductors are not hoses. TERRACE_IRRIG has no height, so no face. No rate change. |
| C4 | C | Origins for the 43 block members | Inside the block, or named as not fitting. No plate growth. | closed. LEACH_CSTR_1, EW_1, EW_2, and EW_9 are in LEACH_EW at z −6000, 600 mm clear. The other 39 have no envelope. No origin was written for them. The plate did not grow. No rate change. |
| C5 | C | The 84 with no block | Farm beds larger than the block are named, not shrunk. | closed. Twenty envelopes are in the sector block. AZOLLA_BED stays 18 m by 5 m, long side on the farm block. CURTAIL and HEAT_SINK have no GEO block and were not placed. Sixty-two have no envelope. The plate did not grow. No rate change. |
| C6 | C | Generic internals | No node still says "shell and nozzles" or "media or gutter". | closed. 146 generic strings replaced. 12 took the class row. 75 of farm, tool, inverter, pv, rectifier, and hab are none, not a tank. 59 with no vessel row are none and not drawn. 53 specific strings left, including the nine cells. No rate change. Mass-layer kg/d nodes 169, 0 off. |
| C7 | C | Relief destinations | Atmospheric nodes name an existing vent edge, or say there is none. | waits |
| C8 | C | Section 8 | Empty, or only a hold. | waits |
| C9 | C | Meshes | An STL, or the solid is still an envelope. | waits |
| C10 | C | Self-copy | Not started until C2 through C9 are accepted. | waits |
