"""STOCK_OUT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-STOCK_OUT-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Three-tier bar/plate/ingot staging rack (AQS-DUTY-072). The seven stock-inlet rows
of the task-04 schedule land on the tier decks at z 160 (registered layout choice);
formed product issues at the +X face at z 600. No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
D = P["design"]
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

parts = {}
TIERS = [160.0, 600.0, 1000.0]                        # deck top faces (N-inlet datum 160, issue datum 600)

# ---------------- uprights + tier frames ----------------
rack = None
for (px, py) in ((0, 0), (L - 60, 0), (0, W - 60), (L - 60, W - 60), (L / 2 - 30, 0), (L / 2 - 30, W - 60)):
    q = box(px, py, 0, 60, 60, H - 20)
    rack = q if rack is None else rack.union(q)
parts["uprights"] = rack
decks = None
for zt in TIERS:
    q = box(0, 0, zt - 30, L, W, 30)
    decks = q if decks is None else decks.union(q)
parts["tier_decks"] = decks
# ---------------- back guard + edge stops ----------------
parts["back_guard"] = box(0, W - 20, 100, L, 20, H - 140)
stops = None
for zt in TIERS:
    q = box(L - 90, 20, zt + 30, 20, W - 40, 120)     # issue-face stops at +X
    stops = q if stops is None else stops.union(q)
parts["edge_stops"] = stops
# ---------------- issue sill + outlet hardware ----------------
parts["issue_sill"] = box(L - 10.0, 200.0, TIERS[1] - 20.0, 10.0, 400.0, 160.0)
parts["drain_well"] = tube(30.5, DN15, (400, 400, 0), "Z", 50)                      # N9 nominal floor drain
parts["vent_stub"] = tube(DN15, DN15 - W15, (600.0, 400.0, H - 25.0), "Z", 25)      # N10 top at the envelope datum z 1500

# ---------------- process inventory solids (not BOM parts) -----------------------
inv = {}
stock = None
for zt, dx in ((TIERS[0], 900.0), (TIERS[1], 700.0), (TIERS[2], 500.0)):
    q = box(60.0, 60.0, zt, dx, W - 120.0, 90.0)
    stock = q if stock is None else stock.union(q)
inv["stock_inventory"] = stock

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="STOCK_OUT")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "stock_out.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "stock_out.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("issue_sill",)                            # the issue-face sill crosses the +X envelope face
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "stock_out_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "STOCK_OUT.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["uprights"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"uprights": 7.85e-6, "tier_decks": 7.85e-6, "back_guard": 7.85e-6, "edge_stops": 7.85e-6,
       "issue_sill": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
report = {
    "rack_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    "inside_size_mm_shell": inside_shell,
    "connection_overhang_mm": overhang,
    "overhang_allowance_mm": slack,
    "overhang_ok": overhang_ok,
    "cad_stl_scope": "in-envelope build solid, metres (EXTERNAL parts excluded: " + ", ".join(EXTERNAL) + ")",
    "external_parts": list(EXTERNAL),
    "cap_solids": len(cap_solid.Solids()),
    "all_parts_valid": valid,
    "part_mass_kg": mass,
    "cadquery": "2.8.0",
}
rows = [
    ["1", f"Rack uprights, 6 x 60 x 60 x {H - 20:.0f} mm", 6, "carbon steel", mass["uprights"], "make",
     "WORK_ORDER step 1; three-tier staging rack (AQS-DUTY-072)"],
    ["2", f"Tier decks at z {'/'.join(f'{t:.0f}' for t in TIERS)}, {L} x {W} x 30 each", 3, "carbon steel",
     mass["tier_decks"], "make", "the seven stock-inlet rows land on the tier decks (task-04 schedule N1..N7)"],
    ["3", "Back guard plate", 1, "carbon steel", mass["back_guard"], "make", "WO step 2"],
    ["4", "Issue-face edge stops at +X", 3, "carbon steel", mass["edge_stops"], "make", "task-04 schedule N8"],
    ["5", "Issue sill +X z 600", 1, "carbon steel", mass["issue_sill"], "make",
     "task-04 schedule N8 (formed metal product to the store; bore not calculated)"],
    ["6", "N9 nominal floor drain + N10 top vent stub", 2, "carbon steel",
     round(mass["drain_well"] + mass["vent_stub"], 1), "make", "task-04 schedule N9/N10"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M12 anchor,ISO 898-1 8.8,4,uprights to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    "# Work order STOCK_OUT\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - stock staging rack.\n\n"
    "1. Fabricate and erect the six uprights; bolt to the slab.\n"
    "2. Fit the three tier decks and the back guard; fit the issue-face edge stops and sill.\n"
    "3. Fit the N9 floor drain and N10 vent stub.\n"
    "4. Load test: rated stock per tier, 1.0 d hold (AQS-DUTY-072).\n"
    "5. Inspect against models/mfg/STOCK_OUT/export/stock_out.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
