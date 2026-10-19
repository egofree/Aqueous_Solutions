# Status board

Document number: AQS-PLAN-004
Revision: A
Date: 2026-10-12
Authority: graph Rev AC. Not a PE stamp. Line 0.1 closed at Rev BH. No rate change.

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

## Closed at Rev AC (2026-10-18/19)

| Item | Where |
| --- | --- |
| D-AIR: CRYO_ASU restored verbatim as the species-conserving recovery box (not an O2 source) | commit 0ed33bb; ruling in `notes/first_principles_audit_2026-10-17.md` |
| D-O2: H2O_ELYZ restored as the oxygen source; diverse N+1 pair with GROW_BED | ruling commit 9b742c4, implementation commit 8189cd1 |
| D-FARM: GROW_BED re-based to crew duty (29.12 m², BVAD2022 DLI-17); TERRACE_IRRIG deleted | commit aba0c4b |
| D-GEO_ORC: heat study encoded reuse-first (HX-9/10 restored, DRY_COOLER rated sink, MET_HX_Q4 rated) | commit 1854208 |
| D-PV: PV parametric from live demand at 2.0× oversize, footprint derived from the array; fixed point 3910 kWp | commits 1854208, ea55066; ruling D-PV 2026-10-18 |
| D-DOCK: dock reclassified as the inter-plant trade boundary (closure-exempt, reported trade statement +0.003 kg/d net); buffer stores AIR_RECEIVER / FOOD_STORE / METAL_STORE | ruling commit b9f3b55, implementation commit 66187cc |
| Balance closed: failing units 43 → 0; `balance --write` convergent and restored in the regen manifest | commits 66187cc, ffbfd90 |
| One governed number: 700+ cited driver keys under dotted tree paths (`flow_graph/param/drivers.json`) | commits dfa2c0a, 8dc0a49 |
| System tree AQS-SYS-TREE-001: 19 sectors / 30 trains / 178 leaves, most-specific-wins toggles | commit eedb79f, `flow_graph/system_tree.yaml` |
| One-command regeneration: 44-stage manifest, successive substitution, receipt + staleness gates | commit d44e7de, `flow_graph/param/regen.py` |
| Generated model workbook (24 sheets, zero hand-maintained numbers) | commit b79ac62, `docs-authority/MODEL_WORKBOOK.xlsx` |
| Working design UI on the unified engine (system-tree / params / regen-status endpoints; tree, drivers, staleness panels) | commit 5024743, `design_tool/web/` |
| T03 P&IDs: 174 graph-derived sheets, AQS-PID-001 series | commits ba310b7, bfea3c8, `docs-authority/_pid_sheets.py` |
| FOUNDRY / POLYMERS study-grade sizing from live demand | commit 882e87a (AQS-DUTY-072/073) |
| FOUNDRY / POLYMERS CadQuery builders (live trains + standby placeholders) | `models/mfg/foundry.py`, `models/mfg/polymers.py` — pending commit |
| Suite green: 43 passed / 0 failed, first fully green suite since the Rev AC pivot | commits 049c93e, 2f96524 |
| Evidence honesty pass: 62 tasks cited, 6 reopened, zero `Evidence: None` | commit 66187cc, `docs-authority/notes/2026-10-19-evidence-pass.md` |

## Open

Active: 0.2

## Current status (2026-10-19)

Graph Rev AC. The unified parametric system is built and current: drivers, system tree, one-command regen with receipt and staleness gates, generated workbook, design UI, graph-derived P&IDs (see the Closed at Rev AC table). Balance: 0 failing units, `balance --write` convergent, suite 43/43. TASK_PLAN regenerated with the evidence honesty pass (568 of 2871 done; `docs-authority/notes/2026-10-19-evidence-pass.md`). FOUNDRY/POLYMERS CadQuery builders and the restored-unit/store CAD are in flight (pending commit). `loops_closed` false. Line 0.2 (cut test) remains open.

## Current status (2026-10-17)

Graph Rev AC. Item 10 closure pass: assumption rates on 25 edges (notes/CLOSURE_PASS.md). loops_closed false. Cut-test script not in this workspace; line 0.2 remains open.

Items 1–9 issued. See notes/LOAD_ROLLUP.md, DIGESTER_LI.md, OIL_POLY_SIZE.md, FOUNDRY_MFG_SIZE.md, GLASS_GAS_CRYO.md, FAB_DESIGN.md, LIFE_SUPPORT.md, POWER_DUTIES.md, DOCK_BOUNDARY.md.

Assays remain deferred (notes/ASSAY_TI_MO.md).

## Historical scope notes (2026-10-16)

Assays deferred (notes/ASSAY_TI_MO.md). Kroll Cl₂/Mg balance complete as stoichiometric check (notes/KROLL_BALANCE.md). CR_CELL duty locked (notes/CR_CELL_DUTY.md). Fluoropolymer train duties locked at concept level (notes/FLUOROPOLYMER_DUTY.md). Rates unset. Active item 0.2 remains open.

Graph Rev K. Missing assays named (notes/ASSAY_TI_MO.md). Kroll placeholder balance shows net-zero Cl₂ and Mg if the existing pot has spare capacity (notes/KROLL_BALANCE.md); not a design rate. CR_CELL duty locked as molten-salt primary (notes/CR_CELL_DUTY.md). Rates unset. Active item 0.2 remains open.

User decisions close external supply for fluoropolymers and for Cr/Mo/Ti (and dependent stainless). Graph Rev J locks TI_CELL (Kroll primary, FFC cold spare) and MO_CELL (molten-salt primary) with Cl₂/anode-gas returns to CRU. Duties: notes/TI_MO_DUTIES.md Rev B. Selection: notes/TI_MO_SELECTION.md. Active item 0.2 (cut test) remains open. Rates unset.

User decisions close external supply for fluoropolymers and for Cr/Mo/Ti (and dependent stainless). Graph Rev I adds F_RECOVER, HF_GEN, VDF_SYN, TFE_SYN, POLY_F, CR_CELL, TI_CELL, MO_CELL with placeholder edges. Duties for TI/MO in notes/TI_MO_DUTIES.md. See notes/BINDING_REQ_2026-10-16.md. Active item 0.2 (cut test) remains open.

| Line | Phase | Work | Check | Status |
| --- | --- | --- | --- | --- |
| 0.1 | 0 | Revision notes Q through BH. Mark drawings that still say Rev N. | Each issued letter Q–BH has `notes_rev_*`. AQ is recorded as not issued. Derived pages and view files say they are not current, or they name BH. No edge rate changes. | closed. 44 notes on the graph. 531 edge rates unchanged. 169 kg/d nodes, 0 off. Derived markdown, and view json, dot, and svg, are marked not current. |
| 0.2 | 0 | Cut test | `python3 flow_graph/loop_closure.py` is run. The report names the graph revision and says the result is not the MVS flag. `mvs.mvs_criteria.loops_closed` stays false. The root `loops_closed` key is reconciled with that report in the same commit. | open |
| 0.3 | 0 | Electrical and thermal book | `ONE_LINE.md`, `POWER.md`, and `HEAT_LADDER.md` name the graph revision they were checked against, or the page is stamped not current. No rate change. | closed for this workspace. ONE_LINE.md and POWER.md issued Rev AC. HEAT_LADDER.md checked Rev X. |
| 1.1 | 1 | Feed assay and the sheet split | The assay is a measured composition on the edge, or the line names the missing measurement. No resize before that composition is on the edge. | waits |
| 1.2 | 1 | Digester | `DIGESTER.md` section 8. Biological feeds do not leave entirely as one gas edge, or the line names the missing volatile-solids measurement. | waits |
| 4.1 | 4 | Relief on pressurized nodes | Each pressurized node has a case and a destination. Each atmospheric node says so. | waits |
| 5.1 | 5 | Solids | Operator box. Meshes match the duties at the revision that enters the phase. | waits |
