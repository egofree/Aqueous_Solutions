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

## 3. Terminal service rows in the nozzle schedules

The audit found three classes of service connection with no schedule row: the plant
power feed at each powered unit, three HVAC and heat service edges at their terminal
units, and the electric half of the ZNBR2 round-trip loss (its issued row N8 covers
the piped heat edge only). The sanctioned generator
(`docs-authority/_nozzle_sched.py`) gains a terminal-row pass; the schedules are
generated output and were regenerated, never hand-edited. The pass appends 71 rows
across 67 schedules and is idempotent (a second run appends nothing).

Row basis (stated in the generator header): the size column carries the AQS-PIP-004
line-list classification verbatim - `cable` for every terminal circuit, so no bore is
claimed; the rating column carries the plant-wide Class 150 convention verbatim with
no flange, breaker or conductor rating implied (named hold: AQS-ELEC-010 rates branch
feeders per load, and the unit feed circuit itself is not separately rated); the power
rows sit at the top-face placeholder (z 800) pending design, which leaves the issued
side-face connection packs of the schedules unchanged; the ZNBR2 row and the HVAC
rows take the face and house placeholder elevation of the edge direction at the
terminal unit.

- Power terminals: 68 rows. The in-scope census is the current graph, not a fixed
  count: 66 present units fed by an SF- (480 V AC distribution), IA-DC (rectifier DC
  bus) or IA-TRIM (electric trim) edge that are not standby_rated and have a schedule
  file. EW_1 already carries its conductor row ("rectifier into the cell", the issued
  precedent) and takes none; LEACH_CSTR_1 and GLASS_DIGEST carry two circuits each
  (unit feed + electric trim) and get two rows - one row covering two edges is the
  conflation this fix removes. The EW_2..EW_9 rows name the DC bus bar per
  AQS-BUS-001 / AQS-ELEC-010.
- HVAC terminals: IA-ADS-CHW and IA-MAU-AIR on HABITATION (N26, N27), SQ-H2O_ELYZ-Q4
  on H2O_ELYZ (N7), each carried as the line-list `cable` class verbatim.
- ZNBR2: N8 (round-trip loss, DN15) stays the piped heat edge IA-ZNBR-HEAT - a cable
  cannot carry a DN bore, so the bare service text is pinned to the piped edge - and
  the new N11 names the electric loss to BOUNDARY_EXPORT at the skid outlet.
- Holds named: no row for the 9 standby_rated units (COMB_HEAT, DRAW, EXTRUDE, FORGE,
  RES_HEAT, RF_HEAT, SINTER, VAC_CAST, VAC_IND - the standby feed is unrated until
  the standby basis issues the rating) and no schedule file for EXT_HALL, FORGE,
  RES_HEAT, RF_HEAT (the generator's no-file rule: machines with no piped process
  connection keep no file). ZNBR2 row N4 ("charge into the battery") matches no graph
  edge and no duty section 4 row (the duty's own N4 is S69B, "NaBr after ORP", which
  the schedule carries as N2): it is recorded schedule-only - the commissioning
  electrolyte charge, unrated, no edge - and the hand row is preserved verbatim.
- Follow-up named: the manufacturing models draw schedule rows as tube hardware. The
  terminal rows are connection records, not nozzle hardware; the next geometry pass
  that rebuilds these units draws the terminals as conductor glands (the MEOH_FC
  conductor idiom) or extends the builders to skip `cable` rows. No model was rebuilt
  in this pass, so no geometry changed.

The tracker merged the new rows into the 67 W2 params files (schedule fields refresh
from the CSV by tag) and re-ran its file checks green.


