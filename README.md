# Aqueous Solutions

Aqueous Solutions is an open engineering design for a small industrial plant that recycles mixed waste and mineral feed into refined materials, and that also houses and feeds the people who run it. This repository holds the whole design: a model of every unit in the plant and every stream between units, the code that sizes each unit from published sources, and the engineering documents and computer-aided design (CAD) models generated from that model. The design is released under the CERN Open Hardware Licence Version 2, Strongly Reciprocal (CERN-OHL-S-2.0).

The design is a study. No part of the plant has been built or tested, and no licensed engineer has reviewed or stamped any part of it. Do not build or operate any part of it without an independent engineering review against the codes that apply where you are.

## 1. What the plant does

### 1.1 Feed and products

The plant is designed to accept solid feed whose composition is uncertain and changes from lot to lot. The feed can be crushed silicate or oxide rock, metal-rich scrap such as printed circuit boards, mixed waste, or any mixture of these. The feed assay schema in `docs-authority/FEED_ASSAY.md` (AQS-ASSAY-001) describes each feed lot as mass fractions in a fixed set of classes, for example free water, metals that can be plated from solution, reactive metals, and silicates and oxides. Each unit is sized for the feed in that range that places the largest load on it.

The products are refined metals, salts, silica and silicon, glass, hydrocarbon fuels and waxes, and polymers. The plant's own workshops turn these materials into parts. The plant also makes clean water, food and electricity for its own use.

### 1.2 The process line

Feed enters a heated leach tank, where hydrochloric acid and sodium chlorate dissolve the metals. The material then separates into three streams:

1. Solids that sink to the floor of the tank are removed and sorted. Glass and ceramic are milled and dissolved in sodium hydroxide to recover silica. The silica is reduced to silicon with carbon char from the pyrolysis reactor described in item 2.
2. Material that floats is mostly plastic and other organic matter. It is dried and then heated without air in a pyrolysis reactor. The vapour is condensed and separated into naphtha, fuel oil and wax.
3. The liquid carries the dissolved metals. It passes through a series of electrowinning cells, each of which plates one group of metals onto a cathode. Aluminium, magnesium and calcium cannot be plated from a water solution, so they are precipitated as hydroxides and then reduced to metal in cells that run on molten chloride salt.

After the metals are removed, the remaining salt solution is split back into hydrochloric acid and sodium hydroxide by bipolar-membrane electrodialysis (BMED). BMED is a membrane stack that uses electric current to separate a salt solution into an acid and a base. Chlorine gas released at the electrowinning and BMED anodes is converted to sodium chlorate in the chlorate regeneration unit and returned to the leach tank. In this way the plant makes its main reagents again from its own spent solution.

### 1.3 Utilities and life support

A roof photovoltaic (PV) array supplies the electricity. Three energy stores hold it for use at night and on dull days: a zinc-bromine flow battery, a methanol system that makes methanol from hydrogen and carbon dioxide and turns it back into electricity in a fuel cell, and a pumped-hydro set that moves water between a roof reservoir and a catch tank. A hydrogen fuel cell runs on the plant's own process hydrogen, and a standby generator supplies the critical loads during an outage.

Heat released by the hot processes is collected in a series of thermal stores, each kept at a lower temperature than the one before it. Heat from a hot process is therefore used again by cooler processes before it is finally rejected. This arrangement, the heat ladder, is described in `docs-authority/HEAT_LADDER.md` (AQS-HEAT-LADDER-001).

Water is recovered from process condensate and from the crew's waste water, then treated, distilled and stored in tanks on the roof and at ground level. An electrolyser splits water into hydrogen and oxygen, and a gas plant purifies and stores oxygen, nitrogen, carbon dioxide and hydrogen. A farm grows food for the crew, and the crew's living quarters are part of the plant. The plant's workshops include a foundry, a polymer line, a glass line and a wafer fabrication line, which make spare parts and new equipment.

### 1.4 Why the plant is meant to sustain itself

The plant is designed to keep running on its own feed and energy, and to produce more food, clean water, materials and energy than it uses. The surplus is sold through the plant's dock, so that the plant earns an income as well as supplying itself. `docs-authority/SURPLUS_PASS_THRESHOLDS.md` (AQS-SUR-001) sets the minimum surplus of each kind that the design must reach.

Every system that keeps the crew alive has a spare unit or a second source that works in a different way. These systems are power, oxygen, water, carbon dioxide removal, heating and cooling, food and sanitation. The spare capacity is sized for an outage of a stated length, taken from a cited code or reliability basis.

The long-term goal is a plant that can make the parts needed to build a second plant from the same kinds of feed. `docs-authority/SELF_COPY_BOM.md` (AQS-BOM-SC-001) records which of those parts the plant can make today and which it cannot.

## 2. How the design is built

### 2.1 Sectors

The model groups the plant's units into sectors. A sector is a set of units that do one job, such as metal recovery or water treatment, and it has an upper-case identifier that is used in file names and on drawings. Table 2.1 lists the sectors by kind. A test (`flow_graph/test_doc_consistency.py`) compares this table with the sector list in the plant graph and fails if the two differ. `docs-authority/SECTOR_DEFINITIONS.md` (AQS-SEC-001) defines each sector in full.

Table 2.1. Plant sectors by kind

| Kind | Sectors |
|---|---|
| Process | DIGESTER (leach tank, electrowinning, and acid and base regeneration), OIL (drying, pyrolysis and separation of hydrocarbons), GLASS (glass and ceramic recovery, and silicon reduction), GAS (gas cleaning and the hydrogen and oxygen headers), FOUNDRY (melting, casting, forming and molten-salt metal cells), POLYMERS (polymer synthesis and forming), FAB (wafer and solar cell fabrication), MFG (machine shop and metal working), NUT (nutrient dosing for the farm) |
| Life support | FARM (grow beds and food store), HAB (living quarters) |
| Utilities | CRYO (gas separation and storage), WTR (water collection and treatment), ELEC (PV array, flow battery, standby generator, fuel cell and power distribution), HEAT (the heat ladder), GEO (ground heat exchanger and heat pump) |
| Energy storage | MEOH (methanol synthesis, storage and fuel cell), PUMPED_HYDRO (roof reservoir and turbine-pump) |
| Export | DOCK (the dock through which surplus is shipped and feed is received) |

### 2.2 The plant graph and its inputs

The plant graph, `flow_graph/plant_flow_graph.json` (AQS-FLOW-GRAPH-001), is the single record of the plant's layout. It lists every unit and every stream that connects two units, with the solved flow rate, composition and energy duty of each. Where a document disagrees with the graph, the graph is correct and the document is regenerated. `flow_graph/system_tree.yaml` (AQS-SYS-TREE-001) arranges the units into sectors, trains and subsystems.

Every independent number in the model is stored once, with its unit and its basis, in `flow_graph/param/drivers.json` (AQS-PAR-001). The basis is one of three kinds. It can be a published source registered in `flow_graph/param/refs.py`, an assumption with an identifier of the form A-M-nnn recorded in `docs-authority/assumptions_manual.json` together with the test that would replace it, or a recorded decision by the project owner. The loader refuses a number that has no basis. The editions of the codes and standards that the design cites are kept in a single table in `flow_graph/param/code_basis.py`, and a test fails if any file cites a different edition.

### 2.3 Sizing and generated outputs

The command `python3 -m flow_graph.param.regen` runs the design pipeline. It solves the mass and energy balances on the graph, sizes each unit from its duty by a cited method, repeats until the results stop changing, and then writes the documents. The generated documents include a duty sheet and a sizing sheet for each unit, piping and instrumentation diagrams (P&IDs), piping isometrics, the line list, the electrical load list and one-line diagram, the model workbook `docs-authority/MODEL_WORKBOOK.xlsx`, and the task plan. A generated file is never edited by hand. To change it, change the input or the generator and run the pipeline again.

The CAD models are also built by code. The FreeCAD scripts in `models/freecad/` build the general arrangement of the plant, and the CadQuery scripts in `models/mfg/` build individual units with drawings, parts lists, and STEP and STL export files.

## 3. What is in the repository

Table 3.1. Top-level folders

| Folder | Contents |
|---|---|
| `flow_graph/` | The plant graph, the system tree, the solver, the sizing code and the regeneration pipeline |
| `docs-authority/` | The design documents, both hand-written and generated, and the registers of documents, assumptions, open questions and tasks |
| `models/` | The FreeCAD and CadQuery scripts and the unit and motor models they build |
| `cad/` | Unit envelope meshes and study solids, stored with Git Large File Storage (LFS) |
| `design_tool/` | A local web application that displays the plant graph and cannot change it |
| `media/` | Rendered process sheets, overview images and an animation |
| `iso/` | An early set of isometric fabrication drawings, which the generated isometrics in `docs-authority/iso/` replace |
| `tables/` | Cut lists, material lists and parts tables |
| `notes/` | Design notes, audits and recorded decisions by the project owner |
| `scripts/` | The command that runs all of the checks |

The [documentation map](docs-authority/README.md) lists the design documents by topic, and the [glossary](docs-authority/GLOSSARY.md) defines the sector names, abbreviations and identifiers used in them.

## 4. Current status

The design is at study level. The mass and energy balances close in the model. The graph's `loops_closed` flag stays false, because no measurement from a built plant yet confirms the model. `docs-authority/PROJECT_PLAN.md` (AQS-PLAN-005) defines when a unit is ready to build and sets the order of the remaining work. The duty sheets do not yet meet that definition. The list of parts that the plant must make to build a copy of itself is incomplete.

The work still to do is recorded in two files. `docs-authority/TASK_PLAN.md` (AQS-PLAN-007) lists each task with the check that proves it is done. `docs-authority/OPEN_QUESTIONS.md` lists the design decisions that are still open and the default that the work proceeds on until each is decided.

## 5. Getting started

You need Git with Git LFS and Python 3.11 or later. FreeCAD and CadQuery are needed only to build the CAD models, and Node.js only to run the design tool.

The CAD files make up most of the repository's size. The model and its tests need only the unit envelopes in `cad/stl/`, so clone without the other CAD files:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/egofree/Aqueous_Solutions.git
cd Aqueous_Solutions
git lfs pull --include="cad/stl/*"

python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

scripts/check_all.sh
```

`scripts/check_all.sh` runs the tests, the check that every generated file is up to date, the citation check and the documentation style check. `scripts/check_all.sh --full` also runs the whole pipeline on the committed files and fails if the pipeline changes anything. The project uses no hosted build service, so you run these checks on your own computer. Run `git lfs pull` later if you need the full CAD models. The design tool's setup is described in [design_tool/README.md](design_tool/README.md).

## 6. Contributing

Contributions of calculations, corrections with a cited source, generators, CAD models, tests and reviews are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before you open a pull request. It explains how to change an input or a generator, how to cite a source, and which checks must pass. Write documents to the [documentation style guide](docs-authority/DOC_STYLE.md) (AQS-DOC-002), which is based on NASA KSC-DF-107 and the IET guide to technical report writing. To find work, read the task plan and the open questions described in section 4. Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## 7. Questions, problems and security

Ask a question or suggest a change by opening an issue on GitHub with the Proposal template. Report a fault in the code with the Tooling bug template. Report an error in the engineering, such as an unsafe relief case or an unsuitable material, with the Design defect template.

Do not open a public issue for a security problem or a committed secret. Report it privately through the repository's Security tab, as described in [SECURITY.md](SECURITY.md).

## 8. Licence

Aqueous Solutions is licensed under the CERN Open Hardware Licence Version 2, Strongly Reciprocal (CERN-OHL-S-2.0). The full text is in [LICENSE](LICENSE).

```
SPDX-License-Identifier: CERN-OHL-S-2.0
Source Location: https://github.com/egofree/Aqueous_Solutions
```

The project uses this licence because it is the licence of the open membrane work that the design builds on, as [CONTRIBUTING.md](CONTRIBUTING.md) explains. That work is the open-sourced off-the-shelf ion-exchange membrane project of SEM-Tech, the electrochemical separation platform of Rowow, which releases its core membranes, cells and general methods under CERN-OHL-S. The plant uses it as the design and fabrication reference for the membranes in the wet line, the BMED stacks and the methanol fuel cell. Its files are linked from [DEPENDENCIES.md](DEPENDENCIES.md) and are not copied into this repository. This project is not a Rowow product.

CERN-OHL-S requires anyone who conveys a modified design, or a product made from it, to make the complete source available under the same licence and to state where it is. Other open designs that the plant uses keep their own licences and are listed in [DEPENDENCIES.md](DEPENDENCIES.md). The design is provided without warranty of any kind, as section 6 of the licence states.
