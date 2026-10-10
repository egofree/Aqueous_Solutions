#!/usr/bin/env python3
"""Resolve the FreeCAD console and accept 1.0, 1.1, or 26.3.

Does not import FreeCAD. Safe to run from system Python on the operator box.

    python3 freecad_host.py
    python3 freecad_host.py --require 1.1

CERN-OHL-S-2.0. The Part console calls in the plant builders
(Part.makeBox, makeCylinder, makeLoft of closed wires, Part::Feature,
Shape assignment, Placement, saveAs, Part.export, argv gate) are not
listed as removed or changed in the FreeCAD 1.1 release notes.
The 1.1.1 AppImage failure on this project was a Ribbon addon crash,
not a Part API break.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ACCEPTED = ("1.0", "1.1", "26")
VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


def candidates() -> list[str]:
    env = os.environ.get("FREECADCMD")
    found = []
    if env and Path(env).is_file():
        found.append(env)
    for name in ("/usr/bin/freecadcmd", "freecadcmd", "FreeCADCmd"):
        path = name if name.startswith("/") else shutil.which(name)
        if path and Path(path).is_file() and path not in found:
            found.append(path)
    return found


def version_of(binary: str) -> str | None:
    try:
        proc = subprocess.run(
            [binary, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (proc.stdout or "") + (proc.stderr or "")
    match = VERSION_RE.search(text)
    return match.group(1) if match else None


def ribbon_crash_path() -> Path | None:
    home = Path.home()
    addon = home / ".local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon"
    if addon.is_dir() and not (addon / "RibbonStructure.json").is_file():
        return addon
    return addon if addon.is_dir() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Check FreeCAD console host")
    ap.add_argument("--require", choices=("1.0", "1.1", "either"), default="either")
    args = ap.parse_args()

    bins = candidates()
    if not bins:
        print("no freecadcmd / FreeCADCmd on PATH and FREECADCMD unset", file=sys.stderr)
        return 2

    rows = []
    for binary in bins:
        ver = version_of(binary)
        rows.append((binary, ver))
        print(f"{binary}  version={ver or 'unreadable'}")

    chosen = next((b for b, v in rows if v and v.startswith(ACCEPTED)), None)
    if chosen is None:
        print("no accepted console (want 1.0.x or 1.1.x)", file=sys.stderr)
        return 3
    ver = next(v for b, v in rows if b == chosen)
    major = ver.split(".", 2)[0] + "." + ver.split(".", 2)[1]
    if args.require != "either" and major != args.require:
        print(f"host is {ver}, required {args.require}", file=sys.stderr)
        return 4

    if major == "1.1":
        addon = ribbon_crash_path()
        if addon is not None and not (addon / "RibbonStructure.json").is_file():
            print(
                "1.1 AppImage will SIGSEGV if this Ribbon addon stays enabled: "
                f"{addon}",
                file=sys.stderr,
            )
            print(f"disable with: mv {addon} {addon}.disabled", file=sys.stderr)
            return 5

    print(f"accepted {chosen} {ver}")
    print("Part::Feature builders do not need an API rewrite for this host.")
    print("Do not round-trip PartDesign bodies through 1.1 if 1.0 must still open them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
