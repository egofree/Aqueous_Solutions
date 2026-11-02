# 2026-11-01 — Lake Boehmer site design: profile, LB_* train, and the crew-0 locale ruling

## What changed

**New locale (X-LOC-05, site basis AQS-SITE-015)**: the Lake Boehmer lake-restoration plant,
Pecos County TX — a mobile, solar-powered, unmanned electrodialysis plant. The locale is its
own technology class (Q-034) and its crew is zero (Q-036, owner 2026-11-01).

- `flow_graph/param/sites/lake_boehmer.json`: the profile (site_code LB, crew 0, climate-grid
  point 31.22 N 102.73 W with the parcel TBD, PV+battery portfolio, air heat rejection, and the
  scaling plan: the fifteen production/manufacturing/life-support sectors eliminated, LIO_BAT
  as the storage and backup replacement set, DRY_COOLER for the ground-loop set, and the ten
  LB_* units plus LIO_BAT promoted and sized by the design pass).
- `flow_graph/plant_flow_graph.json` Rev AD: the LB_* placeholder units
  (LB_INTAKE, LB_DEGAS, LB_DEGAS_SCRUB, LB_SOFTEN, LB_ED1, LB_ED2, LB_PROD_TANK,
  LB_PROD_OUTLET, LB_BRINE_RETURN, LB_CHEM_STORE) and their sixteen placeholder edges under
  `WTR.lake-boehmer-train`; no rates. The feed edge carries the derived assay
  (TDS 105 g/L, sulfate 7.5 g/L) and the H2S design note. The open product/brine return edges
  carry the Q-037 honesty note: with both streams returned, the net lake salt removal is about
  zero. `flow_graph/system_tree.yaml` partitions the train.
- `flow_graph/param/drivers.json`: twenty-eight `WTR.lake-boehmer.*` entries (throughput, feed
  assay and its verification flags, product criteria, ED transfer-function values, auxiliaries,
  battery contingency, degasser basis, container layout), every one with a ref, register or
  owner basis.
- `flow_graph/param/lake_boehmer.py`: the locale design pass (AQS-SITE-015). Computes the ED
  specific energy (SEC = F·ΔC_eq·U_cp/(CE·3.6e6), module docstring), the module counts (with
  one spare module per stage, A-M-451), the container counts, the PV nameplate (D-PV rule at
  the site drivers) and the battery store (night plus contingency days, A-M-443). With
  `--write` it stamps `params.lb_design` inside the lake_boehmer locale worktree only; for
  every other site it validates and writes nothing, so the baseline regeneration stays
  byte-identical. Registered as manifest stage `lake_boehmer_design` after `edge_sectors`.
- `flow_graph/param/scaling.py` and `flow_graph/param/portfolio.py` (Q-036): a crew of zero
  admits a life-support elimination when the action records the ruling
  (`scaling.crew_zero_ruling`); a non-life-support unit is never waived by it, and the energy
  guard is unchanged. The redundancy two-source rule does not bind a life-support function at a
  crew of zero (portfolio.redundancy). Energy functions still need different-technology
  replacements.
- `flow_graph/param/test_lake_boehmer.py`: salt closure, the SEC transfer function, module and
  container counts, the PV/battery formulas, the keep/eliminate plan, the guard scoping, the
  redundancy relief, and the stamp and no-write behaviour. `test_site_units` locales set
  extended with lake_boehmer.

**Authority records**: assumptions A-M-434..A-M-451 (feed values and their verifications,
ED transfer function, auxiliaries, contingency day, container envelope and counts, feed-calcium
gap, product basis, stage split, degasser basis, N+1 rule); OPEN_QUESTIONS Rev D with Q-036
(crew-0 locale ruling) and Q-037 (return-to-lake salt-removal honesty); GLOSSARY Rev C (TWDB,
RRC, MPGCD, GHI, NWS, SEC, SMCL, TSWQS); SITE_BASIS_LAKE_BOEHMER.md (AQS-SITE-015 Rev A) with
the design basis, the train, the honest mass balance, power and storage, the container concept,
safety, and the gaps (bathymetry, full ionic assay, radioactivity/arsenic, parcel, tower design,
recovery confirmation).

## Incident record

The first authoring session for this change set lost shell execution and the file-edit tool
degraded (a full disk; 2.7 G freed afterwards): the graph edit was applied in pieces and the
tool truncated the file tail, which was repaired by reverting `plant_flow_graph.json` to HEAD
and re-applying the whole Rev AD change from the recorded JSON with a checked applier
(json round-trip and identifier assertions before and after each write). `refs.py` was
reconstructed the same way and verified by key comparison against HEAD (delta: the nine Boehmer
references plus the SANDER2015 amendment). No generated file was hand-edited; the regenerated
outputs came from the regen stages only.

## Verification

Ran, on this tree, in order:

1. Full regeneration `python3 -m flow_graph.param.regen` — converged (all stages ok, doc
   phase stable at pass 3, receipt vouches 476 patterns, graph sha b3ee606fa8e5). The new
   `lake_boehmer_design` stage runs as a validator at the baseline and writes nothing.
   `regen --check`: 1773 files, 0 stale. One real defect surfaced and was fixed forward: the
   instrument-index generator asserted every process unit into its loop table, so the nine
   process LB_* units gained AUTH entries (`docs-authority/_instr_index.py`, 10 instruments
   with their X-LOC-05 bases); LB_PROD_OUTLET is a bookkeeping boundary and is exempt by the
   existing rule. A flock wrapper around the whole regen deadlocks at `mfg_tracker` (the
   tracker takes the design lock itself); the regen runs without the outer wrapper and the
   stages self-lock.
2. `docs-authority/_assumptions_register.py` — ok (regenerates AQS-REG-002; 18 new entries
   A-M-434..A-M-451). `docs-authority/_doc_register.py` — ok (AQS-SITE-015 registered). The
   docs map row for the new page added to `docs-authority/README.md` (hand-maintained index).
   Four `replaced_by` strings in the new assumptions were reworded off the vendor-data phrase
   the X-GOV-20 gate bans (stack acceptance test / as-built stack data wording).
3. Targeted locale-context suite (`AQS_SITE=lake_boehmer`): site scaling, profile, units,
   power, stamp, outputs, constants and lake_boehmer tests — 79 passed. Two tests were made
   env-explicit (the scaling-render and design-pass no-write tests rendered/asserted
   baseline-context text); their assertions are unchanged in meaning.
4. Full baseline suite `python3 -m pytest -q flow_graph/`: 211 passed, 3 failed — all three
   are the concurrent MET_HX_Q4 CAD session's tree state, outside this write-set: the
   envelope check names MET_HX_Q4; the citation findings are MET_HX_Q4 untracked drawing and
   script paths; the style scanner crashes reading a tracked-but-deleted MET_HX_Q4 drawing
   page. No failure names a lake_boehmer artifact.
5. Full locale-env suites compared: `AQS_SITE=lake_boehmer` fails 8 and `AQS_SITE=death_valley`
   fails 9, all in the same mechanism classes — the baseline solver gates (misfit, roof),
   the in-place locale-run refusals in test_regen, plus the shared MET_HX_Q4 findings. The
   locale graph only converges inside its own regenerated worktree, so these are the
   established locale-mechanism behaviour, not regressions.
6. Baseline graph diff is additive: +616 lines, the only deletions are the revision, date and
   notes_rev_AC header lines. `sites/` untouched. `check_all.sh --full` (regeneration
   idempotence of HEAD) is left to the reviewer; it needs a commit first. Note for the
   reviewer: the full regen rewrote the derived tree (unit params.json rev stamps to AD, the
   registers, the views and MODEL_WORKBOOK) and regenerated DRAWING_REGISTER.md and
   DERIVED_REVISIONS.md, which the concurrent MET_HX_Q4 session had also modified — generated
   files, regenerated from the current tree including that session's on-disk drawings.
