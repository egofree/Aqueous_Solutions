"""POLY_F manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-POLY_F-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
PVDF/PTFE emulsion polymerization kettle: Hastelloy C-276 wetted vessel D150 x H225,
60 C, persulfate-initiated emulsion (ULLMANN_FLUOROPOLY class), agitated, jacketed.
VDF/TFE monomer from the gas train; resin to FILM_CAST/POWDER_RESIN. No measured rate
is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
D = P["design"]
L, W, H = P["size_mm"]
DN15, W15 = A["DN15_OD_mm"] / 2, A["DN15_wall_mm"]
CX, CY = 300.0, 300.0

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

parts = {}
# ---------------- frame: base + kettle support skirt ----------------
parts["base"] = box(0, 0, 0, L, W, 40)
parts["support_skirt"] = tube(110.0, 78.0, (CX, CY, 40), "Z", 460)   # skirt to the kettle bottom z 500

# ---------------- kettle D150 x H225, Hastelloy, jacketed ----------------
kettle = tube(D["D_mm"] / 2, D["D_mm"] / 2 - 6, (CX, CY, 500.0), "Z", D["H_mm"])
parts["kettle"] = kettle
parts["jacket"] = tube(D["D_mm"] / 2 + 14.0, D["D_mm"] / 2 + 6.0, (CX, CY, 500.0), "Z", D["H_mm"] - 30)
parts["dished_top"] = cq.Workplane("XY").sphere(D["D_mm"] / 2 + 6.0).translate((CX, CY, 500.0 + D["H_mm"])).intersect(
    box(CX - 100, CY - 100, 500.0 + D["H_mm"] - 25.0, 200, 200, 30))
# ---------------- agitator: shaft + impeller ----------------
parts["agitator_shaft"] = rod(9.0, (CX, CY, 520.0), "Z", 340)
imp = None
for zz in (600.0, 660.0):
    q = box(CX - 55.0, CY - 10.0, zz, 110.0, 20.0, 8.0)
    imp = q if imp is None else imp.union(q)
parts["impeller"] = imp
parts["motor"] = box(CX - 60.0, CY - 60.0, 860.0, 120.0, 120.0, 100)   # 0.1 kW drive
frame = box(0, 0, 0, L, W, 40)
for (px, py) in ((0, 0), (L - 50, 0), (0, W - 50), (L - 50, W - 50)):
    frame = frame.union(box(px, py, 40, 50, 50, 1160))                 # posts to the z 1200 envelope datum
frame = frame.union(box(0, 0, 1160, L, W, 40))                         # top rail z 1160..1200 (monomer-pigtail carrier)
parts["support_frame"] = frame

# ---------------- nozzle hardware ----------------
parts["vdf_inlet"] = tube(DN15, DN15 - W15, (CX - 60.0, -30.0, 160.0), "Y", 40)      # N1 -Y
parts["tfe_inlet"] = tube(DN15, DN15 - W15, (CX + 60.0, -30.0, 160.0), "Y", 40)      # N2 -Y
parts["resin_chute"] = box(CX - 30.0, CY - 35.0, 640.0, 60.0, 35.0, 120.0)           # N3 solids out +X
parts["powder_chute"] = box(CX - 30.0, CY + 15.0, 640.0, 60.0, 35.0, 120.0)          # N4 solids out +X
parts["pvdf_stub"] = tube(DN15, DN15 - W15, (CX + 55.0, CY, 560.0), "X", 60)         # N5 +X
parts["scrap_stub"] = tube(DN15, DN15 - W15, (CX - 55.0, CY, 560.0), "X", -60)       # N6 -X
parts["drain_well"] = tube(30.5, DN15, (CX, CY, 0), "Z", 40)                          # N7 through the skirt
parts["vent_stub"] = tube(DN15, DN15 - W15, (CX, CY + 60.0, 955.0), "Y", 40)          # N8 top

# ---------------- process inventory ----------------
inv = {"emulsion_inventory": rod(D["D_mm"] / 2 - 7, (CX, CY, 505.0), "Z", 140)}       # emulsion fill

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="POLY_F")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "poly_f.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "poly_f.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("vdf_inlet", "tfe_inlet", "resin_chute", "powder_chute", "scrap_stub")
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "poly_f_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "POLY_F.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
sb = cq.Compound.makeCompound([parts["kettle"].val()]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"base": 7.85e-6, "support_frame": 7.85e-6, "support_skirt": 7.85e-6, "kettle": 8.9e-6, "jacket": 7.85e-6,
       "dished_top": 8.9e-6, "agitator_shaft": 7.85e-6, "impeller": 7.85e-6, "motor": 7.85e-6,
       "vdf_inlet": 7.85e-6, "tfe_inlet": 7.85e-6, "resin_chute": 7.85e-6, "powder_chute": 7.85e-6,
       "pvdf_stub": 7.85e-6, "scrap_stub": 7.85e-6, "drain_well": 7.85e-6, "vent_stub": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
report = {
    "kettle_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
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
    ["1", f"Kettle OD {D['D_mm']} x {D['H_mm']} mm, Hastelloy C-276 wetted, PTFE gasketed", 1,
     "Hastelloy C-276", mass["kettle"] + mass["dished_top"], "make",
     f"duty section 3 material row; {D['chemistry'] if 'chemistry' in D else D['vessel']}"],
    ["2", "Jacket, OD +28 x 195 mm", 1, "carbon steel", mass["jacket"], "make", "60 C duty; AQS-DUTY-072"],
    ["3", "Support skirt + four-post frame to the monomer-rail datum", 1, "carbon steel",
     round(mass["base"] + mass["support_skirt"] + mass["support_frame"], 1),
     "make", "WO step 1"],
    ["4", "Agitator: shaft + 2 impellers + 0.1 kW drive", 1, "Cu/steel",
     round(mass["agitator_shaft"] + mass["impeller"] + mass["motor"], 1), "make", "design mixer row"],
    ["5", "N1/N2 monomer DN15 stubs -Y z 160 (VDF; TFE)", 2, "carbon steel",
     round(mass["vdf_inlet"] + mass["tfe_inlet"], 1), "make", "task-04 schedule N1/N2"],
    ["6", "N3/N4 discharge chutes +X z 600 (PVDF/PTFE resin; powder)", 2, "carbon steel",
     round(mass["resin_chute"] + mass["powder_chute"], 1), "make", "task-04 schedule N3/N4 (solids)"],
    ["7", "N5 PVDF DN15 stub +X z 560 (to FILM_CAST N2)", 1, "carbon steel", mass["pvdf_stub"], "make",
     "task-04 schedule N5"],
    ["8", "N6 off-spec scrap DN15 stub -X z 560", 1, "carbon steel", mass["scrap_stub"], "make",
     "task-04 schedule N6"],
    ["9", "N7 drain through the skirt + N8 vent stub", 2, "carbon steel",
     round(mass["drain_well"] + mass["vent_stub"], 1), "make", "task-04 schedule N7/N8"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "fasteners.csv").write_text(
    'item,size,grade,qty,location,basis\n'
    '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,8,kettle flange,study\n'
    '2,M12 anchor,ISO 898-1 8.8,4,base to slab,study\n')
(HERE / "WORK_ORDER.md").write_text(
    "# Work order POLY_F\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - fluoropolymer kettle.\n\n"
    "1. Fabricate the Hastelloy kettle and dished top; PTFE-gasket the flange.\n"
    "2. Fit the jacket and the support skirt on the base plate.\n"
    "3. Fit the agitator shaft, impellers and drive; megger the motor.\n"
    "4. Fit the N1/N2 monomer stubs, N3/N4 discharge chutes, N5/N6 liquor stubs, N7 drain and N8 vent.\n"
    "5. Test: pressure/leak hold per the duty sheet, then a water batch trial at 60 C.\n"
    "6. Inspect against models/mfg/POLY_F/export/poly_f.step; record dimensions on the traveller.\n")
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
