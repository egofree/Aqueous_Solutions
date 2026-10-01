# Matplotlib PFD / SLD exporters (optional)

Licence: **CERN-OHL-S-2.0**  
Date: 2026-10-01

## Primary renders

**`flow_graph/views/`** (JSON + DOT + **SVG**) are the published diagram
artefacts. Regenerate with `render_layer_views.py` from
`plant_flow_graph.json`.

## This directory

Optional matplotlib / drawlib sheet generators (legacy PFD/SLD style).
Graph-bridged via `../../pfd_bridge.py` where noted in
`../../LEGACY_PFD_SCRIPTS.md`.

- **Not required** to consume the share package.
- **PNGs are not shipped** in this publish tree (Mike: `demote_drop_pngs`).
- Hub working copies remain at
  `Diagrams/aqueous_diagrams/pfd_scripts/` + hub-root `*_pfd.png` /
  `electrical_sld.png` — leave those untouched when refreshing share.

## Optional local regenerate

```bash
cd flow_graph/exporters/matplotlib
# system python with matplotlib; writes PNGs next to these scripts
/usr/bin/python3 mass_flow_pfd.py
/usr/bin/python3 electrical_sld.py
# …or any other sheet in this folder
```

Do not commit regenerated PNGs into share.
