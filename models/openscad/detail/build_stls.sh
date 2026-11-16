#!/bin/bash
# Compile detail + manufacturing parts. Needs OpenSCAD.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/stl"
mkdir -p "$OUT"
for f in "$HERE"/*.scad; do
  b="$(basename "$f" .scad)"
  echo "render $b"
  openscad -o "$OUT/$b.stl" "$f"
  # OpenSCAD emits the same triangles in a different order every run; canonicalize
  # so a rebuild is byte-identical (models/openscad/detail/normalize_stl.py).
  python3 "$HERE/normalize_stl.py" "$OUT/$b.stl"
done
# Publish where models/freecad/import_mfg.py reads them (models/export/detail).
PUB="$HERE/../../export/detail"
mkdir -p "$PUB"
cp -f "$OUT"/*.stl "$PUB"/
