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
oxidation), but its placeholder model stubs (`models/units/HCL_BURNER`,
"not yet dimensioned", no duty sheet) still rolled two unassignable envelope
rows into the plant BOM. The stubs are removed with the unit. The EOL matrix
is Rev E: the roster itself grew 1020 → 1436 lines as the build-out and M3
BOMs rolled in, so the honest split is 1380 classed / 56 unassigned — each of
the 56 held with a named reason (51 material not identified on the newer
build-out BOM lines, 4 duty-sheet §3 pending at unit task 09, 1 pointer row);
173 composition holds (fluoropolymer 86, Ti 25, Nd/Dy 5, Pt-Rh 1).

**New §3 material selections** (X-MAT-22, AQS-STD-002): AQUA_TANK and
GROWBED_A join the issued set (HDPE/EPDM liner class, CPVC loop piping,
Cu/Zn/brass excluded from wetted faces for ichthyotoxicity; GROWBED_A pairs
with the anaerobic GROWBED_B whose selection anticipated it). RAS added to the
glossary.

## Verification

`python3 -m flow_graph.param.regen` green; `pytest flow_graph/` 204 passed /
1 skipped; `scripts/check_all.sh` clean. The task plan regenerates with the
three task-01 closures cited and X-END-02 at the Rev E status.
