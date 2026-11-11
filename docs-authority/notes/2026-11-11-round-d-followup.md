# Round D follow-up: the audit findings closed

Date: 2026-11-11. Task: the follow-up round that the 2026-11-10 QC audit prescribed
(docs-authority/audits/AUDIT_2026-11-10_qc.md): findings F-20261110-06 to F-20261110-12,
plus the two defects this round found in its own work. Continuation of
`2026-11-10-qa-audit-round-d.md`.

## Decision

The route-families delta now meets the recovery-first rule and the audit's fix list:

- Silicon recovered first (F-20261110-06): the crop, square-off and pot scrap return to the
  CZ charge (A-M-487), the reclaimed saw kerf and the silicon of retired cells enter the
  chlorosilane loop (A-M-485/486), the recycled SiCl4 is hydrogenated back to trichlorosilane
  (A-M-489) so the loop bleeds only the impurity chlorides, the baghouse fume is briquetted
  back into the burden (A-M-488), and the crib silicate recovered from the leach feed is the
  furnace burden (A-M-490) - the dock quartz draw IA-QUARTZ-MU is retired (0 kg/d, the edge
  returns if a driver change leaves a shortfall). The spent-shell export/import pair is
  retired; the shell make-up draws from the shop recovered-silica pool. The SI_REDUCE and
  SI_REFINE recovery records stamp every credit and loss. Converged rates (kg/d): crib
  briquette 0.4415, retired-cell silicon 0.4187, reclaimed kerf 0.4013, loop bleed 0.0343,
  chlorine make-up 0.0092, electronic-grade silicon 1.0034.
- The recovery gate tests classes, not text (F-20261110-07): every live dock input carries an
  explicit params.dock_class written by the new dock_class manifest stage; each pending import
  names the task that retires it, and the gate fails when that task closes with the import
  still present. The loss check extends to the acid-leach sink. The Kroll, molybdenum and
  chromium carbon reductants are re-pointed to plant pyrolysis char. The anhydrous AlCl3
  top-up falls to 24.0474 kg/d (the shortfall after the 14.8424 kg/d reactive-Al hydroxide
  cake the aluminium line draws from the sink circuit) and is registered as pending under the
  new task X-QA-19.
- Graph movers (F-20261110-08): the goods-export re-seed band and the IA-HOP-01 snap band
  read the balance_residual_band_kg_d driver (A-M-491) instead of a literal; the heat stage
  hands the solved grease duty to the power sizing as an in-memory override, so it no longer
  writes the graph file mid-stage; the baghouse-note owner is an explicit params.note_owner
  field instead of a text-prefix test. The shop export stays closed on the shop balance
  (X-QA-12 keeps that work; its done-when now also covers the S08 entrained-silicate
  residual, F-20261110-01).
- Hard-coded values moved to registered drivers (F-20261110-09): the solvent tank loss
  coefficient and ambient (A-M-492), the least grease-kettle diameter (A-M-493), the
  cold-box nozzle row step and bed-edge clearance in the shared nozzle library; the
  materials-roster count assert is now a membership invariant; the retired no-op writer
  calls are deleted; the silicon route is the single writer of the SI_REDUCE design values.
- Manifest declarations (F-20261110-10): the fabrication pages are declared by the
  docs-authority/fab/*.md pattern, and the CAD acceptance record and build log are declared
  stage outputs; the hazard-area CSV declaration from the delta is kept.
- The derived-revision register no longer depends on commit state (F-20261110-11): the class
  and by-design tables decide before the working-tree test, so a register refresh commit
  after a landing is no longer needed.
- The CAD lane is byte-reproducible (F-20261110-12): every builder writes its fixed STEP
  product name at export and the drawing writer stamps a fixed creation date and document
  identifier, so no normalize pass is needed on the build path; the committed STEP files are
  rebuilt at the fixed names; check_all --full gains a gate that rebuilds the CAD lane in its
  temporary worktree and compares every declared CAD output byte for byte.

Assumptions A-M-485 to A-M-493 are registered in the same round (value, units, where used,
basis, sensitivity, replacing test, task).

## Defects this round found and fixed

- The sink-circuit cake transfer subtracted the cake mass from the current edge rate every
  pass, so the circulating pair IA-SINK-01 / IA-WET-FLOAT-01 decayed 14.8424 kg/d per pass
  and the graph phase never converged. The pre-cake base of each edge is now stamped once
  (params.pre_al_cake_kg_d, 376.1 / 343.1 kg/d at the route landing) and the rate is always
  computed from that base.
- The graph writers used two trailing-newline conventions and one non-standard indent, so
  consecutive stages rewrote the same content to different bytes and no stage run was
  byte-stable. Every graph writer now serializes indent=2 with no trailing newline, the
  format the committed graph carries.

## Design consequence

The store re-solve under this round's loads moved the ZNBR2 charge book, and the live
headspace purge fell to 29.0 m3/h - below the 30 m3/h duty class figure (VENT_SCRUB band
mid, W12(1)). The duty figure stays the sizing class; the column continues to size on the
live purge (D_req 82.7 mm inside the PVC-U DN100 column, which carries the larger of the
two diameters), and the manufacturing model asserts hardware coverage instead of the
transition-era "live bounds duty" relation.

## Verification

- The regeneration converges: the graph phase reaches its fixed point in one pass from the
  converged tree, and the document phase is byte-stable across consecutive full runs.
- python3 -m flow_graph.param.recovery reports no flags on the converged graph; the
  recovery-first test module passes.
- scripts/check_all.sh --full passes at the round head (tests, staleness, authority
  contract, citations, documentation style, regeneration idempotence, CAD-lane byte check).
