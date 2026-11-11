"""ROOF_TANK manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 649 mm, y along 520 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 649 x 520 x 748 mm, node size_mm - the study registry box (params size_note
  records it as read back from the cad/stl registry); the duty sheet carries no size
  line and the AQS-MFG-001 study page a generic 1000 x 600 x 800: the node governs,
  the older figure is a named hold (WORK_ORDER W12). The build fills the node box.
- Body: rectangular welded-plate PVC-U tank, the HOPPER/FLOAT_SINK house idiom for
  plate tanks (the study fab page: "Shell 6 mm on metal, 10 mm on polymer. Shop
  weld."): floor and walls 10 mm inside the envelope with a 20 mm hold-down rim
  frame closing the top, so every face port's root reaches the wall at any position
  along the full 649 mm face chord (a round shell would leave the outer ports of
  the two chord-packed rows floating beyond the shell projection). Wall 10 mm is
  the study fab-page value; no node thickness is booked (hold, W12).
- Internals: dip pipe and stilling well (the AQS-MFG-001 study page
  `docs-authority/fab/ROOF_TANK.md`), drawn as concentric tubes exactly as
  CATCH_TANK; plus the PVDF air coil of duty section 3 ("IA-POT-01 is cooled to
  40 C by a passive PVDF air coil, AQS-STD-002 section 10") - a PVDF OD 16
  stacked-turn coil, 4 turns at a 300 mm mean diameter in the lower tank with two
  OD 16 stubs through the +X wall (study dimensions: no
  authority sizes the coil; the drawn area is reported, A-HX-style, and no duty
  figure exists to check it against). AQS-STD-002 section 10 Rev J records the
  IA-POT-01 trim superseded by X-RSZ-06; the duty sheet section 3 text stands as the
  wetted-basis authority (plan rule 5) and the conflict is a named hold (W12). The
  node internals row is none, so the tracker records no internal solid.
- Material: PVC-U drawn per duty section 3 ("PVC-U or HDPE, per AQS-STD-002 rule
  M1"); the hot draw at up to 85 C is cooled at the coil line, not the shell (duty
  section 3). The unresolved HDPE alternative is a named hold (W12). CA does not
  apply to the polymer.
- Nozzles: all 26 rows of docs-authority/nozzles/ROOF_TANK.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs flush at
  the envelope faces with roots through the plate walls, the schedule rating column
  (Class 150) carried verbatim as text, no flange (W4 110 % rule - no process
  pressure stated). N18 is a solids row drawn at DN15 and labeled bore not
  calculated. N9 drain boss on the tank floor, tip at its 50 datum; N10 vent on the
  +Y rim bar flush at the top head (its 800 datum predates the 748 box - hold,
  W12). The two 160/600 rows pack the full face chord (the plate walls reach the
  whole chord).
- A-VES: the liquor volume at the working level net of the well, dip pipe and coil
  is computed from the model and reported; the duty claims a two-minute holdup
  figure (0.2783 m3 at 200 t/d circulation) but no designed volume, so no residence
  time is derived from the model volume.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402

GN = graph_node.graph_node("ROOF_TANK")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 649 x 520 x 748, study registry box
REV = P["graph_revision"]

T_PLINTH = 20.0
T_WALL = 10.0                   # study fab-page polymer wall - no node booking (WORK_ORDER W12)
CX, CY = L / 2, W / 2                                       # tank centre
T_BASE = 20.0                                               # rim frame bar, envelope idiom
Z_FLOOR = T_PLINTH + T_WALL                                 # tank floor top, 30
Z_LIQ = H - T_BASE - 40.0                                   # working level below the rim
WELL_OD, WELL_T = 110.0, 5.0                                # stilling well (study)
DIP_OD, DIP_T = 60.0, 4.0                                   # dip pipe inside the well (study)
WELL_Z0, WELL_Z1 = Z_FLOOR - 5.0, H - T_BASE + 5.0          # laps the floor and the rim bars
DIP_Z0, DIP_Z1 = 100.0, H - T_BASE + 5.0                    # hung from the rim bars
COIL_TUBE = 16.0                                            # PVDF coil tube OD (study)
COIL_R, COIL_PITCH, COIL_H = 150.0, 60.0, 240.0             # mean radius, pitch, height (study)
COIL_Z0 = 80.0
CA = materials.ca_for("PVC-U")                              # 0.0, polymer: AQS-STD-001
RHO = materials.density("PVC_U")                            # 1400, lib table

# Envelope and design both come from the graph node; no hard-coded duplicate stays.


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth + tank body + rim
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
# welded-plate tank: floor and walls T_WALL inside the envelope, open top, closed
# by the 20 mm hold-down rim frame at the envelope top (HOPPER/FLOAT_SINK idiom)
tank = box(0, 0, T_PLINTH, L, W, H - T_PLINTH - T_BASE).cut(
    box(T_WALL, T_WALL, T_PLINTH, L - 2 * T_WALL, W - 2 * T_WALL, H))
parts["tank"] = tank
rim = (box(0, 0, H - T_BASE, L, T_BASE, T_BASE)
       .union(box(0, W - T_BASE, H - T_BASE, L, T_BASE, T_BASE))
       .union(box(0, T_BASE, H - T_BASE, T_BASE, W - 2 * T_BASE, T_BASE))
       .union(box(L - T_BASE, T_BASE, H - T_BASE, T_BASE, W - 2 * T_BASE, T_BASE)))
parts["rim_frame"] = rim

# ---------------------------------------------------------------- dip pipe + stilling well
well = (cq.Workplane("XY", origin=(CX, CY, WELL_Z0)).circle(WELL_OD / 2)
        .circle(WELL_OD / 2 - WELL_T).extrude(WELL_Z1 - WELL_Z0))
well = well.union(cq.Workplane("XY", origin=(CX, CY, WELL_Z1 - 5)).circle(WELL_OD / 2)
                  .extrude(5))                                               # well cap laps top head
parts["stilling_well"] = well
dip = (cq.Workplane("XY", origin=(CX, CY, DIP_Z0)).circle(DIP_OD / 2)
       .circle(DIP_OD / 2 - DIP_T).extrude(DIP_Z1 - DIP_Z0))
parts["dip_pipe"] = dip

# ---------------------------------------------------------------- PVDF air coil (duty section 3)
# built as a stacked-turn coil: four OD 16 tube turns (tori, 300 mm mean diameter,
# 60 mm turn pitch) joined by OD 16 risers at the +X side, with two OD 16 stubs
# through the shell wall at the bottom and top turns - a coil is hardware and its
# ends must penetrate the shell; the primitives union reliably where the swept
# helix does not
turns = 4
turn_z = [COIL_Z0 + i * COIL_PITCH for i in range(turns)]
coil = None
for z_t in turn_z:
    t = cq.Workplane(obj=cq.Solid.makeTorus(COIL_R, COIL_TUBE / 2,
                                            cq.Vector(CX, CY, z_t), cq.Vector(0, 0, 1)))
    coil = t if coil is None else coil.union(t)
for z_lo, z_hi in zip(turn_z, turn_z[1:]):
    r = (cq.Workplane("YZ", origin=(CX + COIL_R - COIL_TUBE / 2, CY - COIL_TUBE / 2,
                                    (z_lo + z_hi) / 2))
         .rect(COIL_TUBE, z_hi - z_lo).extrude(COIL_TUBE))
    coil = coil.union(r)
for z_t in (turn_z[0], turn_z[-1]):
    s = (cq.Workplane("YZ", origin=(CX + COIL_R - 10.0, CY - COIL_TUBE / 2, z_t))
         .rect(COIL_TUBE, COIL_TUBE).extrude((L - T_WALL / 2) - (CX + COIL_R - 10.0)))
    coil = coil.union(s)
parts["coil"] = coil
coil_dev_mm = turns * 2 * math.pi * COIL_R + (turns - 1) * COIL_PITCH
coil_area_m2 = coil_dev_mm / 1000.0 * math.pi * COIL_TUBE / 1000.0

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)


def od_of(r):
    return dn.pipe_od("DN15") if r["size"] == "solids" else dn.pipe_od(r["size"])


layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = CX - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    hw = "DN15" if dnl == "solids" else dnl
    od = dn.pipe_od(hw)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if dnl == "solids":
        s = nozzles.stub("DN15", 50.0)
        note = SOLIDS_NOTE
    else:
        s = nozzles.hose_barb(hose_id(hw), Hose[hw], root_od=od)
    if r["face"] == "bottom":                             # N9: boss on the base head
        s = nozzles.stub(hw, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 60.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N10: 800 datum predates the 748 box
        s = nozzles.hose_barb(hose_id(hw), Hose[hw], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 80.0, W - 15.0), (L, W, H))
        note = "vent on the +Y rim bar, flush at the 748 envelope top; schedule datum 800 predates the box - WORK_ORDER W12"
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm clamped to {round(h_d, 1)} mm "
                     "(barb radius rule) - WORK_ORDER W12")
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "solids" if dnl == "solids" else "hose", "dn": hw,
                  "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_shell_liq = ((L - 2 * T_WALL) * (W - 2 * T_WALL) * (Z_LIQ - Z_FLOOR)) / 1e9
v_well = math.pi * (WELL_OD / 2 - WELL_T) ** 2 * (Z_LIQ - WELL_Z0) / 1e9
v_dip = math.pi * (DIP_OD / 2 - DIP_T) ** 2 * max(Z_LIQ - DIP_Z0, 0.0) / 1e9
v_coil = math.pi * (COIL_TUBE / 2) ** 2 * coil_dev_mm / 1e9
v_liq = round(v_shell_liq - v_well - v_dip - v_coil, 4)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="ROOF_TANK")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / "roof_tank.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
assert len(solid.Solids()) == 1, f"assembly split into {len(solid.Solids())} solids"
solid.exportStl(str(out / "roof_tank.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "ROOF_TANK.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "roof_tank.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); the duty sheet carries no "
    "size line and the fab study page envelope predates the node (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_liq,
    "holdup_basis": "reported, no residence derived: the duty section 2 two-minute "
    "figure (0.2783 m3 at 200 t/d circulation) is not a designed volume (A-VES)",
    "tank": {"wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall (10 mm); "
             "no thickness booked on the node (WORK_ORDER W12)",
             "body": "rectangular welded-plate tank, floor and walls inside the "
             "envelope, rim frame closes the top (HOPPER/FLOAT_SINK idiom)",
             "internals": {"source": "docs-authority/fab/ROOF_TANK.md (AQS-MFG-001 "
                           "study page): dip pipe, stilling well; duty section 3: "
                           "passive PVDF air coil",
                           "stilling_well": {"od_mm": WELL_OD, "wall_mm": WELL_T,
                                             "z_mm": [WELL_Z0, WELL_Z1]},
                           "dip_pipe": {"od_mm": DIP_OD, "wall_mm": DIP_T,
                                        "z_mm": [DIP_Z0, DIP_Z1]},
                           "coil": {"tube_od_mm": COIL_TUBE, "mean_radius_mm": COIL_R,
                                    "turns": 4, "z_mm": [turn_z[0] - COIL_TUBE / 2, turn_z[-1] + COIL_TUBE / 2],
                                    "area_drawn_m2": round(coil_area_m2, 4),
                                    "area_basis": "drawn area, NOT a calculated duty "
                                    "area: no authority sizes the coil (duty section 3; "
                                    "AQS-STD-002 section 10 Rev J records the trim "
                                    "superseded - conflict held, WORK_ORDER W12)"},
                           "basis": "internals named by the issued study page and duty "
                           "section 3; dimensions study values (WORK_ORDER W12); node "
                           "internals row none, so the tracker records no internal solid"}},
    "material": {"class": "PVC-U", "ca_mm": CA,
                 "basis": "duty section 3: PVC-U or HDPE per AQS-STD-002 rule M1; "
                 "PVC-U drawn, the HDPE alternative is a named hold (WORK_ORDER W12); "
                 "corrosion allowance does not apply to the polymer"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces with roots "
    "through the plate walls (every position along the face chord reaches the wall); "
    "solids rows DN15 labeled bore not calculated; the two 160/600 rows pack the "
    "full face chord; the schedule rating column (Class 150) is carried verbatim as "
    "text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Rectangular welded-plate tank, floor and walls {T_WALL:g} mm, "
          f"{L:g} x {W:g} x {H - T_PLINTH - T_BASE:g}, with a {T_BASE:g} mm top "
          "hold-down rim frame, on the plinth", 1, "PVC-U plate",
     round(mass["tank"] + mass["rim_frame"] + mass["plinth"], 1), "make",
     "study registry envelope (node size_mm); wall the study fab-page polymer value; "
     "CA 0 mm (AQS-STD-001 polymer rule); duty section 3 PVC-U-or-HDPE conditional "
     "hold (WORK_ORDER W12)"],
    ["2", f"Stilling well, OD {WELL_OD:g} x wall {WELL_T:g}, z {WELL_Z0:g}..{WELL_Z1:g}",
     1, "PVC-U pipe", mass["stilling_well"], "make",
     "internals issued by the AQS-MFG-001 study page (fab/ROOF_TANK.md); dimensions "
     "study values (WORK_ORDER W12); node internals row none"],
    ["3", f"Dip pipe inside the well, OD {DIP_OD:g} x wall {DIP_T:g}, "
          f"z {DIP_Z0:g}..{DIP_Z1:g}", 1, "PVC-U pipe", mass["dip_pipe"], "make",
     "same study-page basis; feed enters down the dip pipe, the well damps the jet "
     "for the level instruments (duty section 5)"],
    ["4", f"PVDF air coil, tube OD {COIL_TUBE:g}, 4 turns at a "
          f"{2 * COIL_R:g} mm mean diameter, {coil_area_m2:.4f} m2 drawn",
     1, "PVDF", round(mass["coil"] * (1780.0 / RHO), 1), "make",
     "duty section 3 (passive PVDF air coil, AQS-STD-002 section 10); area reported "
     "as drawn - no authority sizes the coil and section 10 Rev J records the trim "
     "superseded (conflict held, WORK_ORDER W12); PVDF density 1780 (lib table)"],
    ["5", "Nozzle set per docs-authority/nozzles/ROOF_TANK.csv: 23 hose barbs "
          "(DN15/DN25/DN50), 1 solids port at DN15 (bore not calculated), 1 drain "
          "boss, 1 vent at the top head", len(schedule), "PVC-U", mass["nozzles"],
     "make", "schedule tags/faces/heights verbatim; atmospheric hose per duty "
     "section 4; barb profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("PVC-U", joint="polymer"), 4,
     "plinth to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note); the duty sheet carries no size "
             "line and the fab study page envelope predates the node (WORK_ORDER W12)",
    "tank_body_mm": [L, W, H - T_PLINTH - T_BASE],
}
p["design"] = {
    "service": "roof water tank, atmospheric; hot draw cooled at the coil line "
               "(duty sections 2, 3 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall", "ca_mm": CA,
    "internals": "dip pipe + stilling well (fab study page) + PVDF air coil (duty "
                 "section 3); dims study",
}
p["layout"] = {
    "frame": "origin at the envelope corner; plate walls inside the envelope, rim "
             "frame closes the top; tank centre x 324.5, y 260, z up",
    "nozzle_spread": "the schedule gives face and height only; the two 160/600 rows "
                     "pack the full face chord (outer barbs near-tangent, hold); "
                     "per-tag positions in check.nozzles_drawn",
    "vent_drain": "N10 vent flush at the top head (the 800 datum predates the box); "
                  "N9 drain boss on the base head, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
