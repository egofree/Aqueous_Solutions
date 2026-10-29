# STL rebuild manifest

Document number: AQS-STL-001  
Revision: B  
Date: 2026-10-29  
Authority: `models/openscad/detail/build_stls.sh` and `models/freecad/import_mfg.py`. The scripts are the record; this page explains them.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: rebuild commands and the list of manufacturing STL files expected before the plant model counts as rebuilt. | 2026-09-27 |
| B | Rewritten to the documentation style guide (AQS-DOC-002). The typed list of files is replaced by the mapping in `import_mfg.py`, and the importer now reads the folder that the build script writes. | 2026-10-29 |

## Purpose and scope

This page tells a builder how to rebuild the STL meshes of the manufacturing equipment and bring them into the FreeCAD plant model. It covers the tools needed, the commands, where the files are written and read, and how to tell that the rebuild is complete. It does not cover the design of the parts; each part is described in its own `.scad` source.

## 1. Tools

Any OpenSCAD on the path will do, either the AppImage or a distribution package. FreeCAD is run headless through `freecadcmd`. Installing a system package is optional, and an unattended agent should not run `sudo apt`. Record the binary used in your local build log, and do not commit workstation paths into this tree.

## 2. Commands

Compile the STL files first, then build the plant model:

```
cd models/openscad/detail && bash build_stls.sh
cd ../../freecad && freecadcmd build_plant.py
```

`build_stls.sh` compiles every `.scad` file in `models/openscad/detail/` into a file of the same name in `models/openscad/detail/stl/`, and copies the results to `models/export/detail/`. `build_plant.py` runs `stamp_materials.py` against `tables/materials.csv`, so the model carries the material of each part.

## 3. When the rebuild is complete

The importer `models/freecad/import_mfg.py` holds the mapping from each manufacturing STL file to the plant units it stands for. Each file named in that mapping must exist after the build. When a file exists, the importer places the mesh and hides, without deleting, the plain box that stood in for the unit. When a file is missing, the importer skips it and the box stays, so a missing file does not stop the build but leaves the model incomplete. Some `.scad` sources, such as the bipolar membrane cell and the induction coil, are compiled for detail work and are not in the mapping.

The pipe racks, cable trays and campus envelopes are also built as FreeCAD Part features by `pipe_services.py` and `campus.py`, so they appear in the model even when their STL files are absent.

Older compiled meshes of the leach reactor, the electrowinning cell and the wet assembly remain in `models/export/` as reference files for checking.

## 4. Where the importer reads

The importer reads from `models/export/detail/`, where the build script publishes, and falls back to `models/openscad/detail/stl/` when that folder is absent. Before revision B it read from `models/detail/stl/`, a folder that nothing writes, so it skipped every mesh.
