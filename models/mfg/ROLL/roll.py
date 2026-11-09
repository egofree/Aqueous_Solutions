"""ROLL manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-ROLL-10 M3).

Graph revision AC. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only.
Two-high bench rolling mill: OD 300 x 640 mm rolls in a screw-adjust stand, entry
and exit rollers, on a common base (AQS-DUTY-072). Layout choices named in
params.json (layout_note); heights, bores and ratings per
docs-authority/nozzles/ROLL.csv (task-04 schedule). No measured rate is claimed.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
import sys
sys.path.insert(0, str(HERE.parent))              # models/mfg: lib
from lib import graph_node  # noqa: E402
GN = graph_node.graph_node("ROLL")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
A = P["assumptions"]
D = GN.design
L, W, H = P["size_mm"]
DN15, W15 = A["DN15_OD_mm"] / 2, A["DN15_wall_mm"]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

def _bad_edges(path):
    """Edges of the exported ASCII STL used by other than two triangles (the tracker's
    manifold rule, so check.json reports the exported file, not an intention)."""
    import collections
    tri = []
    vs = []
    for ln in open(path):
        f = ln.split()
        if f and f[0] == "vertex":
            vs.append((float(f[1]), float(f[2]), float(f[3])))
            if len(vs) == 3:
                tri.append(vs)
                vs = []
    use = collections.Counter()
    for t in tri:
        for i in range(3):
            a, b = t[i], t[(i + 1) % 3]
            use[(min(a, b), max(a, b))] += 1
    return sum(1 for c in use.values() if c != 2)

parts = {}
CY = 400.0                                            # roll centreline
RD = D["rolls_D_mm"] / 2                              # 150
ROLL_Z = 950.0                                        # bottom roll centre (pass line ~1000)

# ---------------- base + stand housings ----------------
base = box(0, 0, 0, L, W, 60)
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60)):
    base = base.union(box(px, py, 60, 60, 60, 300))
parts["base"] = base
stand = box(560, CY - 120, 60, 380, 240, 1150)        # the mill stand window block
stand = stand.cut(box(600, -1.0, 880, 300, W + 2.0, 260))   # full-width roll window slot
parts["stand"] = stand

# ---------------- two-high rolls + chocks ----------------
parts["bottom_roll"] = rod(RD, (560, 0.0, ROLL_Z - RD), "Y", W)   # roll axis across the full width
parts["top_roll"] = rod(RD, (560, 0.0, ROLL_Z + RD + 10), "Y", W)
chocks = None
for zz in (ROLL_Z - RD, ROLL_Z + RD + 10):
    q = box(570, 60.0, zz - 60, 390, 140.0, 120)   # bearing caps crossing the stand face (+X): fuse
    chocks = q if chocks is None else chocks.union(q)
parts["roll_chocks"] = chocks
parts["screw_down"] = rod(25.0, (650.0, CY, 1150.0), "Z", 350)   # z 1150..1500: overlaps the stand top band, reaches the frame datum

# ---------------- entry / exit roller tables ----------------
table = None
for xx in range(120, 520, 100):
    for zz in (ROLL_Z - 20.0,):
        q = rod(40.0, (xx, 50.0, zz), "Y", 700)   # across the width, inside the frame
        table = q if table is None else table.union(q)
# exit rollers start 10 mm clear of the stand face (x 940): a roller that kissed the
# face along a tangent line left the export non-manifold at the contact line
for xx in range(990, 1440, 100):
    q = rod(40.0, (xx, 50.0, ROLL_Z - 20.0), "Y", 700)
    table = table.union(q)
# roller pedestals: one column under each roller end, tied to the base
ped = None
for xx in list(range(120, 520, 100)) + list(range(990, 1440, 100)):
    for y0 in (30.0, 730.0):
        q = box(xx - 15.0, y0, 60.0, 30.0, 40.0, 835)
        ped = q if ped is None else ped.union(q)
table = table.union(ped)
parts["table_rollers"] = table

# ---------------- nozzle hardware ----------------
parts["billet_stop"] = box(20.0, CY - 60.0, 60.0, 30.0, 120.0, 950)   # N1/N3 entry guide, full height to the base
parts["sheet_guide"] = box(1440.0, CY - 60.0, 60.0, 60.0, 120.0, 950)  # N2 sheet guide, full height to the base
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)                  # N4
parts["vent_stub"] = tube(DN15, DN15 - W15, (750.0, 400.0, 55.0), "Z", 760)     # N5 up to z 800, through the base

# ---------------- process inventory solids (not BOM parts) -----------------------
inv = {"strip_inventory": box(0.0, CY - 40.0, ROLL_Z - 12.0, 700.0, 80.0, 24.0)}   # strip on the pass line

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="ROLL")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "roll.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
body = body.clean()                                   # drop boolean slivers: the audit gate reads this mesh
cap_solid = body.val()
cap_solid.exportStl(str(out / "roll.stl"), tolerance=0.3, angularTolerance=0.3, ascii=True)

EXTERNAL = ("billet_stop", "sheet_guide")             # schedule hardware at the frame faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "roll_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "ROLL.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["base"].val(), parts["stand"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"base": 7.85e-6, "stand": 7.85e-6, "bottom_roll": 7.85e-6, "top_roll": 7.85e-6,
       "roll_chocks": 7.85e-6, "screw_down": 7.85e-6, "table_rollers": 7.85e-6,
       "billet_stop": 7.85e-6, "sheet_guide": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
# ---------------- acceptance record: nozzles_drawn -------------------------------
# Every row of docs-authority/nozzles/ROLL.csv, recorded from the placement this
# build draws.
sched_rows = {}
with open(HERE.parents[2] / "docs-authority" / "nozzles" / "ROLL.csv") as f:
    for _r in csv.DictReader(f):
        sched_rows[_r["tag"]] = _r
PLACE = {
    "N1": {"style": "solids", "face": "-X", "part": "billet_stop", "drawn_height_mm": 160.0,
           "note": "billet-to-roll entry guide at the -X roll side (x 20..50, full height "
                   "z 60..1010, so it covers the z 160 inlet datum); solids row, bore not "
                   "calculated"},
    "N2": {"style": "solids", "face": "+X", "part": "sheet_guide", "drawn_height_mm": 600.0,
           "note": "plate/sheet guide flush at the +X face (x 1440..1500, full height "
                   "z 60..1010, so it covers the z 600 outlet datum); solids row, bore not "
                   "calculated"},
    "N3": {"style": "solids", "face": "-X", "part": "billet_stop", "drawn_height_mm": 160.0,
           "note": "continuous billet/slab entry, the same -X entry guide as N1 (x 20..50, "
                   "z 60..1010); solids row, bore not calculated"},
    "N4": {"style": "drain", "face": "bottom", "part": "drain_well", "drawn_height_mm": 0.0,
           "note": "drain well flush at the envelope bottom (z 0), sump face at the 50 datum"},
    "N5": {"style": "vent", "face": "top", "part": "vent_stub", "drawn_height_mm": 800.0,
           "note": "vent DN15 riser at (x 750, y 400) through the base, z 55..815 at the 800 "
                   "datum"},
}
drawn = {}
for tag, rec in PLACE.items():
    row = sched_rows[tag]
    rec = dict(rec)
    rec["dn"] = row["size"] if rec["style"] == "carried" else "DN15"
    rec["height_mm"] = float(row["height_mm"])
    rec["schedule_rating"] = row["rating"]
    rec["service"] = row["service"]
    drawn[tag] = rec
assert set(drawn) == set(sched_rows), sorted(set(drawn) ^ set(sched_rows))

report = {
    "nozzles_drawn": drawn,
    "frame_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    "inside_size_mm_shell": inside_shell,
    "connection_overhang_mm": overhang,
    "overhang_allowance_mm": slack,
    "overhang_ok": overhang_ok,
    "cad_stl_scope": "in-envelope build solid, metres (EXTERNAL parts excluded: " + ", ".join(EXTERNAL) + ")",
    "external_parts": list(EXTERNAL),
    "cap_solids": len(cap_solid.Solids()),
    "all_parts_valid": valid,
    "part_mass_kg": mass,
    "non_manifold_edges_ascii": _bad_edges(str(out / "roll.stl")),
    "cadquery": "2.8.0",
}
rows = [
    ["1", f"Base 1500 x 800 x 60 with four posts; table-deck rollers", 1, "carbon steel",
     round(mass["base"] + mass["table_rollers"], 1), "make", "WORK_ORDER step 1"],
    ["2", f"Two-high stand: window 300 x 260 x 260, housings to z 1210", 1, "carbon steel",
     mass["stand"], "make", "AQS-DUTY-072 two-high bench class"],
    ["3", f"Rolls OD {D['rolls_D_mm']} x {D['roll_L_mm']} (bottom fixed, top screw-adjust)", 2,
     "cast steel (roll class)", round(mass["bottom_roll"] + mass["top_roll"], 1), "make",
     f"design rolls row; {D['rolled_kg_d']} kg/d rolled"],
    ["4", "Roll chocks 380 x 140 x 120 in the stand window", 4, "carbon steel", mass["roll_chocks"], "make",
     "WO step 2"],
    ["5", f"Screw-down OD 50 through the stand top", 1, "carbon steel", mass["screw_down"], "make",
     "gap adjustment per WO step 3"],
    ["6", "N1/N3 entry guide -X at the pass line; N2 sheet guide +X", 2, "carbon steel",
     round(mass["billet_stop"] + mass["sheet_guide"], 1), "make", "task-04 schedule N1/N2/N3"],
    ["7", "N4 drain well + N5 vent stub", 2, "carbon steel", round(mass["drain_well"] + mass["vent_stub"], 1),
     "make", "task-04 schedule N4/N5"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
fast = ('item,size,grade,qty,location,basis\n'
        '1,M12 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,8,chock caps,study\n'
        '2,M12 anchor,ISO 898-1 8.8,4,base to slab,study\n')
(HERE / "fasteners.csv").write_text(fast)
wo = (f"# Work order ROLL\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - two-high bench mill.\n\n"
      f"1. Fabricate the base and table rollers; set on anchors.\n"
      f"2. Erect the stand; seat the roll chocks and both rolls; fit the screw-down.\n"
      f"3. Set the roll gap at the pass line z {ROLL_Z + RD:.0f}; fit the entry guide and sheet guide.\n"
      f"4. Fit the N4 drain and N5 vent.\n"
      f"5. Test: roll gap parallelism, then a trial pass of the CONT_CAST billet.\n"
      f"6. Inspect against models/mfg/ROLL/export/roll.step; record dimensions on the traveller.\n")
(HERE / "WORK_ORDER.md").write_text(wo)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
