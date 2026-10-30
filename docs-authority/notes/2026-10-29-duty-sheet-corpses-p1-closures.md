# 2026-10-29 — Duty-sheet corpses healed; the three P1 closures and the HCL_BURNER close-out

## What changed

**Generator bug (`docs-authority/_duty_basis.py`)**: the create path was
`open(p, 'w').write(author(...))` — the file truncated *before* `author()`
evaluated, so an exception mid-author left a zero-byte sheet; and once the
empty file existed, the update path never matched anything on it, so the
corpse stuck forever. Three duty sheets were in that state
(AQUA_TANK, GROWBED_A, ATMOS — the desk-P1 queue). The create path now fires
on a zero-byte sheet too, and the content is authored before the file is
opened, so the bug class cannot recurse.

**The three desk-P1 closures** (task plan FARM-AQUA_TANK-01,
FARM-GROWBED_A-01, WTR-ATMOS-01): the graph balances were already closed —
AQUA_TANK 203.8 kg/d in and out, GROWBED_A 202.8 kg/d in and out, ATMOS 0/0 —
the sheets simply did not exist. All three now carry issued §1 basis lines and
the task plan marks them done with the sheet as evidence.

**HCL_BURNER close-out (X-END-02)**: the unit left the design at graph Rev AC
(A-M-255 — the EW cathode H₂ goes to the H₂ pool, anode Cl₂ all to leach
oxidation), but its placeholder model stubs (the HCL_BURNER unit-BOM
directory, "not yet dimensioned", no duty sheet) still rolled two
unassignable envelope rows into the plant BOM. The stubs are removed with the
unit. The EOL matrix is Rev E, restated with the roster correction that
followed later the same day: the plant BOM rosters from the graph (present
units), so the retired units and the superseded envelope BOMs leave the
matrix; the classing rules cover the material families the build-out BOMs
introduced. Every remaining unassigned line is a named hold - the standby
machines awaiting their unit task 10/12 designs (owner programme gate) and the
AQS-INV-004 pointer row - and the composition holds (fluoropolymer, Ti, Nd/Dy,
Pt-Rh recovery units) continue. The live tally is in
`docs-authority/EOL_RETURN.md` and `docs-authority/inventory/EOL_RETURN.csv`.

**New §3 material selections** (X-MAT-22, AQS-STD-002): AQUA_TANK and
GROWBED_A join the issued set (HDPE/EPDM liner class, CPVC loop piping,
Cu/Zn/brass excluded from wetted faces for ichthyotoxicity; GROWBED_A pairs
with the anaerobic GROWBED_B whose selection anticipated it). RAS added to the
glossary.

## Verification

`python3 -m flow_graph.param.regen` green; `pytest flow_graph/` 204 passed /
1 skipped; `scripts/check_all.sh` clean. The task plan regenerates with the
three task-01 closures cited and X-END-02 at the Rev E status.
