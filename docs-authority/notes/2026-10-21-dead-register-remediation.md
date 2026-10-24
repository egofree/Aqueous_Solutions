# 2026-10-21 - Dead register lane remediation (`A-M-282..316`)

## Discovery

Full-tree scanning during Wave-1 prep found graph/driver rows citing register rows
`A-M-282..300` that never landed: the max committed register id was `A-M-281`, and
`A-M-280`/`A-M-281` were later occupied by unrelated live rulings (NaOH import ruling,
crew-of-4). The dead lane's citation contexts were self-describing, but no prose row
text survived anywhere (`notes/` grep clean), so recovery was verified to be
**reconstruction per semantic cluster**, not re-occupation of the dead numbering.
Working map: 35 citation groups with +-170-char contexts (extracted 2026-10-21).

## Decision

Rebuild one register row per semantic cluster (values/units/verification taken verbatim
from the surviving citing driver rows), re-homing every dead citation to the new row id
instead of reusing dead numbers where the meaning differs. `A-M-280` (pot-cell ctx)
stays valid since the new row `A-M-282` genuinely owns that cluster; all other dead
numbers remap forward. Live rows `A-M-280`/`A-M-281` untouched (append-only diff
verified: all 281 pre-existing rows byte-identical and in place).

## Remap table (dead ref -> new row)

| dead ref              | cluster                                                           | new row |
|-----------------------|-------------------------------------------------------------------|---------|
| A-M-282 pot-cell ctx  | terminal V / anode j / CE / bath hold                             | A-M-282 (rebuilt) |
| A-M-282 N+1/standby   | N+1 alternate policy, standby-zero                                | A-M-283 |
| A-M-280 Kroll/dock ctx| D-DOCK feedstock import ruling                                    | A-M-284 |
| A-M-284 dock-import   | (kept - same ruling cluster)                                      | A-M-284 |
| A-M-284 export ctx    | pot-line export margin                                            | A-M-285 |
| A-M-281 knock-out     | investment wax/shell reclaim split                                | A-M-286 |
| A-M-284 litho ctx     | LITHO_STUB retirement into 3 real tools                           | A-M-287 |
| A-M-282 AUD bounding  | wafer starts/d bounding value                                     | A-M-288 |
| A-M-283 fluoro rate   | AQS-RATE-FP-MET design case                                       | A-M-289 |
| A-M-283 CRU supersedes| halogen loop closes on CRU balance (supersedes no-internal-sink)   | A-M-290 |
| A-M-285 stub cluster  | REMIN 291, VCD 292, BLOW_MOLD 293, ELECTRODE_COAT 294, SOLAR_PV_CELL 295, GEO_ORC 296 | A-M-291..296 |
| A-M-286 load-basis    | X-ELS-02 Rev C residual pass                                      | A-M-301 |
| A-M-286 heat-battery  | Q1..Q4 store holds/swings                                         | A-M-302 |
| A-M-287..290 driver rows | headers DN/rho                                                 | A-M-303..306 |
| A-M-291..294 geo      | bore capacity/spacing/pumps                                       | A-M-307..310 |
| A-M-295/296 MEOH      | subcool / PEM cell design point                                   | A-M-311/312 |
| A-M-297/298/300 fire  | pump head margin / refill duration                                | A-M-313/314/315 |
| A-M-284 ca-add ctx    | melt Ca deoxidizer fraction                                       | A-M-316 |

## Stage A-C steps

1. **Stage A**: 35 rows appended to `docs-authority/assumptions_manual.json` (A-M-282..316)
2. **Stage B**: 48 register/owner/note/basis/source field remaps in
   `flow_graph/param/drivers.json` (44 generic text remaps + 25 structured
   `register`-by-path remaps for HB/HDR/GEO/MEOH/fire)
3. **Stage C**: 170 refs remapped in hand-source modules: `foundry_poly.py` (102),
   `write_graph.py` (8), `fluoro_train.py` (5), `stub_activation.py` (21),
   `_load_list.py` (3), `models/mfg/foundry.py` (21), `models/mfg/polymers.py` (8),
   `regen_manifest.json` (2)
4. **Regen**: `python3 -m flow_graph.param.regen` (multi-pass fixed point) self-heals
   all generated notes, duty pages, views, P&IDs, LOAD_LIST, registers and receipts
5. **Gates**: `regen --check` 0-stale (920 files), `check_authority_contract.py`
   projection=on-disk (178/557), `pytest` 43/43 — all pass

## Pass-order / keyword discipline (recorded for any future re-run)

The context-driven remapper is order-sensitive:
- exact-phrase replacements run first (parenthetical pairs, supersedes-lines, bracket
  ranges (`A-M-284..285`) and dock/range-only contexts)
- the **token remaps** (removing the remaining bare `A-M-28XX`) run interleaved with the
  exact set so created ids are never reprocessed by later passes; unconditional remaps
  run LAST (281 → 286)
- keyword windows are scoped same-line-first, small fallback radius to avoid
  cross-note contamination; word-boundary guarded patterns (e.g. `Cl2` matches `Pot
  Cl2` and the chlorine-ruling line, not the `MgCl2` salt-chemistry lines)

## Number of value changes during remediation: 0

Rebuilt rows copy the citing assessment value verbatim from the drivers that cite it,
and `git show HEAD:plant_flow_graph.json` vs regenerated graph: 3482 numeric values
match exactly (multiset identity) — a pure string/provenance transition, no sizing or
basis moves. The X-ELS-02 planned `need` re-derivation is a separate, later step.
