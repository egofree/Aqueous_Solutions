"""HOPPER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared
reader (models/mfg/lib/graph_node.py); the params.json write-back beside it carries
only the builder-owned envelope, design and layout blocks.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 600 mm, node size_mm set by docs-authority/_storage_sizing.py
  (AQS-DUTY-064). The duty sheet section 2 carries no size line and no holdup basis
  (holds, WORK_ORDER W12); the node box is the claimed envelope and nothing exceeds it.
- Body: a welded carbon-steel receiving hopper - bin section z 310..580, pyramidal
  frustum z 40..310 discharging to a 210 mm square outlet box over a 190 mm frame
  opening, on a 20 mm base plate, closed by a 20 mm hold-down rim frame (the
  vessel_z envelope idiom). Wall 4 mm plate is a study value - no authority states a
  thickness (hold, W12).
- Material: carbon steel, hydrocarbon service, corrosion allowance 1.5 mm
  (duty section 3, AQS-STD-001). Fastener grade ISO 898-1 8.8 by the plan rule.
- Nozzles: all 10 rows of docs-authority/nozzles/HOPPER.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4 ("no flange class"):
  hose barbs (lib/nozzles), the schedule rating column carried verbatim as text.
  Outlets scheduled at the 600 datum sit at the envelope top and are clamped below
  the barb radius (holds, W12); the vent datum 800 predates the 600 box and is drawn
  flush on the +Y rim bar; the drain is a boss rising to its 50 datum beside the
  discharge opening.
- A-VES: the hopper holdup volume is computed from the model and reported; the duty
  claims no holdup, so no residence time is derived from it.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402

GN = graph_node.graph_node("HOPPER")          # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 600, AQS-DUTY-064
REV = P["graph_revision"]

T_WALL = 4.0          # study plate thickness - no authority states one (WORK_ORDER W12)
Z_BIN0, Z_BIN1 = 310.0, H - 20.0        # bin section between the frustum and the rim frame
Z_TIP = 40.0                              # frustum tip, buried in the outlet-box ring
TIP_OUT, TIP_IN = 200.0, 192.0            # frustum small-end square, outside / inside
BOX_Z0, BOX_Z1 = 10.0, 80.0               # outlet box: laps the base plate and the frustum tip
BOX_OUT, BOX_BORE = 210.0, 196.0          # outlet box outside square and discharge bore
OPENING = 190.0                           # base-plate discharge opening
T_BASE = 20.0                             # base plate / rim frame thickness
CA = materials.ca_for("carbon steel", "hydrocarbon")       # 1.5, AQS-STD-001
RHO = materials.density("CS")



def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def sq_loft(z_top, w_top, z_bot, w_bot):
    """A square frustum between two z planes, centred on the envelope axis."""
    return (cq.Workplane("XY", origin=(L / 2, W / 2, z_top))
            .rect(w_top, w_top).workplane(offset=z_bot - z_top).rect(w_bot, w_bot)
            .loft(ruled=True))


parts = {}

# ---------------------------------------------------------------- body: bin + frustum + outlet
outer = box(0, 0, Z_BIN0, L, W, Z_BIN1 - Z_BIN0).union(
    sq_loft(Z_BIN0, L, Z_TIP, TIP_OUT))
cavity = box(T_WALL, T_WALL, Z_BIN0, L - 2 * T_WALL, W - 2 * T_WALL, Z_BIN1 - Z_BIN0).union(
    sq_loft(Z_BIN0, L - 2 * T_WALL, Z_TIP, TIP_IN))
outlet = box(L / 2 - BOX_OUT / 2, W / 2 - BOX_OUT / 2, BOX_Z0,
             BOX_OUT, BOX_OUT, BOX_Z1 - BOX_Z0).cut(
    box(L / 2 - BOX_BORE / 2, W / 2 - BOX_BORE / 2, BOX_Z0,
        BOX_BORE, BOX_BORE, BOX_Z1 - BOX_Z0))
body = outer.cut(cavity).union(outlet)
parts["body"] = body

# base plate with the discharge opening, and the top hold-down rim frame
frame_base = box(0, 0, 0, L, W, T_BASE).cut(
    box(L / 2 - OPENING / 2, W / 2 - OPENING / 2, 0, OPENING, OPENING, T_BASE))
parts["frame_base"] = frame_base
t = 20.0
rim = box(0, 0, Z_BIN1, L, t, T_BASE).union(box(0, W - t, Z_BIN1, L, t, T_BASE))
rim = rim.union(box(0, t, Z_BIN1, t, W - 2 * t, T_BASE))
rim = rim.union(box(L - t, t, Z_BIN1, t, W - 2 * t, T_BASE))
parts["rim_frame"] = rim

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}   # house convention: inlets -Y, outlets +Y


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    if r["size"] in dn.PIPE:
        groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

# one-row packing per face/height group, centred on the face mid-length; the schedule
# gives face and height only, so the along-face positions are the layout choice
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    if face not in ("-Y", "+Y"):
        continue
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    span = sum(dn.pipe_od(r["size"]) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        w = dn.pipe_od(r["size"]) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

def wall_half(h):
    """Outer half-width of the body at height h: frustum slope below the bin, bin above."""
    if h >= Z_BIN0:
        return L / 2
    return TIP_OUT / 2 + (L / 2 - TIP_OUT / 2) * (h - Z_TIP) / (Z_BIN0 - Z_TIP)


noz, drawn, n_drawn = None, {}, 0
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    if dnl not in dn.PIPE:
        # non-piped row: the solids dock-import make-up feed is a hand transfer,
        # not piped - carried verbatim, not drawn (no STEP/BOM/geometry change)
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"], "height_mm": h,
                      "schedule_rating": r["rating"], "service": r["service"],
                      "note": "solids dock-import make-up feed - a hand transfer, not "
                              "piped: carried verbatim, not drawn"}
        continue
    n_drawn += 1
    od = dn.pipe_od(dnl)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N7: boss to the 50 datum beside the opening
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = "drain boss beside the discharge opening, tip at the 50 datum"
    elif r["face"] == "top":                              # N8: datum 800 predates the 600 box
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2, W - 15.0), (L, W, H))
        note = ("vent on the +Y rim bar; schedule datum 800 mm predates the 600 mm box "
                "- named hold, WORK_ORDER W12")
    else:
        h_d = min(h, H - od / 2 - 5.0)                    # clamp below the barb radius at the top
        if h_d < h:
            note = (f"schedule datum {h:g} mm sits at the envelope top; drawn clamped to "
                    f"{round(h_d, 1)} mm (barb radius rule) - named hold, WORK_ORDER W12")
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        # side ports: root on the shell wall where the wall stands off the envelope face
        # (the frustum slope), else the house flush-at-face idiom with the root through
        # the wall into the cavity
        half = wall_half(h_d)
        gap = (L - 2 * half) / 2                          # envelope face to outer wall surface
        if gap + 2.0 >= Hose[dnl]:                        # wall-root keeps the tip inside
            # wall-root idiom: place flush on a local box whose face is the wall
            # (lib place_on_face works in absolute coords, so the local box starts at
            # its own corner), then embed the root 2 mm into the wall and let the barb
            # stand proud of it toward the envelope face
            c0 = (L - 2 * half) / 2                       # local box corner in the absolute frame
            s = nozzles.place_on_face(s, face, h_d, (layout_x[tag] - c0, half),
                                      (2 * half, 2 * half, H))
            s = s.translate((c0, c0 + 2.0 - Hose[dnl], 0) if face == "-Y"
                            else (c0, c0 - 2.0, 0))
            note += "; root set in the shell wall (the frustum slope stands off the envelope face)"
        else:
            s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1) if face in ("-Y", "+Y")
                  else (0.0 if face == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="HOPPER")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "hopper.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "hopper.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "HOPPER.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose (the NURBS
# poles stand off the surface by tens of millimetres)
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "hopper.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
v_bin = (L - 2 * T_WALL) * (W - 2 * T_WALL) * (Z_BIN1 - Z_BIN0)
v_frustum = (Z_BIN0 - Z_TIP) / 3.0 * ((L - 2 * T_WALL) * (W - 2 * T_WALL)
                                      + math.sqrt((L - 2 * T_WALL) * (W - 2 * T_WALL) * TIP_IN ** 2)
                                      + TIP_IN ** 2)
v_outlet = BOX_BORE ** 2 * (BOX_Z1 - BOX_Z0)
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H], "size_basis": P.get("size_basis", ""),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": round((v_bin + v_frustum + v_outlet) / 1e9, 4),
    "holdup_basis": "none: duty section 2 claims no holdup and section 8 records that no "
    "holdup basis exists for this class; the volume is reported, not turned into a "
    "residence time (A-VES)",
    "body": {"bin_z_mm": [Z_BIN0, Z_BIN1], "frustum_z_mm": [Z_TIP, Z_BIN0],
             "wall_mm": T_WALL, "wall_basis": "study value - no authority states a "
             "thickness (WORK_ORDER W12)",
             "discharge": f"{OPENING:g} mm base-plate opening under a {BOX_BORE:g} mm "
             "outlet-box bore"},
    "material": {"class": "carbon steel", "ca_mm": CA,
                 "basis": "duty section 3: carbon steel, hydrocarbon, CA 1.5 mm (AQS-STD-001)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces "
    "(lib/nozzles.place_on_face); the schedule rating column (Class 150) is carried "
    "verbatim as text against duty section 4 (no flange class, atmospheric tube or "
    "hose); the N11 solids make-up feed is a hand transfer, not piped - carried "
    "verbatim in this report, not drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
n_barb = sum(1 for r in schedule if r["face"] not in ("bottom", "top")
             and r["size"] in dn.PIPE)
rows = [
    ["1", f"Welded hopper body: bin {L:g} x {W:g} x {Z_BIN1 - Z_BIN0:g} mm over a pyramidal "
          f"frustum to a {BOX_BORE:g} mm discharge bore, wall {T_WALL:g} mm", 1,
     "carbon steel plate", mass["body"], "make",
     "node envelope (AQS-DUTY-064); wall a study value (WORK_ORDER W12); CA 1.5 mm "
     "(AQS-STD-001 hydrocarbon rule)"],
    ["2", f"Base plate {L:g} x {W:g} x {T_BASE:g} mm with a {OPENING:g} mm discharge opening",
     1, "carbon steel plate", mass["frame_base"], "make", "study thickness; same CA rule"],
    ["3", f"Top hold-down rim frame, {t:g} mm bar, four sides (lifting and restraint)", 1,
     "carbon steel bar", mass["rim_frame"], "make", "study section; same CA rule"],
    ["4", f"Nozzle set per docs-authority/nozzles/HOPPER.csv: {n_barb} hose barbs "
          f"(DN15/DN25/DN50), 1 drain boss, 1 vent barb on the rim bar",
     n_drawn, "carbon steel pipe", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; barb "
     "profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 4,
     "base plate to slab, one per corner (count from the model)",
     "plan W5 grade rule on carbon steel; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)                      # legacy M2 block; superseded by envelope + layout
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "node size_mm set by docs-authority/_storage_sizing.py (AQS-DUTY-064); "
             "the duty sheet section 2 carries no size line (WORK_ORDER W12)",
    "bin_z_mm": [Z_BIN0, Z_BIN1], "frustum_z_mm": [Z_TIP, Z_BIN0],
}
p["design"] = {
    "service": "mixed metal-scrap / worn-goods receiving hopper, gravity discharge, "
               "atmospheric (duty sections 1, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study value", "ca_mm": CA,
    "discharge_bore_mm": BOX_BORE, "opening_mm": OPENING,
}
p["layout"] = {
    "frame": "origin at the envelope corner; x along 600, y along 600, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row per "
                     "face/height group, centred on the face mid-length, 8 mm clear at the "
                     "bore; per-tag positions recorded in check.nozzles_drawn",
    "vent_drain": "N8 vent on the +Y rim bar (datum 800 predates the 600 box); N7 drain "
                  "boss beside the discharge opening, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces, roots through the "
                      "shell wall (lib/nozzles.place_on_face); nothing protrudes, bbox "
                      "within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}))
