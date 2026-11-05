"""CRYO_N2 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AC. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. (W2 fields by the
tracker; the layout and study blocks beside them are builder-owned).

Placement frame: x along 300 mm, y across 300 mm, z up 2000 mm, origin at the
envelope corner. Every dimension is an authority figure or a named layout choice:

- The node carries no design, no internals and no diameter (duty section 8: "No
  diameter on this node"). Per the house rule, a unit whose duty sheet books no
  internals gets the shell machine: shell + heads + nozzles + supports. The shell
  is the node size_mm box 300 x 300 x 2000 itself (316L t 3, study; a cold_box
  vacuum jacket is not named anywhere and none is drawn), on a 20 mm skid.
- Nozzles: all 8 rows of docs-authority/nozzles/CRYO_N2.csv at tag, face, height
  and bore - every schedule datum fits this envelope (inlet z 400, outlet z 1500,
  outlets z 600, drain datum 50, vent flush at the 2000 top). Inlets -Y, outlets
  +Y (house face mapping). Atmospheric joints are hose barbs per duty sections 4
  and 6 (the vent stays on the gas edge, not the room); no flange is drawn and
  the schedule rating column (Class 150) is carried verbatim as text.

Materials per docs-authority/duties/CRYO_N2.md section 3: 316L, condensation,
corrosion allowance 0 mm, no carbon steel.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles  # noqa: E402

GN = graph_node.graph_node("CRYO_N2")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
REV = P["graph_revision"]

# ------------------------------------------------------------------ cited constants
L, W, H = [float(v) for v in P["size_mm"]]                # 300 x 300 x 2000
SKID_T = 20.0             # skid plate, study
SHELL_T = 3.0             # shell wall, house study (no thickness stated; W12)
CA = materials.ca_for("316L")                             # 0.0
RHO = materials.density("316L")


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


parts = {}

# ---------------------------------------------------------------- skid + shell (the envelope box)
parts["skid"] = box(0, 0, 0, L, W, SKID_T)
shell = box(0, 0, SKID_T - 5.0, L, W, H - SKID_T + 5.0).cut(   # laps the skid 5 so the union fuses
    box(SHELL_T, SHELL_T, SKID_T + SHELL_T, L - 2 * SHELL_T, W - 2 * SHELL_T,
        H - SKID_T - 2 * SHELL_T))
parts["shell"] = shell

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

# along-face packing per face/height group, centred on the face mid-length
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"] if r["size"] != "solids" else "DN15"),
                                       r["tag"]))
    span = sum(dn.pipe_od(r["size"] if r["size"] != "solids" else "DN15") + 8.0
               for r in rows) - 8.0
    assert span <= L - 60.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        d = r["size"] if r["size"] != "solids" else "DN15"
        layout_x[r["tag"]] = round(x + dn.pipe_od(d) / 2, 1)
        x += dn.pipe_od(d) + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    dnl_hw = "DN15" if dnl == "solids" else dnl
    note = "atmospheric hose joint at the envelope face (duty sections 4 and 6)"
    if r["face"] == "bottom":                              # N3: flush at z 0, boss to the datum
        s = nozzles.stub(dnl_hw, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (60.0, W / 2), (L, W, H))
        note = "drain flush at z 0 through the skid, boss to the 50 datum"
    elif r["face"] == "top":                               # N4: flush at the 2000 top
        s = nozzles.stub(dnl_hw, 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2, W / 2), (L, W, H))
        note = "vent flush at the 2000 mm top datum (duty section 6: to the gas edge, not the room)"
    else:
        s = nozzles.hose_barb(hose_id(dnl_hw), Hose[dnl_hw], root_od=dn.pipe_od(dnl_hw))
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        # extension stub into the cavity so the union crosses the shell wall
        y0 = SKID_T + 2.0 if face == "-Y" else W - SKID_T - 44.0
        s = s.union(rod(dn.pipe_od(dnl_hw) / 2, (layout_x[tag], y0, h), "Y", 42.0))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl_hw, "face": face, "height_mm": h,
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="CRYO_N2")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cryo_n2.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "cryo_n2.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CRYO_N2.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": P["size_mm"], "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "shell": {"wall_mm": SHELL_T, "note": "the node size_mm box is the shell; no internals, no "
              "diameter and no packing are named on the node or the duty sheet (holds, W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "hose barbs flush at the envelope faces (lib/nozzles.place_on_face); every "
    "schedule datum fits this envelope; schedule rating column (Class 150) carried verbatim as "
    "text, no flange drawn (duty sections 4 and 6)",
    "part_mass_kg": mass, "cad_stl_scope": "full build, metres (the build fills the node "
    "size_mm box exactly)", "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell 300 x 300 x {H - SKID_T:g} mm, t {SHELL_T:g}, welded closed, on a "
          f"{SKID_T:g} mm skid", 1, "316L", round(mass["shell"] + mass["skid"], 1), "make",
     "node size_mm box (the build is the shell machine: shell + nozzles + supports); shell t 3 "
     "is the house study value, no thickness stated (W12); duty section 3 CA 0 mm"],
    ["2", f"Nozzle set per docs-authority/nozzles/CRYO_N2.csv ({len(schedule)} rows)", len(schedule),
     "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights/bore verbatim; atmospheric hose per duty sections 4 and 6; "
     "barb profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 x 30 wedge anchor", fasteners.grade_for("316L"), 4,
     "skid to the slab", "plan grade rule; seismic anchorage per the frame check task"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["layout"] = {
    "frame": "origin at the envelope corner; the shell is the node size_mm box on a 20 mm skid",
    "nozzle_spread": "single row per face/height group centred on the face mid-length, 8 mm "
                     "clear at the bore; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N4 flush at the 2000 top datum; N3 flush at z 0 through the skid pass, boss "
                  "to the 50 datum",
    "hardware_idiom": "hose barbs flush at the envelope faces with extension stubs into the "
                      "cavity (lib/nozzles.place_on_face); nothing protrudes, bbox = size_mm",
}
p["study"] = {
    "skid_t_mm": SKID_T, "shell_t_mm": SHELL_T,
    "note": "study values not stated by any authority (the node carries no design and the duty "
            "no thickness)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}))
