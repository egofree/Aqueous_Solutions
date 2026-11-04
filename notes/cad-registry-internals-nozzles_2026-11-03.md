# CAD registry refresh, tracker internals column, terminal schedule rows - 2026-11-03

Three bookkeeping corrections from the CAD-representation audit. No sizing, driver,
duty-prose or geometry value changes anywhere in the batch.

## 1. `cad/stl` registry refreshed against the manufacturing builds

Audit finding: for several units the registry STL in `cad/stl/<UNIT>.stl` is the study
envelope tray while a real parametric build sits in `models/mfg/<UNIT>/export/`. The
registry is the X-PAR-04 envelope file, so the honest state is: the registry carries the
build when the build's bounding box matches the graph `size_mm` within the 1 mm gate
(`flow_graph/param/test_envelopes.py`), and stays the envelope box with the scope named
when it does not. Nothing is resized and no geometry is rebuilt in this pass.

Registry replaced from the export build (build solid bounding box matches `size_mm`;
the mesh is converted to the registry convention, ASCII metres, vertices unchanged in
shape; X-PAR-04 re-run green, all four meshes read back closed and manifold):

| Unit | Facets | Source mesh | Note |
|---|---|---|---|
| TFE_SYN | 3580 | `models/mfg/TFE_SYN/export/tfe_syn.stl` | fills the 600 x 600 x 1200 envelope |
| VDF_SYN | 3580 | `models/mfg/VDF_SYN/export/vdf_syn.stl` | fills the 600 x 600 x 1200 envelope |
| POLY_STOCK | 532 | `models/mfg/POLY_STOCK/export/poly_stock.stl` | no `size_mm` on the node, so the gate does not bind the registry; the build is the honest content |
| POLY_FIBER | 80 | `models/mfg/POLY_FIBER/export/poly_fiber.stl` | fills the 3100 x 1300 x 1900 envelope |

Registry kept as the study envelope box, scope recorded (the export build does not
fill the claimed envelope, so a replacement would fail the X-PAR-04 gate; the tracker
section 7 `cad/stl now` cell already reads "envelope box, ~N f (build STL in export/)"
for each of these):

- ACID_POLISH_SCRUB: build measures 845.7 x 960.0 x 3719.7 mm against the 1000 x 1000 x 4103 envelope.
- OIL_PYRO: build 320.0 x 319.9 x 491.0 against 500 x 500 x 670.
- BLACK_DIGEST: build 910.0 x 910.0 x 771.0 against 1100 x 1100 x 1260.
- HF_GEN: build 1199.5 x 630.0 x 1400.0 against 1200 x 700 x 1500.
- PELLET: build 1450.0 x 550.0 x 875.0 against 1500 x 800 x 1500.
- BAGHOUSE: export is itself the envelope box (44 facets, same box as the registry).
- COMMON_AREA, GALLEY, MEDICAL, REC_DAYROOM, SLEEP_QUARTERS, WASHROOM: export is a
  plain room box (28 facets); the registry box stays.
- BEE_HIVE: deliberate study-box convention (the build overruns the node box by the
  stand and lid laps; the X-PAR-04 gate keeps the envelope box in the registry).
- QUAIL_CAGE, RABBIT_HUTCH: build is a framed cage/hutch whose outline equals the
  registry box; the registry box stays until the farm geometry lane replaces the
  registries from those builds.

Holds named: the five under-filled builds (ACID_POLISH_SCRUB, OIL_PYRO, BLACK_DIGEST,
HF_GEN, PELLET) need either a flush rebuild on the geometry lane (the POLY_COND
idiom: connection hardware flush at the envelope faces) or a node-envelope decision
before their registries can carry the build. Nothing is fabricated in the meantime.

## 2. Section 7 internals column carries the model evidence

The audit found the section 7 "Internal on node" column under-reporting: it read only
the node internals row (`node.internals` / `params.internals`), while the electrode
banks of the EW cells live in `params.sizing` (25 cathodes / 26 anodes per cell,
`AQS-DUTY-051`), the BMED triplet construction and the MeOH-train beds are booked on
their issued sheets and model BOMs, and the accepted builders draw that hardware. The
generator (`models/mfg/tracker.py`) is fixed, not the output:

- The column, renamed "Internal evidence", carries the node internals row where the
  node states one (the four units with explicit rows, H2O_ELYZ among them, verbatim),
  and otherwise the unit's disposition from the AQS-DSN-INT-001 internals register
  (`docs-authority/inventory/INTERNALS.json`): 183 units now name the issued
  sizing-sheet, duty or manufacturing-model-BOM evidence (EW cells: the electrode
  array per `sizing/EW_CELLS.md`; BMED_ACID: the triplet construction per
  `sizing/BMED_STACK.md`; MEOH_SYNTH: the catalyst-bed BOM row; HX8: the PVDF bundle
  construction), 11 carry the register's stated-none disposition verbatim (OIL_PYRO
  among them: "the pyrolysis retort is the shell itself"), and the three boundary
  accounting nodes read none.
- `rec['internals']` stays the bare node row: the work tiers and the W2 params.json
  `internals` key keep their node-row meaning, so no tier shifted and no W2 file
  changed (the tracker rewrote 197 params.json byte-identically).
- The section 7 preamble states the join and names the register authority.

