# CAD lane byte stability — 2026-11-15

Status: verified on the engine-v2 consolidation (wt-cadfix, 2026-11-16). The
cad stage selection (cad_motors, cad_detail_stls, cad_freecad, cad_envelopes,
cad_mfg_models) runs back-to-back with byte-identical outputs across all
cad-owned files and rc=0 in both passes; the check_all CAD byte gate is green;
and the death_valley site regeneration with --cad converges (its doc phase
never converged before the fix). Evidence in the Verification section below.

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

## cad_freecad — FCStd container stamps and element-map sidecars

`models/freecad/plant.FCStd` changed every pass. The document content was
stable; three container-level artefacts were not. FreeCAD writes the save time
into every zip entry date, and `plant_groups.patch_visibility_fcstd` re-zipped
the archive with fresh wall-clock entries; FreeCAD also records
`LastModifiedDate` and `LastModifiedBy` inside `Document.xml`; and the
per-shape `*.Shape.Map.txt` element-map sidecars carried run-dependent bytes.
`models/freecad/fcstd_write.py` rewrites the archive: the deterministic stamp
date (`models/mfg/lib/stamp_date.py`, the graph's own date field) on every
entry, the two Document.xml properties normalised, and — the piece the first
port round still missed — the element-map sidecars dropped. FreeCAD 1.0 writes
the same logical map in a different entry order, and renumbers the
`:1.b.<n>` child names to match, on every run: 14 sidecars (FB_HAB_CORE, the
FR_* imported units, PK_1 and 8 more) oscillated across two otherwise clean
regeneration passes, with no hex shape Tags anywhere to renumber. The
sidecars are derived data — `SaveElementMaps` saves them as a load cache, and
a loader re-derives the map from the BRep when they are absent (probed: with
`SaveElementMaps=False` FreeCAD skips writing them and the document loads
normally) — so the rewrite drops them instead of trying to canonicalise a
traversal order it cannot see. `transparency.patch_fcstd` and
`plant_groups.patch_visibility_fcstd` write through `fcstd_write`; the zip
member list and its order are stable run to run (verified on extracted
snapshots). The clash registers (`CAD_CLASH.json`, `CAD_CLASH_EQUIP.json`)
were already byte-stable.

## Deferred (sibling lane)

`models/mfg/HDR_H2/check.json`, `HDR_N2/check.json`, `ZNBR2/check.json`
(cad_mfg_models outputs, owned by the manufacturing-model lane) changed once
between passes 1 and 2 — quantized sizes settling with the locale graph
(rack-hall bays 37 to 29, orifice id 4.9 to 4.8 mm) — and were stable
afterwards. No oscillation; recorded here for completeness.

## Verification (wt-cadfix, 2026-11-16)

The verification pass also carried two landed engine-v2 breaks out of the way
(the CA_POT/MG_POT schedule rows and the EW draw-script params read; recorded
in notes/mfg_cad_leg_repairs_2026-11-16.md) and the cad_freecad sidecar strip
above, both prerequisites for the stage selection to reach its second pass.

1. Two back-to-back regens of the full cad stage selection, all five stages,
   --cad: rc=0 in both passes; sha256 over every cad-owned output
   (motors export trees, the detail STL trees in models/openscad/detail/stl
   and models/export/detail, cad/stl, the FreeCAD products, the clash
   registers, the mfg export/drawing/check trees) identical across the two
   passes - 3143 files, identical hash manifests (manifest sha256
   0394060c1a4d8e7b). plant.FCStd alone: two further cad_freecad probes
   byte-identical (6b90a489047e0ca9).
2. The check_all CAD byte gate (the cad_outputs leg: cad_mfg_models rebuilt
   from HEAD in a temporary worktree, byte-compared against the committed
   tree): green, rc=0 with no differing file.
3. The death_valley site regeneration with --cad and the pass cap raised to
   8, site runner: rc=0 - the inner regeneration converged (a non-converged
   doc phase fails the run - so the original blocker is resolved) - and
   sites/death_valley/ written: 260 output(s) differ from the baseline
   (SITE_OUTPUTS.json lists them). sites/ is ignored by git by design; the
   outputs are on-disk artefacts of the tree that ran the regeneration.

