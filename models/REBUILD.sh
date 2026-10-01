#!/usr/bin/env bash
# Share-tree plant rebuild. Paths under models/ (not hub cad/).
# Needs /usr/bin/freecadcmd 1.0. OpenSCAD optional (--stls).
set -euo pipefail
MODELS="$(cd "$(dirname "$0")" && pwd)"
SHARE="$(cd "$MODELS/.." && pwd)"
FC="$MODELS/freecad"
DO_STLS=0
PLANT_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --stls) DO_STLS=1 ;;
    --plant-only) PLANT_ONLY=1 ;;
    -h|--help)
      echo "Usage: bash models/REBUILD.sh [--stls] [--plant-only]"
      echo "  Links tables/materials.csv and export/detail STLs into models/"
      echo "  layout expected by stamp_materials.py / import_mfg.py, then"
      echo "  runs /usr/bin/freecadcmd build_plant.py"
      exit 0
      ;;
  esac
done

if [ ! -x /usr/bin/freecadcmd ]; then
  echo "/usr/bin/freecadcmd missing — use FreeCAD 1.0 apt binary, not the 1.1 AppImage"
  exit 1
fi

# Path shims: builders assume hub-style cad/materials.csv and cad/detail/stl/
if [ -f "$SHARE/tables/materials.csv" ]; then
  ln -sfn ../tables/materials.csv "$MODELS/materials.csv"
  echo "linked models/materials.csv -> tables/materials.csv"
fi
mkdir -p "$MODELS/detail"
if [ -d "$MODELS/export/detail" ]; then
  ln -sfn ../export/detail "$MODELS/detail/stl"
  echo "linked models/detail/stl -> models/export/detail"
fi

if [ "$DO_STLS" = 1 ]; then
  if ! command -v openscad >/dev/null 2>&1; then
    echo "openscad not on PATH — skip STL compile (use shipped models/export)"
  else
    bash "$MODELS/openscad/detail/build_stls.sh"
    # Publish compiled STLs where import_mfg looks (and keep export/ in sync)
    mkdir -p "$MODELS/export/detail"
    if [ -d "$MODELS/openscad/detail/stl" ]; then
      cp -f "$MODELS/openscad/detail/stl/"*.stl "$MODELS/export/detail/" 2>/dev/null || true
      # refresh symlink target content
      ln -sfn ../export/detail "$MODELS/detail/stl"
    fi
  fi
fi

if [ "$PLANT_ONLY" = 1 ] || [ "$DO_STLS" = 0 ] || [ "$DO_STLS" = 1 ]; then
  cd "$FC"
  /usr/bin/freecadcmd build_plant.py
  echo "plant.FCStd rebuild done (SCALE_M from params.py; not from flow_graph)"
fi
