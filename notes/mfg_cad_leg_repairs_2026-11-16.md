# MFG cad-leg repairs — 2026-11-16

`python3 -m flow_graph.param.regen --stage cad_mfg_models` failed on engine-v2:
the calcium- and magnesium-pot builders asserted on schedule rows their PLACE
records did not place — `['N10']` in `models/mfg/CA_POT/ca_pot.py`, then
`['N11']` in `models/mfg/MG_POT/mg_pot.py`. Both rows landed with the
instrument-index controls wave (commit 0ec28e7ca, the four new units' loops)
and name the BRINE_CRYS recovery route (the X-QA-11 dock-import round):

- CA_POT N10, "crystallized CaCl2 to the calcium pot (recovered, was the dock
  import)", DN15 Class 150, inlet, z 160 — stream IA-BRINE-CACL2.
- MG_POT N11, "crystallized MgCl2 to the magnesium pot (recovered, was the
  dock import)", DN15 Class 150, inlet, z 160 — stream IA-BRINE-MGCL2.

The graph and the nozzle schedules agreed; only the drawing builders lagged.

Fix, the established inlet idiom per unit, no new sizing:

- `ca_pot.py`: N10 as `brine_inlet_group_3` — the N2 idiom (chute box flush at
  the -X face, z 130..220, DN44-class lance into the bath at z 160) in a study
  slot beside N2/N7 (chute y 490..650, lance centre y 570). The group joins the
  EXTERNAL face hardware, the density table, the nozzles_drawn record and the
  BOM as item 20.
- `mg_pot.py`: N11 inside `inlet_groups` — the N10 launder idiom (flush at the
  -Y face, z 130..220, lance into the bath at z 160) in a study slot beside N10
  (launder x 34..70, lance x 52, the melt inventory cut like N3/N4). The
  nozzles_drawn record and BOM item 12c carry it (4 inlets).

A static check of every builder against its schedule (the same tag-set compare
the builders assert at the end of a build) shows no remaining coverage gap.
Found while regenerating the CAD stages on the wt-cadfix recovery branch; the
CAD byte-stability port (notes/cad_byte_stability_2026-11-15.md) needs the
whole cad group green, and the cad group includes cad_mfg_models.

## EW draw scripts: the dropped params read

The same regeneration exposed a second landed break: commit 89d57cfc4 (X-QA-18
step 3) removed `P = json.loads((HERE / "params.json").read_text())` — its own
comment read "draw scripts read it" — from the nine `models/mfg/EW_*/ew_*.py`
builders without updating the `draw_ew_*.py` readers, which still unpack
`ns["P"]` for `graph_revision`, `size_mm` and the nozzle services. The first
cad_mfg_models run reached the drawing leg and died on `KeyError: 'P'`.

Fix: each builder now exposes `P = GN.as_params()` beside the sizing read — the
graph reader merge the CA_POT idiom uses — so the draw contract is served from
the graph, the authority the refactor intended, not from the tracker-merged
params.json file. Builder bodies do not reference `P`; the build bytes are
unchanged. `draw_ew_1.py` runs green end to end.

