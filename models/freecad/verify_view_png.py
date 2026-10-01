#!/usr/bin/env python3
"""One-shot: open plant.FCStd, fit view, save a check PNG. Run with GUI FreeCAD:

    cd models/freecad   # this repo
    /usr/bin/freecad verify_view_png.py

Or with plant already open, paste the body of verify() into the Python console.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FCSTD = HERE / "plant.FCStd"
OUT = HERE / "animation" / "verify_view.png"
WIDTH, HEIGHT = 1280, 720


def verify():
    import FreeCAD as App
    import FreeCADGui as Gui

    OUT.parent.mkdir(parents=True, exist_ok=True)

    if FCSTD.is_file():
        # Close empty docs; open plant if not already
        names = [d.Name for d in App.listDocuments().values()]
        if "plant" not in names and str(FCSTD) not in names:
            App.open(str(FCSTD))

    doc = App.ActiveDocument
    if doc is None:
        raise SystemExit("No active document — open plant.FCStd first")

    Gui.ActiveDocument = Gui.getDocument(doc.Name)
    view = None
    for _ in range(100):
        Gui.updateGui()
        if Gui.ActiveDocument and Gui.ActiveDocument.ActiveView:
            view = Gui.ActiveDocument.ActiveView
            break
        time.sleep(0.05)
    if view is None:
        raise SystemExit("No ActiveView")

    # Unhide Part features if everything is invisible
    shown = 0
    for obj in doc.Objects:
        try:
            vo = obj.ViewObject
            if vo is None:
                continue
            if hasattr(vo, "Visibility") and not vo.Visibility:
                # only force-show solid-ish objects
                if obj.TypeId.startswith("Part::") or "Shape" in obj.TypeId:
                    vo.Visibility = True
            if hasattr(vo, "Visibility") and vo.Visibility:
                shown += 1
        except Exception:
            pass

    t0 = time.time()
    while time.time() - t0 < 2.0:
        Gui.updateGui()
        time.sleep(0.05)

    try:
        view.setAnimationEnabled(False)
    except Exception:
        pass
    try:
        view.viewAxonometric()
    except Exception:
        pass
    view.fitAll()
    for _ in range(20):
        Gui.updateGui()
        time.sleep(0.05)

    view.saveImage(str(OUT), WIDTH, HEIGHT, "White")
    # also Current background
    out2 = HERE / "animation" / "verify_view_current.png"
    view.saveImage(str(out2), WIDTH, HEIGHT, "Current")

    sz = OUT.stat().st_size if OUT.exists() else 0
    sz2 = out2.stat().st_size if out2.exists() else 0
    print("visible_candidates≈%d" % shown)
    print("wrote %s (%d bytes)" % (OUT, sz))
    print("wrote %s (%d bytes)" % (out2, sz2))
    print("Open those PNGs. If still empty gradient, Fit all in the GUI and check object Visibility.")
    # leave FreeCAD open for inspection
    return OUT


if __name__ == "__main__":
    verify()
else:
    try:
        import FreeCADGui  # noqa: F401

        verify()
    except ImportError:
        print("Need /usr/bin/freecad (GUI), not freecadcmd")
        raise
