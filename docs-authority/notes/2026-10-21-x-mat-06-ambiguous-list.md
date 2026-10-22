# X-MAT-06 — Ambiguous audit list resolved (AQS-STD-002 Rev M §13)

Date: 2026-10-21. Item: X-MAT-06 (closed; depends X-MAT-01, unit task 01 — both done). Triage: desk P2.

## What was done

1. **Done-when evidence (machine).** New `docs-authority/_ambiguous_units.py`: builds the section 2
   ambiguous roster (77 units — 14 audit bullets), covers each from (a) 27 units resolved by the
   issued doc sections, (b) 18 units by the §13.1 hand-adjudication rows, (c) 32 units by the
   generated §13.2 per-unit table (wetted stream + carrier + temperature basis + node material, from
   the graph and the regenerated line-list rows). `--done` exits 1 if any roster unit is uncovered.
   Green at closure: no misses.
2. **Two material conflicts adjudicated against the issued bases (graph rows corrected):**
   - **HDR_H2**: AQS-REV-H2-001 §2 classifies the header *wet, reducing, acid (M3)* → PVC-U, bonded.
     The graph `headers.py` stamp said "316L tube, orbital-welded" — contradicted the issued review
     and the §6 ruling. Corrected to `PVC-U, bonded; wet acid H2 + sweep air per AQS-REV-H2-001` .
     The §11 Rev K sentence ("HDR_H2 (316L, class M1)") reworded to the same ruling (per-cell
     dielectric flange + condensate trap kept; plastic run carries no isolated conductors).
     Line-list: the 13 wetted HDR_H2 lines (dry gas M1 ×9, hot-leach P2 ×2, acid/brine P1 ×2)
     reclass to the **new P1 wet-acid-header family** (AQS-PIP-004 Rev C); census 23 families,
     0 catchalls. `mandate` and §12.1 updated.
   - **Q3_A/Q3_B**: heat batteries hold 100 °C water (t_nom, AQS-DUTY-008 sec. 5); PP-H is an 80 °C
     class material ([S4]). `heat_battery.py` now displays `MAT_TIER`: Q3 = SA-240 304L, welded;
     Q4 (70 °C) + Q4_BUS keep PP-H. Same hold-energy basis; sizing untouched.
3. **Graph/param changes** (both display-material rows; no rates) under flock, full `regen --write`:
   pass-invariant — IA-PV-01 336.8304 unchanged across two consecutive full passes and equal to
   HEAD (the 336.7016 golden in AGENTS background predates an earlier committed lane; the value did
   not move in this lane). pytest 43/43; `regen --check` 920 files 0 stale; authority contract green.
4. **Generator staleness fix.** `_duty_basis.py` only rendered §3 for *new* sheets; existing sheets
   kept default templates even when the graph gained an issued `design.material`. Now it re-renders
   §3 **only where it still holds a default template** (three template prefixes) and the graph
   carries design/design_storage material; hand-written per-unit texts (e.g. the AQS-REV-H2-001 rows)
   are never overwritten. 19 sheets refreshed (Q3_A/B now carry the 304L row; HDR_O2 carries its
   ASTM G93 row; HDR_H2's custom text preserved unchanged).
5. **Doc.** MATERIALS_STD Rev M: history row M; §12.1 counts updated (dry gas 47→38, hot leach
   46→44, acid/brine 54→52) + the new P1 header family row; §12.2 pot-cell promise reworded (the pot
   selection stands open under unit task 09, tracked on the X-MAT pot-cell follow-up — pot cells are
   not §2 items); §11 reword; §13 (method + 23 hand rows incl. the previously unstated temperatures
   — GLASS_DIGEST Q3-tier basis, RELIEF_H2/H2_DRYER edge stamps, MEOH_COND/WS_SOLV/BMED_UPW_POLISH
   edge stamps, 0-duty stubs declared "no wetted stream" — + generated §13.2 table + §13.4 pointer
   list). X-GOV-20 wording gate respected (the vendor-skid phrasing is not reintroduced).
6. **Board.** X-MAT-06 in DONE_X, EVIDENCE_PASS → MATERIALS_STD.md, dated closure comment;
   TASK_PLAN line 582 ticked.

## Open holds named in §13 (not blockers of the done-when)

- Pot cells (MG_POT/CA_POT/F_RECOVER/POLY_STOCK wetted selection) — unit task 09, X-MAT follow-up.
- H2_DRYER regeneration temperature; ZNBR2 hypobromite coupon verification.
- WS gasket detail — X-MAT-03; PIP-003 Rev B class sheet for the "—" families.
- MET_HX_Q4 material statement activates with melt-heat-recovery sizing (0 kW stub today).

## Verification

`_ambiguous_units.py --done` OK; `_service_census.py` 323 rows / 23 families / 0 catchalls;
`_material_temps.py` 73 edges / 0 exceed; pytest 43; regen --check 0 stale; authority contract green.
