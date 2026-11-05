"""POLY_OLEFIN manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the node
design block of the graph (the reactor construction figures). Rebuilds every solid.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 1200 mm, node size_mm (reactor-class study minimum: DN150 at
  1 d hold-up of the naphtha feed at 750 kg/m3 melt density; wall by ASME VIII-1
  UG-27 at 5 MPa). The build fills the box (vent riser to the envelope top, the
  X-PAR-04 registry gate).
- Reactor per the node design block: D 150 x H 225 shell, wall 3.8 mm (the node
  wall_mm row; UG-27 at the 5 MPa design), base and top heads, on a support ring
  over 4 legs and the plinth. The node names no agitator and no jacket - none is
  drawn (hold, W12); the op window is 150-250 C at 1-5 MPa (AQS-SIZE-OIL-POLY).
- Material: SA-240 316L, welded (ASME IX) per duty section 3 (the node design row
  matches). CA 0 mm (AQS-STD-001 rule).
- Nozzles: all 6 rows of docs-authority/nozzles/POLY_OLEFIN.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections (duty section 4: hose,
  atmospheric; the connecting line makes the joint at the face, the CATCH_TANK
  idiom). The 160 inlets and 600 outlet datum draw as issued; row N3 carries the
  line-list classification `solids` (non-piped transfer) in its size column: drawn
  at DN15, bore not calculated, per plan W4, and labeled. The drain passes to the
  envelope bottom (50 datum); the vent riser stands on the top head and flushes at
  the envelope top (the 800 datum is the schedule placeholder - hold, W12). The
  rating column (Class 150) is carried verbatim as text, no flange (W4 110 % rule).
- A-VES: the node envelope basis books the 1 d hold-up of the naphtha feed at
  750 kg/m3 (0.39 L at the 0.2941 kg/d feed) - an existing holdup basis; the gross
  shell volume (3.6 L) is reported from the model and no residence time beyond the
  node basis is derived.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("POLY_OLEFIN")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 1200
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

T_PLINTH = 20.0
CX, CY = L / 2, W / 2                                      # vessel axis
D = float(DS.get("D_mm", 150.0))                           # shell OD
H_SHELL = float(DS.get("H_mm", 225.0))                     # shell height
T_WALL = float(DS.get("wall_mm", 3.8))                     # node design wall
R_IN = D / 2 - T_WALL
Z_RING0, Z_RING1 = 608.0, 616.0                            # support ring (annulus OD 220)
Z_SH0 = Z_RING1                                            # base head 616..628
Z_SH1 = Z_SH0 + 12.0 + H_SHELL                             # shell 628..853
Z_HEAD = Z_SH1 + 20.0                                      # top head 853..873
MAT = "316L"                                               # duty section 3 / node
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)                               # 8000, lib table

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert D == 150.0 and H_SHELL == 225.0 and T_WALL == 3.8, "POLY_OLEFIN node design changed"
assert Z_HEAD < H, "vessel must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_dn(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + stand
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
legs = None
for gx in (CX - 80.0, CX + 80.0):
    for gy in (CY - 80.0, CY + 80.0):
        leg = box(gx - 15.0, gy - 15.0, T_PLINTH - 2.0, 30.0, 30.0,
                  Z_RING0 - T_PLINTH + 4.0)                # laps the support ring
        legs = leg if legs is None else legs.union(leg)
parts["legs"] = legs
ring = (cq.Workplane("XY", origin=(CX, CY, Z_RING0)).circle(110.0)
        .circle(55.0).extrude(Z_RING1 - Z_RING0))
parts["support_ring"] = ring

# ---------------------------------------------------------------- vessel (316L)
base_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
             .extrude(12.0))
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0 + 12.0)).circle(D / 2)
         .circle(R_IN).extrude(H_SHELL))
top_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
            .extrude(Z_HEAD - Z_SH1))
parts["vessel"] = base_head.union(shell).union(top_head)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 45.0                       # face hardware reach (the CATCH_TANK idiom)

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(dn.pipe_od(r["size"] if str(r["size"]).startswith("DN") else "DN15") + 8.0
               for r in rows) - 8.0
    x = CX - span / 2
    for r in rows:
        dnl = r["size"] if str(r["size"]).startswith("DN") else "DN15"
        layout_x[r["tag"]] = round(x + dn.pipe_od(dnl) / 2, 1)
        x += dn.pipe_od(dnl) + 8.0

noz_pieces, drawn = [], {}
for r in schedule:
    tag, size0, face0 = r["tag"], r["size"], r["face"]
    is_dn = str(size0).startswith("DN")
    dnl = size0 if is_dn else "DN15"   # non-piped rows drawn DN15, bore not calculated (plan W4)
    od_s = dn.pipe_od(dnl)
    if face0 == "bottom":               # drain: boss under the base head, flush at z 0
        s = tube_dn(dnl, Z_SH0 + 5.0).translate((CX + 45.0, CY, 0.0))
        note = "drain boss under the base head, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, CX + 45.0
    elif face0 == "top":                # vent: riser on the top head, flush at the box top
        s = tube_dn(dnl, H - Z_HEAD + 10.0).translate((CX, CY, Z_HEAD - 10.0))
        note = ("vent riser on the top head, flush at the envelope top; the "
                "schedule datum 800 is the placeholder (hold, WORK_ORDER W12)")
        z_d, x_d = H, CX
    else:
        h = float(r["height_mm"])
        z_d = h                          # 160 and 600 fit the 1200 box; drawn as issued
        x_d = layout_x[tag]
        s = (tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)) if face0 == "inlet" else
             tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x_d, W, z_d)))
        bore_txt = (f"{dnl} open-bore tube" if is_dn else
                    "non-piped solids transfer (line-list classification): drawn DN15, "
                    "bore not calculated (plan W4)")
        note = ("schedule datum drawn as issued; " + bore_txt + " flush at the "
                "envelope face (duty section 4: atmospheric joints are hose; the "
                "connecting line makes the joint at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": size0, "face": face0,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_gross = round(math.pi * R_IN ** 2 * H_SHELL / 1e6, 4)    # L
feed = 0.294127                                            # kg/d, node sizing block
v_1d = round(feed / 750.0, 4)                              # L at 750 kg/m3

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    if k == "nozzles":
        for piece in noz_pieces:
            solid = piece if solid is None else solid.union(piece)
        continue
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {
    "plinth_stand": (parts["plinth"].val().Volume() + parts["legs"].val().Volume()
                     + parts["support_ring"].val().Volume()) * materials.density("CS") / 1e9,
    "vessel": parts["vessel"].val().Volume() * RHO / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "reactor-class study minimum; DN150 at 1 d hold-up of the "
    "naphtha feed at 750 kg/m3 melt density; wall by ASME VIII-1 UG-27 at 5 MPa "
    "(node envelope basis)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "the skid chain (plinth, stand, vessel, drain and vent) fuses "
    "to one solid; the face-stub connections stay separate until the connecting "
    "lines make their joints",
    "vessel": {"od_mm": D, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_HEAD],
               "wall_basis": "node design wall_mm (UG-27 at the 5 MPa design, "
               "AQS-SIZE-OIL-POLY op window 150-250 C at 1-5 MPa)",
               "gross_volume_L": v_gross,
               "internals": {"source": "none: the node internals row is none and "
                             "the node names no agitator and no jacket",
                             "basis": "none drawn (WORK_ORDER W12)"}},
    "a_ves": {"gross_volume_L": v_gross, "holdup_1d_L": v_1d,
              "basis": "the node envelope basis books the 1 d hold-up of the "
              "0.2941 kg/d naphtha feed at 750 kg/m3 (an existing basis); the "
              "gross shell volume is reported from the model and no residence "
              "time beyond the node basis is derived (A-VES)"},
    "material": {"class": "SA-240 316L, welded", "ca_mm": CA,
                 "basis": "duty section 3 (the node design row matches): SA-240 "
                 "316L, welded (ASME IX); CA 0 mm (AQS-STD-001 rule)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: atmospheric joints are hose; the W4 110 percent rule "
    "draws no flange where no process pressure is stated); the schedule rating "
    "column (Class 150) is carried verbatim as text; datums draw as issued; the "
    "N3 solids row drawn DN15, bore not calculated (plan W4)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Vessel OD {D:g} x wall {T_WALL:g}, shell {H_SHELL:g} with heads, z "
          f"{Z_SH0:g}..{Z_HEAD:g}, on the support ring, 4 legs and the plinth", 1,
     "SA-240 316L plate (welded, ASME IX)", round(mass["vessel"] + mass["plinth_stand"], 1),
     "make",
     "node design D/H/wall (wall by UG-27 at the 5 MPa design, AQS-SIZE-OIL-POLY); "
     "duty section 3 matches; CA 0 mm (AQS-STD-001)"],
    ["2", "Nozzle set per docs-authority/nozzles/POLY_OLEFIN.csv: 6 atmospheric "
          "open-bore tube connections at the envelope faces (3 inlets on -Y at "
          "160, the N3 solids row drawn DN15 bore not calculated, drain under "
          "the base head, vent riser to the envelope top)", len(schedule),
     "316L tube", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table; "
     "the N3 solids row is a non-piped transfer drawn per plan W4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "vessel": {"od_mm": D, "axis_xy_mm": [CX, CY], "z_mm": [Z_SH0, Z_HEAD]},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "vertical cylindrical oligomerization reactor: SA-240 316L vessel "
               "D 150 x H 225, wall 3.8 (UG-27 at 5 MPa), op window 150-250 C at "
               "1-5 MPa (node design block, AQS-SIZE-OIL-POLY)",
    "mat": "SA-240 316L, welded (duty section 3; the node design row matches)",
    "ca_mm": CA,
    "wall_mm": T_WALL, "wall_basis": "node design wall_mm (UG-27 at 5 MPa)",
    "internals": "none drawn (node internals row none; the node names no "
                 "agitator and no jacket; WORK_ORDER W12)",
    "purchased": "none named on the node or the duty sheet - none drawn "
                 "(WORK_ORDER W12)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at (300, 300); support "
             "ring z 608..616, shell 628..853, top head 853..873; vent riser to "
             "the envelope top (fills the node box, X-PAR-04 registry gate)",
    "nozzle_spread": "side rows flush at the envelope faces (the CATCH_TANK "
                     "idiom: the connecting line makes the joint at the face); "
                     "N1/N2/N4 in on -Y at 160; N3 solids out on +Y at 600; "
                     "drain boss under the base head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "face hardware flush at the envelope faces; nothing protrudes",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
