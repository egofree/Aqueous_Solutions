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
