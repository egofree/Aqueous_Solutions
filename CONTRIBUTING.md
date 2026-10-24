# Contributing to Aqueous Solutions

Thank you for helping. This repository is an engineering design, so the rules
below exist to keep every number traceable and every document consistent with
the model. Read [README.md](README.md) first for the project and the repository
map.

## Ground rules

1. **The graph is the authority.** `flow_graph/plant_flow_graph.json` is the
   single source of plant topology. `flow_graph/param/drivers.json` holds every
   independent input. Documents, sheets, drawings, views, the workbook and the
   task plan are generated from them. Where a document and the graph disagree,
   the graph wins and the document is regenerated.
2. **Never hand-edit a generated file.** This includes `docs-authority/duties/`,
   `docs-authority/sizing/`, `docs-authority/pid/`, `flow_graph/views/`,
   registers, `docs-authority/MODEL_WORKBOOK.xlsx` and
   `docs-authority/TASK_PLAN.md`. Change the generator or its inputs, then run
   `python3 -m flow_graph.param.regen`. The staleness gates fail if a derived
   file lags the graph.
3. **Every number has a basis.** A value is either solved by the parametric
   model, cites a published reference registered in `flow_graph/param/refs.py`
   (edition and clause, table or page), or is a registered assumption (below).
   Do not invent values, and do not use supplier quotations or vendor data
   sheets as a design basis; size from need and from published methods.
4. **Size from need, for the bounding case.** Units, rates and spaces are sized
   from actual demand across the assay envelope and the bounding electrical
   load. A layout or block restriction that blocks a sized design is revised,
   not the design.
5. **Redundancy is intentional.** Energy and life-support systems (power, O2,
   water, CO2 removal, thermal, food, sanitation) carry N+1 or diverse backups
   sized by calculation for a defined outage. Do not remove a backup because it
   looks surplus to the daily balance.
6. **The plant sustains itself.** Production is sized for internal demand plus a
   saleable surplus, and every surplus stream has a defined outlet.
7. **Documents describe structure, not current counts.** Do not write how many
   files, units, sectors, documents, tests, stale files or commits there are,
   how large the repository is, or the current value of a driver: those facts
   go stale on the next change. Point to the authority or the command that
   reports them. Generated outputs may state their own counts, since they
   regenerate. A list that must agree with the graph is generated from it or
   checked by a test, never kept in step by hand; enforce invariants with
   checks, not prose.
8. **Identifiers are allocated, never reused.** A new page under
   `docs-authority/` states `Document number:` in its first lines, using the
   next free number from
   `python3 docs-authority/_doc_register.py --next AQS-SERIES`. If a page is
   renumbered, its old number stays on a `Former number:` line. The register
   (`DOC_REGISTER.md`) is generated from these lines. Task, assumption,
   open-question, unit and stream ids also take the next unused id. The tests
   fail on a duplicate.

## Assumptions register

Any value that is not solved and has no published source is an assumption. Add
it to `docs-authority/assumptions_manual.json` in the same commit, with value,
units, where used, basis, sensitivity, the test that would replace it, and the
task. Then run:

```bash
python3 docs-authority/_assumptions_register.py
```

It regenerates the register (AQS-REG-002) and fails on an incomplete entry.

## Citing sources and standards

- Register each reference once in `flow_graph/param/refs.py` and cite it by key
  with `cite('KEY')`. Give the edition year and the clause, table or page.
- Name standards by body, number and edition (for example ASME B31.3-2022,
  NFPA 30-2024, IEC 60034-1). Quote no copyrighted standard text beyond a short
  clause reference.
- Open-source designs that the plant builds on are attributed in
  [DEPENDENCIES.md](DEPENDENCIES.md). Link to them; do not copy their files into
  this repository unless their licence allows it and the attribution is kept.

## Workflow

1. Pick work. The master task list is `docs-authority/TASK_PLAN.md`
   (AQS-PLAN-007). Each open task has a "Done when" check and a `Triage:` tag
   (desk, hardware or owner). Open an issue or comment on one to say you are
   taking a task, so work is not duplicated.
2. Fork the repository and create a branch from `main` named for the task, for
   example `x-par-02-leach-balance` or `fix/line-list-dn`.
3. Make the change in the model, the drivers, a generator or a calculator
   (`docs-authority/_*.py`, `flow_graph/param/`), not in its output.
4. Regenerate and run the checks (below). All must pass. Commit every file
   the regen changed: on a clean tree a full regen changes nothing, so any
   change it makes belongs to your change.
5. Close the task only where a file in the repository proves it. Cite that file,
   rerun `python3 docs-authority/_task_plan_gen.py`, and update every page the
   change made untrue in the same commit. A change that leaves a contradicted
   page behind is not done.
6. Open a pull request against `main` and fill in the template. Keep one task,
   or one closely related set of tasks, per pull request.

### Required checks

The project uses no hosted build service: you run the checks on your own
machine before you submit. One command runs them all from the repository root:

```bash
scripts/check_all.sh            # or: make check
```

It runs, in order:

```bash
pytest flow_graph/                              # tests, including the 1 % misfit gate
python3 -m flow_graph.param.regen --check       # no generated file lags its inputs
python3 flow_graph/check_authority_contract.py  # the design tool matches the graph
python3 -m flow_graph.check_citations           # no stale document number, sector, path or commit
python3 -m flow_graph.check_doc_style           # abbreviations defined, no working jargon
```

Before you push, commit and run the full set, which adds a check that a full
regeneration of `HEAD` changes nothing, twice (slow):

```bash
scripts/check_all.sh --full     # or: make check-full
```

To run the checks automatically before every push from your clone, install
the optional local Git hook with `scripts/install_pre_push_hook.sh` (or
`make install-hooks`).

Maintainers run the same script on every pull request before merging. A pull
request that fails it is not merged.

### Large files

STL, FreeCAD and other CAD exports (`cad/stl/`, `models/`) are stored with Git
LFS. The tests need only the unit envelopes in `cad/stl/`, a small part of it. Clone
with `GIT_LFS_SKIP_SMUDGE=1`, then run `git lfs pull --include="cad/stl/*"`;
run a plain `git lfs pull` only when you need the full CAD models. Every LFS
download counts against the project's monthly bandwidth quota. Do not commit
build outputs, caches, virtual environments, archives or editor files;
`.gitignore` lists them.

## Writing style

Documents are engineering records. Follow the style guide,
[docs-authority/DOC_STYLE.md](docs-authority/DOC_STYLE.md) (AQS-DOC-002). It is
distilled from two published guides, linked from the style guide:

- NASA KSC-DF-107 Rev F, *Technical Documentation Style Guide*:
  <https://standards.nasa.gov/sites/default/files/standards/KSC/F/0/ksc-df-107_rev_f_07082017.pdf>
- IET, *A Guide to Technical Report Writing*:
  <https://ias.ieee.org/wp-content/uploads/2023/06/2020-01-16_IET_Technical_Report_Writing_Guidelines.pdf>

In short: write for an engineer who does not know the project; put the answer
first; use short, plain sentences and SI units; define every abbreviation in
the glossary; use shall, should, will and must as the guide defines them; and
leave out working jargon from the tools used to produce the design. Generator
text templates follow the same guide. State what is a
study value and what is checked. Every design here is a study; nothing is
stamped by a licensed engineer, and documents must not claim otherwise.

## What not to commit

- Secrets of any kind (tokens, keys, passwords, `.env` files).
- Personal data, or machine-specific paths such as home directories or temp
  directories. Use paths relative to the repository root.
- Editor, agent or tool scratch files (session logs, plans, lock files,
  receipts that are not part of the regeneration pipeline).
- Material from other projects.

Report a committed secret privately; see [SECURITY.md](SECURITY.md).

## Licence of contributions

This project is licensed under the CERN Open Hardware Licence Version 2,
Strongly Reciprocal ([CERN-OHL-S-2.0](LICENSE)), the licence of the SEM-Tech
open membrane work it builds on. By submitting a contribution you agree that it
is licensed under CERN-OHL-S-2.0 and that you have the right to license it so.

CERN-OHL-S requires that anyone who conveys a modified design, or a Product made
from it, also makes the complete corresponding Source available under the same
licence, and states the Source Location. For this project the Source Location is
<https://github.com/egofree/Aqueous_Solutions>. If you build or distribute a
derivative, keep the licence and copyright notices, mark your modifications with
the date, and publish your modified Source at a location you name on the
Product or its documentation (CERN-OHL-S-2.0 sections 3 and 4).

New source files should carry the SPDX identifier where the format allows a
comment:

```python
# SPDX-License-Identifier: CERN-OHL-S-2.0
```

## Conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
