# Instrument loops for the loop-less units (X-CTL-01 per-unit extension), 2026-10-20

Document number: AQS-PLAN-007 note (working record; no new AQS number).

Authority: X-CTL-01 (AQS-CTL-001 instrument index), X-CTL-03 (AQS-CTL-003 SIF/cause-and-effect) and X-SAF-01 (AQS-SAF-001/008
HAZOP closure evidence). Graph state: Rev AC fixed point, HEAD ff4ac7e at lane start. Concurrent lanes in the same tree while this
ran: duties (§1/§6 sheets), nozzles (csvs), task-plan evidence. No commits (lane order).

## Why the 62 units owned no loop

`flow_graph/inventory/other.py` (AQS-INV-004, graph-side) emits instrument rows only where the unit (a) has a `nozzles/<UNIT>.csv`,
(b) has liquid inflow with class not in farm/product/building/hab, or (c) is hcl_synthesis/pem_electrolyser — and it skips the
boundary/header/relief classes outright. So: FOUNDRY 27 and POLYMERS 10 machines are solid-fed and had no nozzle csv at the last
AQS-INV-004 regen; headers (HDR_CO2/H2/N2/O2/UPW, NCG_HEADER, Q4_BUS), relief stacks (RELIEF_H2/CRYO) and the boundary node are
class-skipped; the stores (FOOD/METAL/POLY_STOCK, PROD_O2/PROD_MEOH, AIR_RECEIVER) fail the class/liquid gate; and EVAP_ACID_VS
holds only a gas-detector row, which AQS-CTL-001 excludes by rule (gas detection is AQS-SAF-006, wired to the fire panel and SIS).
The evidence audit (notes/2026-10-20-evidence-audit.md, T08 residual) named this as X-CTL-01 per-unit authoring work; this lane
did it in the docs-side generator (`_instr_index.py`), not in `other.py`, per the lane write scopes.

## What was authored — 123 loops, 599 -> 722 tags, 138 -> 199 units

By tag letters: TE 61 (8 are independent SIF elements numbered -90), LT 25, PT 13, AE 8 (Cl2 x5, HF, pH, ORP), IT 5 (pot-cell
current), FT 4, ST 2, LSH 2, PSH 2 (rupture indication, DI), ZT 1 (forge ram). By PLC: FOUNDRY 55, POLYMERS 26, DIGESTER 10,
CRYO 9, HEAT 6, OIL 5, GAS 4, HAB 2, WTR 2, FARM 2, GLASS 1, ELEC 1 — all AI except the 4 discrete points (LSH x2, PSH x2).
Every range cites its graph param, edge or inventory artifact in the CSV `basis` column; nothing is invented. Loop classes:

- **Pot cells** (AL/CA/MG/CR/MO): cell current IT (0-5000/10/200/50/10 A, 2 x design `I_A`), bath TE type K (band from design
  `bath_T_C` 650-700 C), hood/anode-gas Cl2 AE 0-100 vol % (offtake edges cited); molten-bath LT on CA/MG (brine make-up edges).
- **Kroll train** TI_CELL: retort TE 0-1100 C and chlorinator TE 0-1000 C (design `retort_T_C`/`chlorinator_T_C`), retort PT
  (house 0-10 bar g fallback; Ar cover), TiCl4 receiver LT (design chemistry, AQS-BAL-KROLL).
- **Melt/cast chain**: IND_MELT/RF_HEAT/CAST_LINE/VAC_IND/VAC_CAST/CONT_CAST/INV_CAST melt TE type B 0-1600 C (Cu/Fe/Zn/Al
  service), pour-ladle/tundish/crucible laser LT, vacuum-chamber PT 0-1000 mbar a; SINTER/RES_HEAT/SHELL_BURNOUT TE + independent
  TE-90 (design T_C 900-1300 C); CONT_CAST per the water-cooled mould design.
- **HF kiln** HF_GEN: spar feed FT (loss-in-weight, 2 x IA-CAF2-MU normal), kiln/offgas TE (design `T_C` 250) + TE-90, offgas HF
  analyzer AE (design `hf_kg_d`), feed blend vat LT (concentrate + acid make-up edges).
- **VDF/TFE trains**: chlorination/cracking/pyrolysis TEs per the design keys (350/650/750 C bands); HF feed-tank LTs.
- **Polymer kettles**: POLY_F/POLY_COND kettle TE + LT (design `T_C`/`jacket_C`/`H_mm`); POLY_OLEFIN TE + TE-90, PT 0-100 bar g
  (design `P_MPa` 5.0 at 1.25 x), LT.
- **Formers**: FILM_CAST melt TE 0-300 C (design `melt_C` 220) + chill-roll ST + feed LT; POWDER_RESIN mill TE + ST (design
  `duty_kW`); PELLET process-water TE.
- **Benches**: WAX_PATTERN/SHELL_BUILD/FLUX_PREP tank TEs + pot/slurry/hopper LTs (design `pot_L`/`slurry_L`/`hopper_L`);
  SHELL_BREAK/STOCK_OUT/METAL_STORE band-by-service TEs (knock-out table, staging condensation watch).
- **Headers**: PT on every gas header (HDR_CO2/H2/N2/O2, NCG_HEADER; 0-10 bar g house fallback, feed edges cited); HDR_UPW PT +
  FT on S01 (2 x normal rule); Q4_BUS hot-water bus TE + PT (65 C design temps).
- **Stores**: PROD_MEOH FT/LT/LSH/TE (IA-MEOH-PROD at 792 kg/m3), PROD_O2 + AIR_RECEIVER PT/TE (receiver/bank pressure),
  FOOD_STORE/POLY_STOCK TE + bin LT.
- **Relief**: RELIEF_H2/RELIEF_CRYO PSH rupture-disc/PSV-lift indication (DI, IEC 60947-5-1).
- **EVAP_ACID_VS**: pH AE 0-14 + ORP AE (NaOH scrub liquor, breakthrough watch on IA-VS-OFF), LT + LSH, FT on the 0.35 m3/h
  recirculation (AQS-INV-001), independent TE-90.
- **Heat machines**: ADS_CHILL drive-water and chilled-water TEs (65 C / 12 C services), MAU_HX, DRY_COOLER.
- **Standby remainder**: GREASE_CA/LI kettle TE + LT, LI_RECOVER/P_CA LT, SI_REDUCE furnace TE (band by service; rates pending
  assay — stated in the basis), EXT_HALL hall-air TE (68.28 kW feed, ventilation watch).
- **AFTERBURNER_FLUE-TE-90**: repairs a pre-existing gap — the SIF initiator existed in sif_list.csv with no index element
  (other.py's sif pass never re-ran after sif_list changed).

Residual: **BOUNDARY_EXPORT** owns no loop by design — it is the DOCK-sector boundary bookkeeping node for loss and curtailment
splits, not a process unit. The generator now asserts that the no-loop set is exactly {BOUNDARY_EXPORT}, so any future unit
without loops fails the run loudly instead of regressing silently.

Precedence rule added to the generator: an AQS-INV-004 row of the same tag letters for one of these units wins over the authored
row (per-letters, SIF -90 rows included), and duplicate tags are asserted against — so the inventory lane can catch up without
collisions.

## HAZOP closure (X-SAF-01 / AQS-SAF-008) — honest numbers

The committed register (34 tracked) was **stale**: regenerating at the current graph *before* the loops gave **78 tracked**
actions = 44 indication (30 temperature + 14 level, all on these units) + 34 relief. The lane brief's "18 indication actions of
34" was computed against the stale register; the real target at the current graph was 44.

After this lane: **0 tracked**. All 44 indication actions are closed by the TE/LT loops above (their deviation rows now carry
the safeguards and raise no action). The 34 relief actions also closed at the same regeneration because the concurrent duties
lane had by then issued the duty-sheet section 6 relief statements (e.g. duties/IND_MELT.md, duties/AL_POT.md) — that closure is
the duties lane's evidence, not this lane's. Final `hazop_actions.csv`: 221 actions — 125 closed at issue, 96 closed in the SIF
pass, 0 tracked; `HAZOP_ACTION_REGISTER.md` tail now reads "No open engineering actions."

SIF/cause-and-effect (AQS-CTL-003, regenerated): 166 functions; new initiators cite the authored tags — IND_MELT-TE-90 (SIL 2,
1oo2), RES_HEAT/SINTER/SHELL_BURNOUT/HF_GEN/POLY_OLEFIN/EVAP_ACID_VS TE-90 (SIL 1), LSH feed trips on EVAP_ACID_VS and
PROD_MEOH. `_sif.py`'s "TE-90 not yet in index" note is gone (was 6 at baseline, 1 after the first pass).

## Verification

- `python3 docs-authority/_instr_index.py` then `_hazop.py` then `_sif.py` (order matters): 722 rows / 123 authored / 62 units
  extended; 0 tracked HAZOP actions; 166 SIFs; duplicate-tag and coverage asserts pass.
- `python3 -m pytest -q`: **43 passed** (before and after).
- `python3 -m flow_graph.param.regen --check`: 875 files, **0 stale**, rc 0.
- T08 detection: `_task_plan_gen.py` run temporarily — task-08 ticked rows **112 -> 173/173** (each cites its loop count in
  AQS-CTL-001); `docs-authority/TASK_PLAN.md` restored with `git checkout` immediately after (not regenerated, per lane order).

## Handoffs (files outside this lane's write set)

1. **CONTROL_ARCH.md (AQS-CTL-002)**: rerun `docs-authority/_plc_arch.py` — the I/O table predates the extension and has no
   PLC-FOUNDRY (55 AI) or PLC-POLYMERS (26 AI) rows; every sector's AI/DI counts also moved.
2. **AQS-INV-004 (`other.py`)**: nozzle csvs now exist for many of these units, so the next inventory regen will start emitting
   generic TE/PT rows for them; `_instr_index.py` resolves precedence per tag letters (inventory wins, duplicate tags asserted).
   Its sif pass will also carry the AFTERBURNER_FLUE element; the authored row stands down then. The AQS-INV-004 "one AI point
   per instrument" count is likewise stale (713 at last regen vs 722 instruments now).
3. **P&IDs (AQS-PID-001)**: the `pid_sheets` regen stage will pick the new tags up onto the unit P&IDs (X-CTL-01's done-when is
   "every tag on every P&ID").
4. **HAZOP_ACTION_REGISTER.md prose**: the "Handoff (not writable from the docs lane)" paragraph in `_hazop.py`'s register text
   still describes the indication-item handoff; it is obsolete now that the items are closed — wording update belongs to the
   HAZOP/controls lane that owns that generator.
5. **TASK_PLAN**: the X-SAF-01 status line ("34 tracked open ... on 17 units") and per-unit task-08 evidence will refresh at the
   parent's next TASK_PLAN regeneration; T08 then reads 173/173.
6. Consumers that read the index but were not regenerated here (their lanes own them): `_commissioning.py`, `_haz_area.py`,
   `_pid_sheets.py`, `_perf_test.py`, `_plc_arch.py`.

## Write set of this lane

`docs-authority/_instr_index.py`; `docs-authority/inventory/INSTRUMENT_INDEX.csv`; `docs-authority/INSTRUMENT_INDEX.md`;
`docs-authority/CAUSE_EFFECT.md` (via `_sif.py`); `docs-authority/HAZOP.md`, `docs-authority/HAZOP_ACTION_REGISTER.md`,
`docs-authority/hazop_actions.csv`, `docs-authority/sif_list.csv` (via `_hazop.py`/`_sif.py`, per the lane brief); this note.
Pre-existing drift corrected by the regen, disclosed: 4 FT basis texts updated to current edge rates (CRU-FT-01, NORTH_DOCK-FT-02,
ZNBR2-FT-01, ZNBR2_BR2_REGEN-FT-01 — the committed index predated the Rev AC fixed point). Files modified in the tree by the
concurrent lanes during this work (duties/*, nozzles/*, `_duty_basis.py`, `duties/_generated.json`, `DERIVED_REVISIONS.md`) are
not this lane's. No commits.
