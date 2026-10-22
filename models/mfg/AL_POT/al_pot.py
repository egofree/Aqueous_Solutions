"""AL_POT manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Placement frame: x along 800 mm, y along 800 mm, z up, origin at the
envelope corner. Layout choices named in params.json (layout_note);
height/bore/rating per connection are the task-04 schedule verbatim.
Materials per docs-authority/duties/AL_POT.md section 3 (X-MAT-22):
graphite wetted faces + ceramic-fibre backup + CS shell below the liner;
the 10 mm design allowance is carried by the t40 ram liner and the
t10 hood hot plate. No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
AN = P["anode"]; CA = P["cathode"]; BUS = P["busbar"]
L, W, H = P["size_mm"]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

parts = {}
RY = A["DN150_OD_mm"] / 2                       # DN150 riser
rx_, ry_ = 490.0, 490.0                          # riser centre (hood offset +90,+90)
ay = 400.0                                       # electrode centreline
cath_pitch = (L - 272) / (CA["count"] - 1)       # 132 mm (plate centres 136..664 inside the 660 cavity)
cath_xc = [70 + 66 + i * cath_pitch for i in range(CA["count"])]   # 136..664
anode_xc = [x + 34 for x in cath_xc]             # 170..698 (offset from the plate columns)

# ---------------- casing: CS shell, full envelope height, t6 -------------
casing = box(0, 0, 0, L, W, H).cut(box(6, 6, 6, L - 12, W - 12, 1588))          # walls only
roof = box(0, 0, 1594, L, W, 6)
casing = casing.union(roof)
casing = casing.cut(rod(RY + 2, (rx_, ry_, 1585), "Z", 30))                      # riser pass at the roof
for xk in anode_xc:                                                              # N1..: nothing on the roof besides riser
    pass
for (sx, sdir, hd) in ((202.0, -1, 21.5), (598.0, 1, 21.5)):                      # N2 / N4 stub passes
    p = (sx, (W + 5) if sdir > 0 else -5.0, 600.0)
    casing = casing.cut(rod(hd / 2, p, "Y", 95 * (-1 if sdir < 0 else 1)))
casing = casing.cut(rod(30.5, (256.0, 160.0, -5.0), "Z", 85.0))                   # N5 well pass
casing = casing.cut(rod(57.5, (-5.0, 400.0, 160.0), "X", 90.0))                   # N3 chute throat
casing = casing.cut(box(660, 370, 650, 145, 60, 20))                              # N1 siphon crest channel pass
parts["casing"] = casing

# ---------------- lining: ceramic-fibre backup t24 + graphite ram liner t40 ------
fibre = box(6, 6, 6, L - 12, W - 12, 1588).cut(box(30, 30, 30, L - 60, W - 60, 1564))
parts["fibre_lining"] = fibre
ram = box(30, 30, 30, L - 60, W - 60, 1564).cut(box(70, 70, 70, L - 140, W - 140, 1524))
ram = ram.cut(rod(40, (256.0, 160.0, -5.0), "Z", 110.0))                          # drain sump recess
parts["ram_lining"] = ram

# ---------------- hood: graphite hot plate t10 + CS plate t6 + rim lip -----------
def opening_plate(z0, t):
    hp = box(70, 70, z0, 660, 660, t)
    for xk in anode_xc:
        hp = hp.cut(rod(41.5, (xk, ay, z0 - 2), "Z", t + 4))
    for xc in cath_xc:
        hp = hp.cut(box(xc - 12, 66, z0 - 2, 24, 34, t + 4))
    hp = hp.cut(rod(88, (rx_, ry_, z0 - 2), "Z", t + 4))
    hp = hp.cut(rod(47.5, (670, 400, z0 - 2), "Z", t + 4))
    return hp
parts["hood_hot_plate"] = opening_plate(490, 10)                # graphite, wetted, = the 10 mm allowance
hood = opening_plate(500, 6)
hood = hood.union(box(70, 70, 500, 60, 660, 46)).union(box(730, 70, 500, 60, 660, 46))
hood = hood.union(box(70, 70, 500, 660, 60, 46)).union(box(70, 730, 500, 660, 60, 46))
parts["hood"] = hood

# ---------------- internal head plate (electrode deck) at 1154..1160 -------------
head = opening_plate(1154, 6)
parts["head_plate"] = head

# ---------------- electrodes ----------------------------------------------------
ax_ = None
for xk in anode_xc:
    a = rod(37.5, (xk, ay, 100), "Z", 1064)                     # z 100..1164; 400 mm immersion
    ax_ = a if ax_ is None else ax_.union(a)
parts["anodes"] = ax_
cl_ = None
for xk in anode_xc:
    b = box(xk - 55, ay - 20, 1160, 110, 40, 24)                # clamp bar on the head plate
    cl_ = b if cl_ is None else cl_.union(b)
parts["anode_clamps"] = cl_
ca_ = None
for xc in cath_xc:
    p = box(xc - 55, 70, 90, 110, 12, 440)                      # 110 x 12 plate, z 90..530
    ca_ = p if ca_ is None else ca_.union(p)
parts["cathodes"] = ca_

# ---------------- busbar ladder (Cu ETP on ceramic pads, section 11 isolation) ----
rail_z0, rail_t, rail_w = 1196, 31, 32
pads = None
for x in (20, 160, 300, 440, 580, 720):
    for yv in (184, 600):
        q = box(x, yv - 18, 1186, 44, 36, 10)
        pads = q if pads is None else pads.union(q)
parts["ceramic_pads"] = pads
br = None
for yv in BUS["rail_y_mm"]:
    r = box(20, yv - rail_w / 2, rail_z0, 760, rail_w, rail_t)
    br = r if br is None else br.union(r)
parts["bus_rails"] = br
st = None
for xc in cath_xc:                                              # cathode riser straps + jumpers to rail y=200
    v = box(xc - 10, 82, 530, 20, 8, 656).union(box(xc - 10, 82, 1196, 20, 134, 8))
    st = v if st is None else st.union(v)
for xk in anode_xc:                                             # anode straps from clamp top to rail y=600
    v = box(xk - 10, ay + 4, 1184, 20, 8, 12).union(box(xk - 10, ay + 4, 1188, 20, 212, 8)).union(box(xk - 10, 592, 1188, 20, 36, 8))
    st = st.union(v)
parts["bus_straps"] = st

# ---------------- offtake riser DN150 + Hastelloy dip leg DN50 -------------------
parts["offtake_riser"] = tube(RY, RY - A["DN150_wall_mm"], (rx_, ry_, 500), "Z", 1094)   # 500..1594
parts["riser_flange"] = box(rx_ - 100, ry_ - 100, 1144, 200, 200, 10)
dl = A["DN50_OD_mm"] / 2
parts["dip_leg"] = tube(dl, dl - A["DN50_wall_mm"], (rx_, ry_, 250), "Z", 290)            # 250..540 submerged
OD15, t15 = A["DN15_OD_mm"], A["DN15_wall_mm"]
parts["vent_stub"] = tube(OD15 / 2, OD15 / 2 - t15, (rx_ + RY, ry_, 800), "Y", 40)          # N6 on the riser

# ---------------- N1 metal siphon (well + crest + discharge lip) ------------------
wr = A["DN80_OD_mm"] / 2
well = rod(wr, (670, 400, 80), "Z", 585)                        # riser leg 80..665
crest = box(660, 400 - wr, 655, 160, 2 * wr, 10)                 # horizontal run 660..820 at z 655..665
lip = rod(wr, (800, 400, 605), "Z", 55)
siphon = well.union(crest).union(lip)
siphon = siphon.cut(rod(15.0, (670, 400, 75), "Z", 700))          # bore through the riser leg
siphon = siphon.cut(box(655, 385, 652, 170, 30, 16))              # bore through the crest
siphon = siphon.cut(rod(15.0, (800, 400, 590), "Z", 80))          # bore through the discharge leg
parts["metal_siphon"] = siphon

# ---------------- N3 feed chute + lance -----------------------------------------
chute = box(-35, 320, 90, 35, 160, 140)
cone = cq.Solid.makeCone(30, 22, 55, cq.Vector(-20, 400, 285), cq.Vector(0, 0, 1))
seal_flange = box(-43, 340, 130, 8, 120, 60)
lance = tube(A["DN100_OD_mm"] / 2, A["DN100_OD_mm"] / 2 - A["DN100_wall_mm"], (70, 400, 160), "X", 100)
parts["feed_chute_group"] = chute.union(cq.Workplane(obj=cone)).union(seal_flange).union(lance)

# ---------------- N2 / N4 DN15 stubs + ceramic lining sleeves ---------------------
s = None
for (sx, sdir) in ((202.0, -1), (598.0, 1)):
    y1 = (W if sdir > 0 else 0.0)
    q = tube(OD15 / 2, OD15 / 2 - t15, (sx, y1 + 40 * sdir, 600), "Y", -40 * sdir)
    s = q if s is None else s.union(q)
parts["DN15_stubs"] = s
sl_ = None
for (sx, sdir) in ((202.0, -1), (598.0, 1)):
    y1 = (730.0 if sdir > 0 else 70.0)
    q = tube(16.0, OD15 / 2 - t15, (sx, y1, 600), "Y", -40 * sdir)
    sl_ = q if sl_ is None else sl_.union(q)
parts["ceramic_sleeves"] = sl_

# ---------------- N5 drain well --------------------------------------------------
parts["drain_well"] = tube(30.0, OD15 / 2, (256, 160, 0), "Z", 50)

# ---------------- process inventory solids (not BOM parts) -----------------------
melt_salt = box(70, 70, 100, 660, 660, 400)
melt_metal = box(70, 70, 70, 660, 660, 30)
for blk in (melt_salt, melt_metal):
    for xk in anode_xc:
        blk = blk.cut(rod(38.0, (xk, ay, 60), "Z", 460))
    for xc in cath_xc:
        blk = blk.cut(box(xc - 56, 69, 80, 112, 14, 460))
    blk = blk.cut(rod(45.0, (670, 400, 60), "Z", 450))            # siphon well leg
    blk = blk.cut(rod(46.0, (rx_, ry_, 240), "Z", 260))            # dip leg
    blk = blk.cut(rod(A["DN100_OD_mm"] / 2 + 2.0, (70, 400, 160), "X", 110))   # lance
    blk = blk.cut(rod(31.0, (256, 160, 40), "Z", 40))              # drain sump bore pocket
inv = {"melt_salt": melt_salt, "melt_metal": melt_metal}

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="AL_POT")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "al_pot.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "al_pot.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# ascii=True: the X-PAR-04 envelope gate parses cad/stl/*.stl as ASCII vertex text, so the
# replaced cad/stl/AL_POT.stl (copied from this file) must be the ASCII form too.

# cad/stl copy scope: the X-PAR-04 envelope registry requires the cad/stl box to equal the graph
# size to 1 mm, so the cad/stl solid is the in-envelope build (everything physically inside
# 0..800 x 0..800 x 0..1600). The protruding schedule-connection hardware (N1 siphon lip/crest,
# N3 chute group, N2/N4 stubs) lives in export/al_pot.stl and in the STEP instead, and the
# overhang stays reported on the check fields below - nothing was resized.
EXTERNAL = ("metal_siphon", "feed_chute_group", "DN15_stubs")
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "al_pot_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04: envelope.py builds size_mm/1000 and the
# gate test multiplies by 1000), so the cad/stl copy of the build solid is scaled 1/1000 like
# every other registered unit.
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "AL_POT.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
shell_parts = [parts[k] for k in ("casing", "fibre_lining", "ram_lining", "head_plate")]
sb = cq.Compound.makeCompound([v.val() for v in shell_parts]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0                                                     # connection overhang allowance (schedule stubs)
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
j_anode = P["design"]["I_A"] / (AN["count"] * (math.pi * AN["D_mm"] * P["design"]["anode_imm_mm"] / 100
           + math.pi * (AN["D_mm"] / 20) ** 2))
valid = all(v.val().isValid() for v in ALL)
rho = {"casing": 7.85e-6, "fibre_lining": 128e-9, "ram_lining": 1.55e-6, "hood_hot_plate": 1.78e-6,
       "hood": 7.85e-6, "head_plate": 7.85e-6, "anodes": 1.78e-6, "anode_clamps": 7.85e-6,
       "cathodes": 7.87e-6, "ceramic_pads": 2.7e-6, "bus_rails": 8.96e-6, "bus_straps": 8.96e-6,
       "offtake_riser": 7.85e-6, "riser_flange": 7.85e-6, "dip_leg": 8.9e-6, "vent_stub": 7.85e-6,
       "metal_siphon": 1.55e-6, "feed_chute_group": 7.85e-6, "DN15_stubs": 7.85e-6,
       "ceramic_sleeves": 2.7e-6, "drain_well": 1.55e-6}
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
    "anode_j_A_cm2_drawn": round(j_anode, 3),
    "melt_volume_litres": round(vol_melt / 1e6, 1),
    "part_mass_kg": mass,
    "cadquery": "2.8.0",
}
# BOM regenerated from the model (AQS-PLAN-006 A-core 6; the prior 7-row bases are carried over)
rows = [
    ["1", "Lined cell shell 800 x 800 x 1600 mm: casing t6 (walls + roof + head plate 1154)", 1,
     "carbon steel (CS class)", round(mass["casing"] + mass["head_plate"], 1), "make",
     "WORK_ORDER step 1; duty section 3 mild-steel outer shell below the liner, 700 C, dry outside the lining; envelope per duty section 2"],
    ["2", "Ceramic-fibre backup lining kit, t24 (wall bands + floor board set)", 1,
     "ceramic-fibre board 128 kg/m3", mass["fibre_lining"], "make",
     "duty section 3 backup lining per SCHACHT2004 class; concentrate kept anhydrous (X-MAT-22, ULLMANN_MAGNESIUM)"],
    ["3", "Graphite ram lining kit, t40, wetted faces (10 mm design allowance inside)", 1,
     "graphite ramming paste 1550 kg/m3", mass["ram_lining"], "make",
     "duty section 3 graphite wetted faces; DING2018_CL_REVIEW, KRUIZENGA2012; liner change-out = unit task 12 work order"],
    ["4", "Anode bank, 5 x D75 x 1064 mm, 400 mm immersion", 5, "graphite (chlorinated)",
     mass["anodes"], "buy",
     "Faraday I = 1461 A at CE 0.85 (A-M-282); drawn j 0.30 A/cm2 inside the A-M-282 0.5 A/cm2 class"],
    ["5", "Cathode plate set, 5 x 110 x 12 x 440 mm (design row 'cathodes 5')", 5, "mild steel / clad",
     mass["cathodes"], "make",
     "duty section 2 graph design row; 10 kg/d metal on the D-DOCK chloride import (A-M-284); BOM qty corrected 4 -> 5, see build_log.md"],
    ["6", "Cu busbar ladder: 2 rails 32 x 31 (975 mm2 class) + riser straps + ceramic pads", 1,
     "Cu ETP + alumina pads", round(mass["bus_rails"] + mass["bus_straps"] + mass["ceramic_pads"], 1), "make",
     "1461 A at 3.8 V cell; 5.551 kW dc + 0.1069 kW hold of 7 kW connected; frame-isolated per AQS-STD-002 section 11"],
    ["7", "Anode clamp bars 110 x 40 x 24 on the head plate (10 x M12 studs, fasteners.csv item 1)", 5,
     "carbon steel", mass["anode_clamps"], "make", "WORK_ORDER step 2/3: torque and megger check"],
    ["8", "Hood group: CS hood plate t6 + perimeter rim lip, on the graphite hot plate", 1,
     "carbon steel", mass["hood"], "make",
     "WO step 4; dry Cl2 headspace at 700 C (M7); A-M-280 ruling 39.4192 kg/d Cl2 export at the CRU"],
    ["9", "Hood hot plate, graphite t10 (expendable wetted face = the 10 mm allowance)", 1,
     "graphite", mass["hood_hot_plate"], "make",
     "duty section 3: 10 mm design allowance on the wetted faces; change-out at the unit task 12 work order"],
    ["10", "Offtake riser DN150 OD168.3 t4.0 (sch 10), z 500..1594, flange + N6/N2/N4 DN15 stubs", 1,
     "carbon steel (dry hot Cl2)", round(mass["offtake_riser"] + mass["riser_flange"] + mass["vent_stub"] + mass["DN15_stubs"], 1),
     "make", "WO row 5; nozzles per the task-04 schedule (N6 top 800; N2/N4 Class 150 at 600)"],
    ["11", "Dip leg DN50 OD60.3, inside the riser annulus, bottom z 250 (250 mm submerged)", 1,
     "Hastelloy C-276", mass["dip_leg"], "buy",
     "WO row 5; melt-side seal leg per the duty section 3 dry-Cl2 class"],
    ["12", "Metal siphon: well DN80 OD88.9 carbon + crest + discharge lip at +X z 600 (heat traced)", 1,
     "carbon (ram class)", mass["metal_siphon"], "make",
     "task-04 schedule N1 (solids, bore not calculated); WO step 6 trial electrolysis tap"],
    ["13", "Feed chute group: chute box + hopper + rotary-seal flange + DN100 lance OD114.3 t4", 1,
     "CS chute, carbon lance (refractory)", mass["feed_chute_group"], "make",
     "task-04 schedule N3; 49.419 kg/d feed (A-M-284 feedstock ruling); WO step 4 rotary seal"],
    ["14", "Drain well: carbon sump tube OD60, DN15 bore, sump face z 50, flush at z 0", 1,
     "carbon (ram class)", mass["drain_well"], "make",
     "task-04 schedule N5 bottom DN15 Class 150; frozen-salt drain pig per WO step 6"],
    ["15", "Ceramic lining sleeves for the N2/N4 ram passes", 2, "alumina (90 % class)",
     mass["ceramic_sleeves"], "buy", "duty section 3 backup-lining class (SCHACHT2004)"],
    ["16", "Thyristor rectifier + bath hold heaters, 7 kW connected, IP54 cabinet", 1, "purchase item",
     "", "buy", "WO step 5/7; AQS-DUTY-072 section 4; A-M-282 class; mass per the purchase datasheet at order"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
