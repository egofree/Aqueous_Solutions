# 2026-11-10 qa-audit merge Round D: route families 2 and 3 landed in the verification snapshot; the silicon route split out

Authority: the Round D prompt (PROMPT_ROUND_D_2026-11-10.md, Aqueous planning reviews, outside
this repository) and the Round D plan (PLAN_ROUNDS_2026-11-10_d.md, same source). Work owner:
Mike Matthews (order of 5 November
2026). Executor: OpenCode round `sisyphus`, 10 November 2026. All work ran in the isolated
verification snapshot `/tmp/opencode/qa-audit-d/verify`; the live repository was not edited.

Continuation of 10 November 2026 (Round D2, prompt PROMPT_ROUND_D2_2026-11-10.md, Aqueous
planning reviews, outside this repository; project-manager authorization under the
already-approved rulings): family 4 (the on-site silicon
and wafer route) landed under the resolved rulings, the companion source edits of the Round D
blocker list were applied, and the eleven tracker nozzle failures were cleared by rebuilding the
affected models. Sections 8 to 12 record the continuation; sections 1 to 7 are the Round D record
they extend.

## 1. Answer first

Route families 2 and 3 of the qa-audit route program are ported and functioning in the
verification snapshot: the sulfuric acid plant (ACID_PLANT), the sodium hydroxide plant
(NAOH_PLANT), the bench solvent plant (SOLV_PLANT) and the shop grease routes are on the graph,
the recovery-first gate passes with no flags, and the two remaining call sites named in the
stash are in. The silicon and wafer route (family 4) does not cohere with this branch and is
split out per the round plan. The full check set does not pass in this round: the landing needs
edits to files the round allowlist does not carry, listed in section 5 with the evidence. The
snapshot is left in its honest post-convergence state for Quality Control.

## 2. What the round ported

The tracked content of live `stash@{0}` (base `65c2d11f`) and its ten untracked modules were
extracted into the snapshot read-only (`stash show -p | git apply` and `archive stash@{0}^3`),
never applied to the live stash. The port carries:

- `flow_graph/param/drivers.json`: 140 driver keys of the route program, plus the two grease
  kettle temperatures added this round against the published lubricants reference
  (ULLMANN_LUBRICANTS) because the stash port omitted them and the grease family cannot run
  without them.
- `flow_graph/param/refs.py`: the 26 published references of the route program.
- `flow_graph/param/fluoro_train.py`: the audited orchestrator (acid-plant-first order) with the
  `cru_cl2_source` standby route block.
- The modules `sulfuric.py`, `caustic.py`, `solvent.py`, `grease.py`, `recovery.py` and
  `test_recovery_first.py` (families 2 and 3 and the recovery gate), and `fab_resist.py`,
  `fab_silicon.py`, `pv_wafer.py`, `si_refine.py` (family 4, see section 4).
- The two remaining call sites from the stash message:
  - `foundry_poly.py` calls `solvent.tf` after the chlorinator carbon monoxide export is rated,
    stamps the recovery-first records of its own ore streams (foundry silica on SHELL_BUILD,
    titanium, molybdenum and chromium on their cells), and seeds `params.base_kg_d` on
    IA-CL2-SHIP. The seed lives in the writer, not in a hand edit of the generated graph; the
    graph in the snapshot is a regeneration output.
  - `write_graph.py` `process()` calls `caustic.tf` at the sodium hydroxide make-up
    (`nb['makeup_mol']`), retiring the flake import IA-NAOH-MU and its salt purge pairing.
- The recovery gate `recovery.py` lists the dock imports that are neither ore, water nor waste
  as pending entries, each with its basis (section 3).

## 3. Recovery-gate pending entries

The audit graph had no feed make-up edge; this branch does, and the farm trade store brings its
own dock lines. Each pending entry names a registered basis; no recovery path is claimed for
any of them.

| Stream | Basis |
|---|---|
| IA-FEED-MU | Feedstock make-up behind the scrap-yard closure (A-M-460); a characterized lot re-points the feed (AQS-ASSAY-001 section 7) |
| NUT_AQUA | Raceway mineral nitrate on the dock mineral manifest (A-M-430: fish stock returns about 13.5 g N/d against an uptake near 260 g N/d) |
| NUT_AQUA_BED | Media-bed nitrate on the same manifest and basis (A-M-430) |
| CA_HOPPER | Free-choice mineral calcium carbonate for the livestock (A-M-430) |
| FR_FINISH | Phosphorus flame-retardant finish of the crew textile line at the reagent resupply class (A-M-225; the fleece basis is A-M-429) |
| IA-WAX-MU | Pattern wax make-up beyond the dewax reclaim (A-M-286); the plant paraffin-cut source is the audit route not landed |
| IA-C-TI, IA-C-MO, IA-C-CR | Carbon reductants at the dock feedstock class (A-M-284); the plant pyrolysis-char re-point is the audit route not landed |

`python3 -m flow_graph.param.recovery` reports `flags: []` on the converged snapshot graph.

## 4. Family-4 coherence check and the split

The round plan requires the audit wafer route (its assumptions A-M-436 and A-M-437) to be
verified against this branch's photovoltaic state after the Q-038, Q-040 and X-QA-04 load
shifts, and split out if it does not cohere. It does not cohere, on four independent grounds:

1. The array state moved. The audit route was computed against a roof array nameplate of
   3146 kW; this branch's graph carries 2633 kW after the load shifts. The audit's fixed
   figures (wafer need about 0.485 kg/d, charge 1.635 kg/d between pulls, silicon-loop chlorine
   make-up 1.5218 kg/d) recompute to 0.406, 1.406 and uncomputable here (below) at this
   nameplate.
2. The audit's silicon assumptions were never registered on this branch, and their numbers were
   reused: A-M-436 and A-M-437 on this branch are the Lake Boehmer hydrogen-sulfide design value
   and the electrodialysis recovery, and A-M-415..A-M-435 generally are the farm, habitation
   and locale families. Fourteen assumption numbers cited by the ported modules name other
   content here (A-M-417, 419, 420, 421, 422, 423, 425, 426, 428, 429, 431, 432, 436, 437).
3. The stash's own driver port omits the `si_refine_*` keys, so the silicon refining loop the
   audit built cannot even be computed from the ported drivers; the graph hunk's
   `si_cl2_kg_d` seed (1.5218 kg/d) is an audit-state number that no live driver set produces.
4. The audit landed that family's graph writes from `balance.py`, which this round's allowlist
   does not carry and the stash did not port.

Decision: split the silicon route out and land families 2 and 3, as the plan provides. In the
snapshot, `pv_cell_line.py` stays at its live revision (the stash delta that coupled it to the
wafer route is not applied), the `fab_resist.tf` call is removed from the orchestrator, and
`solvent.tf` takes the resist acetone draws only when RESIST_SYN is on the graph.
`fab_silicon.py` and `pv_wafer.py` remain in the tree as the compute libraries the resist and
cell-line designs cite; `si_refine.py` remains ported but unreachable until its family lands.

## 5. What still blocks a green full check, with evidence

The graph phase of the regeneration converges (four passes to a stable graph,
sha256 prefix `804885067f5e`). The document phase and the test set need companion edits that
the round allowlist does not carry. A diagnostic probe copy (never part of the round delta)
isolated the blockers: with only the system-tree leaves added, the full regeneration completes
green, and the remaining failures are exactly these.

| Blocker | Evidence |
|---|---|
| `flow_graph/system_tree.yaml` needs one leaf per new unit | `flow_graph/system_tree.py` validate() fails: "graph units missing from tree (3): ACID_PLANT, NAOH_PLANT, SOLV_PLANT". The audit's own family commits hand-edit this file (5b10cf53f, e510b5d6c, 42cc55f7c). With the three leaves added, the probe regeneration completes |
| `flow_graph/param/solver.py` must integrate the caustic liquor strength | `test_param_misfit` fails: IA-NAOH-MU graph 0.000 vs solved 4.394 kg/d (the import is retired but the solver still books it) and IA-BASE-PPT +1.94 %. The audit's solver differs by 109 lines for this content |
| `flow_graph/param/materials3.py` roster | `test_sec3_materials` fails: ACID_PLANT carries no section 3 material selection; the audit's materials3 covers the new units |
| `docs-authority/_internals.py` | `test_internals` fails: the new units hold the task-09 hold text |
| `docs-authority/GLOSSARY.md` | `test_doc_style` fails: four abbreviations used by the generated PARAMETRIC_MODEL.md are undefined (BCS, DNQ, SGL, SKF) |
| Tracker failure set | 11 built units gained process connections whose CAD models do not carry the new nozzles (EVAP_BASE, GW_INTAKE, HDR_H2, LEACH_CSTR_1, MEOH_TANK, MFG_SHOP, OIL_FRAC, P_CA, TI_CELL, WET_BENCH, WS_SOLV). BEFORE set: 200 units, 0 failures; AFTER: 203 units, 11 failing. The plan requires separate Mike approval for new tracker failure ids |
| Assumption numbering | The fourteen collided A-M numbers above; renumbering needs new register entries (the audit's family assumptions exist nowhere on this branch) and is an owner decision, not a silent fix |

The instrument index and the task plan needed no source edits: their stages pick the new units
up once `OTHER_INVENTORY.csv` and the task plan are refreshed (pipeline stage runs inside the
snapshot, recorded in the run log).

## 6. Checks run

- Regeneration attempts inside the snapshot: full runs recorded in
  `/tmp/opencode/qa-audit-d/regenA.log`; the graph phase converges, the document phase stops at
  the model workbook (system tree, above).
- Recovery gate: no flags; its test module passes.
- Tracker `--check`: BEFORE (isolated snapshot at the round base) 200 units, 0 named failures;
  AFTER (snapshot) 203 units, 11 named failures, all of the nozzle-drawn class above. Logs:
  `/tmp/opencode/qa-audit-d/tracker-BEFORE.log`, `tracker-AFTER.log`.
- The probe evidence is at `/tmp/opencode/qa-audit-d/probe*` and is not part of the round
  delta.
- Round D2: the full regeneration completes (`all stages ok`, graph sha 88eeb8994d44; the
  bootstrap runs of `inventory_other`, `task_plan` and `unit_sizing_sweep` in `--stage` mode
  preceded it, the Round D pattern: a failing doc stage aborts the pass before the stages that
  would unblock it can run); the tracker reports 205 of 205 units with no named failures
  (`d2-tracker-2.log`); the logs are `/tmp/opencode/qa-audit-d/d2-*`.

## 7. Recommendation

Families 2 and 3 are ready to land once the companion edits of section 5 are authorized as
their own round or an allowlist extension: the system-tree leaves, the solver integration, the
materials and internals rosters, and the glossary entries are mechanical and the probe shows
they are sufficient for a green full check apart from the tracker approvals. Family 4 needs its
own design pass: its assumptions must be registered under fresh numbers against this branch's
array state, and its graph writes re-homed from `balance.py` to a manifest stage.

## 8. Round D2: family 4 landed under the resolved rulings

The silicon and wafer route is on the graph and regenerated (section 9), its assumptions are
registered under fresh ids (section 10), and the split-out mechanics of section 4 are undone:
`pv_cell_line.py` carries the stashed family-4 delta, the `fab_resist.tf` call is restored in the
orchestrator, `solvent.tf` picks the resist draws up through its RESIST_SYN gate, and `si_refine.tf`
is reachable through a manifest stage. The owner ruling of 2026-10-29 (t58u) stands as the route
basis: electronic-grade silicon is made on site (SI_REDUCE reduces quartz ore with pyrolysis char,
SI_REFINE closes the chlorosilane loop), the silicon of retired cells returns first on IA-PV-EOL,
and the only dock inputs of the family are raw ore (IA-QUARTZ-MU) and waste streams.

## 9. Family-4 rates from the live array, and the arithmetic

Every family-4 rate is a computed output of the parametric chain
`pv_wafer.need -> fab_silicon.design -> si_refine.design`, and the chain reads the PV_ARRAY
nameplate from the graph, so nothing is hand-seeded. Landing the family's own electrical loads
moved the nameplate twice (2654 kW at the Round D state, 2771 kW after the first family-4 pass)
and the loop settled at:

- PV_ARRAY nameplate 2770 kW (the converged solve of the daily balance with the family-4 loads:
  SI_REDUCE 0.718 kW, SI_REFINE 3.667 kW, the RESIST_SYN batch heater, the SOLAR_PV_CELL line
  and the fab tools).
- Cell replacement need: life (1 - 0.80)/0.005 = 40 a, replacement 1/40 + 0.0005 = 2.55 %/a,
  so 2770 kW x 2.55 % = 193 W/d of cells; one 125 mm semi-square cell at 19 %
  gives 2.375 W, so 68.5 cells/d.
- Wafer need: 68.5 cells x cell mass = 0.4267 kg/d of solar wafers (the audit figure 0.485 kg/d
  was computed at 3146 kW; 0.485 x 2770/3146 = 0.427 confirms the scaling).
- CZ charge: the fab-start and solar-wafer body need sets a 33.52 kg charge every 22.8 d, of
  which the electronic-grade silicon rate is 1.4669 kg/d (the audit figure 1.635 kg/d is the
  same chain at 3146 kW plus the fab wafer starts, which do not scale with the array).
- Silicon loop: at yield 0.85 (Siemens) the loop carries 1.4669/0.85 = 1.7261 kg/d of silicon;
  the retired-cell return 0.4267 kg/d comes off the metallurgical feed, leaving 1.2991 kg/d
  reduced from 3.5004 kg/d of quartz ore and 1.0741 kg/d of char.
- Chlorine make-up: the SiCl4 purge carries (1.7261 - 1.4669) x 4 x 35.453/28.0855 = 1.3118 kg/d
  of chlorine plus impurity chlorides 0.0536 kg/d, so IA-CL2-SIREF carries 1.3654 kg/d -
  computed each pass, never seeded (the audit's hand-seeded 1.5218 kg/d belonged to its 3146 kW
  state). `foundry_poly.py` nets it into IA-CL2-SHIP parametrically and `si_refine.tf` re-nets
  the export whenever the cell need moves it.

## 10. Assumption ids: the collision resolved under fresh numbers

The fourteen audit assumption ids that name other content on this branch are re-registered under
A-M-471 to A-M-484 (the branch manual ended at A-M-470); every existing branch entry is untouched.
The ported modules and the ported driver register fields cite the new ids only.

| Audit id | New id | Content |
|---|---|---|
| A-M-417 | A-M-471 | fab_silicon: wafer-fab silicon and blanket gas from the wafer need |
| A-M-419 | A-M-472 | si_refine: on-site silicon, reduction and refining (t58u) |
| A-M-420 | A-M-473 | foundry_poly: char reductant of the chlorinators |
| A-M-421 | A-M-474 | sulfuric: on-site 98 wt% sulfuric acid (ACID_PLANT) |
| A-M-422 | A-M-475 | caustic: on-site NaOH make-up (NAOH_PLANT) |
| A-M-423 | A-M-476 | recovery-first rule (t61u) |
| A-M-425 | A-M-477 | acid-kiln campaigns (Q-034) |
| A-M-426 | A-M-478 | naoh_route CHLOR_ALKALI (Q-035 / Q-036) |
| A-M-428 | A-M-479 | solvent: on-site bench solvent (SOLV_PLANT) |
| A-M-429 | A-M-480 | grease: on-site shop grease |
| A-M-431 | A-M-481 | cru_cl2_source: two chlorine sources (HCL_OX default) |
| A-M-432 | A-M-482 | fab_resist: on-site DNQ-novolac photoresist (RESIST_SYN) |
| A-M-436 | A-M-483 | CZ hot-zone heater from a heat-loss model |
| A-M-437 | A-M-484 | pv_wafer: cell line sized from the roof-array replacement need |

Citations that name this branch's own content stay: A-M-430 (raceway nitrate basis) and A-M-460
(scrap-yard closure) in `recovery.py`, the branch textile-roster A-M-429 citations in
`foundry_poly.py`, `write_graph.py` and `recovery.py` (the fleece basis, distinct from the audit's
grease id), the heat-ledger findings A-M-453/454/455 in `write_graph.py`, and A-M-178 (the branch's
own PV cell-line tools id) in `pv_cell_line.py`.

Driver provenance: the four silicon-refining keys the stash omitted are ported from
`origin/qa-audit` (2756435e) verbatim - `si_refine_yield_TCS_SIEMENS` 0.85,
`si_refine_yield_SILANE_FBR` 0.8, `si_refine_kWh_kg_TCS_SIEMENS` 60, `si_refine_kWh_kg_SILANE_FBR`
20 kWh/kg, Siemens and silane-FBR class values - and registered under A-M-472. The two grease
kettle temperatures Round D added against ULLMANN_LUBRICANTS now carry their register entry
(A-M-480), and the ported `naoh_route` register field drops the audit's trailing comma. In all,
126 ported driver register fields were retargeted to the new ids.

## 11. Round D2: the graph writes re-homed and the companions applied

The audit hung the family-4 graph writes inside `balance.py physics()`. They are re-homed to the
manifest stage `si_route` (`python3 -m flow_graph.param.si_refine --write`), which runs
`fab_silicon.tf` then `si_refine.tf` after the specialty sizing lane and before
`write_graph_power`, so the roof re-solve sees the new SF feeds in the same pass and the cell
rate always follows the latest nameplate; `balance_report` depends on it. The stage is
idempotent at the fixed point and the graph phase of a full regeneration reaches its fixed-point
sha in one pass from the converged tree. The X-QA-06 study class the route supersedes
(`specialty_sizing.py` sizing SI_REDUCE from `si_kgd` 1.8 kg/d, 3 cells/d) is overtaken by the
route rates in the same pass - the replacement A-M-466's own replaced_by line names it - and the
leftover SI_REDUCE study params that lane writes are inert bookkeeping beside the route's live
values. The graph is a regeneration output throughout; `si_cl2_kg_d` is written by
`foundry_poly.py` as its computed make-up, never by hand.

The companion edits of the Round D blocker list (section 5), each adapted from the audit
counterpart: the system-tree leaves for NAOH_PLANT, ACID_PLANT, SOLV_PLANT, RESIST_SYN and
SI_REFINE plus the litho-train and glass-train descriptions; the caustic liquor strength in
`solver.py` (`evap` carries the make-up liquor water, `naoh_balance` returns liquor mass at
`caustic.product_wt`, the check compares IA-NAOH-LIQ); the section 3 material selections for the
five route units in `materials3.py` (the roster gate count moves 39 to 44 with the lane note, the
same mechanical bump REE_RECOVER took on 2026-10-31); the internals dispositions for the five
units in `_internals.py`, with the SI_REDUCE disposition restated on the route basis; and the
glossary entries BCS, DNQ, SGL and SKF (Rev F). The manifest output lists carry the new units'
fab pages, BOMs, maintenance files and the hazard-area register.

## 12. Round D2: the tracker nozzle failures cleared

The Round D AFTER set (11 units) and the rows family 4 added are cleared: every affected model
was rebuilt from its tracker-refreshed schedule, one unit at a time, and
`python3 models/mfg/tracker.py --check` reports 205 of 205 units with no named failures (the
BEFORE set was 200 units, 0 named failures; the five unit-count additions are the landed route
units, not failures). Fourteen units rebuilt without a source change - their builders draw the
schedule verbatim (WS_SOLV, GW_INTAKE, HDR_H2, LEACH_CSTR_1, the three LITHO tools, MFG_SHOP,
OIL_FRAC, PV_ARRAY, SOLAR_PV_CELL, WET_BENCH, WS_AMMONIA, CRU). Eight builders needed the new
rows added, each in the house idiom and each because the landed routes rated a connection the
model did not carry:

- AL_POT: two DN15 chlorine-draw stubs (IA-RESIST-CL2, IA-CL2-SIREF) beside the existing pair.
- CRYO_ASU: the two CZ-argon rows join the bed spread, which now points inward and steps 90 mm
  inside the bed radius so added rows stay in the envelope.
- EVAP_BASE: the second liquor inlet (IA-NAOH-LIQ) spreads the -Y inlets in x so the tubes stay
  distinct and the mesh reads back manifold.
- MEOH_TANK: the carbonylation and formaldehyde methanol draws join the packed +Y group, whose
  barbs now reach from the face through the shell wall at their x.
- P_CA: the four caustic-route rows (lime, kiln residue, slaker water, grit) draw as DN15-class
  risers and chutes; the rows are rated edges now, no longer a hold.
- SI_REDUCE: a schedule-verbatim nozzle block (charge chutes, hood-air and off-gas tubes, drain,
  lid vent riser, the power terminal carried).
- TI_CELL: two chlorinator-CO stubs beside the N12 export (the solvent and resist phosgenation
  draws).
- WAFER_FAB: the side groups re-centre on the envelope (the ten wafer-route rows had pushed the
  old left-anchored pack past the box).

The rebuilds changed only the builders' own outputs (STEP, STL, drawings, check.json, BOM keys)
under `models/mfg/<UNIT>/` and the registered `cad/stl` copies.

## 13. Rounds D3 and D4: the quick pass made byte-stable at the full fixed point

The closing `check_all --full` failed its staleness gate (1338 of 1823 derived files stale)
although every regeneration had exited clean. The cause sat in the test suite, not in the tree:
the regen test runs the solver/writer stages in place (quick mode), and that quick pass
re-stamped the graph off the full fixed point, so the receipt's graph digest no longer matched
the graph on disk and every receipt-vouched file read stale. Three movers, each a stage-order
effect between the quick subset and the full pass:

1. IA-GOODS-SHIP: `write_graph` process re-seeded the closed-shop value (324.823348 kg/d) every
   pass, and `balance` (full pass only) re-closed it to the reconciled 324.823746 kg/d. The shop
   parks a 0.000398 kg/d residual at the fixed point: the foundry polymer draw and the goods
   export are a coupled pair of by-difference closures, and their settled point is one rounding
   grain off the raw in/out sum.
2. The baghouse fines note (IA-BAG-01): process re-stamped the assay-rebasis text and
   `fluoro_train` (full pass only) re-stated the on-site photoresist route note.
3. The ZNBR2 cycling book (IA-ZNBR-HEAT, HL-Q4-REJ, IA-DC-REJ and the cycling_thermal block):
   the heat stage's store solve read the 0.2 kW commercial register stamps the specialty stage
   writes for the grease kettles, where a full pass has the solved kettle duty (0.00008 / 0 kW)
   on the graph at heat time; the two stamps give cycling books 15.6 kWh/d apart.

The seed itself stays - it anchors the foundry solver's input across passes and the loop does
not converge without it (a plain removal drifts one grain per pass). It moved in memory:

- `foundry_poly.solve()` seeds IA-GOODS-SHIP to the closed-shop value before it reads the shop
  remnant and restores the edge before returning, so every reader of the solver (the foundry
  stage, the power stage's melt duty register) derives the same polymer draw, melt charge and
  melt energy whatever pass position it runs at.
- `write_graph` process re-seeds the graph edge only outside the reconciliation band
  (0.001 kg/d, the band `balance` snaps the hopper line in), and keeps an existing photoresist
  route note on the baghouse edge (the note-ownership rule already used for the goods export).
- `write_graph` heat solves the cycling book from the grease solver's design output - the same
  pure solve the fluoro stage calls - and restores the register stamp after the power chain
  reads it, so the store book no longer depends on which stage last wrote the kettle stamps.

With these, a quick pass on the converged tree writes nothing (graph digest unchanged), two
consecutive full regenerations are byte-identical, and `scripts/check_all.sh --full` exits 0.

