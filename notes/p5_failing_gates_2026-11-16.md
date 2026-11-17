# The post-P4 failing gates: tests and style re-pointed to the v2 contracts (2026-11-16)

Document number: AQS-SERIES-002
Revision: A
Date: 2026-11-16

The P4 cutover (AQS-SERIES-001) left two check legs red, byte-identical
before and after the flip: 11 test failures and 19 doc-style findings. This
note records, failure by failure, which side was wrong: the test, the
artifact, or the engine.

## Doc style (AQS-DOC-002): 19 findings, all fixed at the source

- FIC, LIC, TIC, BA, TAN, RTG were undefined abbreviations. They are
  standard technical terms (ISA-5.1 controller tag letters, the
  bright-annealed tube finish, total ammonia nitrogen, the radioisotope
  thermoelectric generator), so they entered GLOSSARY.md (Rev G) instead of
  being spelled out page by page. INSTRUMENT_INDEX, the HDR_UPW duty sheet,
  PARAMETRIC_MODEL, TEST_PLAN and OPEN_QUESTIONS resolve through the
  glossary with no edit.
- "landed" (ASSUMPTIONS_REGISTER, OPEN_FINDINGS), "vouch"/"re-derived"
  (MIGRATION_LEDGER) are session jargon. The sources were reworded: the
  assumptions manual says "in force", the audit table says "is committed",
  the ledger says verification/recomputed. The register regenerated through
  docs-authority/_assumptions_register.py, which also picked up the P4
  canonical last-digit rate corrections it had missed.
- The ledger's CRIT, MARK, TAGF/TAGH/TAGZ are code constants, now cited in
  code spans; "EG refining" is spelled out as electronic-grade silicon
  refining.

## The eleven test failures

- Unit-materials sweep and internals hold (4 tests):
  docs-authority/inventory/UNIT_MATERIALS.json and INTERNALS.md were
  retained v1 outputs gone stale at the P4 flip - their generators were not
  re-run after the BRINE_CRYS and NUT_AN material selections issued
  (A-M-503/A-M-497). Both regenerated clean: the sweep open set is empty and
  the task-09 hold is gone. The tests were right.
- Site constants (2 tests): the v2 ports of evap_design, inventory,
  cold_box, process and relief_vent, and the safety and electrical
  renderers, hard-coded the baseline gravity, standard atmosphere and air
  constants that task X-LOC-03 requires every model module to read from
  flow_graph/param/site.py. True engine defect; the modules now read the
  baseline profile through site.py (explicit baseline sid, so the solve
  stays payload-pure). Every committed document re-renders byte-identical,
  because the baseline constants equal the literals.
- Stale citations (1 test): 14 citations named paths that had moved (the
  ISO_SHEETS census CSV's pre-move location under the repository top, the
  retired notes tree, the envelopes module and the site_units module named
  without their extensions), one printf-style media pattern the scanner
  cannot read, one deliberate missing-document fixture, and one prefix
  string. Each citation was corrected at its source; the missing-document
  fixture in test_render_sizing now uses a real, unregistered path.
- CRYO_O2 N10 (1 test): the ammonia-oxidation oxygen feed nozzle carried the
  600 mm study-box datum, which fits no side-rail band of the A-M-167 rack
  (H 600), and no build record existed. The datum is revised to the 520 mm
  top-rail datum the rack's other outlets draw at, the schedule CSV, the
  builder docstring, the drawing notes and WORK_ORDER W4 were brought to
  the same state, and the builder re-ran so check.json records the row.
- Generator registry (2 tests): the v1 registry in regen_manifest.json did
  not account for the engine v2 writers (check.py, graph_io.py), the v2
  input manifest (linguist-generated, unowned) or the OpenSCAD STL
  normalizer the cad_detail_stls stage invokes. The manifest gained an
  engine-v2 not_stages entry, the input_manifest_v2 key and the stage
  invokes glob; the registry test reads the new key.

## The engine defect the round surfaced

The manifest's package fingerprint hashed only the files directly under
flow_graph/v2/, so an edit to the functions/ or render/ subpackages - the
bulk of the engine - moved no fingerprint and the staleness check reported
fresh. The fingerprint now walks the whole package tree (test modules and
the bytecode cache still excluded), as its docstring always claimed.

## Verification

pytest flow_graph/ is green (1555 passed before this round; every fixed
file re-run individually). check_all.sh --full is green except the CAD
output leg, which belongs to the CAD recovery lane in flight (wt-cadfix).
The engine v2 update re-issued the seed-provenance documents whose graph
hash the CRYO_O2 seed-note rewording moved, and the v2 manifest.
