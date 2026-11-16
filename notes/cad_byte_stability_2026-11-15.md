# CAD lane byte stability — 2026-11-15

The CAD stages made the regeneration doc phase non-convergent: with `regen --cad`,
every pass rewrote byte-different files, so the doc loop never reached a fixed
point and a site regeneration (locale worktree, X-LOC-04) failed after its pass
cap. An instrumented 8-pass run of the death_valley locale (hash of every
cad-owned file per pass) showed exactly three oscillating stages:
`cad_detail_stls`, `cad_freecad` and `cad_motors`. `cad_envelopes` and
`cad_mfg_models` changed once between the first two passes (the locale stamp and
one quantized size settling) and were then stable. Fixes follow the
byte-stability regime the manufacturing lane established (AQS-PLAN-006,
`models/mfg/lib/step_export.py`): a generated artifact is a pure function of its
inputs — no wall clock, no run order, fixed ordering.

## cad_motors — STEP header wall clock

`models/motors/MF-*/export/*.step` (20 files) changed every pass. The only
varying bytes were the `FILE_NAME` timestamp in the STEP header, written from
the wall clock by the Open CASCADE writer that `cq.Assembly.save()` drives.
`models/motors/build.py` now exports through `models/mfg/lib/step_export.py`
(named products, header stamp from the graph date — the same export the
manufacturing models use). Verified: two exports in fresh processes are
byte-identical.

## cad_detail_stls — OpenSCAD facet order

All 96 published STLs changed every pass. The triangle sets are identical
between runs (sorted vertex multisets compare equal); OpenSCAD 2021.01 emits
the same geometry in a different facet order each run. `build_stls.sh` now
canonizes every render through `models/openscad/detail/normalize_stl.py`:
within a facet the vertex cycle is rotated to its smallest vertex (winding
preserved), facets are sorted, OpenSCAD's number tokens kept verbatim. The
same geometry serializes to identical bytes in any run. Verified: two
independent renders are byte-identical after canonization, and the pass is
idempotent.

## cad_freecad — FCStd container stamps

`models/freecad/plant.FCStd` changed every pass. The document content was
stable; two container-level stamps were not: FreeCAD writes the save time into
every zip entry date, and `plant_groups.patch_visibility_fcstd` re-zipped the
archive with fresh wall-clock entries; FreeCAD also records `LastModifiedDate`
and `LastModifiedBy` inside `Document.xml`. The new
`models/freecad/fcstd_write.py` rewrites the archive with the deterministic
stamp date (`models/mfg/lib/stamp_date.py`, the graph's own date field) and
normalizes those two Document.xml properties; `transparency.patch_fcstd` and
`plant_groups.patch_visibility_fcstd` now write through it. Verified: rewriting
the same entries twice is byte-identical. The clash registers
(`CAD_CLASH.json`, `CAD_CLASH_EQUIP.json`) were already byte-stable.

## Deferred (sibling lane)

`models/mfg/HDR_H2/check.json`, `HDR_N2/check.json`, `ZNBR2/check.json`
(cad_mfg_models outputs, owned by the manufacturing-model lane) changed once
between passes 1 and 2 — quantized sizes settling with the locale graph
(rack-hall bays 37 to 29, orifice id 4.9 to 4.8 mm) — and were stable
afterwards. No oscillation; recorded here for completeness.
