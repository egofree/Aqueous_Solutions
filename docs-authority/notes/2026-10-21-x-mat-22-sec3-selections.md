# X-MAT-22 close-out (duty section 3 material selections lane note)

Date: 2026-10-21. Task: AQS-PLAN-007 X-MAT-22 "Duty section 3 material selections batch". Board: X-MAT-22
now `[x]` with Evidence `docs-authority/MATERIALS_SEC3.md`. The lane did three things: issued a duty
section 3 material selection for each of the 38 units that held unit task 09 on the generic
"Selection pending" template, issued the AQS-STD-002 section 12.2 brine family (one pending row split
into two issued rows), and refreshed every derived register that keyed on those holds.

## Data of record and render path

- `flow_graph/param/materials3.py` (new): 38 per-unit selections as top-level graph `params.sec3_material`
  (mat/basis/alt/note/task) per node. New regen manifest stage `sizing_materials3` at index 20
  (inserted after `write_graph_vent`, before `storage_sizing`; `writes_graph`, `quick`);
  `regen_manifest.json` now carries 55 stages.
- `docs-authority/_duty_basis.py`: the section 3 renderer gained a `sec3_material` branch, composed as
  `3. Material. {mat}. Basis: {basis} Alternative: {alt}. {note} ({task})`. It renders where old section 3
  starts with "Selection pending" OR already ends with "(X-MAT-22)" (self-healing re-render, so note edits
  converge without hand-editing sheets), and `author()` composes the same for future new sheets. The
  X-MAT-06 one-liner behaviour for pre-existing graph-node-material sheets is preserved byte-identically.
- Full regen (`python3 -m flow_graph.param.regen`): 78 stage runs, 0 failed, converged across passes with the
  graph sha stable at `32ec2f0e1999637c27733e3b4062f77a62816f824c83fc9127bd9c1da1237d8a`;
  `sizing_materials3` idempotent (identical post_sha on both passes). `regen --check`: 920 files, 0 stale.

## The selections (no invented rates)

Every selection carries: bounding environment from the unit's own duty sections 1-2 (graph design/sizing
rows + A-M register), a named degradation mechanism where the house selection differs from the issued
section 12 families, an alternative with its switch condition, and a qualitative longevity/cost basis with
the measured basis deferred to named first-article work orders (unit task 12 class). Governing
first-principle for the pot family (650-700 C molten chloride): Fe-Cr-Ni loses Cr selectively to the melt;
graphite wetted faces + 90 % alumina backup + steel shell below the liner (DING2018_CL_REVIEW,
DING2021_ENG, KRUIZENGA2012). Full rationale and the per-unit table: AQS-STD-006
(`docs-authority/MATERIALS_SEC3.md`, Rev A).

## Brine family (AQS-STD-002 section 12.2, Rev O)

The single pending last row split into two issued rows: ambient import legs NORTH_DOCK -> MG_POT/CA_POT
(PVDF wetted, concentrate kept anhydrous per ULLMANN_MAGNESIUM) and the molten MgCl2 return TI_CELL ->
MG_POT (~700 C, graphite/Ni-200 launder). `MATERIALS_STD.md` bumped Rev N -> O (revision row + header);
`docs-authority/_line_list.py` brine branch split keyed on `sid == 'IA-MGCL2-KROLL'`; LINE_LIST regenerated
(562 lines, class census `—` = 20).

## Effects on the derived registers (all regenerated, not hand-edited)

- Roster sweep (`_unit_materials.py` -> AQS-STD-005 + UNIT_MATERIALS.json): **176 issued, 0 open** (the
  re-pointed gate keeps the open set empty — see Gates).
- Internals (`_internals.py` -> AQS-DSN-INT-001): 61 defined / 82 none / **33 open** (was 68 open). The
  former "same hold as task 09" closes leave; pot cells close on issued mfg-BOM evidence
  (`models/mfg/AL_POT/bom.csv` etc.), service/melt units on quoted duty section 3 text. SINTER stays
  honestly open (rule-4 named gap: its muffle hot-zone detail has no keyword-evidenced internal yet).
- EOL return (`_eol.py` -> AQS-END-002 Rev D): unassigned **73 -> 3** (2 HCL_BURNER lines at unit task 01,
  1 pointer row), held total **159 -> 101** (fluoropolymer 67, Ti 25 + Nd/Dy 5, Pt-Rh 1, duty-pending 2,
  pointer 1). Classing is by duty section 3 keyword (material proxy), not by measured mass; the
  X-END-02 board note carries the new numbers.
- Fab route sheets (`_fab_routes.py`): the 46 generator-owned sheets re-quote the issued duty section 3
  selection (cut at a sentence boundary) and the refreshed internals disposition; no fab sheet reads
  "Material: Selection pending" any more. The route wording keyed on the pending flag is now driven by
  the precise template-line markers, not a substring scan (some issued notes embed the honest
  "unit task 02 pending" sizing phrase).
- Assumptions: **A-M-318..328** (11 entries, task X-MAT-22, `needs_verification` true with named
  verification tests = the unit task 12 first-article/verification campaigns). Register: 328 curated /
  836 scanned, passes.
- Task plan (`_task_plan_gen.py`): X-MAT-22 tuple + DONE_X + EVIDENCE_PASS; all 38 unit `-09` items `[x]`;
  X-END-02 PARTIAL string updated to Rev D numbers. TASK_PLAN/MASTER_PLAN regenerated
  (2024 `[x]` lines; 0 open `-09 Materials` items).
- Sources: refs.py is this repo's citation registry (NOT the Paper's master-bibliography, which was not
  touched). 13 web-verified entries added (DING2018_CL_REVIEW, DING2021_ENG, KRUIZENGA2012, KROLL1940,
  ULLMANN_MAGNESIUM, ULLMANN_TITANIUM, ULLMANN_WAX, MANG2007, WANG2006_ADS, SCHACHT2004, ASM_V1, ASM_V7,
  + one corrected duplicate removal) -> 267 entries; one accidentally truncated duplicate
  (ULLMANN_FLUOROPOLY) removed.

## Gates

- `pytest -q`: **90 passed** (ring-fence: 84 pre-lane + 6 new gate tests in
  `flow_graph/param/test_sec3_materials.py`). The 2 prior hold-state tests were rewritten, not silenced:
  `test_unit_materials.py::test_the_open_set_is_the_named_pending_work` now asserts the roster sweep open
  set stays empty and the former brine trio render issued with AQS-STD-006 named;
  `test_internals.py::test_open_set_is_the_named_gap_and_task09_hold` (renamed
  `..._after_xmat22`) asserts no "same hold as task 09" pointer remains and the pot cells / H2O_ELYZ are
  defined. The new suite guards: 38 selections issued and rendered, section 12.2 brine rows clean of
  pending text, roster open set empty, internals hold gone, EOL holds clean, lane refs registered.
- X-GOV-20 vendor scan: covered by `test_no_vendor_basis` in the suite; the additions avoid the phrases.
- `flow_graph/check_authority_contract.py`: ok. `docs-authority/_gasket_census.py`: OK.

## Register bookkeeping

- `DOC_REGISTER.md` (hand-maintained): AQS-STD-006 row added (MATERIALS_SEC3.md, Rev A); AQS-STD-002 row
  revision synced H -> O in the same commit (the doc revision it must name).
- The known AQS-STD-002 duplicate-row drift in DOC_REGISTER (`AQS-STD-002_CODE_BASIS.md`) is older lane
  residue and stays for its own fix (not this write-set).

## What this lane does not claim

No sizing (task 02 stays open on GREASE_CA, GREASE_LI, P_CA, LI_RECOVER, SI_REDUCE and the other unsized
units), no relief cases, no measured rates or lives anywhere, and no pot-cell verification - the
X-MAT-21 coupon work and the task 12 first-article campaigns remain the hardware-gated replacements for
the qualitative bases.
