"""MEOH_FERM manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the node
design block of the graph (the construction figures). Rebuilds every solid.

Placement frame: x along 425 mm, y along 425 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 425 x 425 x 600 mm, node size_mm (set by flow_graph/param/reactor_design.py,
  X-MFG-31). The duty section 2 prose still names "Envelope 2200 x 900 x 1400 mm" -
  the node governs and the older figure is named (holds, W12). The build fills the
  node box (vent riser to the top).
- Vessel per the node design block: D 125, H 100, wall 4.0 mm, on a stand with base
  head, top head, and the 50 mm PIR insulation the node material row books (insulation
  envelope OD 225, AQS-DUTY-062 class). Wetted alloy: PVC-U per duty section 3
  (AQS-STD-002 rules M1 and M2, no metal wetted part); the node design material row
  "HDPE (PE100)" predates the duty selection and is superseded for the wetted parts
  (hold, W12). CA does not apply to the polymer.
- Agitation per the node: the mixer row names a daily recirculation pump - drawn as
  its purchased envelope (plan rule 6) with a DN15 recirculation loop to the vessel.
  No top-entry agitator is named on the node, so none is drawn (hold, W12). The
  heater mat (0.74 W, node heat_W) is the second purchased envelope, under the base.
- Nozzles: all rows of docs-authority/nozzles/MEOH_FERM.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections flush at the envelope
  faces (duty section 4: hose, atmospheric; the connecting line makes the joint at
  the face, the CATCH_TANK idiom - the shell stands off the faces). The 160 inlet
  draws as issued; the 600 outlet datums clamp to 570.7 (the od + 8 rule - hold,
  W12); row N6 carries the line-list classification `solids` (non-piped transfer) in
  its size column: drawn at DN15, bore not calculated, per plan W4, and labeled.
  The drain passes to the envelope bottom (50 datum); the vent riser stands on the
  top head inside the insulation bore and flushes at the envelope top (the 800 datum
  is the schedule placeholder).
- A-VES: the duty section 2 working volume is an existing holdup basis (48 h at the
  S78 feed: V = 0.0007 m3) - the model working level is set by it and reported; no
  new residence-time claim.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 425 x 425 x 600
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

T_PLINTH = 20.0
CX, CY = L / 2, W / 2                                      # vessel axis
D = float(DS.get("D_mm", 125.0))                           # shell OD
T_WALL = float(DS.get("wall_mm", 4.0))                     # node wall
R_IN = D / 2 - T_WALL
H_SHELL = float(DS.get("H_mm", 100.0))                     # shell height
Z_RING0, Z_RING1 = 212.0, 220.0                            # support ring (annulus OD 180)
Z_PAD0, Z_PAD1 = Z_RING1, Z_RING1 + 10.0                   # heater mat envelope (purchased)
Z_SH0 = Z_PAD1                                             # shell base 230
Z_SH1 = Z_SH0 + H_SHELL                                    # 330... node H_mm 100
Z_HEAD = Z_SH1 + 20.0                                      # top head 350 (base head 230..240)
Z_INS0, Z_INS1 = Z_RING0 - 4.0, Z_HEAD + 18.0              # PIR envelope 208..368
OD_INS = D + 2 * 50.0                                      # node: 50 mm PIR
T_VENT = Z_HEAD - 10.0                                     # vent riser seat in the top head
MAT = "PVC-U"                                              # duty section 3 (governs wetted)
CA = materials.ca_for(MAT)                                 # 0.0, polymer: AQS-STD-001
RHO = materials.density("PVC_U")                           # 1400, lib table
RHO_PIR = 35.0                                             # PIR board, study bulk value
V_WORK = float(DS.get("V_work_L", 0.72))                   # node / duty section 2 basis

assert L == 425.0 and W == 425.0 and H == 600.0, "MEOH_FERM node envelope changed"
assert D == 125.0 and H_SHELL == 100.0 and T_WALL == 4.0, "MEOH_FERM node design changed"
assert Z_HEAD < Z_INS1 < H, "vessel must stay inside the envelope"


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
ring = (cq.Workplane("XY", origin=(CX, CY, Z_RING0)).circle(90.0)
        .circle(30.0).extrude(Z_RING1 - Z_RING0))
parts["support_ring"] = ring

# ---------------------------------------------------------------- purchased envelopes (rule 6)
pad = (cq.Workplane("XY", origin=(CX, CY, Z_PAD0)).circle(70.0)
       .circle(31.0).extrude(Z_PAD1 - Z_PAD0))
parts["heater_pad"] = pad                                  # 0.74 W mat envelope
pump = box(25.0, 210.0, T_PLINTH, 90.0, 90.0, 120.0)
parts["recirc_pump"] = pump                                # daily recirculation pump envelope

# ---------------------------------------------------------------- vessel (PVC-U) + PIR envelope
base_head = (cq.Workplane("XY", origin=(CX, CY, Z_PAD1 - 2.0)).circle(D / 2)
             .extrude(Z_SH0 - Z_PAD1 + 2.0))
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
         .circle(R_IN).extrude(H_SHELL))
top_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
            .extrude(Z_HEAD - Z_SH1))
parts["shell"] = base_head.union(shell).union(top_head)
ins = (cq.Workplane("XY", origin=(CX, CY, Z_INS0)).circle(OD_INS / 2)
       .circle(D / 2 + 4.0).extrude(Z_INS1 - Z_INS0))
ins = ins.union(cq.Workplane("XY", origin=(CX, CY, Z_INS1)).circle(OD_INS / 2)
                .circle(6.0).extrude(8.0))                 # top cap with a vent gap
parts["insulation"] = ins

# ---------------------------------------------------------------- recirculation loop (DN15, wetted)
# inject: pump top -> riser -> horizontal at z 300 -> down into the top head
# return: base-head tap -> horizontal at z 226 -> drop into the pump top
def seg_x(y, z, x0, x1):
    x0, x1 = min(x0, x1), max(x0, x1)
    return (cq.Workplane("YZ", origin=(x0, y, z))
            .circle(21.3 / 2).circle(21.3 / 2 - 2.77).extrude(x1 - x0))


def seg_y(x, z, y0, y1):
    y0, y1 = min(y0, y1), max(y0, y1)
    return (cq.Workplane("XZ", origin=(x, y1, z))
            .circle(21.3 / 2).circle(21.3 / 2 - 2.77).extrude(y1 - y0))


loop = seg_x(230.0, 300.0, 60.0, CX - 40.0)                # inject horizontal
loop = loop.union(seg_y(CX - 40.0, 300.0, CY - 45.0, 230.0))
loop = loop.union(tube_dn("DN15", 46.0).translate((CX - 40.0, CY - 45.0, 300.0)))   # drop to head
loop = loop.union(tube_dn("DN15", 170.0).translate((60.0, 230.0, 130.0)))           # pump riser
loop = loop.union(tube_dn("DN15", 8.0).translate((CX - 40.0, CY + 45.0, 224.0)))    # base tap lap
loop = loop.union(seg_x(CY + 45.0, 226.0, 90.0, CX - 40.0))                          # return horizontal
loop = loop.union(tube_dn("DN15", 98.0).translate((90.0, CY + 45.0, 128.0)))        # drop to pump
parts["recirc_loop"] = loop

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 45.0                       # face hardware reach (the CATCH_TANK idiom)
CLAMP_MARGIN = 0.7

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
    if size0 == "cable":                                  # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": size0, "face": face0,
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
    is_dn = str(size0).startswith("DN")
    dnl = size0 if is_dn else "DN15"   # non-piped rows drawn DN15, bore not calculated (plan W4)
    od_s = dn.pipe_od(dnl)
    if face0 == "bottom":               # drain: boss under the base, flush at the envelope bottom
        s = tube_dn(dnl, Z_SH0 + 5.0).translate((CX + 45.0, CY, 0.0))
        note = "drain boss under the base head, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, CX + 45.0
    elif face0 == "top":                # vent: riser on the top head inside the insulation bore
        s = tube_dn(dnl, H - T_VENT + 5.0).translate((CX, CY, T_VENT - 5.0))
        note = ("vent riser on the top head, flush at the envelope top; schedule "
                "datum 800 is the placeholder (hold, WORK_ORDER W12)")
        z_d, x_d = H, CX
    else:
        h = float(r["height_mm"])
        hi = H - od_s - 8.0
        z_d, clamp = (round(min(max(h, od_s / 2 + CLAMP_MARGIN), hi), 1),
                      h > hi)
        if clamp:
            note = (f"schedule datum {h:g} mm predates the box; clamped to {z_d:g} mm "
                    "(the od + 8 rule - hold, WORK_ORDER W12)")
        else:
            note = "schedule datum drawn as issued"
        x_d = layout_x[tag]
        s = (tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)) if face0 == "inlet" else
             tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x_d, W, z_d)))
        bore_txt = (f"{dnl} open-bore tube" if is_dn else
                    "non-piped solids transfer (line-list classification): drawn DN15, "
                    "bore not calculated (plan W4)")
        note += (f"; {bore_txt} flush at the envelope face (duty section 4: "
                 "atmospheric joints are hose; the connecting line makes the joint "
                 "at the face, the CATCH_TANK idiom)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": size0, "face": face0,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (reported, A-VES)
area = math.pi * R_IN ** 2                                 # mm2
z_level = round(Z_SH0 + V_WORK * 1e6 / area, 1)
assert z_level < Z_SH1, (z_level, Z_SH1)

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
    "plinth": parts["plinth"].val().Volume() * materials.density("CS") / 1e9,
    "stand": (parts["legs"].val().Volume() + parts["support_ring"].val().Volume())
             * materials.density("CS") / 1e9,
    "shell": parts["shell"].val().Volume() * RHO / 1e9,
    "insulation": parts["insulation"].val().Volume() * RHO_PIR / 1e9,
    "purchased": (parts["heater_pad"].val().Volume() * 1500.0
                  + parts["recirc_pump"].val().Volume() * materials.density("PP")) / 1e9,
    "recirc_loop": parts["recirc_loop"].val().Volume() * RHO / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "L x W x H mm, set by flow_graph/param/reactor_design.py "
    "(X-MFG-31); the duty section 2 prose line 'Envelope 2200 x 900 x 1400' "
    "predates it (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "the skid chain (plinth, stand, vessel, insulation envelope, "
    "pump envelope, recirculation loop, drain and vent) fuses to one solid; the "
    "four face-stub connections (N1, N2, N3, N6) are the CATCH_TANK-idiom face "
    "hardware and stay separate until the connecting lines make their joints; "
    "every solid closed and manifold",
    "vessel": {"od_mm": D, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_HEAD],
               "insulation": {"od_mm": OD_INS, "thickness_mm": 50.0,
                              "class": "PIR (node material row), 35 kg/m3 study bulk"},
               "working_level_mm": z_level,
               "working_volume_m3": round(V_WORK / 1000.0, 5),
               "holdup_basis": "duty section 2: the 48 h working volume V = 0.0007 m3 "
               "is an existing holdup basis - the model level is set by it and "
               "reported (A-VES); no new residence-time claim",
               "internals": {"source": "none: the node internals row is none; the "
                             "node mixer row names the daily recirculation pump",
                             "basis": "no top-entry agitator named on the node - "
                             "none drawn (WORK_ORDER W12); agitation is by the "
                             "recirculation loop"}},
    "a_mach_named": {"purchased": "daily recirculation pump (node mixer row) and the "
                     "0.74 W heater mat (node heat_W) drawn as envelopes and "
                     "interfaces per plan rule 6; ratings read the maker sheets at "
                     "order"},
    "material": {"class": "PVC-U", "ca_mm": CA,
                 "basis": "duty section 3: PVC-U wetted per AQS-STD-002 rules M1 "
                 "and M2, no metal wetted part; above 60 C the thermoplastic is "
                 "CPVC - the node T_C 35 sits inside the class; the node design "
                 "HDPE row predates the duty selection and is superseded for the "
                 "wetted parts (hold, WORK_ORDER W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: atmospheric joints are hose; the W4 110 percent rule "
    "draws no flange where no process pressure is stated); the schedule rating "
    "column (Class 150) is carried verbatim as text; clamped datums named in "
    "nozzles_drawn; the N6 solids row drawn DN15, bore not calculated (plan W4)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Vessel OD {D:g} x wall {T_WALL:g} x {H_SHELL:g} shell, heads, on the "
          "stand (support ring + 4 legs) on the plinth", 1, "PVC-U plate/pipe",
     round(mass["shell"] + mass["stand"] + mass["plinth"], 1), "make",
     "node design D/H/wall (X-MFG-31); wetted alloy PVC-U per duty section 3 (the "
     "node HDPE row superseded - hold, WORK_ORDER W12); CA 0 mm (AQS-STD-001 "
     "polymer rule)"],
    ["2", f"PIR insulation envelope OD {OD_INS:g} x 50 wall class, z "
          f"{Z_INS0:g}..{Z_INS1:g}, top cap", 1, "PIR (35 kg/m3 study)",
     mass["insulation"], "make",
     "node material row: 50 mm PIR; the duty section 5 instruments and the heat "
     "duty (0.74 W) sit under it"],
    ["3", "Daily recirculation pump (node mixer row) and 0.74 W heater mat - "
          "envelopes and interfaces", 2, "PP envelope / silicone mat", mass["purchased"],
     "buy", "purchased items per plan rule 6; ratings read the maker sheets at order"],
    ["4", "Recirculation loop DN15 PVC-U: pump to top head and shell base to pump",
     1, "PVC-U tube", mass["recirc_loop"], "make",
     "the node agitation basis (daily recirculation); no top-entry agitator named "
     "on the node - none drawn (WORK_ORDER W12)"],
    ["5", "Nozzle set per docs-authority/nozzles/MEOH_FERM.csv: 6 atmospheric "
          "open-bore tube connections at the envelope faces (drain under the base, "
          "vent riser on the top head; N6 solids row drawn DN15, bore not "
          "calculated)", len(schedule), "PVC-U", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table; "
     "the 600 datums clamped to 570.7 (hold, WORK_ORDER W12); the cable schedule "
     "row is carried, never drawn"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 4,
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
    "insulation_z_mm": [Z_INS0, Z_INS1],
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "methanol fermenter (S77/S78): PVC-U vessel D 125 x H 100 (node "
               "design), 50 mm PIR, recirculation-pump agitation (node mixer row)",
    "mat": "PVC-U wetted per AQS-STD-002 rules M1 and M2 (duty section 3); the "
           "node HDPE row is superseded for the wetted parts (WORK_ORDER W12)",
    "ca_mm": CA,
    "internals": "none drawn (node internals row none; the node mixer row names "
                 "the daily recirculation pump - drawn as its envelope, rule 6)",
    "purchased": "recirculation pump and 0.74 W heater mat - envelopes and "
                 "interfaces per plan rule 6",
})
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at (212.5, 212.5); "
             "support ring z 212..220, heater pad 220..230, shell 230..330, top "
             "head 330..350, PIR envelope 208..368; pump envelope at the front-left "
             "floor corner; vent riser to the box top",
    "nozzle_spread": "side rows flush at the envelope faces (the CATCH_TANK idiom: "
                     "the connecting line makes the joint at the face); N1 in on -Y "
                     "at 160; N2/N3/N6 out on +Y (600 datums clamped to 570.7); "
                     "drain under the base at x +45; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "face hardware flush at the envelope faces; nothing protrudes",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
