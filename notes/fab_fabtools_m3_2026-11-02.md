# Wafer-fab and fab-tools lane to M3 — 2026-11-02

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7;
recipe patterns `models/mfg/H2_DRYER/` (machine skid with node design block) and
`models/mfg/CRU/` (envelope fill with the hold-down frame). Graph Rev AD. One
commit per unit (plan rule 4); this note gains a section per accepted unit.
Lane: WAFER_FAB, WET_BENCH, LITHO_ALIGN, LITHO_COAT, LITHO_DEV, SOLAR_PV_CELL,
ELECTRODE_COAT, BLOW_MOLD, BMED_UPW_POLISH. Every dimension comes from the
unit's own graph node, duty sheet and issued nozzle schedule; purchased tools
are drawn as their envelope and interface per plan rule 6; misfits are
§7-reported, never resized.

## WAFER_FAB (wafer-fab tool row, FAB, tier 7) — commit 1

- `models/mfg/WAFER_FAB/wafer_fab.py` on the shared lib. Route F-MACH (the `fab`
  class sits in the F-MACH row of plan section 4). Acceptance A-core + A-MACH +
  A-SC. Build 1000 × 600 × 800 mm against the node envelope: inside, exact; one
  closed manifold mesh; `cad/stl/WAFER_FAB.stl` replaced from the build;
  `tracker --check WAFER_FAB` green.
- Machine per the node equipment list (the calculated connected load,
  0.4417 kW): CZ puller (0.2317 kW), ingot cool/anneal (0.02 kW), crop/grind/
  edge tools (0.04 kW) and the FAB_TOOL dry row (ox, RTA, metal, probe standby,
  0.12 kW) drawn as purchased-class station envelopes per plan rule 6 on the
  bench deck; N2 purge distribution (0.03 kW) as the DN15 header with four drop
  legs. Four-post hold-down frame pins the registry box (X-PAR-04); A-MACH
  guard and 8 slab anchors. Station arrangement is the layout choice (W12).
- Nozzles: all 14 schedule rows at tag, face, height and bore as atmospheric
  open-bore tube stubs flush at the envelope faces (duty section 4: nozzle
  DN15, no flange class); the four `solids` rows are non-piped transfers drawn
  DN15, bore not calculated (plan W4); drain and vent flush at the envelope
  faces. Material per duty section 3: 316L where the stream is wet, CA 0 mm.
- The envelope-era drawing set (GA.md and the stamped ga/iso/nozzle sheets)
  was superseded by the 8-sheet fabrication set (GA front/side, nozzle
  orientation, bench, stations, purge, connection hardware, iso; SVG + PDF,
  title blocks per AQS-DWG-002).
- A-SC: the parts the on-site shop makes (bench, frame, purge distribution,
  connection hardware) are flagged make in the BOM and cross-referenced to
  AQS-BOM-SC-001; the station tools are purchased envelopes.

## WET_BENCH (RCA/etch wet bench, FAB, tier 7) — commit 2

- `models/mfg/WET_BENCH/wet_bench.py` on the shared lib. Route F-MACH (the
  `wet_bench` class sits in the F-MACH row of plan section 4). Acceptance
  A-core + A-MACH + A-SC. Build 1000 × 600 × 800 mm against the node envelope:
  inside, exact; one closed manifold mesh; `cad/stl/WET_BENCH.stl` replaced
  from the build; `tracker --check WET_BENCH` green.
- Bench per the node equipment list: SC1 and SC2 baths 10 L nominal at 80 °C
  with immersion heater envelopes (2.479 kWh/d each, purchased per plan rule 6),
  DHF etch bath at ambient, DIW rinse bay, on the bench deck inside the
  four-post hold-down frame. Wetted material per duty section 3: PVC-U per
  AQS-STD-002 rules M1 and M2, no metal wetted part; above 60 °C the
  thermoplastic is CPVC — the node equipment rows give the 80 °C bath
  temperatures, so the heated baths are CPVC. The node rows name PP tanks; the
  duty selection governs (plan rule 5) — hold W12. Bath wall 10 mm and the DHF/
  rinse bath sizes are study/layout values (W12).
- Nozzles: all 13 schedule rows at tag, face, height and bore as atmospheric
  open-bore tube stubs drawn polymer (duty section 3: no metal wetted part);
  drain and vent flush at the envelope faces. `DIW` added to the glossary
  (the node equipment row's term).
- The envelope-era drawing set superseded by the 7-sheet fabrication set.
  A-SC: bench, frame, baths and connection hardware flagged make and
  cross-referenced to AQS-BOM-SC-001; heaters and N2 gun set are buy rows.

## LITHO_ALIGN / LITHO_COAT / LITHO_DEV (litho train, FAB, tier 7) — commits 3-5

- `models/mfg/LITHO_ALIGN/litho_align.py`, `models/mfg/LITHO_COAT/litho_coat.py`,
  `models/mfg/LITHO_DEV/litho_dev.py` on the shared lib. LITHO_ALIGN and
  LITHO_COAT carry the section 4 route hold by name (no route row names the
  `aligner`/`coater` classes); LITHO_DEV is F-MACH (the `wet_bench` class).
  Builds 1200 × 600 × 800, 1200 × 800 × 1400 and 1200 × 600 × 900 mm against
  the node envelopes: inside, exact; closed manifold meshes; `cad/stl` replaced
  from the builds; `tracker --check` green on each.
- LITHO_ALIGN per the node design block and AQS-LITH-001 rev C (named on the
  node): 6061 frame/base, aluminium stage, 4140 leadscrew (shop lathe),
  chrome-on-glass mask (shop mill); the 365 nm LED array (1 W optical) is the
  purchased envelope. Duty §2 prose still carries the seed figure 500 × 500 ×
  800; the node governs, older figure named (WS_SOLV precedent).
- LITHO_COAT per the node design block and note (A-M-287): spin bowl and coat
  catch bowl 316L (duty §3), 150 mm vacuum chuck (node chuck_mm), spin-chuck
  motor 0.75 kW peak and softbake hotplate 0.3 kW at 100 °C as purchased
  envelopes with node ratings; no vacuum source named on the node or duty —
  none drawn (W12).
- LITHO_DEV: wet develop bench, 316L bowl (TMAH class developer on the shared
  WET_BENCH chemistry fork), puddle dispense point (40 mL/wafer node figure);
  no purchased item named — none drawn (WS_SOLV precedent).
- Systemic observation, carried not fixed: `dot` 2.42.4 intermittently takes a
  "trouble in init_rank" error path on the byte-identical `views/mfd.dot`
  (verified identical to HEAD), rendering two layouts alternately; a regen
  pass can then fail doc-convergence and a retry converges. The LITHO_COAT
  full regen was cut by a shell timeout mid-run once and left a partial
  receipt in that commit; the amended commit carries the corrected, fully
  regenerated tree and check_all is green on it.
