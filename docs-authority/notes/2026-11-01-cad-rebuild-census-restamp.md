# 2026-11-01 — CAD lane: plant rebuilt from current builders; unit-map census re-stamped

## What changed

The CAD artifacts had drifted: `plant.FCStd` predated the manufacturing STL
refresh in `cad/stl/`, and the OpenSCAD detail STLs no longer matched their
`.scad` sources. The rebuild ran the canonical sequence
(`docs-authority/REBUILD.md` AQS-REB-001 Rev D, §3):

1. `bash models/openscad/detail/build_stls.sh` — all 51 detail parts
   recompiled with the host OpenSCAD (2021.01) and republished to
   `models/export/detail/`. 94 committed STLs changed content; the previous
   files were built from older sources.
2. `bash models/REBUILD.sh --plant-only` — `build_plant.py` reassembled
   `plant.FCStd` from the current builders (import path shims, graph dims,
   overlap resolver, regroup, fire rooms, materials stamp, plant groups).
   Object totals are unchanged — 1181 objects (1097 Part::Feature,
   66 Mesh::Feature, 18 groups) — but the geometry underneath is refreshed,
   including 17 units resized from the graph and 23 d1b massing features.
3. `clash_check.py`: 240 solids paired, **0 clashes**.
   `clash_equip.py`: 149 solids, **0 clashes, 0 corridor hits**.
   `sanity_model.py`: EW cascade pitch 750 mm exact on all 8 gaps; the six
   placed-copy check boxes match; no issued-skid overlaps.
4. `models/freecad/unit_freecad_map.json` re-stamped: revision E → F,
   `graph_revision` B → AC (the graph has been Rev AC, 218 nodes, since
   2026-10-17 while the stamp still read B). No row changed: every `mapped`
   and `massing_only` row's Feature is present in the new inventory and every
   `cadquery_export` row has its STEP/STL artifact.
5. `models/freecad/UNIT_MAP_COVERAGE.md` regenerated to Rev F from that
   inventory (the Rev B census tables it carried were historical):

| Census (Rev F) | Count |
|---|---|
| Map rows | 150 (mapped 60, massing_only 41, cadquery_export 36, placeholder_skip 7, unmapped 6) |
| Graph nodes (Rev AC) | 218 — 200 present, 16 placeholder, 2 retired |
| Rowed present units covered | 135/146 (92.5 percent) |
| Present nodes without a row | 54 — 13 with an own-name Feature in plant.FCStd, 41 with none |
| Present units with CAD by any route | 148/200 (74.0 percent) |

## Pipeline conflict found (not worked around)

The regeneration manifest stage `cad_envelopes`
(`python3 -m flow_graph.param.envelopes`) writes **study envelope boxes** to
`cad/stl/*.stl`. That directory now also hosts manufacturing geometry written
by `models/mfg/style_builders.py` (which states it "replaces
`cad/stl/<U>.stl` from the build"; e.g. `AL_POT.stl`, `CAST_LINE.stl`,
`TI_CELL.stl` and roughly 90 other files above 100 kB). Running the full
`regen --cad` today would overwrite manufacturing STLs with massing boxes.
This rebuild deliberately did not run that stage — the placement exports were
receipt-current (`regen --check`: 0 of 1575 files stale) and `cad/stl/` was
left byte-identical (all 202 STL checksums verified unchanged). The manifest
stage and the manufacturing publisher need an owner decision on how they
share `cad/stl/`; until then `cad_envelopes` must not be run blindly.

## Open items observed (recorded, not redesigned here)

- `S13_CLASS_TREAT` is retired on the graph while `d1b_massing.py` still
  draws its massing feature.
- 54 present graph units have no map row (census now counts them);
  41 of them have no CAD at all — mostly ladder heat batteries, headers and
  litho/habitation fitout.
- `PROD_MEOH` / `PROD_O2` storage tanks remain unmapped pending a D-DOCK
  placement (as documented at map Rev D).

## Verification

- `git status` after the rebuild shows exactly the intended write-set:
  94 detail STLs, `plant.FCStd`, the re-stamped map, the regenerated coverage
  page and this note. `cad/stl/` and `media/3d/` untouched.
- Census counts reproduce from the committed map + graph with the inventory
  method named in the coverage page header (`/usr/bin/freecadcmd`).
- `scripts/check_all.sh` run before commit; the new `.FCBak` backup stays
  out of the commit via the existing `*.FCBak` ignore rule.
