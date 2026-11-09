# 2026-11-08: reservation adoption and the single size claim

This record states what changed and why. It closes the six bounding-box holds the
tracker carried (BEE_HIVE, CRYO_ASU, GROW_BED, HDR_H2, HDR_N2, HDR_O2) and settles the
schema question behind the seventh unit, GW_INTAKE, which carried two disagreeing size
claims on one node.

## The schema decision (Q-042, Q-043)

A node carried up to three size fields with a silent precedence (`params.envelope`,
`params.sizing`, `params.size_mm`), and `size_basis` was absent on the units whose
boxes were study placeholders. The owner ruling of 2026-11-08: one claim per node -
`params.size_mm` with `params.size_basis` - written by that unit's sizing authority;
the legacy `params.envelope` duplicate is removed. All 45 nodes that carried the
duplicate held values identical to `size_mm` except GW_INTAKE, whose two claims
disagreed and are settled under Q-043. The nine electrowinning nodes carried a stale
`size_mm` beside the authoritative sizing stamp; the stale duplicate is removed and
the sizing stamp governs. `models/mfg/tracker.py` reads the new precedence, and
`node_size_basis` now returns the node's `size_basis`.

## The six reservations are sizing outputs, not build read-backs

The reservation is computed from each unit's own sizing authority and registered
layout, never from the build bounding box - the tracker misfit check compares the
build against an independent claim, so it keeps its meaning:

- HDR_H2, HDR_N2, HDR_O2: `flow_graph/param/headers.py` (AQS-DUTY-075) stamps the
  modelled segment length with a cross-section covering the larger of the sized
  manifold and the largest branch the issued schedule carries (the EN-rounded OD
  series, AQS-PIP-004). The three builders rebuilt inside it and now draw every
  schedule row, including the formerly missing HDR_H2 N17 (ZNBR2 hydrogen strip) and
  HDR_N2 N2/N14, which the rebuild picked up from the refreshed schedule mirror.
- CRYO_ASU: `flow_graph/param/cold_box.py` stamps the modelled skid extents - the
  beds zone beside the purchased machinery row with the 20 mm margin, the basin
  width plus the -Y hose-makeup lap, and the issued z 2000 vent datum as the
  assembly top (registered study layout, W12). The builder reads the skid extents
  from the node design block.
- BEE_HIVE: the stack dimensions are the registered assumption A-M-468, the node
  design block carries the component dims (`hive_stack_mm`), and
  `farm_hab.parts_hive` builds from that block instead of deriving the stack from
  `size_mm` - the reservation is the assembly envelope, the components are inputs.
- GROW_BED: the growing area is the A-M-229 duty (29.12 m2) framed per the
  registered assumption A-M-469 (4 x 2 nominal bays, 15 mm walls, canopy 900 + 15 mm
  rail); the node design block carries the layout (`grow_bed_layout_mm`), the
  builder reads it, and the reservation is the framed array.

## GW_INTAKE (Q-043)

The node carries the X-LOC-13 well-head claim (800 x 800 x 600 mm; the submersible
pump is downhole, not plant-side). The former study solid (900 x 700 x 1800, "unit
task 02 sizing pending") is withdrawn. The unit gains its own builder
(`models/mfg/GW_INTAKE/gw_intake.py`, the shared close-out builder): head plate set,
two-leaf hatch, discharge-head boss, the three schedule rows drawn and recorded,
build 800 x 800 x 600 inside the reservation.

## The acceptance-record generations

With the tracker coverage check live (the earlier 2026-11-08 record), the 24 units
whose records lacked a `nozzles_drawn` section and the 15 units whose records
predated the terminal rows needed their builders brought current. 14 of the 15
record-gap units rebuilt from the refreshed schedule mirror with the carried-record
idiom added; their records now cover their schedules. The 17 no-section builders
with model programs take the same treatment in the same round. 7 flagged units
(FLUX_PREP, GALLEY, POLY_FIBER, QUAIL_CAGE, RABBIT_HUTCH, WASHROOM, WAX_PATTERN)
have no builder program at all - they are pre-model units whose schedules the
task-04 generator issued; bringing them up to date means writing their
manufacturing models, which is the standing X-MFG queue, not a record migration.

## Checks

`python3 docs-authority/_assumptions_register.py` clean (A-M-468, A-M-469 added);
`python3 models/mfg/tracker.py --check` shows no misfit and full schedule coverage
for every unit this round rebuilt; the six named holds are cleared. The remaining
named failures at this record are the units whose builders are still being brought
current in this round.
