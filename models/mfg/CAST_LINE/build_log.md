# CAST_LINE build log - FOUNDRY-CAST_LINE-10 acceptance

Date: 2026-10-25. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/CAST_LINE/cast_line.py` + `params.json`; drawing set `models/mfg/CAST_LINE/drawings/`;
build script chain run headless on the build machine:

    $CADQUERY_PYTHON cast_line.py          # build + checks + bom.csv + STEP/STL
    $CADQUERY_PYTHON draw_cast_line.py     # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py    # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    python3 docs-authority/_pid_sheets.py  # re-appends the AQS-PID-001 register section
    $CADQUERY_PYTHON draw_cast_line.py     # PDF pass from the stamped SVGs

## Tool versions (recorded per AQS-PLAN-006 5.1)

- CadQuery 2.8.0 (in a dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh for the STL manifold check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step. Run recorded above with tool versions. check.json written by the build.
2. Bounding box: the build solid exactly 1500 x 800 x 1500 (bbox_abs_mm [0, 0, 0] .. [1500.0, 800.0, 1500.0]) = the duty section 2 envelope to within the 1 mm registry rule: PASS. The scheduled connection hardware sits flush with or inside the envelope faces; nothing was resized and no connection overhang is claimed (check.json `cad_stl_scope`).
3. Every nozzle of the task-04 schedule (docs-authority/nozzles/CAST_LINE.csv, N1..N6) modeled and cross-checked in-model against the parsed CSV: N1 -X/160, N2 -Y/600, N3/N4 +X/600, N5 bottom/50, N6 top/800, at schedule bore and rating. The schedule names faces generically (inlet/outlet/bottom/top), so the compass assignment is the registered study choice (params.json layout_note, mirrored per tag as `schedule_face`); the model honors schedule bore, rating and height verbatim.
4. Every internal is a solid: mould seats (backing platen + seat frame + water jacket shell), fine-graphite inserts with cast cavities and riser passes, refractory trough + distribution header + bottom-fill risers + drain well, pour ladle with lining, roller table with shafts and pillow blocks, shear block with knife insert, guards, hood plenum, gantry. No internal is represented by text.
5. Materials/thickness match duty section 3 (X-MAT-22): fine graphite hot faces (inserts, risers, trough wetted faces - chemically indifferent to the Cu melt class), carbon-steel backing and structure with no corrosion allowance on the dry CS members. The melt-path wear allowance is a task 12 first-article item; no measured pit rate is claimed.
6. BOM regenerated from the model: bom.csv (15 rows: qty, material, mass from solid volumes, make/buy). The prior hand rows' bases are carried over; the mould-change chain (safe working load 250 kg chain hoist) is a purchase item named with the rating per A-MACH.
7. Every bolted joint in fasteners.csv: M16 T-bolts x12 (posts, clamps), M12 anchors x6, M12 hex socket cap screws x28 (seat frames, pillow blocks, knife insert, trolley lug), M8 hex socket cap screws x8 (jacket covers). Welded seams covered by the part-sheet callouts (AQS-PLAN-006 W7). Joint convention: bolted/press-fitted interfaces are modeled touching or with 0.1 mm interference so the build solid stays one manifold body (check.json `joint_convention`); clearance joints are not modeled apart - trunnion pins press into the fork saddle line and roller shafts into the pillow-block bushings.
8. Drawings exist and name the graph revision: 8 sheets (ga_front, ga_side, nozzle_orient, fr01, mt01, ps01, gd01, iso01) as SVG + PDF under models/mfg/CAST_LINE/drawings/. Each SVG carries the AQS-DWG-001 title block (content-hash revision per ASME_Y14_35/ISO_7200, applied by docs-authority/_drawings.py) plus the fab-notes band with the keys (dimensions, weld calls, tolerances from the build geometry). DRAWING_REGISTER.md holds the rows (AQS-MFG-CAST_LINE-<SHEET>).
9. STEP and STL exist: export/cast_line.step (named assembly) and export/cast_line.stl (full build solid). cad/stl/CAST_LINE.stl is replaced by the build: the in-envelope build solid in metres and ASCII per the X-PAR-04 registry (parsed bbox exactly 1500 x 800 x 1500; gate test passes). STL checked closed and manifold (trimesh: watertight True, 0 degenerate edges after vertex merge, one island; the same holds for the mm-scale export). The machine is manual (0 kW node duty): no electrical view is claimed, and the mould-jacket cooling water is a utility loop with no graph edge and no rate claim - sized at the task 12 first articles (params.json holds).
10. Duty section 7 points at the model: the sheets regenerate with the manufacturing-model line (duty_basis 7 names `models/mfg/CAST_LINE/cast_line.py`); the graph design row and the duty size line agree (size_mm [1500, 800, 1500], moulds 2, pour_kg_d 3).
11. WORK_ORDER.md carries every hold by name (holds section added this lane).

## Corrections made on the way in (recorded, not silently resolved)

- End-rail length: the roller-table end rail was drawn 70 mm long in X, overshooting the envelope to 1540; corrected to 30 mm so the line ends exactly at x 1500 (+X face pick).
- Frame connectivity: two mid-span cross members and the guard floor channel originally had edge-only or no contact with the frame; the members, legs, guard posts, guide-rail posts and the static-shear pedestal are now welded with real volume overlap, and the bearer rails ride overlapping the frame rails (no edge-only contact anywhere).
- Roller ends: the roller bodies ended coplanar with the bearer-rail faces, which produced coincident-face tessellation artifacts; the rollers now span past both rail faces with end shafts press-fitted through both pillow-block bushings.
- Connection check scope: the in-model cross-check compares the model against the schedule's face vocabulary via the registered `schedule_face` mapping; the compass face itself stays the registered layout choice.

## Holds (named; the plant keeps them open)

- Unit task 12 (first articles + real BOM at order): jacket cooling-water utility loop sizing and commissioning (no rate claimed here), mould insert change-out traveller, shear campaign, ladle relining campaign.
- X-MAT-21 / A-M-318 pot-cell verification: the mould-cycle wear allowances and refractory campaign data stay study proportions until that campaign reports.
- Mould-change gantry: safe working load 250 kg chain hoist is a fit choice against the modeled seat mass; no load calculation is claimed (A-MACH: purchased item named with the rating, guard and anchor drawn).
- Unit task 02 remains open for the unsized duty (none for CAST_LINE - its sizing study AQS-DUTY-072 is issued; -02, -04, -06, -09 evidence cited in TASK_PLAN).

## What is NOT claimed

No mould residence time, no cooling-water rate, no mould pit rate, no wyde-rate claim of any kind (every number carries a basis: the graph design row, the task-04 schedule or a duty-sheet section), no measured wear allowance, no PE stamp. The -11 fabrication-detail pass (full dimension chains per part, weld symbol schedule, tolerance stack) continues on top of these sheets.
