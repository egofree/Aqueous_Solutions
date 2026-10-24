# AL_POT build log - FOUNDRY-AL_POT-10 / FOUNDRY-AL_POT-11 acceptance

Date: 2026-10-21. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Model source: `models/mfg/AL_POT/al_pot.py` + `params.json`; drawing set `models/mfg/AL_POT/drawings/`;
build script chain run headless (about 45 s elapsed on the build machine):

    $CADQUERY_PYTHON al_pot.py         # build + checks + bom.csv + STEP/STL
    $CADQUERY_PYTHON draw_al_pot.py    # 8 SVG sheet sources (notes bands, no title block yet)
    python3 docs-authority/_drawings.py      # AQS-DWG-001 title blocks + DRAWING_REGISTER.md rows
    python3 docs-authority/_pid_sheets.py    # re-appends the AQS-PID-001 register section
    $CADQUERY_PYTHON draw_al_pot.py    # PDF pass from the stamped SVGs

## Tool versions (recorded per A-PLAN-006 5.1)

- CadQuery 2.8.0 (in a dedicated virtual environment; the plan's 2.8.0 pick holds), python 3.13.
- trimesh 5.1.1 for the STL manifold check; cairosvg for the SVG -> PDF pass.

## A-core evidence (check.json is the machine-checked copy)

1. Builds headless from params.json with no manual step. Run recorded above with tool versions. check.json written by the build.
2. Bounding box: shell assembly exactly 800 x 800 x 1600 (bbox_abs [-0.3, -0.0, -0.1] .. [800.0, 800.0, 1600.4], boolean tolerance rounding only) = the duty section 2 envelope to within 1 mm: PASS. The task-04 schedule connections protrude by design outside the shell faces (<= 50 mm, the siphon/lip and chute are connection hardware, not resized geometry); nothing was resized, overhang per face recorded in check.json (`connection_overhang_mm`).
3. Every nozzle of duty section 4 (docs-authority/nozzles/AL_POT.csv, N1..N6) modeled at its face, height, bore and rating: N1+X/600 siphon lip, N2 -Y/600 DN15 Class 150, N3 -X/160 chute+lance, N4 +Y/600 DN15 Class 150, N5 bottom DN15 sump face z 50, N6 top/riser/800 DN15. Faces (which wall) are not given by the schedule; the assignment is registered in params.json `layout_note` and on nozzle_orient.
4. Every internal is a solid: anode bank (5 rods), cathode plates (5), clamps, bus rails/straps/pads, hood hot plate, hood + rim, head plate, riser, dip leg, siphon, chute group, drain well, sleeves. The melt salt and metal layer are included as named solids in the STEP assembly (process inventory; not BOM parts). No internal is represented by text.
5. Materials/thickness/corrosion allowance match duty section 3 (X-MAT-22): CS shell t6 below the liner; ceramic-fibre t24 backup; graphite ram t40 wetted liner and t10 hood hot plate carrying the 10 mm design allowance; graphite anodes A-M-282 class; mild-steel/clad cathodes; Cu bus on ceramic pads per AQS-STD-002 section 11; CS riser in dry hot Cl2 (M7); Hastelloy C-276 dip leg. Drawn anode current density 0.296 A/cm2 (check.json), inside the A-M-282 0.5 A/cm2 class envelope stated on the duty sheet - no rate invented.
6. BOM regenerated from the model: bom.csv (16 rows: qty, material, mass from solid volumes, make/buy). The prior 7-row hand BOM's descriptions and bases are carried over and split to the modeled part level.
7. Every bolted joint in fasteners.csv: clamp studs 10 x M12, hood rim 16 x M10, anchors 4 x M12. Rotaries/welded seams covered by the part-sheet weld callouts (AQS-PLAN-006 W7).
8. Drawings exist and name the graph revision: 8 sheets (ga_front, ga_side, nozzle_orient, sh01, hd01, el01, aux01, iso01) as SVG + PDF under models/mfg/AL_POT/drawings/. Each SVG carries the AQS-DWG-001 title block (content-hash revision per ASME_Y14_35/ISO_7200, applied by docs-authority/_drawings.py) whose title names "AQS-PLAN-006 M3; graph revision AC", plus the fab-notes band on the sheet; the keys (dimensions, welds, tolerances) are sheet notes from the build geometry. The register DRAWING_REGISTER.md holds the 8 rows (AQS-MFG-AL_POT-<SHEET>, rev = content hash c1270b3c etc.), and the stamp hash was verified against the on-disk SVG after stamping.
9. STEP and STL exist: export/al_pot.step (named assembly incl. process inventory) and export/al_pot.stl (full assembly incl. the protruding schedule-connection hardware; binary-checked watertight by trimesh). cad/stl/AL_POT.stl is replaced by the build: the in-envelope build solid (casing, lining, head plate, hood group, electrodes, bus, riser, dip leg, sleeves, drain; the three connection-hardware groups named in check.json `external_parts` live at the faces only), in metres and ASCII per the X-PAR-04 envelope registry (the gate test parses ASCII vertex text and multiplies by 1000; the registry requires the box to equal the graph size to 1 mm - parsed bbox exactly 800 x 800 x 1600). STL checked closed and manifold (trimesh: watertight True, 0 degenerate edges after vertex merge, 13254 faces). Nothing was resized; the <= 50 mm connection overhang stays reported on check.json.
10. Duty section 7 points at the model: the sheets regenerate with the manufacturing-model line (duty_basis 7. Code names `models/mfg/AL_POT/al_pot.py`); the graph design row and the duty size line still agree (800 x 800 x 1600 envelope, same basis strings).
11. WORK_ORDER.md carries every hold by name (Hold list section added this lane).

## Corrections made on the way in (recorded, not silently resolved)

- Cathode count: the duty section 2 graph design row says `cathodes 5` (AQS-PAR-001); the prior hand BOM row 3 and WORK_ORDER step 2 said 4 plates. The model draws 5 and bom.csv row 5 carries the corrected quantity; WORK_ORDER step 2 re-points at the design row. No sizing value was changed - the count is the recorded graph design.
- Nozzle heights vs. the current envelope: the task-04 schedule was authored against the earlier pot envelope; the heights are honored verbatim and the layout (melt top z 500 below the z-600 Cl2 nozzles so the 700 C headspace stays dry, M7; internal head plate deck at 1154; textures at the roof datum 1594) is the study layout that fits both the schedule and design row. This is recorded as params.json `layout_note`.
- bus rail section: drawn 32 x 31 = 992 mm2 for the issued 975 mm2 class (round stock cut, basis row 6).

## Holds (named; the plant keeps them open)

- X-MAT-21 / A-M-318 pot-cell verification: first-article liner and anode change-out data, bath analysis, shell-liner inspection vs the 10 mm allowance. This model's resistance/lining thicknesses are study proportions until that campaign reports.
- Unit task 12 (first articles + real BOM at order): clamp torque schedule, refractory campaign, hood gasket set.
- D-DOCK feedstock program (A-M-284): the unit is live on the ruling; import logistics are the feed gate, not this model.
- Unit task 02 remains open for the unsized duty (none for AL_POT - its sizing study AQS-DUTY-072 is issued; listed for completeness of the -10 dependency note: -02, -04, -06, -09 evidence cited in TASK_PLAN).

## What is NOT claimed

No residence-time claim from the melt volume (0.187 m3 drawn solids; duty sheet 1.024 m3 envelope stays a box rule), no measured corrosion rate, no PE stamp. The -11 fabrication-detail pass (full dimension chains per part, weld symbol schedule, tolerance stack) continues on top of these sheets.
