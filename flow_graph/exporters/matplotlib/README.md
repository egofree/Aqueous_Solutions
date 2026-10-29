# Matplotlib flow diagram scripts

Document number: AQS-FLOW-GRAPH-001 annex  
Revision: B  
Date: 2026-10-29  
Licence: CERN-OHL-S-2.0

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: the optional matplotlib sheets described | 2026-10-01 |
| B | Purpose and scope added; the scripts that the regeneration runs, and where their images go, stated from `flow_graph/regen_derived.py`; the statement that no image is published corrected | 2026-10-29 |

## 1. Purpose and scope

This folder holds Python scripts that draw process flow diagrams (PFDs) and an electrical single-line diagram with matplotlib. The plant graph `flow_graph/plant_flow_graph.json` is the only authority for units, streams and rates; the scripts draw from it where they are bridged to it through `flow_graph/pfd_bridge.py`, and `flow_graph/LEGACY_PFD_SCRIPTS.md` states which scripts are bridged. The primary diagrams of the project are the layer views in `flow_graph/views/`, which `flow_graph/render_layer_views.py` writes from the graph as JSON, DOT and SVG files.

## 2. Images built by the regeneration

The stage `regen_derived` of `flow_graph/param/regen_manifest.json` runs `flow_graph/regen_derived.py`, which runs some of these scripts and moves each image to `media/pfd/`: the scripts for the completion, continuous recycling, glass and ceramic, master disassembly, oil line, polishing bank and wet-line factory diagrams (`*_pfd.py`). Those images are tracked and are rebuilt by `python3 -m flow_graph.param.regen`.

## 3. Other scripts

The other scripts in this folder are not run by the regeneration, and their images are not tracked. Each script writes its image to the folder `images/` next to it if that folder exists, and otherwise into this folder (`sector_style.OUT_DIR`). To draw one, install the packages in `requirements.txt` and run the script, for example:

```bash
cd flow_graph/exporters/matplotlib
python3 electrical_sld.py
```

Do not commit the images these scripts write; an image that should be tracked must be added to `flow_graph/regen_derived.py` and to the outputs of its stage.
