# Whole-plant completion roadmap (2026-10-21)

Plan to take the board from 1608/2887 done to full closure. Every wave gates its Done-when on
specific evidence, per AQS-PLAN-007 task mechanics. Sources: the live board census,
COMPLIANCE_MATRIX.md section 11, and the refreshed AQS-QA-002 record.

## Wave 0 - Standards deliverables (the 9 Open(design) compliance rows)

Author each as generated docs with an owning `_*.py` module, never prose:
- CMP-NFPA-03: X-ELS-09 electrical area-classification drawings (one sheet per classified zone,
  generator reads the graph's gas-source map).
- CMP-NFPA-06 / NFPA-08: X-SAF-01 HAZOP -> LOPA program from the graph relief/interlock list;
  SIF/SIL-assignment register (X-CTL-03), ISA-84 wording in STANDARDS_BASIS.
- CMP-NEC-04 / NEC-07: one-line/load-list short-circuit + arc-flash basis update,
  ampacity/OCPD coordination table exporter for every branch.
- CMP-OSH-02 / OSH-10: machine-guarding and guardrail schedule (X-RED-03 frames, pot cells,
  conveyors), emergency lighting fixture schedule tied to REMAINING_BLD egress paths.
- CMP-ISO-03 / ISO-06: ISO-14644 cleanliness-class basis for FAB; ISO 9001-style doc-control
  index over the _generated set.

## Wave 1 - Sweep the calculation tail (T02 50, T04 19, T13 52)

Family sweeps exactly like the T02 unit-sizing sweep already committed: one generator per task
family, per-unit rows with stated bases, idempotent, scrub-self-healing. No hand-edits.

Update 2026-10-21 (citation-integrity remediation, before the per-family sweeps): a full-tree
scan found graph/driver rows citing register rows `A-M-282..300` from a dead lane that never
landed its register rows. This was remediated by reconstruction from the self-describing citing
sources: +35 register rows (`A-M-282..316`), 48 drivers-field remaps, 170 source-ref remaps,
plus the regen self-heal of every generated artifact. Zero numeric value changes (3482-value
multiset identity vs HEAD), all gates pass (pytest 43/43, regen --check 0-stale, authority
contract projection=on-disk). Full record: `2026-10-21-dead-register-remediation.md`. The
previously-blocked citation basis for the sweeps is now clean; the per-family sweeps continue
with the register resolvable end-to-end.

## Wave 2 - Internals and materials (T06 171, T09 172)

- T06: internals definition per unit class (trays/packing for scrubbers and columns, spargers,
  inlet/outlet devices) or "none with basis" statements, generated from unit class + service data.
- T09: per-wetted-stream material picks under AQS-STD-002 with the AQS-ASSAY-001 Rev C bounding
  table; family-level mapping (glass for halides, PTFE-lined for trace HF, 316L where legal).

## Wave 3 - CAD acceptance + drawings (T10 172, T11 172)

- T10: author CadQuery builders for the units still missing models (scrubbers, BMED/EW stacks,
  heat batteries, cryo cold boxes, fuel cell) in the foundry/foundry_poly pattern; then log M3
  acceptance per AQS-PLAN-006 section 5 per unit.
- T11: fabrication-drawing generator per accepted model: dimensions, welds, tolerance stack,
  OCPD/pressure ratings on the sheet. DRAWING_REGISTER extends automatically.

## Wave 4 - Buildable output (T12 127, T14 172, T15 172)

- T12: BOM completion from the accepted models (fastener/valve/instrument rolls).
- T14: installation sheets (anchor bolt layouts, weights/lift plans from STRUCT_ROWS).
- T15: commissioning sheets wired to COMMISSIONING.md stages; test procedures reference the
  instrument loop register (AQS-INST-001) and the relief cases (section 6 of each duty sheet).

## Wave 5 - Hardware-gated closure (demands physical runs)

A-M-169 compressor first article, A-M-176 RO/EDI module bench, X-INV-02B motor first articles,
X-INV-03-WF-01..04 wire families, X-MFG-41 stack test, X-MAT-21 coupon tests. These stay open
until bench/article data exists; the plan does NOT close them on paper.

## Standing resolution drive

QC-09 (H2 bank 19.0 model vs 17.406 kg independent) closes with a register-tracked design
change in the CRYO lane: resize the tube bank to hold the 19 kg basis, or re-state Q-004 at
17.406 kg with the margin documented. Wave-0 prerequisite for CRYO T-by-T completion.
