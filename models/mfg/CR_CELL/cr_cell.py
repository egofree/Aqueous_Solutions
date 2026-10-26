"""CR_CELL manufacturing model, AQS-PLAN-006 work order (X-MFG lane, FOUNDRY-CR_CELL-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Placement frame: x along 800 mm, y along 800 mm, z up, origin at the envelope
corner. The cell makes chromium: Cr(III) molten-salt electrolysis at 700 C, 18.95 A at
2.8 V (A-M-282 Faraday class) behind the carbochlorination loop, on the D-DOCK
feedstock ruling (A-M-284); the chlorinator CO leaves as fuel-gas class export. Layout choices named in params.json (layout_note); heights, bores and
ratings per docs-authority/nozzles/CR_CELL.csv (task-04 schedule). Materials per
docs-authority/duties/CR_CELL.md section 3: graphite wetted faces + ceramic-fibre
backup + CS shell below the liner. No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
AN = P["anode"]; CA = P["cathode"]; BUS = P["busbar"]
L, W, H = P["size_mm"]
D = P["design"]

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

parts = {}
RY = A["DN50_OD_mm"] / 2                        # DN50 riser (gas < 1 kg/d class)
rx_, ry_ = 550.0, 550.0                         # riser centre (hood offset +150,+150)
ay = 400.0                                      # electrode centreline
BATH = D["bath_top_mm"]                         # bath top z 350 (250 mm immersion, tips z 100)
cath_pitch = (L - 272) / CA["count"]            # plate centres across the 660 cavity
cath_xc = [70 + 66 + i * cath_pitch for i in range(CA["count"] - 1)]   # 2 plates
anode_xc = [165 + i * 235 for i in range(AN["count"])]                 # 165, 400, 635
bw, bh = BUS["rail_w_mm"], BUS["rail_t_mm"]     # 25 mm2 class rail

# ---------------- casing: CS shell, full envelope height, t6 -------------
casing = box(0, 0, 0, L, W, H).cut(box(6, 6, 6, L - 12, W - 12, 1588))          # walls only
roof = box(0, 0, 1594, L, W, 6)
casing = casing.union(roof)
casing = casing.cut(rod(RY + 2, (rx_, ry_, 1585), "Z", 30))                      # riser pass at the roof
casing = casing.cut(rod(A["DN15_OD_mm"] / 2 + 1, (-5.0, 400.0, 160.0), "X", 90.0))   # N2 brine inlet pass
casing = casing.cut(rod(A["DN15_OD_mm"] / 2 + 1, (544.0, W - 40, 600.0), "Y", 90.0)) # N4 CO export pass (+Y at 600)

casing = casing.cut(rod(30.5, (256.0, 160.0, -5.0), "Z", 85.0))                  # N4 drain well pass
casing = casing.cut(rod(57.5, (L - 40, 400.0, 605.0), "X", 90.0))                # N1 tap well pass (+X z 600)
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
        hp = hp.cut(rod(AN["D_mm"] / 2 + 4.5, (xk, ay, z0 - 2), "Z", t + 4))
    for xc in cath_xc:
        hp = hp.cut(box(xc - 12, 66, z0 - 2, 24, 34, t + 4))
    hp = hp.cut(rod(RY + 30, (rx_, ry_, z0 - 2), "Z", t + 4))
    hp = hp.cut(rod(A["DN15_OD_mm"] / 2 + 6, (544.0, W - 70, z0 - 2), "Z", t + 4))   # N4 CO stub pass
    return hp
parts["hood_hot_plate"] = opening_plate(BATH - 10, 10)          # graphite, wetted, at the bath top
hood = opening_plate(BATH, 6)
hood = hood.union(box(70, 70, BATH, 60, 660, 46)).union(box(730, 70, BATH, 60, 660, 46))
hood = hood.union(box(70, 70, BATH, 660, 60, 46)).union(box(70, 730, BATH, 660, 60, 46))
parts["hood"] = hood

# ---------------- internal head plate (electrode deck) at 1154..1160 -------------
head = opening_plate(1154, 6)
parts["head_plate"] = head

# ---------------- electrodes ----------------------------------------------------
ax_ = None
for xk in anode_xc:
    a = rod(AN["D_mm"] / 2, (xk, ay, 100), "Z", 1064)           # z 100..1164; 250 mm immersion
    ax_ = a if ax_ is None else ax_.union(a)
parts["anodes"] = ax_
cl_ = None
for xk in anode_xc:
    b = box(xk - 45, ay - 20, 1160, 90, 40, 24)                 # clamp bar on the head plate
    cl_ = b if cl_ is None else cl_.union(b)
parts["anode_clamps"] = cl_
ca_ = None
for xc in cath_xc:
    p = box(xc - 55, 70, 90, 110, 12, 300)                      # 110 x 12 plate, z 90..390
    ca_ = p if ca_ is None else ca_.union(p)
parts["cathodes"] = ca_

# ---------------- busbar ladder (Cu ETP on ceramic pads, section 11 isolation) ----
rail_z0, rail_t, rail_w = 1196, BUS["rail_t_mm"], BUS["rail_w_mm"]
pads = None
for x in (20, 160, 300, 440, 580, 720):
    for yv in (184, 600):
        q = box(x, yv - 18, 1186, 44, 36, 10)
        pads = q if pads is None else pads.union(q)
parts["ceramic_pads"] = pads
br = None
for yv in (184, 600):
    r = box(20, yv - rail_w / 2, rail_z0, 760, rail_w, rail_t)
    br = r if br is None else br.union(r)
parts["bus_rails"] = br
st = None
for xc in cath_xc:                                              # cathode riser straps to the - rail
    v = box(xc - 10, 82, 390, 20, 8, 800).union(box(xc - 10, 82, 1190, 20, 110, 6))
    st = v if st is None else st.union(v)
for xk in anode_xc:                                             # anode straps from clamp top to + rail
    v = box(xk - 10, ay + 4, 1184, 20, 8, 12).union(box(xk - 10, ay + 4, 1188, 20, 196, 6)).union(box(xk - 10, 570, 1188, 20, 60, 6))
    st = st.union(v)
parts["bus_straps"] = st

# ---------------- offtake riser DN50 + dip leg -----------------------------------
parts["offtake_riser"] = tube(RY, RY - A["DN50_wall_mm"], (rx_, ry_, BATH), "Z", 1594 - BATH)
parts["riser_flange"] = box(rx_ - 70, ry_ - 70, 1144, 140, 140, 10)
dl = A["DN15_OD_mm"] / 2
parts["dip_leg"] = tube(dl, dl - A["DN15_wall_mm"], (rx_, ry_, BATH - 100), "Z", 150)   # returns caught brine fog
parts["vent_stub"] = tube(A["DN15_OD_mm"] / 2, A["DN15_OD_mm"] / 2 - A["DN15_wall_mm"], (rx_, ry_ - RY, 800), "Y", -40)  # N6 on the riser at z 800, in-envelope

# ---------------- N4 CO export stub (+Y at z 600) ---------------------------------
parts["co_stub"] = tube(A["DN15_OD_mm"] / 2, A["DN15_OD_mm"] / 2 - A["DN15_wall_mm"], (544.0, W - 40, 600.0), "Y", 45)

# ---------------- N1 Cr-metal tap well (+X at z 600) ------------------------------
wr = 44.45                                        # tap-well bore class (DN80 study form, OD 88.9)
well = rod(wr, (670, 400, 80), "Z", 535)                        # riser leg 80..615
crest = box(660, 400 - wr, 605, 160, 2 * wr, 10)                 # horizontal run 660..820 at z 605..615
lip = rod(wr, (800, 400, 555), "Z", 55)
tap = well.union(crest).union(lip)
tap = tap.cut(rod(15.0, (670, 400, 75), "Z", 700))               # bore through the riser leg
tap = tap.cut(box(655, 385, 602, 170, 30, 16))                   # bore through the crest
tap = tap.cut(rod(15.0, (800, 400, 540), "Z", 80))               # bore through the discharge leg
parts["cr_tap_group"] = tap

# ---------------- N2/N3 feed chutes (-X at z 160) ---------------------------------
ch1 = box(-35, 320, 130, 35, 160, 90)                            # chromite concentrate chute
ch2 = box(-35, 480, 130, 35, 160, 90)                            # carbon reductant chute
parts["feed_chutes"] = ch1.union(ch2)

# ---------------- N4 drain well ---------------------------------------------------
parts["drain_well"] = tube(30.0, dl, (256, 160, 0), "Z", 50)

# ---------------- process inventory solids (not BOM parts) -----------------------
bath_h = BATH - 100
melt_salt = box(70, 70, 100, 660, 660, bath_h)
melt_metal = box(70, 70, 70, 660, 660, 30)
for blk in (melt_salt, melt_metal):
    for xk in anode_xc:
        blk = blk.cut(rod(AN["D_mm"] / 2 + 1, (xk, ay, 60), "Z", BATH))
    for xc in cath_xc:
        blk = blk.cut(box(xc - 56, 69, 80, 112, 14, bath_h + 20))
    blk = blk.cut(rod(16.0, (670, 400, 60), "Z", 450))            # tap well leg
    blk = blk.cut(rod(dl + 1, (rx_, ry_, 240), "Z", 160))         # dip leg
    blk = blk.cut(rod(A['DN15_OD_mm'] / 2 + 1, (256.0, 240.0, 160.0), 'Y', 200))  # N2 liquor inlet bore
    blk = blk.cut(rod(31.0, (256, 160, 40), "Z", 40))             # drain sump bore pocket
inv = {"melt_salt": melt_salt, "melt_metal": melt_metal}

# ---------------- export, checks, BOM --------------------------------------------
asm = cq.Assembly(name="CR_CELL")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cr_cell.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
cap_solid = body.val()
cap_solid.exportStl(str(out / "cr_cell.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)

EXTERNAL = ("cr_tap_group", "feed_chutes", "co_stub")   # schedule hardware outside the faces (overhang reported)
in_env = None
for k, v in parts.items():
    if k in EXTERNAL:
        continue
    in_env = v if in_env is None else in_env.union(v)
in_env_solid = in_env.val()
in_env_solid.exportStl(str(out / "cr_cell_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
in_env_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CR_CELL.stl"),
                                    tolerance=0.0005, angularTolerance=0.4, ascii=True)

ALL = list(parts.values()) + list(inv.values())
shell_parts = [parts[k] for k in ("casing", "fibre_lining", "ram_lining", "head_plate")]
sb = cq.Compound.makeCompound([v.val() for v in shell_parts]).BoundingBox()
tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
slack = 50.0
inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                    and sb.zmin >= -1 and sb.zmax <= H + 1)
overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
            "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
overhang_ok = all(v <= slack + 1 for v in overhang.values())
j_anode = D["I_A"] / (AN["count"] * (math.pi * AN["D_mm"] * D["anode_imm_mm"] / 100
           + math.pi * (AN["D_mm"] / 20) ** 2))
valid = all(v.val().isValid() for v in ALL)
rho = {"casing": 7.85e-6, "fibre_lining": 128e-9, "ram_lining": 1.55e-6, "hood_hot_plate": 1.78e-6,
       "hood": 7.85e-6, "head_plate": 7.85e-6, "anodes": 1.78e-6, "anode_clamps": 7.85e-6,
       "cathodes": 7.87e-6, "ceramic_pads": 2.7e-6, "bus_rails": 8.96e-6, "bus_straps": 8.96e-6,
       "offtake_riser": 7.85e-6, "riser_flange": 7.85e-6, "dip_leg": 7.85e-6, "vent_stub": 7.85e-6,
       "co_stub": 7.85e-6, "cr_tap_group": 1.55e-6, "feed_chutes": 7.85e-6, "drain_well": 1.55e-6}
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
    "anode_j_A_cm2_drawn": round(j_anode, 4),
    "bath_volume_litres": round(vol_melt / 1e6, 1),
    "part_mass_kg": mass,
    "cadquery": "2.8.0",
}
rows = [
    ["1", "Lined cell shell 800 x 800 x 1600 mm: casing t6 (walls + roof + head plate 1154)", 1,
     "carbon steel (CS class)", round(mass["casing"] + mass["head_plate"], 1), "make",
     "WORK_ORDER step 1; duty section 3 CS outer shell below the liner, 700 C, dry outside the lining; envelope per AQS-DUTY-072 cell-class study minimum"],
    ["2", "Ceramic-fibre backup lining kit, t24", 1, "ceramic-fibre board 128 kg/m3",
     mass["fibre_lining"], "make", "duty section 3 backup lining class (SCHACHT2004); anhydrous concentrate (X-MAT-22)"],
    ["3", "Graphite ram lining kit, t40, wetted faces", 1, "graphite ramming paste 1550 kg/m3",
     mass["ram_lining"], "make", "duty section 3 graphite wetted faces; DING2018_CL_REVIEW; liner change-out at the unit task 12 work order"],
    ["4", f"Anode bank, {AN['count']} x D{AN['D_mm']} x 1064 mm, {D['anode_imm_mm']:.0f} mm immersion", AN["count"],
     "graphite (chlorinated)", mass["anodes"], "buy",
     f"Faraday I = {D['I_A']} A at CE 0.85 (A-M-282); drawn j {j_anode:.4f} A/cm2; {D['chemistry']}"],
    ["5", f"Cathode plate set, {CA['count']} x 110 x 12 x 300 mm", CA["count"], "mild steel / clad",
     mass["cathodes"], "make", f"{D['metal_kg_d']:.4f} kg/d Cr metal on the D-DOCK feedstock ruling (A-M-284)"],
    ["6", f"Cu busbar ladder: 2 rails {BUS['rail_w_mm']} x {BUS['rail_t_mm']} mm ({BUS['mm2']} mm2 class) + straps + ceramic pads", 1,
     "Cu ETP + alumina pads", round(mass["bus_rails"] + mass["bus_straps"] + mass["ceramic_pads"], 1), "make",
     f"{D['I_A']} A at {D['cell_V']} V cell; {D['dc_kW']} kW dc + {D['hold_kW']} kW hold of {D['connected_kW']} kW connected; frame-isolated per AQS-STD-002 section 11"],
    ["7", f"Anode clamp bars 90 x 40 x 24 on the head plate ({AN['count'] * 2} x M10 studs, fasteners.csv item 1)", AN["count"],
     "carbon steel", mass["anode_clamps"], "make", "WORK_ORDER step 2/3: torque and megger check"],
    ["8", "Hood group: CS hood plate t6 + perimeter rim lip, on the graphite hot plate", 1,
     "carbon steel", mass["hood"], "make", "WO step 4; dry Cl2 headspace at 700 C (M7)"],
    ["9", "Hood hot plate, graphite t10 (expendable wetted face)", 1, "graphite",
     mass["hood_hot_plate"], "make", "duty section 3 wetted-face class; change-out at the unit task 12 work order"],
    ["10", f"Offtake riser DN50 OD {A['DN50_OD_mm']} t {A['DN50_wall_mm']}, z {BATH:.0f}..1594, flange + N5 vent at top", 1,
     "carbon steel (dry hot Cl2)", round(mass["offtake_riser"] + mass["riser_flange"] + mass["vent_stub"], 1), "make",
     "WO row 5; nozzles per the task-04 schedule (N5 vent top 800)"],
    ["11", "Return dip leg DN15, inside the riser annulus, bottom z 250", 1, "carbon steel",
     mass["dip_leg"], "make", "WO row 5; brine-fog return seal leg"],
    ["12", f"N4 CO export stub DN15 at +Y z 600 ({D['co_kg_d']} kg/d, fuel-gas class)", 1,
     "carbon steel (dry hot gas)", mass["co_stub"], "make",
     "task-04 schedule N4"],
    ["12b", f"N2/N3 feed chutes -X z 160: Cr2O3 chromite concentrate + carbon reductant ({D['feed_kg_d']} kg/d)", 2,
     "CS chute, refractory throat", mass["feed_chutes"], "make",
     "task-04 schedule N2/N3; A-M-284 feedstock ruling"],
    ["13", "N1 Cr-metal tap group: well DN80-class carbon + crest + discharge lip at +X z 600", 1,
     "carbon (ram class)", mass["cr_tap_group"], "make",
     "task-04 schedule N1 (solids, bore not calculated); WO step 6 trial-electrolysis tap"],
    ["14", "N5 drain well: carbon sump tube OD 60, DN15 bore, sump face z 50, flush at z 0", 1,
     "carbon (ram class)", mass["drain_well"], "make",
     "task-04 schedule N5 bottom DN15 Class 150; frozen-salt drain pig per WO step 6"],
    
    ["16", f"Thyristor rectifier + bath hold heaters, {D['connected_kW']} kW connected, IP54 cabinet", 1,
     "purchase item", "", "buy", "WO step 5/7; AQS-DUTY-072 section 4; A-M-282 class; mass per the purchase datasheet at order"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
fast = ('item,size,grade,qty,location,basis\n'
        '1,M10 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,6,anode clamp bars,study\n'
        '2,M8 x 25 hood bolts,ISO 898-1 8.8,12,hood rim flange,study\n'
        '3,M10 anchor,ISO 898-1 8.8,4,cell shell to slab,study\n')
(HERE / "fasteners.csv").write_text(fast)
wo = (f"# Work order CA_POT\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - D-DOCK feedstock program (A-M-284).\n\n"
      f"1. Fabricate the 800 x 800 x 1600 mm shell; line 70 mm (casing + ceramic fibre + ram) for {D['bath_T_C']:.0f} C service.\n"
      f"2. Set the {CA['count']} cathode plates on the pocket wall; hang the {AN['count']} x D{AN['D_mm']} mm anodes at {D['anode_imm_mm']:.0f} mm immersion.\n"
      f"3. Fit the busbar ladder ({BUS['mm2']} mm2 Cu class for {D['I_A']} A) and the DC drops; torque and megger-check.\n"
      f"4. Mount the hood, DN50 offtake with return dip leg, the N4 CO stub, and the N2/N3 feed chutes.\n"
      f"5. Wire the {D['connected_kW']} kW rectifier; interlock hood draft, bath temperature and cover position.\n"
      f"6. Test: dry-out and melt-up curve, then trial electrolysis; tap the Ca metal at N1, route the Cl2 export (water-treatment class).\n"
      f"7. Inspect against models/mfg/MO_CELL/export/cr_cell.step; record dimensions on the traveller.\n")
(HERE / "WORK_ORDER.md").write_text(wo)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
