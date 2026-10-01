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
done
ls -l "$OUT"
