"""FLOAT_SINK manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AC. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (params
  size_note records the M0 study envelope; no design sizing exists on the node or
  the duty sheet). The build fills it; the study-box basis is a hold (WORK_ORDER W12).
- Body: open-top CPVC float/sink separator tank - floor and walls 10 mm (study, no
  authority states a thickness), closed by a 20 mm hold-down rim frame. Sink zone
  x 0..690, float zone x 700..990, divided by a CPVC weir plate to z 700; the float
  launder is a channel along the +X wall with its overflow lip at z 700 and its
  channel floor at z 640. Both are layout solids from the duty section 1 separation
  duty (float plastics / sink grit); the node internals row is none, so the tracker
  records no internal solid (holds, W12).
- Material: CPVC wetted per duty section 3 (AQS-STD-002 M1/M2/M5; feed arrives from
  LEACH_CSTR_1 at up to 85 C); corrosion allowance does not apply to the polymer.
- Nozzles: all 6 rows of docs-authority/nozzles/FLOAT_SINK.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs
  (lib/nozzles), the schedule rating column carried verbatim as text, no flange
  (W4 110 % rule - no process pressure stated). N6 is a solids row drawn at DN15
  and labeled bore not calculated. Ports pack centred on the face mid-length per
  face/height group; the zoning against the weir is the fabricator's (W12).
- A-VES: the liquor volume at the 720 mm working level net of the weir and launder
  is computed from the model and reported; the duty claims no holdup, so no
  residence time is derived from it.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402

GN = graph_node.graph_node("FLOAT_SINK")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800, study registry box
REV = P["graph_revision"]

T_WALL = 10.0          # study plate thickness - no authority states one (WORK_ORDER W12)
T_BASE = 20.0                                   # rim frame thickness, envelope idiom
Z_LIQ = 720.0                                   # working level: below the 780 inner rim
WEIR_X = 690.0                                  # weir plate x 690..700, to z 700
WEIR_T = 10.0
WEIR_TOP = 700.0
LIP_X = 920.0                                   # launder inner lip x 920..930, top z 700
CHAN_X = 930.0                                  # channel floor x 930..990, z 640..650
CHAN_Z = 640.0
CA = materials.ca_for("CPVC")                   # 0.0, polymers: AQS-STD-001 shop rule
RHO = materials.density("CPVC")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- tank shell (open top)
tank = box(0, 0, 0, L, W, H - T_BASE).cut(
    box(T_WALL, T_WALL, T_WALL, L - 2 * T_WALL, W - 2 * T_WALL, H))
parts["tank"] = tank

t = 20.0
rim = box(0, 0, H - T_BASE, L, t, T_BASE).union(box(0, W - t, H - T_BASE, L, t, T_BASE))
rim = rim.union(box(0, t, H - T_BASE, t, W - 2 * t, T_BASE))
rim = rim.union(box(L - t, t, H - T_BASE, t, W - 2 * t, T_BASE))
parts["rim_frame"] = rim

# ---------------------------------------------------------------- weir + launder
# welded in: the weir laps 5 mm into the floor, the launder floor laps 5 mm into the
# +X wall and the lip laps through the channel floor band, so every union fuses
weir = box(WEIR_X, T_WALL + 10, T_WALL - 5, WEIR_T, W - 2 * (T_WALL + 10), WEIR_TOP - T_WALL + 5)
parts["weir"] = weir
launder = box(LIP_X, T_WALL + 10, CHAN_Z - 5, 10, W - 2 * (T_WALL + 10),
              WEIR_TOP - CHAN_Z + 5)                       # lip plate, top at the overflow z 700
launder = launder.union(box(CHAN_X, T_WALL + 10, CHAN_Z,
                            L - 5 - CHAN_X, W - 2 * (T_WALL + 10), 10))
parts["launder"] = launder

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}   # house convention: inlets -Y, outlets +Y
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

def od_of(r):
    """Port outside diameter from the schedule bore; solids rows drawn at DN15."""
    return dn.pipe_od("DN15") if r["size"] == "solids" else dn.pipe_od(r["size"])


layout_x = {}
for (face, z), rows in sorted(groups.items()):
    if face not in ("-Y", "+Y"):
        continue
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = dn.pipe_od("DN15" if dnl == "solids" else dnl)
    dnl_hw = "DN15" if dnl == "solids" else dnl
    if dnl == "solids":
        s = nozzles.stub("DN15", 50.0)
        note = SOLIDS_NOTE
    else:
        s = nozzles.hose_barb(hose_id(dnl_hw), Hose[dnl_hw], root_od=od)
        note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N4: boss to the 50 datum
        s = nozzles.stub(dnl_hw, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (300.0, W / 2), (L, W, H))
        note = "drain boss in the sink zone floor, tip at the 50 datum"
    elif r["face"] == "top":                              # N5: datum 800 is the envelope top
        s = nozzles.hose_barb(hose_id(dnl_hw), Hose[dnl_hw], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2, W - 15.0), (L, W, H))
        note = "vent on the +Y rim bar, flush at the 800 envelope top"
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm clamped to {round(h_d, 1)} mm "
                     "(barb radius rule) - WORK_ORDER W12")
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "solids" if dnl == "solids" else "hose",
                  "dn": dnl_hw, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if face == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- process inventory (not a BOM part)
liq = box(T_WALL, T_WALL, T_WALL, L - 2 * T_WALL, W - 2 * T_WALL, Z_LIQ - T_WALL)
liq = liq.cut(parts["weir"]).cut(parts["launder"])
inv = {"liquor": liq}

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="FLOAT_SINK")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / "float_sink.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "float_sink.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "FLOAT_SINK.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "float_sink.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
v_liq = inv["liquor"].val().Volume() / 1e9
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); no design sizing on the node "
    "or the duty sheet (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": round(v_liq, 4),
    "holdup_basis": "none: duty section 2 claims no holdup; the model volume at the "
    "720 mm working level is reported, not turned into a residence time (A-VES)",
    "tank": {"wall_mm": T_WALL, "wall_basis": "study value - no authority states a "
             "thickness (WORK_ORDER W12)",
             "weir": {"x_mm": [WEIR_X, WEIR_X + WEIR_T], "top_z_mm": WEIR_TOP,
                      "note": "sink zone x 0..690, float zone x 700..990 (layout solids "
                      "from the duty section 1 separation duty; node internals row none)"},
             "launder": {"lip_x_mm": LIP_X, "lip_top_z_mm": WEIR_TOP,
                         "floor_z_mm": [CHAN_Z, CHAN_Z + 10]}},
    "material": {"class": "CPVC", "ca_mm": CA,
                 "basis": "duty section 3: CPVC wetted (AQS-STD-002 M1/M2/M5, 85 C feed); "
                 "corrosion allowance does not apply to the polymer"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces "
    "(lib/nozzles.place_on_face); solids rows DN15 labeled bore not calculated; the "
    "schedule rating column (Class 150) is carried verbatim as text against duty "
    "section 4 (atmospheric tube or hose, no flange class)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"CPVC tank shell, open top, {L:g} x {W:g} x {H - T_BASE:g} mm, wall "
          f"{T_WALL:g} mm, floor {T_WALL:g} mm", 1, "CPVC", mass["tank"], "make",
     "study registry envelope (node size_mm); wall a study value (WORK_ORDER W12); "
     "CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"Top hold-down rim frame, {t:g} mm bar, four sides", 1, "CPVC",
     mass["rim_frame"], "make", "study section; same polymer rule"],
    ["3", f"Weir plate, x {WEIR_X:g}..{WEIR_X + WEIR_T:g}, to z {WEIR_TOP:g} "
          "(sink / float divider)", 1, "CPVC", mass["weir"], "make",
     "layout solid from the duty section 1 separation duty (float plastics / sink grit); "
     "node internals row none (WORK_ORDER W12)"],
    ["4", f"Float launder: lip plate x {LIP_X:g}..{LIP_X + 10:g} (overflow z {WEIR_TOP:g}), "
          f"channel floor z {CHAN_Z:g}", 1, "CPVC", mass["launder"], "make",
     "layout solid, same basis; launder discharge elevation is a layout choice against "
     "the schedule datum (WORK_ORDER W12)"],
    ["5", "Nozzle set per docs-authority/nozzles/FLOAT_SINK.csv: 4 hose barbs "
          "(DN15/DN25/DN50), 1 drain boss, 1 solids port at DN15 (bore not calculated)",
     len(schedule), "CPVC", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "barb profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CPVC"), 4,
     "tank floor to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)                      # legacy M2 block; superseded by envelope + layout
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note); no design sizing on the node or "
             "the duty sheet (WORK_ORDER W12)",
    "tank_body_mm": [L, W, H - T_BASE],
}
p["design"] = {
    "service": "float/sink separation of leach sink solids, up to 85 C, atmospheric "
               "(duty sections 1, 3 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study value", "ca_mm": CA,
    "weir_top_z_mm": WEIR_TOP, "working_level_mm": Z_LIQ,
}
p["layout"] = {
    "frame": "origin at the envelope corner; x along 1000, y along 600, z up",
    "zones": "sink zone x 0..690 (weir at 690..700), float zone x 700..990 with the "
             "launder at the +X wall (lip top z 700, channel floor z 640)",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row per "
                     "face/height group, centred on the face mid-length, 8 mm clear at "
                     "the bore; the zoning against the weir is the fabricator's",
    "vent_drain": "N5 vent on the +Y rim bar flush at the 800 top; N4 drain boss in the "
                  "sink zone floor, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces, roots through "
                      "the shell wall (lib/nozzles.place_on_face); nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}))
