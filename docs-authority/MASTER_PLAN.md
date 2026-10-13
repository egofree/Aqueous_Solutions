# Status board

Document number: AQS-PLAN-004
Revision: A
Date: 2026-10-12
Authority: graph Rev BH. Not a PE stamp. Line 0.3 closed in this revision. No rate change.

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

Active: 1.1

| Line | Phase | Work | Check | Status |
| --- | --- | --- | --- | --- |
| 0.1 | 0 | Revision notes Q through BH. Mark drawings that still say Rev N. | Each issued letter Q–BH has `notes_rev_*`. AQ is recorded as not issued. Derived pages and view files say they are not current, or they name BH. No edge rate changes. | closed. 44 notes on the graph. 531 edge rates unchanged. 169 kg/d nodes, 0 off. View json, dot, and svg, and the derived pages other than `LOOP_CLOSURE.md`, are marked not current. |
| 0.2 | 0 | Cut test | `python3 flow_graph/loop_closure.py` is run. The report names the graph revision and says the result is not the MVS flag. `mvs.mvs_criteria.loops_closed` stays false. The root `loops_closed` key is reconciled with that report in the same commit. | closed. Report `flow_graph/derived/LOOP_CLOSURE.md` names Rev BH, all eight components pass within 1%, and the last line says the result is not the MVS flag. Root `loops_closed` left true. `mvs.mvs_criteria.loops_closed` left false. Mass-layer kg/d nodes 169, 0 off at 1e-4. No rate change. |
| 0.3 | 0 | Electrical and thermal book | `ONE_LINE.md`, `POWER.md`, and `HEAT_LADDER.md` name the graph revision they were checked against, or the page is stamped not current. No rate change. | closed. `ONE_LINE.md` names Rev BH. IA-PV-01 is 27.88 kW on the edge. `POWER.md` names Rev BH and is not current for the EW-1 current: the page says 5.3 kW, the node is 6.0 kW study. `HEAT_LADDER.md` names Rev BH. HX-8 and the Q3 draws are present. No present edge from Q1, Q2, or Q3 lands on Q4_BUS. `HEAT_LADDER_DUTIES.md` stays the Rev K note. No rate change. |
| 0.3 | 0 | Electrical and thermal book | `ONE_LINE.md`, `POWER.md`, and `HEAT_LADDER.md` name the graph revision they were checked against, or the page is stamped not current. No rate change. | waits |
| 1.1 | 1 | Feed assay and the sheet split | The assay is a measured composition on the edge, or the line names the missing measurement. No resize before that composition is on the edge. | waits |
| 1.2 | 1 | Digester | `DIGESTER.md` section 8. Biological feeds do not leave entirely as one gas edge, or the line names the missing volatile-solids measurement. | waits |
| 4.1 | 4 | Relief on pressurized nodes | Each pressurized node has a case and a destination. Each atmospheric node says so. | waits |
| 5.1 | 5 | Solids | Operator box. Meshes match the duties at the revision that enters the phase. | waits |
