"""IND_MELT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-IND_MELT-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Medium-frequency coreless induction remelt furnace, tilt pour: Cu/Fe/Zn/Al scrap and
pot metals, 10 kg crucible, ceramic-fibre hot face 150 mm in a 4 mm CS casing
(AQS-DUTY-072; A-M-282/A-M-283 melt basis). The ten charge rows of the task-04
schedule land on the common charge chute (-X, z 160); the melt rows leave through
four DN15 stubs and the tilt-pour lip (+Y / +X at z 600). No measured rate is
claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
CR = P["crucible"]; CO = P["coil"]
L, W, H = P["size_mm"]
D = P["design"]
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
cx, cy = 480.0, 500.0                                 # crucible centreline
BATH = 600.0                                          # melt-row datum z 600

# ---------------- casing: CS shell t4, full envelope height ----------------
casing = box(0, 0, 0, L, W, H).cut(box(4, 4, 4, L - 8, W - 8, 1492))
casing = casing.cut(rod(DN15 + 1, (cx, W + 5.0, BATH), "Y", 95))          # N1/N8/N13/N14 stub passes
for sx in (300.0, 480.0, 660.0):
    casing = casing.cut(rod(DN15 + 1, (sx, W + 5.0, 600.0), "Y", 30))     # stub rows
casing = casing.cut(box(500, 400, 590, 40, 120, 20))                      # N9 slag spout channel
casing = casing.cut(rod(30.5, (500, 500, -5.0), "Z", 85.0))               # N16 drain pass
casing = casing.cut(rod(DN15 + 1, (500, 500, 800.0), "Z", 40))            # N17 vent pass
casing = casing.cut(box(-5.0, 420, 130, 60, 160, 90))                     # charge chute opening
parts["casing"] = casing

# ---------------- lining: ceramic-fibre hot face t150 ----------------
fibre = box(4, 4, 4, L - 8, W - 8, 1492).cut(box(154, 154, 154, L - 308, W - 308, 1192))
fibre = fibre.cut(box(60, 420, 120, 100, 160, 120))                       # chute throat recess
parts["fibre_lining"] = fibre

# ---------------- induction coil: 12 copper turns around the crucible zone ----
coil = None
for i in range(CO["turns"]):
    z = 320 + i * 40
    t = tube(CO["tube_od_mm"] / 2, CO["tube_od_mm"] / 2 - CO["tube_wall_mm"], (cx, cy, z), "Z", 20)
    coil = t if coil is None else coil.union(t)
parts["induction_coil"] = coil
# coil leads out through the casing (+X at z 360)
parts["coil_leads"] = tube(CO["tube_od_mm"] / 2, CO["tube_od_mm"] / 2 - CO["tube_wall_mm"],
                           (cx + 75.0, cy, 360.0), "X", 60)

# ---------------- crucible + pedestal ----------------
parts["crucible"] = tube(CR["D_mm"] / 2, CR["D_mm"] / 2 - 12, (cx, cy, 300), "Z", CR["H_mm"])
parts["crucible_pedestal"] = cyl_rod = rod(70.0, (cx, cy, 154), "Z", 146)   # on the fibre floor

# ---------------- tilt frame: trunnion pins on both -X / +X walls ----------------
parts["trunnion_pins"] = rod(40.0, (cx, cy, 500.0), "Y", 60).union(
    rod(40.0, (cx, cy, 500.0), "Y", L - 60)).translate((0, 0, 0)).cut(rod(0.01, (0, 0, 0), "X", 1))
parts["trunnion_pins"] = rod(40.0, (-25.0, cy, 500.0), "X", 60).union(
    rod(40.0, (L - 35.0, cy, 500.0), "X", 60))
parts["tilt_frame"] = box(154, 400, 470, 130, 200, 60)                    # tilt cradle under the shell band

# ---------------- hood + vent ----------------
hood = box(154, 154, BATH + 250, L - 308, W - 308, 30)
hood = hood.cut(rod(DN15 + 1, (500, 500, BATH + 245.0), "Z", 40))
parts["hood"] = hood
parts["vent_stub"] = tube(DN15, DN15 - W15, (500.0, 500.0, BATH + 280.0), "Z", 120)   # N17 up to z 800..920

# ---------------- charge chute (-X at z 160) ----------------
chute = box(-35.0, 420, 130, 60, 160, 90)
lip = box(20.0, 430, 190, 40, 140, 30)
parts["charge_chute"] = chute.union(lip)

# ---------------- melt DN15 stubs (+Y at z 600): N1/N8/N13/N14 ----------------
st = None
for sx in (300.0, 480.0, 660.0):
    q = tube(DN15, DN15 - W15, (sx, W - 34.0, BATH), "Y", 40)
    st = q if st is None else st.union(q)
parts["melt_stubs"] = st
parts["pour_spout"] = box(cx - 60.0, cy - 70.0, BATH - 20.0, 150, 140, 40)   # tilt-pour lip (+X side of the cradle)
parts["slag_spout"] = box(500, 400, 580, 60, 70, 30)                          # N9 slag return (+X at 600)

# ---------------- N16 drain well ----------------
parts["drain_well"] = tube(30.5, DN15, (500, 500, 0), "Z", 50)

# ---------------- process inventory solids (not BOM parts) ----------------
melt = rod(CR["D_mm"] / 2 - 13, (cx, cy, 310), "Z", CR["H_mm"] - 40)          # melt in the crucible
inv = {"melt_inventory": melt}

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="IND_MELT")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "ind_melt.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "ind_melt.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("charge_chute", "pour_spout", "slag_spout", "trunnion_pins", "melt_stubs")   # tilt + schedule hardware at the faces
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "ind_melt_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "IND_MELT.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
shell_parts = [parts[k] for k in ("casing", "fibre_lining")]
sb = cq.Compound.makeCompound([v.val() for v in shell_parts]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
valid = all(v.val().isValid() for v in ALL)
rho = {"casing": 7.85e-6, "fibre_lining": 128e-9, "induction_coil": 8.96e-6, "coil_leads": 8.96e-6,
       "crucible": 1.78e-6, "crucible_pedestal": 1.78e-6, "trunnion_pins": 7.85e-6,
       "tilt_frame": 7.85e-6, "hood": 7.85e-6, "vent_stub": 7.85e-6, "charge_chute": 7.85e-6,
       "melt_stubs": 7.85e-6, "pour_spout": 7.85e-6, "slag_spout": 7.85e-6, "drain_well": 7.85e-6}
mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
vol_melt = sum(v.val().Volume() for v in inv.values())
report = {
    "shell_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
    "shell_bbox_abs": [round(sb.xmin, 1), round(sb.ymin, 1), round(sb.zmin, 1),
                       round(sb.xmax, 1), round(sb.ymax, 1), round(sb.zmax, 1)],
    "inside_size_mm_shell": inside_shell,
    "connection_overhang_mm": overhang,
    "overhang_allowance_mm": slack,
    "overhang_ok": overhang_ok,
    "cad_stl_scope": "in-envelope build solid, metres (EXTERNAL parts excluded: " + ", ".join(EXTERNAL) + ")",
    "external_parts": list(EXTERNAL),
    "cap_solids": len(cap_solid.Solids()),
    "all_parts_valid": valid,
    "melt_volume_litres": round(vol_melt / 1e6, 1),
    "part_mass_kg": mass,
    "cadquery": "2.8.0",
}
rows = [
    ["1", "Furnace casing 1000 x 1000 x 1500 mm, CS t4 (walls + roof)", 1, "carbon steel",
     round(mass["casing"], 1), "make", "duty section 3 (study 4 mm CS casing); WORK_ORDER step 1"],
    ["2", "Ceramic-fibre hot face, t150", 1, "ceramic-fibre board 128 kg/m3", mass["fibre_lining"], "make",
     "design lining row (AQS-DUTY-072); SCHACHT2004 class"],
    ["3", f"Induction coil, {CO['turns']} turns x OD {CO['tube_od_mm']} mm Cu, around the crucible zone", 1,
     "Cu ETP tube", round(mass["induction_coil"] + mass["coil_leads"], 1), "make",
     f"medium-frequency coreless class; {D['connected_kW']} kW connected, {D['peak_kW']} kW peak (A-M-283)"],
    ["4", f"Crucible, D{CR['D_mm']} x {CR['H_mm']} mm, {CR['kg']} kg, graphite", 1, "graphite",
     mass["crucible"], "buy", "design crucible row; change-out at the unit task 12 work order"],
    ["5", "Crucible pedestal and tilt cradle", 1, "graphite + CS", round(mass["crucible_pedestal"] + mass["tilt_frame"], 1),
     "make", "WORK_ORDER step 2; tilt pour per the design service row"],
    ["6", "Trunnion pins -X/+X at z 500", 2, "carbon steel", mass["trunnion_pins"], "make", "WORK_ORDER step 2"],
    ["7", "Hood plate with N17 vent pass", 1, "carbon steel", mass["hood"], "make", "WORK_ORDER step 4"],
    ["8", f"N1/N8/N13/N14 melt DN15 stubs +Y z 600 (pour, caster, atomizer, investment)", 4, "carbon steel",
     mass["melt_stubs"], "make", "task-04 schedule N1/N8/N13/N14"],
    ["9", "N9 slag-return spout +X z 600", 1, "carbon steel (refractory class)", mass["slag_spout"], "make",
     "task-04 schedule N9 (solids, bore not calculated)"],
    ["10", "Charge chute -X z 160 (the ten charge rows land here)", 1, "CS chute, refractory throat",
     mass["charge_chute"], "make", "task-04 schedule N2..N7/N10..N12/N15; A-M-284 feedstock ruling"],
    ["11", "N16 drain well: sump OD 60, DN15 bore, flush at z 0", 1, "carbon (ram class)",
     mass["drain_well"], "make", "task-04 schedule N16 bottom DN15 Class 150"],
    ["12", "Medium-frequency power supply, 25 kW connected, cabinet", 1, "purchase item", "", "buy",
     "WO step 5; A-M-283 class; mass per the purchase datasheet at order"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
fast = ('item,size,grade,qty,location,basis\n'
        '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,8,hood rim,study\n'
        '2,M12 anchor,ISO 898-1 8.8,4,casing to slab,study\n')
(HERE / "fasteners.csv").write_text(fast)
wo = (f"# Work order IND_MELT\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - the melt train anchor.\n\n"
      f"1. Fabricate the 1000 x 1000 x 1500 mm casing (CS t4); fit the t150 ceramic-fibre hot face.\n"
      f"2. Set the crucible on its pedestal; wind and clamp the {CO['turns']}-turn coil; fit the trunnions and tilt cradle.\n"
      f"3. Route the coil leads through the +X pass; megger the coil to the casing.\n"
      f"4. Mount the hood with the N17 vent; fit the N1/N8/N13/N14 melt stubs and the N9 slag spout.\n"
      f"5. Wire the {D['connected_kW']} kW medium-frequency supply; interlock lid position and coil water flow.\n"
      f"6. Test: coil dry-out, then first melt at the {CR['kg']} kg batch; prove the tilt-pour lip at +X.\n"
      f"7. Inspect against models/mfg/IND_MELT/export/ind_melt.step; record dimensions on the traveller.\n")
(HERE / "WORK_ORDER.md").write_text(wo)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
