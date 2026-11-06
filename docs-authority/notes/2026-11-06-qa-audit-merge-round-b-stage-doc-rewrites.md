# 2026-11-06 qa-audit merge round B: four sizing-stage doc generators take the audit rewrite

This record states what the round merged from `origin/qa-audit` and why. Owner ruling
(2026-11-05): merge the best engineering content by strategic review, not a mechanical
replay; no force-push. The regeneration ran in a scratch worktree and its result was
committed; the main working tree was never the regenerator's write target.

## What was merged

Four sizing-stage modules that this branch wires and never modified take the audit branch's
rewrite. The plant graph does not change: the physics and every booked figure stay as they
were, and the regenerated duties restate them in the audit branch's clearer form.

- `flow_graph/param/evap_design.py` - AQS-DUTY-060 Rev C: document number, revision and
  purpose-and-scope added; the basis written as sentences with the driver values; the
  evaporation-train comparison table carries labelled rows with units; the trim-heater
  statement states both units explicitly.
- `flow_graph/param/h2_compressor.py` - AQS-DUTY-067 Rev C: the compressor description reads
  its pressures from the drivers (`h2c_P1_bar`, `h2c_P2_bar`) instead of literals, the
  installed-units count comes from the `h2c_units` driver (2, one standby), and the duty page
  is rewritten to the style guide with the per-stage table. Every driver it names exists on
  this branch.
- `flow_graph/param/scale_down.py` - AQS-SITE-005 Rev F: the revision table restructured;
  no limit value changed.
- `flow_graph/param/upw_polish.py` - AQS-DUTY-070 rewrite: purpose and scope, sentence basis
  with the driver values, numbered and labelled tables.

Regenerated outputs: the four duty pages plus the `DOC_REGISTER` re-hash. The graph is
byte-identical (verified in the scratch run).

## Deferred, with reasons

- `flow_graph/param/fluoro_train.py` - the audit delta reads `base_kg_d` off the
  IA-CL2-SHIP edge, a field of the audit branch's X-RTE rated-cases route bookkeeping that
  this graph does not carry. Belongs to the route-bookkeeping family review.
- `flow_graph/param/pv_cell_line.py` - the audit delta couples the cell line to the audit's
  wafer route (`pv_wafer`, A-M-437), absent here; this plant replaces its roof array from
  its own cell line. Belongs to the wafer-route family review.

Both stay in the qa-audit tree for their family rounds.

## Checks

`pytest flow_graph/` passes (237 passed, 1 skipped, 1 xfailed). `scripts/check_all.sh --full`
passes on the committed tip, including the scratch regeneration that changes nothing twice.
