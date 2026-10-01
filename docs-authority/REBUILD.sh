#!/bin/bash
# Operator-box rebuild. Needs OpenSCAD on PATH and /usr/bin/freecadcmd 1.0.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAD="$ROOT/cad"
if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad not on PATH — compile STLs on the operator box"
  exit 1
fi
if [ ! -x /usr/bin/freecadcmd ]; then
  echo "/usr/bin/freecadcmd missing — use the 1.0 apt binary, not the 1.1 AppImage"
  exit 1
fi
bash "$CAD/detail/build_stls.sh"
cd "$CAD/freecad"
/usr/bin/freecadcmd build_plant.py
echo "plant.FCStd + stamped materials done"
