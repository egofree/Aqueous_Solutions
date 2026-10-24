# Agent and contributor rules

These rules apply to anyone changing the model, human or automated. They
complement [CONTRIBUTING.md](CONTRIBUTING.md). Follow the plan file. Do not keep
a second list of exceptions.

## Repository roles

- `flow_graph/plant_flow_graph.json` is the sole topology authority.
  `flow_graph/param/drivers.json` holds every input parameter. Registered
  references (`flow_graph/param/refs.py`) and A-M assumptions
  (`docs-authority/assumptions_manual.json`) back both.
- **Generated artifacts are never hand-edited**: duties (`docs-authority/duties/`),
  sizing (`docs-authority/sizing/`), views (`flow_graph/views/`), registers,
  `docs-authority/MODEL_WORKBOOK.xlsx`, P&IDs (`docs-authority/pid/`) and the task
  plan. They regenerate with `python3 -m flow_graph.param.regen`.
- Use paths relative to the repository root in code and documents. Do not commit
  machine-specific paths, credentials, personal data, or tool and session scratch
  files.

## Verification

After any graph, drivers or transfer-function change, in order:

1. `pytest flow_graph/` (includes the 1 % misfit gate)
2. `python3 -m flow_graph.param.regen --check` (staleness gates)
3. `python3 flow_graph/check_authority_contract.py` (authority contract)

All three must pass before a commit. Each change carries a dated change record in
`notes/` or `docs-authority/notes/`; the task plan's evidence pass reads them.

## Environment

- STLs and FreeCAD files are stored with Git LFS. Run `git lfs pull` before CAD
  work.
- Python dependencies are in `requirements.txt`. CadQuery and FreeCAD are only
  needed for the CAD builders; set the `CADQUERY_PYTHON` environment variable if
  CadQuery lives in a separate interpreter.
- `docs-authority/_*.py` are the study calculators and generators (keep the
  naming). Some one-shot historical studies pin a frozen graph by git ref and are
  not part of the regeneration pipeline.

## Concurrency

- When more than one process may write the model at the same time, serialise
  every write to the graph, `drivers.json` or `refs.py` with a lock, for example
  `flock "${AQS_LOCK:-.aqs-design.lock}" <command>`. Writers that skip the lock
  corrupt each other's staged JSON. The lock file is ignored by git.
- If an interrupted session leaves partial work, inventory `git status` and
  finish the work from the script headers and assert messages, which carry the
  design intent. Do not restart the same objective from scratch without checking
  what is already on disk.

## Regenerator

- `flow_graph/param/regen_manifest.json` is the stage graph. `--quick` runs only
  the graph-writing stages (no documents, no receipt) for what-if passes. The
  design check (AQS-QA-002) refreshes on every full run.
- `balance --write` is the proven regime. If the graph hash cycles after a writer
  change, instrument signature hashes across full passes before reverting; a
  quantised threshold flip shows as a two-point cycle.
- Coverage gaps usually hide in a unit-list filter in a generator, not in missing
  data. Extend the generator and rerun it; never hand-edit its output.

## Loop

1. Read the plan. The master task list is `docs-authority/TASK_PLAN.md`
   (AQS-PLAN-007). Engineering limits and holds are in
   `docs-authority/PROJECT_PLAN.md`. The close-out record is
   `docs-authority/MASTER_PLAN.md`. Tick a task only with a cited file, and rerun
   `docs-authority/_task_plan_gen.py`.
2. Read only the authority the active item needs.
3. Do that item. Stay inside what it asks.
4. Prove it. Run the check the plan states for that item. The check is on the
   files, not on the intention.
5. Write the proof back. In the same commit, update the status board and every
   page the change made untrue. A revision note moves with a revision. A drawing
   or derived file that still names an older revision is regenerated or marked.
6. Stop. The item is done when its check passes and the board matches the files.
   If the check cannot pass, record the missing fact on the board and stop.

## Assumptions

Every new assumption gets an entry in `docs-authority/assumptions_manual.json` in
the same commit (value, units, where used, basis, sensitivity, replacing test,
task). Run `docs-authority/_assumptions_register.py`; it regenerates AQS-REG-002
and fails on a bad entry.

## Sizing

Values the parametric model solves (AQS-PAR-001) come from
`flow_graph/param/solver.py` with drivers in `flow_graph/param/drivers.json` and
references in `refs.py`. `python3 -m flow_graph.param.write_graph` writes them to
the graph, and `pytest flow_graph/param/test_param_misfit.py` fails on a misfit
over 1 %. Nothing is fixed arbitrarily. Size every unit, rate and space for the
bounding case from actual need (AQS-ASSAY-001 envelope, AQS-ELEC-007 bounding
load). Constraints exist only to make the parts integrate. When a restriction
blocks a sized design, revise the restriction. Sizing-driven rate and layout
changes are approved by default; each is still documented, propagated to every
affected file, register-tracked, and committed with the checks passing.
Supplier quotations and vendor data are not a design basis.

## Regeneration

After any change to the graph, the drivers or a transfer function, run
`python3 -m flow_graph.param.regen` (AQS-PAR-001). The receipt it writes and the
staleness gates in `docs-authority/_rev_stamp.py` prove the tree is current.

## Self-sustaining plant

The plant produces commodities beyond its internal needs, so it sustains itself
in money as well as in material. Production, power and storage are sized for
internal demand plus a saleable surplus, and every surplus stream has a defined
outlet (product store, export meter). PV is sized at `pv_oversize_factor` (2.0)
times the nameplate that closes the daily balance.

## Redundancy

Build redundancy into every energy and life-support system wherever possible
(power, O2, water, CO2 removal, thermal, food, sanitation). A backup that looks
surplus to the daily balance is intentional; do not recommend removing it on
need alone. Size each backup by calculation for a defined outage of the primary
(N+1 or a diverse technology), with the duration from a cited reliability or code
basis (for example NFPA 110 / NFPA 111), and track it in the X-RED tasks.

## Owner decisions

Questions that need the project owner's decision go in
`docs-authority/OPEN_QUESTIONS.md` with the default the work proceeds on. Do not
decide them silently.

## Done

Housekeeping is part of the item, not a later pass. A commit that changes the
work and leaves the board or a contradicted page behind is not done. Do not
bypass hooks or checks, rewrite published history, or force-push.

The plan holds the engineering limits. Read them there when an item touches them.
Do not copy them into this file.
