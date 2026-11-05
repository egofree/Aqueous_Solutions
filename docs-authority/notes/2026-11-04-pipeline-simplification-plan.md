# Generation pipeline: map of the layers and a simplification plan (2026-11-04)

This record maps the layers that generate files in the repository, classifies each layer, and
proposes a simpler pipeline with an ordered migration. It changes no stage. Task X-QA-18 in
`docs-authority/TASK_PLAN.md` carries the acceptance test. Figures are as read at commit
c9314e5c; `python3 -m flow_graph.param.regen --dry-run` lists the present stages.

## 1. Layers

Table 1.1. Generation layers

| Layer | Inputs | Outputs (tracked) | Called by | Class |
| --- | --- | --- | --- | --- |
| 1. Drivers, references, assumptions, site profiles | hand-written | `flow_graph/param/drivers.json`, `refs.py`, `assumptions_manual.json`, `sites/*.json` | people | essential (the inputs) |
| 2. Graph-writing stages (`write_graph`, the `sizing_*` stages, `balance --write`, `edge_sectors`, `style_builders`) | layer 1 and the graph itself | `flow_graph/plant_flow_graph.json`, rewritten in place by every stage | `regen.py` graph loop, repeated until the graph hash is stable | essential in function; circular in form: each stage reads and rewrites the same file, and `style_builders` writes sizes taken from CAD builders back into the graph |
| 3. Balance closures by difference (`balance.py` closure table) | graph | graph edge rates | layer 2 | essential where a closure is physical; masks errors where a product rate is closed by difference (for example IA-GOODS-SHIP) |
| 4. Study calculators (`docs-authority/_*_sizing.py`, `_ew_sizing.py`, `_rect_ew_sizing.py`) | drivers, graph | sizing pages under `docs-authority/sizing/`; some values are copied into drivers by hand | doc stages, and other calculators by subprocess | essential, but several hold literals that belong in drivers |
| 5. Document stages (duties, P&IDs, line list, load list, registers, inventories, workbook, task plan) | graph, drivers, other documents | the derived files listed in `DERIVED_REVISIONS.md` | `regen.py` doc phase, repeated until no output changes | essential; some are circular (`feeds_back_from` in the manifest: documents that read other documents' outputs) |
| 6. Provenance manifests and the receipt (`duties/_generated.json`, `pid/_generated.json`, `media/_generated.json`, `*._generated.json`, `flow_graph/derived/_regen_receipt.json`) | the run | tracked JSON | generators and `regen.py` | bookkeeping-only: they record that a stage ran, so that commit-order staleness can be cleared |
| 7. Derived-file register (`_rev_stamp.py` writing `DERIVED_REVISIONS.md`) | Git history, layer 6 | `docs-authority/DERIVED_REVISIONS.md` | `rev_stamp` stage; `regen --check` | bookkeeping-only; before d76d5521 also the main source of stamp-only commits |
| 8. Document and drawing registers (`_doc_register.py`, drawing register) | page headers | `DOC_REGISTER.md`, `DRAWING_REGISTER.md` | doc stages | essential as indexes; the document-number invariant is already enforced by `test_doc_numbers.py` |
| 9. Manufacturing tracker (`models/mfg/tracker.py`) | graph, duty pages, committed CAD outputs | `models/mfg/*/params.json` (copies of graph values), section 7 of `MFG_MODEL_PLAN.md` | `mfg_tracker` stage; by hand with `--check` | partly redundant: `params.json` duplicates graph values that the builders could read directly (several builders already read the graph) |
| 10. CAD builders and export (`models/mfg/*/*.py`, `build_all.py`, OpenSCAD, FreeCAD) | `params.json`, graph | STEP, STL, SVG drawings, BOM and fastener CSVs; `cad/stl` registry | `regen --cad`, or by hand per unit | essential; outputs are large, partly non-deterministic before c34881ce, and mostly not in LFS |
| 11. Checks (`scripts/check_all.sh`, pytest gates, citation and style checks, idempotency check) | everything | none (after d76d5521) | people, the optional pre-push hook | essential |

Evidence of bookkeeping cost: of the commits on this branch ahead of `origin/main` up to
873b2d1a, 55 change only derived files, and 19 of those are not yet pushed (listed in the review
report). Before 9c5ebf13 every graph change rewrote every P&ID title block; before d76d5521 every
graph commit rewrote every row of the register and needed a separate commit.

## 2. Proposed pipeline

1. Inputs: drivers, references, assumptions and site profiles (unchanged).
2. Solve: one balance and sizing pass that reads the inputs and returns the solved model as a
   value. Sizing functions are pure: same inputs, same result. The graph file is written once at
   the end, not rewritten by each stage. CAD builders do not write sizes back; where a machine
   build sets an envelope, the sizing function computes that envelope.
3. Generate: every document, drawing and CAD model is a function of the solved model. Builders
   read the graph directly; `params.json` copies are removed.
4. Provenance: one manifest records, for each output, the hash of the inputs it was made from.
   Staleness is the comparison of that hash with the present inputs, computed on demand. No
   commit-order rule, no receipt lists, no stamp register written to the tree.
5. Determinism: every writer produces identical bytes for identical inputs and writes a file
   only when its content changes. The idempotency check enforces this.
6. Tracked versus derived: inputs and hand-written pages are tracked. Large binary outputs (STEP,
   STL, large SVG) go to LFS, or are left untracked and built on demand, as the owner decides.
7. Checks: invariants (document numbers, balances, misfit limit, materials rules, no dock import
   outside raw feed and waste) are tests run by `scripts/check_all.sh` on the contributor's
   machine. No hosted CI.

## 3. Migration, in order

Each step is a separate commit, reversible by reverting that commit, and passes
`scripts/check_all.sh --full` before and after.

1. Done in this review: the register records status only (d76d5521); `regen --check` is read-only;
   P&ID title blocks print the graph revision (9c5ebf13); STEP exports are byte-stable (c34881ce).
   Risk: none known. Check: `scripts/check_all.sh --full` passes with no diff.
2. Move the remaining literals of the study calculators into drivers (X-QA-06, X-QA-09). Risk:
   values change if a literal and its driver disagree. Check: misfit test and idempotency.
3. Replace `models/mfg/*/params.json` by direct graph reads in the builders, one family of
   builders per commit. Risk: a builder that relied on a hand-held value in `params.json`.
   Check: `models/mfg/tracker.py --check` and a rebuild with no geometry change.
4. Add the input-hash manifest beside the receipt, and make `_rev_stamp.py` decide staleness from
   it. Run both rules in parallel until they agree on every file. Risk: a generator whose inputs
   are under-declared shows current when it is stale. Check: a test that changes each declared
   input and expects the dependent outputs to show stale.
5. Remove the receipt lists, the per-generator `_generated.json` manifests and the commit-order
   rule. Risk: loss of the history the register gave; `--report` style output can be rebuilt from
   the manifest. Check: staleness test suite and `--full`.
6. Fold the graph-writing stages into one solve function that writes the graph once. Remove the
   write-back from `style_builders`. Risk: the largest change; hidden order dependencies between
   stages. Check: the graph after the change equals the graph before it, byte for byte, then the
   misfit and balance tests.
7. Decide tracked versus derived for CAD outputs (X-QA-14) and apply it for new commits only;
   published history is not rewritten. Check: `git lfs ls-files` covers the agreed patterns.
