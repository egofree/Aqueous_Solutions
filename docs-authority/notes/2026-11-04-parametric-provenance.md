# Parametric sizing provenance: written rule and enforcement check (2026-11-04)

Scope: the parametric-sizing rule (AGENTS.md Sizing) and a new gate that enforces it.
Every unit of the model must trace to the registered sizing machinery; this change adds
the rule where the sizing evidence is described and adds the check that fails when a unit
has no registered sizing basis.

## Changes

- `AGENTS.md` (Sizing): the rule is now operative - every size is computed from demand and
  supply through the drivers and the transfer functions (AQS-PAR-001); a number that cannot
  name its driver, transfer function or assumption basis does not enter the model; a
  hard-coded size is a defect, and an interim value survives only as a registered
  assumption. One sentence points at the new gate.
- `docs-authority/DESIGN_CHECK.md` (AQS-QA-002) Rev C, through its generator
  `docs-authority/_design_check.py`: section 1 (purpose and scope) states the same rule and
  the provenance check where the page describes what it verifies. No check, tolerance or
  result changed.
- `flow_graph/param/test_parametric_provenance.py` (new): the enforcement gate.

## Gate logic

Two tests read the graph, `docs-authority/inventory/SIZING_COVERAGE.json` (the evidence
registry; its build asserts the cited sizing document names the unit and the unit is a
present, non-boundary node) and `docs-authority/assumptions_manual.json`:

1. Sized units: every present, non-boundary unit carrying a `params.design` block must be
   in the registry or named in a registered assumption's where/files field. A design block
   with neither is the unregistered plug-value pattern the sizing audits stopped.
2. Whole plant: no present, non-boundary unit may sit outside both mechanisms - a unit
   with neither has no sizing calculation anywhere.

An assumption counts only through its designated usage fields (where, files), matched on
whole-token boundaries. Coverage gaps are fixed by extending
`flow_graph/param/sizing_coverage.py` (or registering an assumption), never by weakening
the test. When this note was written both tests passed; the unit lists they check are
reported by `pytest flow_graph/param/test_parametric_provenance.py -v` and by the registry
itself, so this note does not repeat their counts.

## Limits of the check (added 2026-11-04 in review)

The two tests compare unit identifiers only. They confirm that each unit is named in the
evidence registry or in an assumption entry; they do not compare any sized value with the
drivers or with the cited sizing document. The registry file was last changed on
2026-10-31, before the tests were added, so the tests passed when they were introduced
without any coverage change. The fixed-literal sweep below covered `flow_graph/param/*.py`
only. It did not cover `flow_graph/param/drivers.json`, the study calculators in
`docs-authority/_*.py` or the CAD builders in `models/mfg/`. Literals found there in review
include `backup_gen_rated_kW` = 40.0 in `drivers.json` (based on a superseded critical-load
list), the rectifier channel frame list, the 1.10 margin and the 6.0 V channel rating in
`docs-authority/_rect_ew_sizing.py`, `SHEET_TO = 9` in `docs-authority/_ew_sizing.py`, and
fixed module and cell counts asserted in the ZNBR2 and H2O_ELYZ builders. The work items
that extend the check to values are in `docs-authority/TASK_PLAN.md` (X-QA group).

## Fixed-literal sweep of the sizing writers (`flow_graph/param/*.py`)

Assignments in sizing positions (kW, kg/d, kg/h, m2, mm, m3) whose right side is a bare
numeric literal were listed and each dispositioned against the registers:

- `flow_graph/param/headers.py:40` `kg_d = 0.0` - accumulator initialization; the value is
  summed from graph edges. Not a size.
- `flow_graph/param/scale_down.py:39` `LATEX_DENSITY_KG_L = 1.1` - registered A-M-331.
- `flow_graph/param/specialty_sizing.py:42` `si_kgd = 1.8` - derivation stated in the
  assignment (3 cells/d x 0.6 kg Si/cell, wafer and kerf class) and published with the
  AQS-DUTY-071 evidence line. Registered through the registry.
- `flow_graph/param/specialty_sizing.py:185` `_ah_kg` - computed from the Faraday constant
  and the hydrogen molar mass. Physics, not a plug.
- `flow_graph/param/stub_activation.py:102` `dev_kW = 0.008` (with the 0.004 and 0.015
  lithography parasitics) - engineering-estimate parasitic classes; the values are
  published in the unit's sizing document (`docs-authority/sizing/LITHO_DEV.md`,
  `duty_kW=0.008`) and the units are registered. Reported, not converted: the estimate is
  not unambiguously driver-derivable, and converting it would change a published value.
- `flow_graph/param/stub_activation.py:213` `rate_kg_h = 2.8` and the extruder/clamp/air
  kW classes `2.2 / 0.75 / 0.75` - registered A-M-293 (where cites SI-MFG-01,
  AQS-REQ-KW-001, AQS-EQP-MFG-001).
- `flow_graph/param/specialty_sizing.py:251` `_bh_ac_basis = 1.2` - cited EPA-453
  practice; the hood faces it sizes are registered A-M-458.

A second sweep over assignments annotated with an equipment unit found formula constants
with named references (PERRY9, IAPWS_IF97, ACGIH, EPA-453) or driver and edge lookups.
Finding: no unregistered equipment-size literal exists in the writers at HEAD; the interim
bases are registered. No literal was converted and no model value changed.

## Verification

- `pytest flow_graph/param/test_parametric_provenance.py` twice: pass, pass (read-only, idempotent).
- `python3 -m flow_graph.param.regen` then `scripts/check_all.sh`: green.
