# Aqueous Solutions

Closed-loop plant that takes waste or natural mineral feedstock and returns metals, salts, silica, hydrocarbons, and regenerated acid. Energy may be external. A second plant is the replication bar: the mass input is waste or feedstock, not a purchased reagent kit.

License: CERN-OHL-S-2.0.

## What the plant does

One leach tank. Hydrochloric acid and sodium chlorate dissolve the feed at 70–85 °C. Three streams leave that tank.

- Sink solids leave on the floor auger, then a vibratory split. Dense plastic joins the dryer. Glass and ceramic are rinsed, burned out, milled, and digested in sodium hydroxide. Quartz that does not open goes to alkali fusion. Silica is dropped, calcined, and reduced with pyrolyzer char.
- Float leaves over the wall weir, is dried, and is cracked in an induction pyrolyzer. The condensate is split into naphtha (C5–C10), fuel oil (C11–C18), and wax (C19–C32). Bottoms return to the auger. Char is the silicon reductant.
- Liquor is coalesced, filtered, and concentrated on a cation-exchange stack, then electrowon in order from gold through zinc. Lithium and the rare earths are bled before the hydroxide cuts. Aluminum, magnesium, and calcium leave as hydroxides and are reduced in chloride pots. Rare-earth oxides are reduced in a separate calcium retort. Boron oxide is reduced in its own retort, not in the silicon arc.

Spent brine is raised to pH 9. An anion-exchange stack concentrates borate, phosphate, sulfate, and fluoride. The cuts are after the stack. Diluate goes to a potassium chloride crystallizer, then to bipolar-membrane electrodialysis, which makes the hydrochloric acid and the sodium hydroxide. Chlorine from the anodes and the pots is absorbed to sodium chlorate and returned with the acid. Aqueous cells do not make aluminum, magnesium, calcium, lithium, titanium, silicon, or the rare earths.

## Layout

```
docs-authority/     duty notes, building stack, CAD protocol, decisions
flow_graph/         plant graph, schema, SVG views, matplotlib exporters
media/pfd/          rendered process sheets
media/              animation stills and plant_phase_d.mp4
models/freecad/     FreeCAD builders. SCALE_M = 1.0 is the build size
models/openscad/    parametric solids
models/export/      STL exports
iso/                ISO sheets
design_tool/        graph UI source
tables/             BOM and material lists
```

The process sheets in `media/pfd/` are the current drawing set. `master_disassembly_pfd.png` is the equipment graph of the disassembly line. The wet line, solids line, oil line, polish bank, and completion sheet are the detail views. Generators live in `flow_graph/exporters/matplotlib/`. Duty notes that are not part of a drawing live in `docs-authority/notes/`.

Graph SVG views under `flow_graph/views/` are the topology export. They are not a substitute for the equipment sheets.

## Rebuild

FreeCAD 1.0 and OpenSCAD are required for the solids. This tree does not vendor those binaries.

```bash
cd models && bash REBUILD.sh
cd models/freecad && /usr/bin/freecadcmd build_plant.py
```

`SCALE_M = 1.0` in `models/freecad/params.py` is the manufacturing size. `2.0` is a review scale only. Level datums and the building stack are in `docs-authority/`. See `docs-authority/REBUILD.md` and `docs-authority/BUILD_3D_FROM_FLOW.md`.

Process sheets:

```bash
cd flow_graph/exporters/matplotlib
python3 master_disassembly_pfd.py
python3 wet_line_factory_pfd.py
python3 glass_ceramic_pfd.py
python3 oil_line_pfd.py
python3 completion_pfd.py
```

## Authority

`docs-authority/AUTHORITY.md` is the lock list. The typed plant graph in `flow_graph/plant_flow_graph.json` is the topology source. Equipment duties written on the process sheets are the drawing source for the disassembly line. Where a sheet and an older note disagree, the sheet is the later drawing.
