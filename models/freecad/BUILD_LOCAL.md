# Build the FreeCAD scripts locally

Stable release is 1.1.4. 26.3 is the next line, in release candidate as of 2026-10-08. The Part console calls in these scripts are unchanged. Use 1.1.4 unless you are testing 26.3.

## Install

Ubuntu or Debian:

```
sudo apt install freecad
freecadcmd --version
```

Or the 1.1.4 AppImage from the FreeCAD releases page. Set `FREECADCMD` to that binary if it is not on `PATH`.

## Check the host

```
cd models/freecad
python3 freecad_host.py
```

It accepts 1.0, 1.1, and 26. It does not import FreeCAD.

## Build one unit

```
freecadcmd leach_cstr.py
freecadcmd ew_cell.py
freecadcmd struvite.py
```

Each writes an FCStd and a STEP next to the script.

## Build the plant

```
freecadcmd build_plant.py
```

This assembles the process cassette and the campus. It needs the unit scripts to have run, or it builds what it owns.

## Export a mesh

From a script, after the shape exists:

```
import MeshPart
mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.1)
mesh.write("unit.stl")
```

The STL files in `cad/stl/` were written without FreeCAD. Replace them with these exports once the console has run.
