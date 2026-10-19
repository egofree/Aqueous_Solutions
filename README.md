# Aqueous Solutions

Closed-loop plant that takes any feed, from silicate and oxide regolith to metal-rich scrap (AQS-ASSAY-001), and returns metals, salts, silica, hydrocarbons, and regenerated acid. Energy may be external. A second plant is the replication bar: the mass input is waste or feedstock, not a purchased reagent kit.

License: CERN-OHL-S-2.0.

## What the plant does

One leach tank. Hydrochloric acid and sodium chlorate dissolve the feed at 70–85 °C. Three streams leave that tank.

- Sink solids leave on the floor auger, then a vibratory split. Dense plastic joins the dryer. Glass and ceramic are rinsed, burned out, milled, and digested in sodium hydroxide. Quartz that does not open goes to alkali fusion. Silica is dropped, calcined, and reduced with pyrolyzer char.
- Float leaves over the wall weir, is dried, and is cracked in an induction pyrolyzer. The condensate is split into naphtha (C5–C10), fuel oil (C11–C18), and wax (C19–C32). Bottoms return to the auger. Char is the silicon reductant.
- Liquor is coalesced, filtered, and concentrated on a cation-exchange stack, then electrowon in order from gold through zinc. Lithium and the rare earths are bled before the hydroxide cuts. Aluminum, magnesium, and calcium leave as hydroxides and are reduced in chloride pots. Rare-earth oxides are reduced in a separate calcium retort. Boron oxide is reduced in its own retort, not in the silicon arc.

Spent brine is raised to pH 9. An anion-exchange stack concentrates borate, phosphate, sulfate, and fluoride. The cuts are after the stack. Diluate goes to a potassium chloride crystallizer, then to bipolar-membrane electrodialysis, which makes the hydrochloric acid and the sodium hydroxide. Chlorine from the anodes and the pots is absorbed to sodium chlorate and returned with the acid. Aqueous cells do not make aluminum, magnesium, calcium, lithium, titanium, silicon, or the rare earths.

## The spine

The plant is one parametric system, not a folder of documents that disagree.

- `flow_graph/plant_flow_graph.json` (AQS-FLOW-GRAPH-001, Rev AC) is the sole topology authority: 178 nodes, 493 edges, solved rates and duties on the edges. Every mass-closing unit balances to ≤ 1e-4 kg/d (43 failing units at the Rev AC pivot, 0 now; suite 43/43).
- `flow_graph/param/drivers.json` (AQS-PAR-001) holds every independent number — 700-plus keys under dotted tree paths, each with units and a basis: a published reference, a register id, or a named owner ruling. One number, one door. The loader refuses a value with no basis.
- `flow_graph/system_tree.yaml` (AQS-SYS-TREE-001) is the decomposition: 19 sectors, 30 trains, 249 nodes, 178 unit leaves. Sandboxing resolves through it at four levels (sector / system / subsystem / unit), most specific wins.
- `python3 -m flow_graph.param.regen` is the one command. 44 stages in dependency order, graph convergence by successive substitution, then every derived document against the final graph sha: duties, sizing sheets, ISO sheets, line lists, P&IDs, views, load list, one-line, workbook, and the task plan. It writes a receipt (`flow_graph/derived/_regen_receipt.json`) and the staleness gates in `docs-authority/_rev_stamp.py` turn red if any of the ~876 derived files lags the graph.
- `docs-authority/MODEL_WORKBOOK.xlsx` is the generated 24-sheet view of the same system: drivers with citations, the tree with rolled-up kW, per-sector unit and stream sheets, the electrical chain, and the heat ledger.
- `docs-authority/TASK_PLAN.md` (AQS-PLAN-007) is the work list: 2871 tasks with done-when checks; a task is checked only where a cited file proves it (evidence pass 2026-10-19, `docs-authority/notes/2026-10-19-evidence-pass.md`).

Owner rulings that fixed the blocking decisions (D-AIR, D-O2, D-FARM, D-GEO_ORC, D-PV, D-DOCK) are recorded in `notes/first_principles_audit_2026-10-17.md`: the electrolyzer is the oxygen source with the grow bed as the diverse N+1 pair; the dock is the inter-plant trade boundary with a reported trade statement, not a closure constraint; PV is derived from the bounding load at 2.0× oversize and the roof footprint derives from it; heat is re-used before it is rejected.

## Layout

```
flow_graph/         the graph, system tree, drivers, solver, regen, SVG views
docs-authority/     authority documents, generated duties/sheets, MODEL_WORKBOOK,
                    TASK_PLAN, notes/ (rulings and change records)
design_tool/        FastAPI + React design UI on the unified engine
models/freecad/     FreeCAD builders. SCALE_M = 1.0 is the build size
models/mfg/         CadQuery unit builders (foundry, polymers, reactors, ...) with
                    per-unit export/ STEP, STL, BOM
cad/                STL envelopes and study solids
iso/                ISO sheets
media/pfd/          rendered process sheets
tables/             BOM and material lists
notes/              audit notes and owner rulings
```

Graph SVG views under `flow_graph/views/` are the topology export. They are not a substitute for the equipment sheets. The process sheets in `media/pfd/` are the current disassembly-line drawing set; generators live in `flow_graph/exporters/matplotlib/`. Unit P&IDs are generated (AQS-PID-001-<unit>, 174 sheets, `docs-authority/_pid_sheets.py`) and registered in the drawing register.

## Design tool

`design_tool/` serves the graph read-only: `GET /api/v1/system-tree`, `GET /api/v1/params`, `GET /api/v1/regen-status` (staleness via the same evaluator regen `--check` runs, so a GET never mutates authority docs). The web UI (`design_tool/web/`) renders the tree with four-level toggles, the drivers table with citation badges, and a regen staleness badge. Nothing in the UI writes the graph, the drivers, or the tree; the write path is edit → `python3 -m flow_graph.param.regen`.

## Rebuild

```bash
python3 -m flow_graph.param.regen          # graph + every derived document
cd models && bash REBUILD.sh               # solids
cd models/freecad && /usr/bin/freecadcmd build_plant.py
```

FreeCAD 1.0 and OpenSCAD are required for the solids; CadQuery for the `models/mfg/` unit builders. This tree does not vendor those binaries. `SCALE_M = 1.0` in `models/freecad/params.py` is the manufacturing size. `2.0` is a review scale only. Level datums and the building stack are in `docs-authority/`. See `docs-authority/REBUILD.md` and `docs-authority/BUILD_3D_FROM_FLOW.md`.

## Authority

`docs-authority/AUTHORITY.md` is the lock list. The typed plant graph in `flow_graph/plant_flow_graph.json` is the topology source. Equipment duties written on the process sheets are the drawing source for the disassembly line. Where a sheet and an older note disagree, the sheet is the later drawing. Where a document and the graph disagree, the graph wins and the document is regenerated.
