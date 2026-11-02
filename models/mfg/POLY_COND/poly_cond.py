"""POLY_COND manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the node
design block of the graph (the kettle construction figures). Rebuilds every solid.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 1200 mm, node size_mm (AQS-DUTY-073 reactor-class study
  minimum; the envelope state is "standby": installed standby, the recipe waits on
  the digester organic assay, AQS-DES-POLY). The build fills the box (vent riser to
  the schedule datum).
- Kettle per the node design block: D 200 x H 300 shell (condensation resin
  kettle), wall 6 mm (study fab-page value; the node books no thickness - hold,
  W12), base and top heads, on a support ring over 4 legs and the plinth. The
  jacket (jacket_C 160, node design row) is drawn as its envelope annulus. The
  agitator per the node design row (agitator_kW 0.18) is drawn as solids - shaft
  and two-blade impeller - into the purchased drive envelope (plan rule 6).
- Material: 316L per duty section 3 (the "Hastelloy option" alternative is a named
  hold, W12). CA 0 mm (AQS-STD-001 rule).
- Nozzles: all 3 rows of docs-authority/nozzles/POLY_COND.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections (duty section 4: hose,
  atmospheric; the connecting line makes the joint at the face, the CATCH_TANK
  idiom). The 160 inlet draws as issued; the drain passes to the envelope bottom
  (50 datum); the vent riser stands on the top head and flushes at the envelope
  top (the 800 datum is the schedule placeholder - hold, W12; the build fills the
  node box, the X-PAR-04 registry gate). The rating column (Class 150) is carried
  verbatim as text, no flange (W4 110 % rule - no process pressure stated).
- A-VES: the duty claims no holdup (the DIGEST_TO_POLY edge stays 0 until the
  assay issues the recipe); the gross shell volume is reported for the record and
  no residence time is derived.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 1200
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

T_PLINTH = 20.0
CX, CY = L / 2, W / 2                                      # kettle axis
D = float(DS.get("D_mm", 200.0))                           # shell OD
H_SHELL = float(DS.get("H_mm", 300.0))                     # shell height
T_WALL = 6.0                                               # study fab-page value (hold)
R_IN = D / 2 - T_WALL
Z_RING0, Z_RING1 = 408.0, 416.0                            # support ring (annulus OD 240)
Z_SH0 = Z_RING1                                            # base head 416..428
Z_SH1 = Z_SH0 + 12.0 + H_SHELL                             # shell 428..728
Z_HEAD = Z_SH1 + 20.0                                      # top head 728..748
OD_JK, ID_JK = 234.0, 212.0                                # jacket envelope (layout choice)
Z_JK0, Z_JK1 = Z_SH0, Z_SH1 - 20.0                         # 416..708
Z_VENT = H                                                 # the riser flushes at the envelope top
MAT = "316L"                                               # duty section 3
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)                               # 8000, lib table
RHO_JK = materials.density("CS")                           # jacket envelope, carbon steel

assert L == 600.0 and W == 600.0 and H == 1200.0, "POLY_COND node envelope changed"
assert D == 200.0 and H_SHELL == 300.0, "POLY_COND node design changed"
assert Z_HEAD < H, "kettle must stay inside the envelope"


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
ring = (cq.Workplane("XY", origin=(CX, CY, Z_RING0)).circle(120.0)
        .circle(65.0).extrude(Z_RING1 - Z_RING0))
parts["support_ring"] = ring

# ---------------------------------------------------------------- kettle (316L) + jacket envelope
base_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
             .extrude(12.0))
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0 + 12.0)).circle(D / 2)
         .circle(R_IN).extrude(H_SHELL))
top_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
            .extrude(Z_HEAD - Z_SH1))
parts["kettle"] = base_head.union(shell).union(top_head)
jacket = (cq.Workplane("XY", origin=(CX, CY, Z_JK0)).circle(OD_JK / 2)
          .circle(ID_JK / 2).extrude(Z_JK1 - Z_JK0))
parts["jacket"] = jacket                                   # jacket_C 160 envelope

# ---------------------------------------------------------------- agitator (solids) + drive envelope
shaft = (cq.Workplane("XY", origin=(CX, CY, 460.0)).circle(10.0)
         .extrude(820.0 - 460.0))
imp = None
for zz in (480.0, 520.0):
    b = box(CX - 60.0, CY - 10.0, zz, 120.0, 20.0, 8.0)
    imp = b if imp is None else imp.union(b)
parts["agitator"] = shaft.union(imp)
parts["drive"] = box(CX - 70.0, CY - 70.0, Z_HEAD, 140.0, 140.0, 120.0)   # 0.18 kW envelope

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 45.0                       # face hardware reach (the CATCH_TANK idiom)

schedule = P["nozzles"]
layout_x = {"N1": CX}
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    od_s = dn.pipe_od(dnl)
    if face0 == "bottom":               # drain: boss under the base head, flush at z 0
        s = tube_dn(dnl, Z_SH0 + 5.0).translate((CX + 45.0, CY, 0.0))
        note = "drain boss under the base head, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, CX + 45.0
    elif face0 == "top":                # vent: riser on the top head, flush at the box top
        s = tube_dn(dnl, Z_VENT - Z_HEAD + 10.0).translate((CX, CY, Z_HEAD - 10.0))
        note = ("vent riser on the top head, flush at the envelope top; the "
                "schedule datum 800 is the placeholder (hold, WORK_ORDER W12)")
        z_d, x_d = Z_VENT, CX
    else:
        z_d = float(r["height_mm"])     # 160 fits the 1200 box; drawn as issued
        x_d = layout_x[tag]
        s = (tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)))
        note = ("schedule datum drawn as issued; open-bore tube flush at the "
                "envelope face (duty section 4: atmospheric joints are hose; the "
                "connecting line makes the joint at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (record, A-VES)
v_gross = round(math.pi * R_IN ** 2 * H_SHELL / 1e6, 4)    # L

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
    "kettle": parts["kettle"].val().Volume() * RHO / 1e9,
    "jacket": parts["jacket"].val().Volume() * RHO_JK / 1e9,
    "agitator": parts["agitator"].val().Volume() * RHO / 1e9,
    "drive": parts["drive"].val().Volume() * materials.density("PP") / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "reactor-class study minimum (AQS-DUTY-073; envelope state "
    "standby - the recipe waits on the digester organic assay, AQS-DES-POLY)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "the skid chain (plinth, stand, kettle, jacket envelope, "
    "agitator, drive envelope, drain and vent) fuses to one solid; the inlet "
    "face stub stays separate until the connecting line makes its joint",
    "kettle": {"od_mm": D, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_HEAD],
               "wall_basis": "study fab-page value (6 mm); the node books no "
               "thickness (WORK_ORDER W12)",
               "gross_volume_L": v_gross,
               "jacket": {"od_mm": OD_JK, "id_mm": ID_JK, "z_mm": [Z_JK0, Z_JK1],
                          "basis": "the node jacket_C 160 row; the jacket geometry "
                          "is the envelope annulus (layout choice, WORK_ORDER W12)"},
               "internals": {"source": "the node design agitator row "
                             "(agitator_kW 0.18)",
                             "basis": "shaft and two-blade impeller drawn as solids "
                             "into the purchased drive envelope (plan rule 6); "
                             "node internals row none, so the tracker records no "
                             "internal solid"}},
    "a_ves": {"gross_volume_L": v_gross,
              "basis": "reported for the record: the duty claims no holdup "
              "(DIGEST_TO_POLY stays 0 until the digester organic assay issues "
              "the recipe); no residence time is derived (A-VES)"},
    "standby": {"state": "installed standby (node envelope state)",
                "basis": "duty section 1 flows are 0; the model covers the "
                "installed geometry the node issues"},
    "material": {"class": "316L", "ca_mm": CA,
                 "basis": "duty section 3: 316L, Hastelloy option; 316L drawn, "
                 "the Hastelloy alternative is a named hold (WORK_ORDER W12); "
                 "CA 0 mm (AQS-STD-001 rule)"},
    "a_mach_named": {"purchased": "agitator drive 0.18 kW (node design row) drawn "
                     "as its envelope and interface, plan rule 6; the rating "
                     "reads the maker sheet at order"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: atmospheric joints are hose; the W4 110 percent rule "
    "draws no flange where no process pressure is stated); the schedule rating "
    "column (Class 150) is carried verbatim as text; datums draw as issued",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Kettle OD {D:g} x wall {T_WALL:g}, shell {H_SHELL:g} with heads, z "
          f"{Z_SH0:g}..{Z_HEAD:g}, on the support ring, 4 legs and the plinth", 1,
     "316L plate/pipe", round(mass["kettle"] + mass["plinth_stand"], 1), "make",
     "node design D/H (X-MFG-31 class, AQS-DUTY-073); wall the study fab-page "
     "value (hold, WORK_ORDER W12); duty section 3 316L, the Hastelloy option a "
     "named hold; CA 0 mm (AQS-STD-001)"],
    ["2", f"Jacket envelope OD {OD_JK:g} / ID {ID_JK:g}, z {Z_JK0:g}..{Z_JK1:g} "
          "(jacket_C 160, node design row)", 1, "carbon steel", mass["jacket"], "make",
     "the jacket service is the 160 C thermal envelope; geometry is the layout "
     "choice annulus (WORK_ORDER W12); the duty sheet carries no jacket pressure"],
    ["3", "Agitator: shaft and two-blade impeller (solids) into the drive "
          "envelope 0.18 kW (node design row)", 1, "316L shaft / PP drive envelope",
     round(mass["agitator"] + mass["drive"], 1), "make (shaft) / buy (drive)",
     "the node agitator_kW row; the drive is the purchased item per plan rule 6, "
     "rating reads the maker sheet at order"],
    ["4", "Nozzle set per docs-authority/nozzles/POLY_COND.csv: 3 atmospheric "
          "open-bore tube connections (inlet at the -Y face, drain under the base "
          "head, vent riser to the schedule datum 800)", len(schedule), "316L tube",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table"],
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
    "kettle": {"od_mm": D, "axis_xy_mm": [CX, CY], "z_mm": [Z_SH0, Z_HEAD]},
    "jacket_z_mm": [Z_JK0, Z_JK1],
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "condensation resin kettle (installed standby): 316L kettle D 200 "
               "x H 300, jacket_C 160 envelope, 0.18 kW agitator into the "
               "purchased drive envelope (node design block, AQS-DUTY-073)",
    "mat": "316L per duty section 3 (the Hastelloy option is a named hold)",
    "ca_mm": CA,
    "wall_mm": T_WALL, "wall_basis": "study fab-page value; the node books no "
                                     "thickness (WORK_ORDER W12)",
    "internals": "the agitator drawn as solids per the node design row; node "
                 "internals row none",
    "purchased": "agitator drive 0.18 kW - envelope and interface per plan rule 6",
})
p["layout"] = {
    "frame": "origin at the envelope corner; kettle axis at (300, 300); support "
             "ring z 408..416, shell 428..728, top head 728..748, jacket envelope "
             "416..708; drive envelope on the top head; vent riser to the schedule "
             "datum 800",
    "nozzle_spread": "N1 in flush at the -Y face at 160 (CATCH_TANK idiom: the "
                     "connecting line makes the joint at the face); drain boss "
                     "under the base head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "face hardware flush at the envelope faces; nothing protrudes",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
