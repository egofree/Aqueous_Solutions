# Manufacturing-model check sweep: non-manifold STLs and bbox misfits, 2026-11-01

Authority: AQS-PLAN-006 sections 1-5 and 7. Scope: every unit named by
`python3 models/mfg/tracker.py --check` on 2026-11-01 (33 of 200 units carried at
least one named failure: 15 "export STL is not closed and manifold", 18
"bbox ... against size_mm ... (misfit to report)"). No envelope, rate or bore
changed (plan rule 3). Nothing was resized.

## Defect class behind the non-manifold STLs

The exported mesh breaks when a builder unions parts that only touch - along a
face, a circle, or a tangent line - instead of overlapping volumetrically. The
boolean leaves a compound of separate solids (or a seam inside one solid), and
per-face tessellation then produces edges used by four triangles. Rebuilding
through the current lib and builders first (the lib `place_on_face` side-face
fix of commit 80f28de3 removed the old protrusions but not these contacts)
confirmed the pattern per builder:

- `style_builders.py` (`add_nozzles`, `column` skirt, `pipe_run` supports): the
  scrubber skirt met the shell along a circle (skirt inner radius = shell outer
  radius), pipe support blocks kissed the pipe bottom along a tangent line, and
  the old inlet/outlet stub construction left a stray no-op-rotate solid. Fixed
  at source: every nozzle stub now roots 10 mm past the shell wall (volumetric
  overlap) and ends flush at the envelope face (the house idiom), the skirt
  interferes 2 mm radially and rises 20 mm into the shell, support block tops
  sink 6 mm into the pipe wall, and `run()` now reads the exported STL back and
  fails the build if it is not closed and manifold. Cleared: ALK_SCRUBBER,
  C29_RECYCLE, CATCH_TANK, F_RECOVER, GREY_TREAT, MET_SCRUB, OIL_FRAC,
  ROOF_TANK, ZNBR2_BR2_REGEN.
- `farm_hab.py` `parts_frame`: the 1 mm wire floor met the leg corners
  edge-to-edge. Fixed: the wire laps 2 mm into every leg. Cleared:
  CHICKEN_COOP, DUCK_PEN, QUAIL_CAGE, RABBIT_HUTCH.
- `ROLL/roll.py`: the first exit-table roller was exactly tangent to the stand
  face (x0 980, r 40, face at 940). Fixed: exit rollers and pedestals start at
  x 990, and check.json now counts non-manifold edges from the exported file
  instead of carrying a hardcoded 1. Cleared: ROLL.
- `vent_scrubber.py` (EVAP_ACID_VS): the committed export was stale against the
  current builder; rebuilding closed the mesh. No builder defect remains.

## The bbox misfits: reported on the board, nothing resized

Every misfit unit was rebuilt (or probed) through its current builder and
reproduced the same box, so the overshoot is the builder's own designed
geometry, not a stale export:

- Pots and cells (AL_POT, CA_POT, MG_POT, MO_CELL, CR_CELL) draw connection
  hardware groups past the envelope on purpose; check.json carries the per-face
  overhang against the 50 mm allowance and the cad/stl registry copy is the
  in-envelope solid, so the X-PAR-04 gate stays green while the assembly export
  carries the full machine.
- Foundry and polymer machines (CONT_CAST, IND_MELT, INV_CAST, FILM_CAST,
  POWDER_RESIN, SHELL_BUILD, SHELL_BURNOUT, FLUX_PREP, WAX_PATTERN, POLY_F)
  draw chutes, frames or process extensions past the nominal box.
- BEE_HIVE (stand wider than the box by design) and BIOFILTER (+12 mm lid, an
  open item already recorded in its build log).
- EVAP_ACID_VS: the off-gas outlet rises 80 mm above the stated height (H+80),
  so the rebuilt assembly measures 318.3 x 318.3 x 1480 against size_mm
  400 x 400 x 1400.
- GW_INTAKE: hold. The node carries two disagreeing size claims -
  `params.envelope.size_mm` 800 x 800 x 600 (X-LOC-13 well head) and study
  `size_mm` 900 x 700 x 1800 ("unit task 02 sizing pending"). The tracker checks
  against the envelope field, the builder build used the study field. Resolving
  which one governs is a sizing/plan decision, not a builder fix; the misfit
  row stands until then.

The tracker (section 7) now writes the measured box against size_mm into the
status cell of every misfitting unit, per the section 7 sentence "a unit whose
assembly bounding box leaves size_mm carries the misfit in its status cell;
nothing is resized". `--check` still names each misfit.

## Verification

- `python3 models/mfg/tracker.py --check`: 0 non-manifold failures; the named
  failures that remain are exactly the reported misfit rows above.
- `bash scripts/check_all.sh` green after each builder fix and on the final
  tree (tests include the X-PAR-04 cad/stl envelope gate).
- One builder fix per commit, then one regeneration commit per affected unit.
