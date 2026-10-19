# Agent rules

Follow the plan file. Do not keep a second list of exceptions.

## Loop

1. Read the plan. The master task list is `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). The engineering limits and holds are in `docs-authority/PROJECT_PLAN.md`. The close-out record of plan lines is `docs-authority/MASTER_PLAN.md`. Check a task on AQS-PLAN-007 only with a cited file, and rerun `docs-authority/_task_plan_gen.py`. The plan names the authority and the active item.
2. Read only the authority the active item needs. Confirm the item is still the active one.
3. Do that item. Stay inside what it asks.
4. Prove it. Run the check the plan states for that item. The check is on the files, not on the intention.
5. Write the proof back. In the same commit, set the line on the status board and update every page the change made untrue. A revision note moves with a revision. A drawing or a derived file that still names an older revision is marked or regenerated. The next session starts from the files alone.
6. Stop. The item is done when its check passes and the board matches the files. If the check cannot pass, write the missing fact on the board and stop. The next item waits.

## Assumptions

Every new assumption gets an entry in `docs-authority/assumptions_manual.json` in the same commit (value, units, where used, basis, sensitivity, replacing test, task). Run `docs-authority/_assumptions_register.py`; it regenerates AQS-REG-002 and fails on a bad entry.

## Sizing

Values the parametric model solves (AQS-PAR-001) come from `flow_graph/param/solver.py` with drivers in `flow_graph/param/drivers.json` and references in `refs.py`; `python3 -m flow_graph.param.write_graph` writes them to the graph, and `pytest flow_graph/param/test_param_misfit.py` fails on a misfit over 1 %. Nothing is fixed arbitrarily. Size every unit, rate, and space for the bounding case from actual need (AQS-ASSAY-001 envelope, AQS-ELEC-007 bounding load). Constraints exist only to make the parts integrate. When a restriction (block size, cell pitch, held rate, "no rate change") blocks a sized design, revise the restriction. Sizing-driven rate and layout changes are approved by default. Each one is still documented, propagated to every affected file, register-tracked, and committed with the checks passing. Owner rule, Mike Matthews, 2026-10-15.

## Regeneration

After any change to the graph, the drivers, or a transfer function, run `python3 -m flow_graph.param.regen` (AQS-PAR-001). The receipt it writes and the staleness gates in `docs-authority/_rev_stamp.py` are the proof the tree is current; the workbook, views, sheets, P&IDs, and task plan regenerate with it. Owner rule, 2026-10-19.

## Self-sustaining plant

The plant produces commodities beyond its internal needs, so it sustains itself in money as well as in material. Production rates, power and storage are sized for internal demand plus a saleable surplus, and every surplus stream has a defined outlet (product store, export meter). PV is sized at `pv_oversize_factor` (2.0) times the nameplate that closes the daily balance: storage still fills on a day at half the mean yield, and the clear-day surplus is exported to the grid when a utility connection exists. Owner rule, Mike Matthews, 2026-10-15 (MASTER_PLAN D75).

## Redundancy

Build redundancy into every energy and life-support system wherever possible (power, O2, water, CO2 removal, thermal, food, sanitation) so the plant rides through failure or downtime of a primary system. A backup that looks surplus to the daily balance is intentional: do not recommend removing it on need alone. Size each backup by calculation for a defined outage of the primary (N+1, or a diverse technology), with the duration taken from a cited reliability or code basis (for example NFPA 110 / NFPA 111 class), and track it in the X-RED tasks. Owner rule, Mike Matthews, 2026-10-15.

## Done

Housekeeping is part of the item, not a later pass. A commit that changes the work and leaves the board or a contradicted page behind is not done.

The plan holds the engineering limits. Read them there when the item touches them. Do not copy them into this file.
