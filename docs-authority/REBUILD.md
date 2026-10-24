# Rebuilding the design from the plant graph

Document number: AQS-REB-001  
Revision: D  
Date: 2026-10-24

| Rev | Description | Date |
|---|---|---|
| — | First issue: menu-driven rebuild script in a private working copy | 2026-09-28 |
| A | Menu options and copy step to the published tree | 2026-09-28 |
| B | Building scale setting (SCALE_M) | 2026-09-28 |
| C | Rebuild described for the published tree layout | 2026-10-01 |
| D | Rewritten for the single regeneration pipeline; the menu script and copy step no longer exist | 2026-10-24 |

## 1. Purpose

This page explains how to regenerate every derived file in the repository (sizing pages, inventories, drawings, views and 3D models) from the plant flow graph, `flow_graph/plant_flow_graph.json`. One command does it. The list of generators and the order they run in is data, kept in `flow_graph/param/regen_manifest.json`.

## 2. Regenerating the documents and data

Run from the repository root:

```bash
python3 -m flow_graph.param.regen            # full run: graph, then documents
python3 -m flow_graph.param.regen --check    # report stale derived files; changes nothing else
python3 -m flow_graph.param.regen --dry-run  # print the plan
```

A full run has two phases.

1. Graph phase. Every stage that writes the graph runs in manifest order. The block repeats until the graph stops changing, because some sizing results feed back into others (for example, power demand and photovoltaic array size).
2. Document phase. Every other stage runs against the final graph. Some documents read each other, so this phase also repeats until no output changes.

The run writes a receipt, `flow_graph/derived/_regen_receipt.json`, that records the graph checksum each output was built from. `--check` uses it to report any derived file that is out of date. Pull requests must pass `--check`.

## 3. Rebuilding the 3D models

The model builds need FreeCAD 1.0 (`/usr/bin/freecadcmd`), OpenSCAD and, for the manufacturing models, CadQuery. They are a separate group so that a machine without those tools can still regenerate the documents:

```bash
python3 -m flow_graph.param.regen --cad
```

A stage whose tool is missing is skipped with a message, and its committed outputs are kept. `models/REBUILD.sh` runs the FreeCAD plant build and the clash checks on their own; `--stls` adds the OpenSCAD detail parts.

Use only `/usr/bin/freecadcmd` (the FreeCAD 1.0 package build). See `docs-authority/FREECAD_PROTOCOL.md`.

## 4. Building scale (SCALE_M)

SCALE_M sets the size of the building itself, not the scale of a drawing. It sets the bay counts, plate length and width, cassette class and the number of living and basement levels, as derived in `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001). The value lives in one place, the line `SCALE_M = 1.0` in `models/freecad/params.py`.

| Value | Use |
|---|---|
| 1.0 | Manufacturing baseline: 1 m in the model is 1 m built (24 m × 18 m plate) |
| 2.0 | Review only: denser packing with more bays and living plates |
| other positive values | Custom; see the derivation in SCALE_MODEL |

WARNING: SCALE_M = 2.0 is for review only. Do not commit it as the default.

After changing SCALE_M, run the full pipeline with `--cad` so that the documents and the model geometry agree.

## 5. Exit status

The pipeline stops at the first stage that fails, prints that stage's command and the end of its output, and exits non-zero. The receipt then records the failure and vouches for nothing.

## 6. Related documents

| Document | Role |
|---|---|
| `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001) | What SCALE_M changes |
| `docs-authority/FREECAD_PROTOCOL.md` | FreeCAD version and template |
| `docs-authority/STL_MANIFEST.md` | OpenSCAD part list |
| `docs-authority/BUILD_3D_FROM_FLOW.md` | How the 3D model follows the graph, and its limits |
| `docs-authority/DERIVED_REVISIONS.md` | Generated list of derived files and whether each is current |
