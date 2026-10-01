#!/usr/bin/env python3
"""Combo View nesting for plant.FCStd via App::DocumentObjectGroup.

Tree (Plant → type → subtype):

    Plant
    ├── Building/{Slabs,Cores_Shafts,Fire_Barriers,Terraces(+GH_),Fitout}
    ├── Process/{Wet,Oil_Glass,Gas,Cryo}
    ├── Life/{Habitation,Farm}
    ├── Electrical
    ├── Labels_Signs
    └── Detail_Meshes

Classification is by object Name prefix (locked plant names). Call
organize(doc) once after all attach() steps, then ensure_visible(doc).
"""
from __future__ import annotations

# (group_path_tuple, match_fn) — first match wins. path is under Plant.
# Leaf groups use a 1-tuple path ("Electrical",); nested use 2-tuple.


def _startswith(name, *prefixes):
    return any(name.startswith(p) for p in prefixes)


def _in(name, *exact):
    return name in exact


def classify(name: str):
    """Return path tuple under Plant, e.g. ('Building','Slabs') or ('Electrical',)."""
    if not name or name.startswith("Plant") or name in _GROUP_NAMES:
        return None

    # Labels / signs — before SLAB_ etc. (label_plate uses LBL_<unit>)
    if _startswith(name, "SIGN_", "LBL_"):
        return ("Labels_Signs",)

    # Detail STL inserts (Phase B) — keep separate from MFG_ replacements
    if _startswith(name, "DETAIL_"):
        return ("Detail_Meshes",)

    # --- Building --------------------------------------------------------
    if _startswith(name, "SLAB_"):
        return ("Building", "Slabs")
    if _startswith(name, "OVERFLOW_", "GH_", "TERRACE_"):
        return ("Building", "Terraces")
    if _startswith(name, "FB_", "HA_"):
        return ("Building", "Fire_Barriers")
    if _startswith(
        name,
        "SHAFT_", "CORE_", "STAIR_", "ELEV_", "ENV_WALL_",
        "SERVICE_", "DOCK",
    ) or _in(
        name,
        "GROUND_PLANE", "DOCK", "ROOF_TANK", "CATCH_TANK",
        "HYDRO_SET", "ARRAY_ROOF",
    ):
        return ("Building", "Cores_Shafts")
    if _startswith(
        name,
        "TOILET_", "LOBBY_", "STAIR_CLR_", "PART_", "WETROOM_", "CORR_",
    ):
        return ("Building", "Fitout")

    # --- Life ------------------------------------------------------------
    if (
        _startswith(name, "HAB", "SLEEP", "GALLEY", "GREY_", "BLACK_")
        or name == "HABITATION"
        or name.startswith("HABITATION_")
        or _in(name, "GREY_TREAT", "BLACK_DIGEST")
    ):
        return ("Life", "Habitation")
    if (
        _startswith(
            name,
            "FARM", "FISH_", "BIOFILTER", "GROW_BED", "GROW_TRAY", "NUTRIENT_", "LED_",
        )
        or name == "FARM"
        or name.startswith("FARM_")
    ):
        return ("Life", "Farm")
    # Shared life header racks (N/S/E/W + HDR_* life tiers).
    # Note: pipe_services replace("_N","_S") on HDR_N2_N yields HDR_S2_S etc.
    if _startswith(name, "RACK_LIFE_") or name.startswith(
        ("HDR_GREY_", "HDR_UPW_", "HDR_ETCH_", "HDR_O2_", "HDR_N2_", "HDR_CO2_",
         "HDR_S2_", "HDR_W2_", "HDR_E2_")
    ):
        return ("Life", "Habitation")

    # --- Electrical ------------------------------------------------------
    if _startswith(
        name,
        "RECTIFIER", "ATS", "SOL_ARK", "ZNBR", "PV_ARRAY", "GND_",
        "TRAY_YARD", "MFG_ELECTRICAL", "MFG_ZNBR",
        "BACKUP_GEN", "GEN_", "FUEL_CELL", "FC_", "GEO_", "MEOH_",
        "YARD_", "CLEAR_", "KO_", "UTIL_ROUGH_",
    ) or _in(name, "ATS", "SOL_ARK_60K", "BACKUP_GEN", "FUEL_CELL"):
        return ("Electrical",)

    # --- Process / Cryo --------------------------------------------------
    if _startswith(
        name,
        "CRYO", "COLD_BOX", "PROCESS_B", "MFG_COLD_BOX",
        "AIR_INTAKE", "MOL_SIEVE", "HEPA_BANK", "STIRLING_",
        "DIST_COL_", "REBOILER_COND", "COMP_EXPAND", "VJ_", "FLUE_CAP",
    ):
        return ("Process", "Cryo")

    # --- Process / Gas ---------------------------------------------------
    if _startswith(
        name,
        "DEMISTER", "ALK_SCRUBBER", "FAN_STACK", "BAGHOUSE", "H2_",
        "ACID_POLISH_",
        "HVAC_", "HX7_", "FINES_TO_CSTR", "SCRUBBER_TO_CRU",
        "MFG_BAGHOUSE", "MFG_H2_", "MFG_SCRUBBER", "MFG_GAS", "MFG_Q4",
    ):
        return ("Process", "Gas")

    # --- Process / Oil + Glass -------------------------------------------
    if _startswith(
        name,
        "DRYER", "INDUCTION_", "QUENCH", "FRACTIONATOR", "AFTERBURNER",
        "C29_", "PROD_C5_", "PROD_C11_", "PROD_C19_", "PROD_C29",
        "RINSE_", "BURNOUT_", "MILL", "NaOH_DIGEST",
        "PROD_SILICATE", "PROD_CA_AL", "PROD_CERAMIC",
        "OIL_LINE", "GLASS_", "RACK_OIL", "HDR_OIL_",
        "MFG_DRYER", "MFG_PYRO", "MFG_QUENCH", "MFG_FRACTIONATOR",
        "MFG_AFTERBURNER", "MFG_RINSE", "MFG_ROTARY", "MFG_MILL",
        "MFG_DIGEST",
    ) or _in(name, "MILL", "QUENCH", "DRYER", "AFTERBURNER", "FRACTIONATOR"):
        return ("Process", "Oil_Glass")

    # --- Process / Wet (default process cassette + grade fab/mfg) --------
    if _startswith(
        name,
        "LEACH_", "LEACHATE_", "CSTR3_", "MIXER", "MEZZANINE", "HOPPER_",
        "VIBRATORY_", "FLOAT_", "SINK_", "EW_", "PK_", "P_Al", "P_Mg", "P_Ca",
        "BMED_", "CRU", "SALT_", "REGEN_", "PAIL_", "HARVEST_",
        "HDR_ACID_", "HDR_H2", "HDR_DUST", "HDR_LIQUOR", "HDR_NAOH",
        "HDR_HCL", "HDR_CAUSTIC",
        "RACK_WET", "RACK_BMED", "TRAY_EW",
        "PROD_METALS", "PROD_Au", "PROD_Ag", "PROD_Cu", "PROD_Pb",
        "PROD_Sn", "PROD_Ni", "PROD_Fe", "PROD_Cd", "PROD_Zn",
        "PROD_HYDROXIDES", "MELT", "NaOH_PRODUCT", "HCl_PRODUCT",
        "WAFER_FAB", "FAB_", "WET_BENCH", "ETCH_", "PV_", "WS_", "S13_",
        "MFG_SHOP", "MFG_CRIB", "MFG_FLOOR",
        "MET_", "WIRE_DRAW", "COLD_MILL", "GAS_ATOMIZER", "MFG_SHREDDER", "MFG_HOPPER",
        "MFG_CONVEYOR", "MFG_LID_", "MFG_LEACH", "MFG_CSTR3", "MFG_FLOAT",
        "MFG_SINK", "MFG_SPLIT", "MFG_EW_", "MFG_VDF", "MFG_CEM",
        "MFG_VALVE", "MFG_CRU", "MFG_MELT", "MFG_TOTES", "MFG_BMED",
        "MFG_PIPE", "MFG_CABLE", "MFG_WET_BENCH", "MFG_ETCH",
        "MFG_FISH", "MFG_BIOFILTER", "MFG_GROW", "MFG_FARM",
        "MFG_NUTRIENT", "MFG_HAB_", "MFG_LIFE_", "MFG_P_",
    ) or _in(
        name,
        "MIXER", "MEZZANINE", "CRU", "MELT", "SALT_FEED",
        "NaOH_PRODUCT", "HCl_PRODUCT", "REGEN_LEACH", "BMED_REGEN",
        "PAIL_STATIONS", "HARVEST_VACUUM_DRUM_FILTER",
        "WAFER_FAB", "MFG_SHOP",
    ) or name.startswith("EW_") or name.startswith("PK_") or name.startswith("PROD_"):
        return ("Process", "Wet")

    # Catch remaining MFG_ meshes as detail
    if _startswith(name, "MFG_", "MASSING_"):
        return ("Detail_Meshes",)

    return None


# Names of groups we create — skip re-parenting them as content
_GROUP_NAMES = frozenset({
    "Plant",
    "Building", "Slabs", "Cores_Shafts", "Fire_Barriers", "Terraces", "Fitout",
    "Process", "Wet", "Oil_Glass", "Gas", "Cryo",
    "Life", "Habitation", "Farm",
    "Electrical", "Labels_Signs", "Detail_Meshes",
})

_TREE = (
    ("Building", ("Slabs", "Cores_Shafts", "Fire_Barriers", "Terraces", "Fitout")),
    ("Process", ("Wet", "Oil_Glass", "Gas", "Cryo")),
    ("Life", ("Habitation", "Farm")),
    ("Electrical", ()),
    ("Labels_Signs", ()),
    ("Detail_Meshes", ()),
)


def _ensure_group(doc, name, parent=None):
    obj = doc.getObject(name)
    if obj is None:
        obj = doc.addObject("App::DocumentObjectGroup", name)
        obj.Label = name
    if parent is not None and obj not in getattr(parent, "Group", []):
        parent.addObject(obj)
    return obj


def organize(doc):
    """Create Plant tree and add every Part/Mesh (and other content) into it."""
    plant = _ensure_group(doc, "Plant")
    nodes = {"Plant": plant}
    for mid, leaves in _TREE:
        mid_g = _ensure_group(doc, mid, plant)
        nodes[mid] = mid_g
        for leaf in leaves:
            nodes[leaf] = _ensure_group(doc, leaf, mid_g)

    placed = 0
    ungrouped = []
    # Snapshot — adding groups mutates doc.Objects
    content = [
        o for o in list(doc.Objects)
        if o.Name not in _GROUP_NAMES
        and o.TypeId != "App::DocumentObjectGroup"
    ]
    for obj in content:
        path = classify(obj.Name)
        if path is None:
            # Still nest under Plant so Combo View is tidy
            if obj not in plant.Group:
                plant.addObject(obj)
            ungrouped.append(obj.Name)
            placed += 1
            continue
        leaf_name = path[-1]
        grp = nodes[leaf_name]
        if obj not in getattr(grp, "Group", []):
            grp.addObject(obj)
        placed += 1

    print(
        "plant groups: %d objects nested under Plant (%d unmatched → Plant root)"
        % (placed, len(ungrouped))
    )
    if ungrouped:
        sample = ", ".join(ungrouped[:24])
        more = "" if len(ungrouped) <= 24 else " …+%d" % (len(ungrouped) - 24)
        print("  unmatched sample: %s%s" % (sample, more))
    return plant


def ensure_visible(doc):
    """Visibility=True on every Part/Mesh and on groups (Combo View open-friendly)."""
    n = 0
    for obj in doc.Objects:
        tid = obj.TypeId or ""
        want = (
            tid.startswith("Part::")
            or tid.startswith("Mesh::")
            or tid == "App::DocumentObjectGroup"
            or hasattr(obj, "Shape")
            or hasattr(obj, "Mesh")
        )
        if not want:
            continue
        try:
            vo = obj.ViewObject
            if vo is not None and hasattr(vo, "Visibility"):
                if not vo.Visibility:
                    vo.Visibility = True
                n += 1
            elif vo is not None:
                n += 1
        except Exception as exc:
            print("visibility skip", obj.Name, exc)
    print("visibility asserted on %d view objects" % n)
    return n


def _vis_vp_block(name: str) -> str:
    return (
        '        <ViewProvider name="%s" expanded="0">\n'
        '            <Properties Count="1" TransientCount="0">\n'
        '                <Property name="Visibility" type="App::PropertyBool" status="1">\n'
        '                    <Bool value="true"/>\n'
        '                </Property>\n'
        '            </Properties>\n'
        '        </ViewProvider>\n'
    ) % name


def patch_visibility_fcstd(path):
    """Force Visibility=true for every Part/Mesh/group in GuiDocument.xml."""
    import re
    import zipfile
    from pathlib import Path

    path = Path(path)
    if not path.is_file():
        print("no fcstd to visibility-patch", path)
        return 0

    with zipfile.ZipFile(path, "r") as zf:
        doc_xml = zf.read("Document.xml").decode("utf-8", errors="replace")
        gui = ""
        if "GuiDocument.xml" in zf.namelist():
            gui = zf.read("GuiDocument.xml").decode("utf-8", errors="replace")
        others = {
            i.filename: zf.read(i.filename)
            for i in zf.infolist()
            if i.filename != "GuiDocument.xml"
        }

    want = set()
    for typ, name in re.findall(r'<Object type="([^"]+)" name="([^"]+)"', doc_xml):
        if (
            typ.startswith("Part::")
            or typ.startswith("Mesh::")
            or typ == "App::DocumentObjectGroup"
        ):
            want.add(name)

    if not gui:
        blocks = "".join(_vis_vp_block(n) for n in sorted(want))
        gui = (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<Document SchemaVersion="1" HasExpansion="1">\n'
            "    <Expand />\n"
            '    <ViewProviderData Count="%d">\n'
            "%s"
            "    </ViewProviderData>\n"
            "</Document>\n" % (len(want), blocks)
        )
        flipped = len(want)
        added = len(want)
    else:
        # Flip existing Visibility → true
        gui, flipped = re.subn(
            r'(<Property name="Visibility" type="App::PropertyBool"[^>]*>\s*'
            r'<Bool value=")[^"]+("/>)',
            r'\g<1>true\g<2>',
            gui,
        )
        existing = set(re.findall(r'<ViewProvider name="([^"]+)"', gui))
        missing = sorted(want - existing)
        added = 0
        if missing:
            insert = "".join(_vis_vp_block(n) for n in missing)
            if "</ViewProviderData>" in gui:
                gui = gui.replace(
                    "</ViewProviderData>",
                    insert + "    </ViewProviderData>",
                    1,
                )
                gui = re.sub(
                    r'(<ViewProviderData Count=")(\d+)(">)',
                    lambda m: "%s%d%s"
                    % (m.group(1), int(m.group(2)) + len(missing), m.group(3)),
                    gui,
                    count=1,
                )
                added = len(missing)

    tmp = path.with_suffix(".fcstd.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in others.items():
            zout.writestr(name, data)
        zout.writestr("GuiDocument.xml", gui.encode("utf-8"))
    tmp.replace(path)
    print(
        "GuiDocument Visibility=true: flipped=%d added_vp=%d want=%d → %s"
        % (flipped, added, len(want), path)
    )
    return flipped + added


def tree_summary(doc):
    """Return nested dict of group → child counts for reporting."""
    plant = doc.getObject("Plant")
    if plant is None:
        return {}

    def walk(grp):
        kids = list(getattr(grp, "Group", []) or [])
        out = {"_count": 0, "_groups": {}}
        for k in kids:
            if k.TypeId == "App::DocumentObjectGroup":
                out["_groups"][k.Name] = walk(k)
            else:
                out["_count"] += 1
        # roll up
        out["_total"] = out["_count"] + sum(
            v["_total"] for v in out["_groups"].values()
        )
        return out

    return {plant.Name: walk(plant)}
