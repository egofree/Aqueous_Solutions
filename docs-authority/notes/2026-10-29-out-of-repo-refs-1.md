# Out-of-repository references, part 1: six equipment lists

Date: 2026-10-29

Six equipment lists cited documents that are not in this repository: `POWER/Power_System_overview.md`, and the root narrative documents `03-silicon-wafer-fabrication.md`, `05-organic-farm-nutrient.md` and `09-air-liquefaction-cryogenic.md`. They also cited the FreeCAD scripts as `freecad/<name>.py`, while the scripts are at `models/freecad/<name>.py`.

The references to the outside documents were removed from the backup generator, fuel cell, geothermal, cryogenic, farm and solar cell equipment lists. Two removals took content with them. The fuel cell list no longer quotes the stack range of the old power narrative, and the geothermal list no longer has the rating row that quoted a 100 kW baseload from it; neither value is on the plant graph or in the drivers, and both were already marked as narrative only. The cryogenic list now says that no rating is taken from earlier narrative documents. The FreeCAD script paths were corrected.

The footers of the backup generator and geothermal flow diagram scripts in `flow_graph/exporters/matplotlib/` also cited the power narrative and were corrected. Their images are built by the site build, which this work does not run, so the committed images keep the old footer until the next site build.

No tag, rating or rule changed.
