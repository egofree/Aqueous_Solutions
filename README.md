# Aqueous Solutions

An open design for a closed-loop, feedstock-agnostic plant that sustains
itself. It takes any feed, from silicate and oxide regolith to metal-rich scrap
and mixed waste (AQS-ASSAY-001), and returns metals, salts, silica,
hydrocarbons and regenerated acid. It makes its own reagents, recovers its own
water and air, grows food for its crew, and sells a surplus. The aim is a
design that a shop can build from the files in this repository alone, using
open-source designs, and that is complete enough to build a second plant.

> **Status.** This is a study-grade engineering design under active
> development. Nothing here is stamped by a licensed engineer. Do not build or
> operate any part of it without independent engineering review against the
> codes that apply where you are.

SPDX-License-Identifier: CERN-OHL-S-2.0. See [Licence](#licence).

## Principles

- **Closed loop.** Every mass stream closes: what enters leaves as product,
  recycle or a defined boundary flow. Reagents (HCl, NaOH, chlorate) are
  regenerated inside the plant, not bought as a kit.
- **Feedstock-agnostic.** Units are sized for the bounding case across the
  assay envelope, not for one feed.
- **Size from need.** Every unit, rate and space is sized from actual demand by
  a cited method. A layout restriction that blocks a sized design is revised.
- **Self-sustaining.** Production, power and storage are sized for internal
  demand plus a saleable surplus. PV is oversized (2.0x) so storage still fills
  on a poor day.
- **Redundancy.** Energy and life-support systems (power, O2, water, CO2
  removal, thermal, food, sanitation) carry N+1 or diverse backups, sized for a
  defined outage from a cited code or reliability basis.
- **Open and traceable.** Built from open-source designs (see
  [DEPENDENCIES.md](DEPENDENCIES.md)). Every number is solved by the model,
  cites a published reference, or is a registered assumption with the test that
  would replace it. No supplier quotations as a design basis.

## What the plant does

One leach tank. Hydrochloric acid and sodium chlorate dissolve the feed at
70–85 °C. Three streams leave that tank.

- **Sink solids** leave on the floor auger, then a vibratory split. Dense
  plastic joins the dryer. Glass and ceramic are rinsed, burned out, milled and
  digested in sodium hydroxide. Quartz that does not open goes to alkali fusion.
  Silica is dropped, calcined and reduced with pyrolyzer char.
- **Float** leaves over the wall weir, is dried, and is cracked in an induction
  pyrolyzer. The condensate is split into naphtha (C5–C10), fuel oil (C11–C18)
  and wax (C19–C32). Bottoms return to the auger. Char is the silicon reductant.
- **Liquor** is coalesced, filtered and concentrated on a cation-exchange stack,
  then electrowon in order from gold through zinc. Lithium and the rare earths
  are bled before the hydroxide cuts. Aluminium, magnesium and calcium leave as
  hydroxides and are reduced in chloride pots. Rare-earth oxides and boron oxide
  are reduced in their own retorts.

Spent brine is raised to pH 9. An anion-exchange stack concentrates borate,
phosphate, sulfate and fluoride. Diluate goes to a potassium chloride
crystallizer, then to bipolar-membrane electrodialysis, which makes the
hydrochloric acid and the sodium hydroxide. Chlorine from the anodes and the
pots is absorbed to sodium chlorate and returned with the acid.

Around this process line sit the utilities and life support: roof PV with
electrochemical, gravity (pumped hydro) and methanol storage; a heat ladder that
re-uses heat before it is rejected; water treatment; an electrolyser for oxygen;
a cryogenic gas plant; a farm and habitat; and in-house manufacturing (foundry,
polymers, glass, wafer fabrication) so the plant can make its own parts.

## Authority chain

The plant is one parametric system, not a folder of documents. Information
flows one way:

```
drivers.json + refs.py + assumptions_manual.json      (inputs, each with a basis)
        │
        ▼
flow_graph/plant_flow_graph.json                       (topology authority: units, streams,
        │                                               solved rates and duties)
        ▼
python3 -m flow_graph.param.regen                      (parametric pipeline: solve, size,
        │                                               converge, then generate)
        ▼
generated outputs                                      (duty sheets, sizing sheets, line list,
                                                        isometrics, P&IDs, views, load list,
                                                        one-line, workbook, task plan)
```

- `flow_graph/plant_flow_graph.json` (AQS-FLOW-GRAPH-001) is the sole topology
  authority. Where a document and the graph disagree, the graph wins and the
  document is regenerated.
- `flow_graph/param/drivers.json` (AQS-PAR-001) holds every independent number
  with units and a basis: a reference key in `flow_graph/param/refs.py`, an
  assumption id (A-M-nnn) in `docs-authority/assumptions_manual.json`, or a
  recorded owner ruling. The loader refuses a value with no basis.
- `flow_graph/system_tree.yaml` (AQS-SYS-TREE-001) is the decomposition:
  sectors, trains, subsystems and units.
- `python3 -m flow_graph.param.regen` runs the pipeline stages in dependency
  order (`flow_graph/param/regen_manifest.json`), writes a receipt
  (`flow_graph/derived/_regen_receipt.json`), and the staleness gates in
  `docs-authority/_rev_stamp.py` fail if any derived file lags the graph.
- `docs-authority/AUTHORITY.md` is the lock list of authority documents.

## Repository map

```
flow_graph/           the graph, system tree, schema, solver and regen pipeline
  param/              drivers.json, refs.py, solver, sizing functions, regen manifest
  views/              generated SVG topology views
  exporters/          process-sheet (PFD) generators
docs-authority/       authority documents and everything generated from the graph
  duties/  sizing/    per-unit duty sheets and sizing calculations (generated)
  pid/  iso/          P&IDs and piping isometrics (generated)
  nozzles/  fab/      nozzle schedules and fabrication routes
  inventory/          building-block inventories (motors, wire, pipe, parts)
  notes/              dated change records and rulings
  _*.py               study calculators and document generators
  TASK_PLAN.md        the master task list (AQS-PLAN-007, generated)
  MODEL_WORKBOOK.xlsx the generated workbook view of the model
design_tool/          read-only design API (FastAPI) and web UI (React/Vite)
models/freecad/       FreeCAD builders for the plant general arrangement
models/mfg/           CadQuery unit builders with STEP/STL exports, drawings and BOMs
models/motors/        motor family models
cad/                  STL envelopes (Git LFS) and study solids
media/  iso/  tables/ rendered process sheets, isometric PDF set, BOM tables
notes/                audit notes and owner rulings
```

## Quickstart

Requirements: Git with Git LFS, Python 3.11 or later. FreeCAD 1.0 and CadQuery
are needed only for the CAD builders; Node.js only for the web UI.

```bash
git clone https://github.com/egofree/Aqueous_Solutions.git
cd Aqueous_Solutions
git lfs pull                       # STL envelopes; needed only for CAD work

python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

python3 -m flow_graph.param.regen          # solve the graph and regenerate every derived file
pytest flow_graph/                         # tests, including the 1 % misfit gate
python3 -m flow_graph.param.regen --check  # staleness gates: no derived file lags the graph
python3 flow_graph/check_authority_contract.py
```

`python3 -m flow_graph.param.regen --quick` runs only the graph-writing stages
for a what-if pass. A full run regenerates several hundred documents; run it
before you commit.

CAD (optional):

```bash
cd models/freecad && freecadcmd build_plant.py      # plant general arrangement
python -m flow_graph.param.envelopes --all          # CadQuery unit envelopes (needs cadquery)
```

Design tool (optional): see [design_tool/README.md](design_tool/README.md). It
serves the graph read-only on the local machine; nothing in the UI writes the
graph, the drivers or the tree.

## How to read the outputs

- **Start with the workbook.** `docs-authority/MODEL_WORKBOOK.xlsx` has drivers
  with citations, the system tree with rolled-up power, per-sector unit and
  stream sheets, the electrical chain and the heat ledger.
- **One unit:** its duty sheet `docs-authority/duties/<UNIT>.md` (mass and
  energy in and out, nozzles, relief case), its sizing sheet under
  `docs-authority/sizing/`, its P&ID under `docs-authority/pid/`, and, where
  it exists, its CAD model, drawings and BOM under `models/mfg/<UNIT>/`.
- **Document numbers.** Every document carries an `AQS-...` number, a revision
  and a date; `docs-authority/DOC_REGISTER.md` lists them.
- **Assumptions.** `docs-authority/ASSUMPTIONS_REGISTER.md` (AQS-REG-002) lists
  every A-M-nnn assumption with its basis, sensitivity and the test that would
  replace it.
- **Progress.** `docs-authority/TASK_PLAN.md` lists every task with a "Done
  when" check. A task is ticked only where a cited file proves it. Each open
  task carries a triage tag: desk, hardware or owner.
- **Study, not stamped.** Values marked study are the model's current best
  calculation, not certified figures.

## Contributing

Contributions are welcome: calculations, corrections with a cited basis,
generators, CAD, tests and reviews. Read [CONTRIBUTING.md](CONTRIBUTING.md)
before you open a pull request. The short version: change inputs or generators,
never generated files; cite every number; run the three checks; and keep every
page consistent with the graph in the same commit. Participation is governed by
the [Code of Conduct](CODE_OF_CONDUCT.md). Report security issues privately as
described in [SECURITY.md](SECURITY.md).

## Licence

Aqueous Solutions is licensed under the **CERN Open Hardware Licence Version 2 –
Strongly Reciprocal** (CERN-OHL-S-2.0). The full text is in [LICENSE](LICENSE).

```
SPDX-License-Identifier: CERN-OHL-S-2.0
Copyright 2026 Mike Matthews and contributors.
Source Location: https://github.com/egofree/Aqueous_Solutions
```

The licence is inherited from the SEM-Tech open membrane project
(S.E.M Technology / Rowow), whose membranes, cell and stack architectures are
released under CERN-OHL-S and which this plant uses in its wet line (chlorate
leach, electrowinning, bipolar-membrane regeneration). Using the same strongly
reciprocal licence keeps the combined design compatible with that work: anyone
who conveys a modified design, or a product built from it, must make the
complete corresponding source available under CERN-OHL-S-2.0 and state where it
is. This project is not a Rowow product, and the licence does not grant use of
the Rowow name or imply its endorsement. Other open designs the plant draws on
keep their own licences and are linked, not bundled; see
[DEPENDENCIES.md](DEPENDENCIES.md).

The design is provided without warranty of any kind; see section 6 of the
licence.
