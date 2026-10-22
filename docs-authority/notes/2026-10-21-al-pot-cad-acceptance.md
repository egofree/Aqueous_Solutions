# FOUNDRY-AL_POT-10/−12 close-out (first M3 CAD acceptance lane note)

Date: 2026-10-21. Board: FOUNDRY-AL_POT-10 `[x]` (first −10 acceptance of the 173; AQS-PLAN-006 M3),
FOUNDRY-AL_POT-12 `[x]` (bom.csv regenerated from the model), −11 open with the honest partial note
(sheets exist; per-part dimension chains and the tolerance stack stay open). A-core acceptance per
AQS-PLAN-006 §5, all 11 criteria evidenced in `models/mfg/AL_POT/build_log.md` (machine-checkable
mirror in `models/mfg/AL_POT/check.json`).

## What was built

- `models/mfg/AL_POT/params.json` (new): data of record authored from the graph node (revision AC),
  the duty sheet (§2/§3/§4), the task-04 nozzle schedule verbatim and the prior hand BOM/WO bases.
  Layout-level study choices (casing t6 / fibre t24 / ram t40 lining package, melt top z 500, head
  plate deck 1154, hopper/lance geometry, compass face assignments) are named `assumptions`/`layout_note`
  - nothing measures.
- `models/mfg/AL_POT/al_pot.py` (new): CadQuery 2.8.0 headless build reading params.json only. Shell
  bbox exactly 800×800×1600 (A-core 2); N1..N6 at the schedule faces/heights/bore/rating (A-core 3;
  compass faces are the registered layout choice); every internal a solid incl. melt inventory only as
  solids, not BOM parts (A-core 4); materials/thickness/CA per duty §3 X-MAT-22 (A-core 5: t40 ram +
  t10 graphite hot plate carry the 10 mm wetted allowance; CS t6 below the liner; Hastelloy dip leg;
  Cu bus on ceramic pads per §11); drawn anode j 0.296 A/cm2 at the model geometry, inside the
  A-M-282 0.5 class - no rate invented. BOM regenerated from the model (16 rows, qty/material/mass/
  make or buy; A-core 6). STEP (named assembly incl. inventory) + STL (A-core 9).
- `cad/stl/AL_POT.stl` replaced from the build in the **X-PAR-04 registry form**: in-envelope build
  solid (the three protruding connection groups - N1 siphon lip/crest, N3 chute group, N2/N4 stubs -
  excluded; the overhang stays reported in check.json, nothing resized), ASCII, metres, exactly
  800×800×1600 ≥1 mm, trimesh watertight with 0 degenerate edges. The X-PAR-04 test
  (`test_envelopes.py`) parses ASCII vertex text from every cad/stl file and multiplies by 1000, so
  the registry form is what keeps that gate green together with the §9 replacement rule.
- `models/mfg/AL_POT/drawings/` (new, 8 sheets × SVG+PDF): ga_front, ga_side, nozzle_orient, sh01,
  hd01, el01, aux01, iso01. SVGs carry the AQS-DWG-001 content-hash title block - **`_drawings.py` was
  extended to enumerate and stamp `models/mfg/*/drawings/*.svg`** (register series AQS-MFG-<UNIT>-<SHEET>,
  title names "AQS-PLAN-006 M3; graph revision AC"); _pid_sheets re-appended its section; the
  register is 542 rows and the stamp hashes verify against the on-disk SVGs. Welds (ISO 2553 callouts)
  and the ISO 2768-m tolerance notes ride on the part sheets; −11 keeps the per-part dimension-chain
  detail open.
- `models/mfg/AL_POT/WORK_ORDER.md`: step 2 re-pointed at the 5-plate design row + a named holds list
  (A-core 11): X-MAT-21/A-M-318 pot-cell verification campaign, unit task 12 first articles, A-M-284
  D-DOCK import gate, A-M-280 Cl2 export accounting.

## Corrections recorded (not silent)

- Cathode count 4 → 5: duty §2's graph design row (`cathodes 5`, AQS-PAR-001) governs; the prior hand
  BOM row 3 and WO step 2 said 4. bom.csv row 5 and the WO now say 5; the mismatch is logged.
- Nozzle schedule heights were authored against the earlier 800-tall envelope layout; the model honors
  every schedule height verbatim and picks the layout that satisfies both the schedule and the current
  1600 envelope (melt top below the z-600 Cl2 nozzles so the 700 C headspace stays dry, M7). Recorded
  in params.json `layout_note`; no schedule value resized.
- Bus rail drawn 32×31 = 992 mm2 for the issued 975 mm2 class rail (rounding to stock, basis row 6).

## Effects on the derived pages (all regenerated, not hand-edited)

- TASK_PLAN.md: FOUNDRY-AL_POT-10 [x] with build_log evidence, −11 [ ] with the partial note naming
  the real `models/mfg/AL_POT/drawings/` path (the note template is now an f-string so the unit name
  renders), −12 [x] with `models/mfg/AL_POT/bom.csv`.
- `_task_plan_gen.py`: `status()` gained the −10 acceptance-evidence branch (build_log + drawings +
  cad/stl existence gated exactly as A-core 9/8 ask) and the −12 bom.csv branch predates; `note()`
  suppresses the "partial: M2" for accepted units and now carries the −11 partial note when a
  drawing set exists. The line-51 T10 comment names AL_POT as the accepted exception.
- `_duty_basis.py` §7 (`7. Code.`) appends the manufacturing-model pointer where `models/mfg/<u>/*.py`
  exists (idempotent, guard on the pointer text): duties/AL_POT.md §7 refreshed (1 changed sheet,
  second pass converged "refreshed 0"); EXPANDER/LEACH_CSTR_1 sheets stay byte-identical because t
  heir §7 already named their model.
- DRAWING_REGISTER.md via `_drawings.py` (new fabrication-drawing glob) + `_pid_sheets.py` (its
  section re-append): 534 → 542 rows.

## Gates

- `pytest -q`: 90 passed (ring-fence: same 90 tests as the X-MAT-22 lane; no new tests), incl.
  X-PAR-04 envelope gate on the replaced cad/stl.
- `regen --check`: 920 files, 0 stale. Authority contract: ok. Gasket census: OK.
- Full regen not needed this lane (no graph-write stage; the manifest sha is unchanged).

## Out of scope / not claimed

No −11 closure (dimension chains / weld symbol schedule / tolerance stack verified per detail), no
other unit touched, no measured rates, no residence-time claim, TRL unchanged, no PE stamp. Next −10
units in triage order: FOUNDRY-CAST_LINE-10, FOUNDRY-CA_POT-10 (each reuses this lane's pattern).
