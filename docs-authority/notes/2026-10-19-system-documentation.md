# System documentation refresh, 2026-10-19

Document number: no new AQS number; working record (narrative/hand-maintained docs only).
Authority: graph Rev AC (`flow_graph/plant_flow_graph.json`, 178 nodes, 493 edges).
Trigger: the unified parametric system (2026-10-18/19) landed after these docs were last
touched; the narrative docs described a pre-unification repo. This pass refreshes
narrative/hand-maintained documentation only. No derived file was regenerated, no code was
changed, no commit was made (the parent session sequences the regen and commits after the CAD
lane lands).

Every claim below was verified against the repo before writing (file cited beside it).

## Documents touched

| Document | Change | Why |
| --- | --- | --- |
| `README.md` (repo root) | Rewritten: new "The spine" section (graph / drivers / system tree / regen / workbook / task plan), layout tree updated (`models/mfg/`, `notes/`), design-tool section, rebuild section now leads with regen, authority section closes with "the graph wins and the document is regenerated" | The old README predated the unified system: no drivers, no tree, no regen command, no workbook, no UI, layout listed `models/freecad` only |
| `AGENTS.md` | Added one "Regeneration" paragraph after Sizing | Task instruction: after any graph/drivers/TF change run `python3 -m flow_graph.param.regen`; receipt + staleness gates are the proof; workbook/views/sheets/P&IDs/task plan regenerate with it |
| `docs-authority/PROJECT_PLAN.md` | Rev A → B: authority restamped graph BH → AC; rev table added; Limits updated — one-number-one-door sentence appended to the graph-authority line; loops_closed line extended (balance closure is a model result, not the flag); D-DOCK trade-boundary limit added; D-PV derivation-direction limit added | Header cited graph Rev BH, stale since 2026-10-17 (graph says AC). The two owner rulings are limits the plan did not carry |
| `docs-authority/internal/MASTER_PLAN.md` | Header authority restamped AC; new "Closed at Rev AC (2026-10-18/19)" table (17 rows: D-AIR/D-O2/D-FARM/D-GEO_ORC/D-PV/D-DOCK, balance closure, drivers, tree, regen, workbook, UI, P&IDs, foundry/polymers sizing + pending-commit builders, suite green, evidence pass); new "Current status (2026-10-19)" block | Close-out record of the D-rulings and the unified-system build, each with the implementing commit hash from `git log --oneline -30`; CAD-lane work marked "pending commit" (uncommitted at 0d9920d) |
| `docs-authority/DESIGN_TOOL_ARCHITECTURE.md` | Rev D → E row in the rev table; three Rev E endpoint rows added to the §7 API sketch; new §13 implementation-status section | The architecture lock doc ended at Rev D (2026-10-01) with no knowledge of the unified-engine wiring; §7 table was missing the three live endpoints |
| `design_tool/README.md` | New "U6 — working design UI on the unified engine" section (three endpoints, panels, toggle precedence, side-effect-free GET note); three rows added to the endpoints table | The README documented the API only through WP-C1; U6 (commit fc083f8) shipped the endpoints and panels undocumented here |
| `design_tool/web/README.md` | TreeTogglePanel row extended with the verified precedence example (train off flags exactly its units; unit flag beats train) | Panels and endpoints were already documented (U6-issued); only the verified-over-HTTP precedence wording was missing |
| `models/freecad/UNIT_MAP_COVERAGE.md` | Header restamped Rev D / 2026-10-19; new "Rev D (2026-10-19)" section; Summary counts and Full table headings marked "Rev B census — historical" | The map json is at Rev D (137 entries, working tree) with 36 foundry/polymers `cadquery_export` rows + 8 restored-unit/store rows from the in-flight CAD lane; the doc's census table still describes Rev B (91 nodes) and must not be silently presented as current |
| `docs-authority/notes/2026-10-19-system-documentation.md` | This record | House rule: every change carries its record |

Note: the task brief placed the coverage doc under docs-authority; the file
lives at `models/freecad/UNIT_MAP_COVERAGE.md` (verified by glob — no copy exists under
docs-authority) and was edited there.

## Facts verified before writing

| Claim | Source |
| --- | --- |
| Graph Rev AC, 178 nodes, 493 edges, `loops_closed: false` | `flow_graph/plant_flow_graph.json` |
| drivers.json: 703 keys at HEAD, 712 in the working tree (CAD lane +9); every key value+units with ref / register / owner basis | `flow_graph/param/drivers.json`, `git show HEAD:flow_graph/param/drivers.json` |
| system_tree.yaml: AQS-SYS-TREE-001 Rev A, 249 nodes = 19 sectors / 30 trains / 178 leaves | `flow_graph/system_tree.yaml` |
| regen: 44 stages in `regen_manifest.json`; receipt `flow_graph/derived/_regen_receipt.json`; `--check` runs `_rev_stamp.py` | `flow_graph/param/regen.py`, `flow_graph/param/regen_manifest.json` |
| 876 derived files under the staleness gates | `docs-authority/DERIVED_REVISIONS.md` header |
| MODEL_WORKBOOK.xlsx: 24 sheets (README, DRIVERS, TREE, ELECTRICAL, HEAT_LEDGER, 19 sector sheets, ...) | loaded with openpyxl |
| Balance: failing units 43 → 0; `balance --write` convergent; suite 43/43 | commits e348e62, 4993875, 456f6a6, 0d9920d |
| P&IDs: 174 graph-derived sheets, AQS-PID-001-<unit> series | commit 3fd9582; `docs-authority/DRAWING_STANDARD.md` |
| UI: `/api/v1/system-tree` (app.py:361), `/api/v1/params` (:421), `/api/v1/regen-status` (:464); ParamsPanel / TreeTogglePanel / RegenStatusBadge components; `store.apply_overrides` server-side precedence | `design_tool/aqs_design_tool/api/app.py`, `design_tool/web/src/components/`, commit fc083f8 |
| D-rulings and outcomes (electrolyzer O2 source, dock trade boundary, GROW_BED re-base, PV 200 %/footprint-derived, heat reuse-first) | `notes/first_principles_audit_2026-10-17.md`, commits 3408108 / db43602 / 6a4aced / f202487 / 7625989 / c369bda / e348e62 |
| Evidence pass: 62 cited, 6 reopened, 568/2871 done | `docs-authority/notes/2026-10-19-evidence-pass.md`, `docs-authority/TASK_PLAN.md` |
| Map Rev D: 137 entries = 93 + 36 foundry/polymers (26 `models/mfg/foundry.py` + 10 `models/mfg/polymers.py`) + 8 restored-unit/store rows | `models/freecad/unit_freecad_map.json` vs `git show HEAD:` (93 rows, Rev C) |

## Verification of this pass

- `git status` shows only the nine files above added to the pre-existing CAD-lane dirt
  (`models/**`, `flow_graph/param/foundry_poly.py`, derived outputs); no derived file
  regenerated by this pass.
- Test suite untouched: no code file modified.
- No commits made.
