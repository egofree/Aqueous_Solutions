#!/usr/bin/env python3
"""Semi-transparent slabs and envelope walls in plant.FCStd.

    Called from build_plant.py after solids exist. Sets:
      1. ShapeMaterial Appearance Transparency (best-effort under freecadcmd)
      2. App property TransparencyPercent for GUI macros
      3. Patches GuiDocument.xml inside the FCStd so ViewObject.Transparency
         is 70–85 when the file is opened in /usr/bin/freecad

Process equipment stays opaque (not listed in TRANSLUCENT_PREFIXES / NAMES).
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
import tempfile
import shutil

# ViewObject percent (0 = opaque, 100 = invisible). Target 70–85.
T_SLAB = 80
T_ENVELOPE = 75
T_GROUND = 85
T_FITOUT = 70

TRANSLUCENT = {
    # name -> percent
    "SLAB_Lm2": T_SLAB,
    "SLAB_Lm1": T_SLAB,
    "SLAB_L0": T_SLAB,
    "SLAB_L1": T_SLAB,
    "SLAB_L2": T_SLAB,
    "HABITATION": T_ENVELOPE,
    "FARM": T_ENVELOPE,
    "WAFER_FAB": T_ENVELOPE,
    "CRYO": T_ENVELOPE,
    "MFG_SHOP": T_ENVELOPE,
    "DOCK": T_ENVELOPE,
    "GROUND_PLANE": T_GROUND,
    "ENV_WALL_N": T_ENVELOPE,
    "ENV_WALL_S": T_ENVELOPE,
    "ENV_WALL_E": T_ENVELOPE,
    "ENV_WALL_W": T_ENVELOPE,
}

# Prefixes for fit-out corridor / toilet / lobby volumes
TRANSLUCENT_PREFIXES = (
    "CORR_",
    "TOILET_",
    "LOBBY_ELEV_",
    "STAIR_CLR_",
    "PART_HAB_",
    "PART_FARM_",
    "WETROOM_",
    "HA_L",  # horizontal assemblies — read through stack
)


def _target_percent(name: str) -> int | None:
    if name in TRANSLUCENT:
        return TRANSLUCENT[name]
    for p in TRANSLUCENT_PREFIXES:
        if name.startswith(p):
            return T_FITOUT
    return None


def apply_document(doc) -> int:
    """Set ShapeMaterial + App property on translucent objects. Returns count."""
    n = 0
    for obj in doc.Objects:
        pct = _target_percent(obj.Name)
        if pct is None:
            continue
        frac = "%.3f" % (pct / 100.0)
        try:
            if hasattr(obj, "ShapeMaterial") and obj.ShapeMaterial is not None:
                m = obj.ShapeMaterial
                m.setAppearanceValue("Transparency", frac)
                obj.ShapeMaterial = m
        except Exception as exc:
            print("ShapeMaterial skip", obj.Name, exc)
        # Persist a hint property for GUI apply / documentation
        try:
            if not hasattr(obj, "TransparencyPercent"):
                obj.addProperty(
                    "App::PropertyInteger",
                    "TransparencyPercent",
                    "View",
                    "Target ViewObject.Transparency (0-100)",
                )
            obj.TransparencyPercent = int(pct)
        except Exception:
            pass
        # ViewObject when Gui is up
        try:
            vo = obj.ViewObject
            if vo is not None and hasattr(vo, "Transparency"):
                vo.Transparency = int(pct)
        except Exception:
            pass
        n += 1
    print("transparency tagged on %d objects" % n)
    return n


def _vp_block(name: str, pct: int) -> str:
    return """        <ViewProvider name="%s" expanded="0" Extensions="True">
            <Extensions Count="1">
                <Extension type="Gui::ViewProviderFaceTexture" name="ViewProviderFaceTexture">
                </Extension>
            </Extensions>
            <Properties Count="3" TransientCount="0">
                <Property name="ShapeAppearance" type="App::PropertyMaterialList" status="1">
                    <MaterialList file="" version="3"/>
                </Property>
                <Property name="Transparency" type="App::PropertyPercent" status="1">
                    <Integer value="%d"/>
                </Property>
                <Property name="Visibility" type="App::PropertyBool" status="1">
                    <Bool value="true"/>
                </Property>
            </Properties>
        </ViewProvider>
""" % (name, pct)


def patch_fcstd(path: Path) -> int:
    """Write / merge GuiDocument.xml Transparency for translucent names."""
    path = Path(path)
    if not path.is_file():
        print("no fcstd to patch", path)
        return 0

    # Discover which translucent names exist in Document.xml
    with zipfile.ZipFile(path, "r") as zf:
        doc_xml = zf.read("Document.xml").decode("utf-8", errors="replace")
        names_in_doc = set(re.findall(r'name="([^"]+)"', doc_xml))
        existing_gui = None
        if "GuiDocument.xml" in zf.namelist():
            existing_gui = zf.read("GuiDocument.xml").decode("utf-8", errors="replace")

    targets = []
    for name in sorted(names_in_doc):
        pct = _target_percent(name)
        if pct is not None:
            targets.append((name, pct))
    if not targets:
        print("transparency patch: no matching objects")
        return 0

    if existing_gui:
        gui = existing_gui
        for name, pct in targets:
            # Replace existing Transparency integer inside that ViewProvider
            pattern = (
                r'(<ViewProvider name="%s"[\s\S]*?'
                r'<Property name="Transparency" type="App::PropertyPercent"[^>]*>\s*'
                r'<Integer value=")(\d+)("/>)'
            ) % re.escape(name)
            gui, count = re.subn(pattern, r"\g<1>%d\g<3>" % pct, gui, count=1)
            if count == 0:
                # Insert a new ViewProvider before </ViewProviderData>
                block = _vp_block(name, pct)
                if "</ViewProviderData>" in gui:
                    gui = gui.replace(
                        "</ViewProviderData>",
                        block + "    </ViewProviderData>",
                        1,
                    )
                    # bump Count if present
                    gui = re.sub(
                        r'(<ViewProviderData Count=")(\d+)(">)',
                        lambda m: '%s%d%s' % (m.group(1), int(m.group(2)) + 1, m.group(3)),
                        gui,
                        count=1,
                    )
    else:
        blocks = "".join(_vp_block(n, p) for n, p in targets)
        gui = (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            "<Document SchemaVersion=\"1\" HasExpansion=\"1\">\n"
            "    <Expand />\n"
            "    <ViewProviderData Count=\"%d\">\n"
            "%s"
            "    </ViewProviderData>\n"
            "</Document>\n" % (len(targets), blocks)
        )

    # Rewrite zip with updated GuiDocument.xml
    tmp = path.with_suffix(".fcstd.tmp")
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            if item.filename == "GuiDocument.xml":
                continue
            zout.writestr(item, zin.read(item.filename))
        zout.writestr("GuiDocument.xml", gui.encode("utf-8"))
    tmp.replace(path)
    print("GuiDocument transparency patched for %d objects → %s" % (len(targets), path))
    return len(targets)


def apply(doc, fcstd_path=None) -> None:
    apply_document(doc)
    if fcstd_path:
        # Caller must save doc before patch; patch runs after saveAs
        pass
