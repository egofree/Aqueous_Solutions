"""CAST_LINE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, desk P4).

Graph revision AC. Study. Not a PE stamp. Reads params.json only; builds
headless with no manual step. Machine: permanent-mould cast line, 3 kg/d Cu
pour class (graph sizing, AQS-DUTY-072), 2 mould seats, 700 mm runout roller
table, manual operation (0 kW electrical duty on the node; no motor claimed).

Placement frame: x along the line (0 = melt-in tail, 1500 = discharge head),
y across (-Y rear guard plane, +Y operator guide rail), z up, origin at the
envelope corner. Connection faces are generic in the task-04 schedule, so the
compass assignment is the registered choice in params.json (layout_note):
N1 enters at -X into an under-deck refractory trough that bottom-fills both
mould stations through risers; N2 scrap drops at -Y; N3/N4 discharge lanes at
+X; N5 trough drain at bottom; N6 vent tap on the hood plenum at top.
Materials per docs-authority/duties/CAST_LINE.md section 3 (X-MAT-22): fine
graphite hot faces, CS backing/structure, 0 corrosion allowance on the dry CS
members (the hot faces are the graphite class). No measured rate is claimed.

Joint modeling convention (AQS-PLAN-006 A-core 4, every internal a solid):
interfaces that are bolted, plugged or press-fitted at fabrication are built
with touching or 0.1 mm interference faces so the build solid stays one
manifold body; each such joint carries its fastener row (A-core 7) or a BOM
note. Articulated clearance joints are not modeled apart: the trunnion pins
are press-fitted into the fork bores, and the roller shafts are press-fitted
into the pillow-block bushings.
"""
import csv, json, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
L, W, H = P["size_mm"]


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)


def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)


parts = {}          # named build parts (each becomes STEP/assembly member)
PORTS = {}          # connection planes for the task-04 cross-check (A-core 3)

# ---------------- frame: legs, rails, cross members, feet + M12 anchors ----------
frame = None
for lx in (100, 760, 1420):
    for ly in (100, 700):
        leg = box(lx - 40, ly - 40, 12, 80, 80, 568)                # leg to z 580: welded into the longitudinal rails
        foot = box(lx - 80, ly - 80, 0, 160, 160, 12)                # foot plate, 4 x M12 anchor holes (fasteners item 2)
        for ax in (lx - 55, lx + 55):
            for ay in (ly - 55, ly + 55):
                foot = foot.cut(rod(7.5, (ax, ay, -1), "Z", 16))
        leg = leg.union(foot)
        frame = leg if frame is None else frame.union(leg)
for ly0 in (50, 350, 650):                                          # longitudinal rails x 60..1440
    frame = frame.union(box(60, ly0, 570, 1380, 100, 30))
for rx0 in (100, 300, 500, 700, 880, 1120, 1340):                   # cross members
    frame = frame.union(box(rx0, 60, 552, 60, 680, 48))             # z 552..600: into the legs below and the rails above
frame = frame.union(box(0, 140, 570, 60, 520, 30))                  # tail plate at x = 0
parts["frame"] = frame

# ---------------- decks: mould-table deck (x 60..800) -----------------------------
DECK = box(60, 140, 590, 740, 520, 10)
for sy in (250, 550):                                               # seat openings 190 x 150 under each seat
    DECK = DECK.cut(box(205, sy - 75, 584, 190, 150, 20))
DECK = DECK.cut(box(50, 360, 584, 140, 80, 20))                     # pour pocket x 50..190, y 360..440
DECK = DECK.cut(rod(38, (340, 400, 584), "Z", 20))                  # drain well / trough pass at x 340
parts["deck"] = DECK

# ---------------- mould stations (2; graph design row moulds = 2) ------------------
seats = None
for sy in (250, 550):
    seat = box(190, sy - 85, 490, 220, 170, 12)                     # seat frame bolted under the deck
    for bx in (205 + 20, 190 + 220 - 20):
        for by in (sy - 65, sy + 65):
            seat = seat.cut(rod(5.5, (bx, by, 488), "Z", 16))
    platen = box(180, sy - 90, 502, 240, 180, 46)                   # steel backing platen
    platen = platen.cut(box(215, sy - 65, 502, 170, 130, 46))
    jack = box(208, sy - 72, 486, 184, 144, 116)                    # water jacket shell t6
    jack = jack.cut(box(214, sy - 66, 486, 172, 132, 122))
    jack = jack.union(box(200, sy - 8, 500, 8, 16, 40))             # CW in/out stubs to the machine-side manifold
    jack = jack.cut(rod(30, (300, sy, 484), "Z", 30))               # riser pass through the jacket floor
    m = seat.union(platen).union(jack)
    seats = m if seats is None else seats.union(m)
parts["mould_seats"] = seats

inserts = None
for sy in (250, 550):
    b = box(220, sy - 60, 490, 160, 120, 110)                       # fine-graphite insert, hot face
    b = b.cut(box(245, sy - 35, 540, 110, 70, 62))                  # open-top cavity 110 x 70 x 60 (see assumptions)
    b = b.cut(rod(12, (300, sy, 488), "Z", 60))                     # bottom-fill riser head into the cavity floor
    inserts = b if inserts is None else inserts.union(b)
parts["mould_inserts"] = inserts

# ---------------- melt path: refractory trough + graphite risers (below deck) ------
launder = box(40, 370, 96, 560, 60, 64).cut(box(46, 376, 100, 548, 48, 60))   # trough x 40..600, invert 100
launder = launder.union(box(280, 246, 96, 44, 300, 64).cut(box(286, 252, 100, 32, 288, 60)))  # header y 246..546
launder = launder.cut(rod(38, (340, 400, 30), "Z", 76))             # drain well pass, N5 below
launder = launder.union(box(40, 364, 90, 566, 72, 12))              # steel base under the refractory invert
launder = launder.union(box(40, 96, 120, 70, 40, 60).cut(box(46, 102, 124, 58, 28, 56)))  # trough head at the N1 face line
risers = None
for sy in (250, 550):
    b = rod(14, (300, sy, 150), "Z", 350)                           # graphite bottom-fill riser D28, melt bore D20 class
    risers = b if risers is None else risers.union(b)
launder = launder.union(risers)
launder = launder.union(tube(38, 15, (340, 400, 12), "Z", 92))      # drain well OD75 to N5 (frozen-slug pig tube)
parts["launder_group"] = launder

# N1 DN15 Class 150 port at the -X face, centre z 160 (molten metal) ----------------
n1 = cq.Workplane(cq.Plane(origin=(0, 400, 160), xDir=(0, 1, 0), normal=(-1, 0, 0))).circle(47.5).circle(10.6).extrude(-16)
n1 = n1.union(rod(10.65, (0, 400, 160), "X", 50))                   # OD21.3 spigot reaches the trough head (x 40..50)
PORTS["N1"] = ("DN15", "Class 150", "-X", 160.0)
parts["n1_port"] = n1

# N2 solids chute at the -Y face, mouth top edge at z 600 --------------------------
n2 = box(650, 0, 520, 100, 200, 80).cut(box(662, 6, 508, 76, 210, 72))
PORTS["N2"] = ("solids", "Class 150", "-Y", 600.0)
parts["scrap_chute"] = n2

# N3/N4 discharge lane guides at the +X face, mouth top edge at z 600 ---------------
n34 = box(1480, 250, 560, 20, 100, 40)
for gy in (550,):
    n34 = n34.union(box(1480, gy, 560, 20, 100, 40))
PORTS["N3"] = ("solids", "Class 150", "+X", 600.0)
PORTS["N4"] = ("solids", "Class 150", "+X", 600.0)
parts["lane_guides"] = n34

# N5 DN15 drain flange under the drain well, face plane z 50 ------------------------
n5 = tube(47.5, 10.6, (340, 400, 50), "Z", 12)                      # flange face at z = 50, down-facing
n5 = n5.union(tube(10.65, 8.2, (340, 400, 16), "Z", 34))            # capped spigot toward the pig tube
PORTS["N5"] = ("DN15", "Class 150", "bottom", 50.0)
parts["n5_port"] = n5

# ---------------- pour station: post, arm, saddle, 12 kg ladle --------------------
post = box(80, 620, 600, 80, 80, 300)                               # tilt post on the deck
post = post.union(box(70, 610, 588, 100, 100, 12))                  # base plate (2 x M16 T-bolts, fasteners item 1)
arm = box(115, 400, 830, 90, 260, 60)                               # tilt arm, y 400..660 over the post
arm = arm.union(box(120, 400, 870, 80, 100, 40))                    # saddle riser on the arm end
arm = arm.union(box(124, 340, 850, 52, 120, 26))                    # saddle bar across the trunnion lugs
ladle = rod(140, (150, 400, 610), "Z", 240)                         # shell OD280 x 240 (12 kg class, see assumptions)
ladle = ladle.cut(rod(115, (150, 400, 618), "Z", 232))              # shell bore
ladle = ladle.union(rod(115, (150, 400, 618), "Z", 30))             # t25 alumina working lining at the floor
ladle = ladle.union(box(130, 350, 810, 40, 26, 40))                 # trunnion lug rear (rim weld to the shell)
ladle = ladle.union(box(130, 424, 810, 40, 26, 40))                 # trunnion lug front (rim weld to the shell)
parts["pour_station"] = post.union(arm).union(ladle)

# ---------------- runout roller table 700 (design table_L_mm = 700), x 800..1500 ---
rollers = None
for rx in (870, 990, 1110, 1230, 1350):                             # roller pitch 120, D70 solid, top at 600
    r = rod(35, (rx, 140, 565), "Y", 520)                           # roller body y 140..660: ends past both rail faces
    r = r.union(rod(10, (rx, 120, 565), "Y", 40))                   # shaft y 120..160, press-fit into the front bushing
    r = r.union(rod(10, (rx, 640, 565), "Y", 40))                   # shaft y 640..680, press-fit into the rear bushing
    rollers = r if rollers is None else rollers.union(r)
    for by0 in (130, 630):                                          # 2-bolt pillow blocks, bore D20 over the shafts
        b = box(rx - 40, by0, 550, 80, 40, 30).cut(rod(9.95, (rx, by0 - 2, 565), "Y", 44))
        rollers = rollers.union(b)
roll_tab = rollers.union(box(800, 100, 540, 700, 110, 40))          # front bearer rail y 100..210, z 540..580:
roll_tab = roll_tab.union(box(800, 590, 540, 700, 110, 40))         # 3D volume overlap with the frame rails (no edge-only contact)
roll_tab = roll_tab.union(box(800, 788, 560, 700, 12, 40))          # front guide rail, the Y = 800 face pick
roll_tab = roll_tab.union(box(880, 680, 0, 60, 120, 560))           # guide-rail posts to the floor,
roll_tab = roll_tab.union(box(1320, 680, 0, 60, 120, 560))          # 120 deep so they overlap the frame cross members
roll_tab = roll_tab.union(box(860, 680, 0, 120, 120, 12))           # post feet plates
roll_tab = roll_tab.union(box(1300, 680, 0, 120, 120, 12))
roll_tab = roll_tab.union(box(1470, 120, 540, 30, 560, 30))         # end rail flush at x = 1500
parts["roller_table"] = roll_tab

# ---------------- static shear / stop block at the line end ------------------------
shear = box(1420, 40, 0, 80, 160, 21 + 600 - 21)                    # pedestal to the floor (z 0..600)
shear = shear.union(box(1400, 60, 620, 22, 120, 40))                # tool-steel knife insert at the -X face
shear = shear.union(box(1420, 40, 600, 80, 160, 200))               # block head z 600..800
shear = shear.union(box(1440, 40, 780, 60, 160, 60))                # strike / stop bar top
PORTS["shear_stop"] = ("solids", "-", "+X", 1500.0)
parts["shear_block"] = shear

# ---------------- vent hood plenum + N6 DN15 tap (top face, z 800) ------------------
hood = box(190, 300, 720, 500, 200, 66).cut(box(202, 312, 720, 476, 176, 66))
hood = hood.union(box(190, 300, 786, 500, 200, 6))                  # top plate t6
n6 = tube(47.5, 10.6, (420, 400, 788), "Z", 12)                     # DN15 flange face at z = 800, up-facing
n6 = n6.union(tube(10.65, 8.2, (420, 400, 770), "Z", 18))
PORTS["N6"] = ("DN15", "Class 150", "top", 800.0)
parts["vent_hood"] = hood
parts["n6_port"] = n6

# ---------------- guards: rear hot-zone panel + knife cover (A-MACH: guard drawn) ---
gr_base = box(60, 0, 0, 780, 12, 12)                                # floor channel under the rear posts
guard = None
for gx in (100, 400, 700):                                          # guard posts on the channel
    p = box(gx - 20, 0, 12, 40, 12, 588)
    p = p.union(box(gx - 40, 0, 0, 80, 40, 12))                     # post base plate overlapping the frame feet
    guard = p if guard is None else guard.union(p)
panel = box(60, 0, 600, 780, 12, 860).cut(box(76, 12, 616, 748, 12, 832))   # opening for the mesh (AQS-BLD-012)
guard = guard.union(panel)
gr_base = gr_base.union(box(60, 0, 0, 80, 60, 12)).union(box(680, 0, 0, 80, 60, 12))  # channel-to-foot gussets
shear_cover = box(1400, 20, 780, 100, 200, 6)                       # fixed cover over the knife zone
shear_cover = shear_cover.union(box(1400, 20, 786, 10, 200, 40)).union(box(1490, 20, 786, 10, 200, 40))
parts["guards"] = guard.union(gr_base).union(shear_cover)

# ---------------- mould-change gantry: columns + beam + hoist lug ------------------
gan = box(260, 60, 0, 80, 80, 1500).union(box(260, 660, 0, 80, 80, 1500))
gan = gan.union(box(260, 60, 1460, 80, 680, 40))                    # beam at the very top, z 1460..1500
gan = gan.union(box(262, 340, 1420, 76, 120, 40))                   # trolley body on the beam
gan = gan.union(box(292, 390, 1260, 16, 120, 160))                  # hook lug plate
gan = gan.cut(rod(20, (300, 450, 1300), "X", 40))                   # hook slot
parts["gantry"] = gan

# ---------------- union + checks ---------------------------------------------------
def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


ORDER = ["frame", "deck", "mould_seats", "mould_inserts", "launder_group", "n1_port",
         "scrap_chute", "lane_guides", "n5_port", "pour_station", "roller_table",
         "shear_block", "vent_hood", "n6_port", "guards", "gantry"]
bp = {k: parts[k] for k in ORDER}
full_solid = union_all([bp[k] for k in ORDER]).val()

# A-core 9 + X-PAR-04: all schedule connection hardware sits flush with or inside the
# envelope faces (verified below), so the registry solid is the whole build; metres + ASCII.
EXTERNAL = ()
out = HERE / "export"
out.mkdir(exist_ok=True)
assy = cq.Assembly()
comp = cq.Compound.makeCompound([bp[k].val() for k in ORDER])
assy.add(comp, name="CAST_LINE_permanent_mould_cast_line")
assy.export(str(out / "cast_line.step"), "STEP")
cq.exporters.export(full_solid, str(out / "cast_line.stl"), opt={"ascii": True})
cq.exporters.export(full_solid, str(out / "cast_line_in_envelope.stl"), opt={"ascii": True})
full_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CAST_LINE.stl"),
                                  tolerance=0.0005, angularTolerance=0.4, ascii=True)

bb = full_solid.BoundingBox()
inside = bool(bb.xmin >= -1 and bb.xmax <= L + 1 and bb.ymin >= -1 and bb.ymax <= W + 1
              and bb.zmin >= -1 and bb.zmax <= H + 1)
near = [round(bb.xmin, 1), round(bb.ymin, 1), round(bb.zmin, 1), round(bb.xmax, 1), round(bb.ymax, 1), round(bb.zmax, 1)]
exact = all(abs(a - b) <= 1 for a, b in
            ((bb.xmin, 0), (bb.ymin, 0), (bb.zmin, 0), (bb.xmax, L), (bb.ymax, W), (bb.zmax, H)))

# task-04 schedule cross-check (A-core 3): parse the CSV, compare face/height/bore/rating
sched = {}
with open(HERE.parents[2] / "docs-authority" / "nozzles" / "CAST_LINE.csv") as f:
    for row in csv.DictReader(f):
        sched[row["tag"]] = row
port_ok = {}
n_runs = 0
for tag, meta in P["connections"].items():
    row = sched.get(tag)
    bore, rating, face, height = PORTS[tag]
    ok = (row is not None and row["size"] == meta["size"] and row["rating"] == meta["rating"]
          and row["height_mm"] == str(meta["height"]) and row["face"] == meta.get("schedule_face", meta["face"]))
    port_ok[tag] = {"ok": bool(ok), "model_face": face, "schedule_face": row["face"] if row else None,
                    "model_height_plane_mm": height, "schedule_height_mm": meta["height"],
                    "model_bore": bore, "model_rating": rating}
    n_runs += 1

rho = {"frame": 7.85e-6, "deck": 7.85e-6, "mould_seats": 7.85e-6, "mould_inserts": 1.78e-6,
       "launder_group": 2.4e-6, "n1_port": 7.85e-6, "scrap_chute": 7.85e-6, "lane_guides": 7.85e-6,
       "n5_port": 7.85e-6, "pour_station": 7.9e-6, "roller_table": 7.85e-6, "shear_block": 7.85e-6,
       "vent_hood": 7.85e-6, "n6_port": 7.85e-6, "guards": 7.85e-6, "gantry": 7.85e-6}
mass = {k: round(bp[k].val().Volume() * rho[k], 1) for k in bp}
valid = all(v.val().isValid() for v in bp.values())

report = {
    "bbox_abs_mm": near,
    "bbox_exact": exact,
    "inside_size_mm": inside,
    "schedule_rows": len(sched),
    "connection_check": port_ok,
    "connections_ok": all(v["ok"] for v in port_ok.values()),
    "cad_stl_scope": "full build solid (no protruding external parts), metres, ASCII",
    "cap_solids": len(full_solid.Solids()),
    "all_parts_valid": valid,
    "design_row_check": {"moulds": 2, "table_L_mm_from_rollers_x": 700, "pour_kg_d": P["design"]["pour_kg_d"]},
    "part_mass_kg": mass,
    "total_model_mass_kg": round(sum(mass.values()), 1),
    "joint_convention": "bolted/press-fitted interfaces modeled touching or with 0.1 mm interference; fastener rows per A-core 7",
    "cadquery": "2.8.0",
}

# BOM regenerated from the model (AQS-PLAN-006 A-core 6; the prior 4-row bases carried over)
M = mass
rows = [
    ["1", "Machine frame weldment 1500 x 800 x 1500: 6 legs SHS 80 x 80 x 5, rails 100 x 30, cross members, tail plate, feet 160 x 160 x 12 with M12 anchor bosses (fasteners.csv item 2: 6 x M12 anchors)", 1,
     "carbon steel", M["frame"], "make",
     "WORK_ORDER step 1; envelope per duty section 2 (A-M-199 forming-class seat); level and shim at the feet"],
    ["2", "Mould-table deck t10, x 60..800 (seat passes, pour pocket, trough/drain passes cut)", 1, "carbon steel",
     M["deck"], "make", "WORK_ORDER step 2; deck plane is the z 600 outlet datum of the task-04 schedule"],
    ["3", "Mould seats x2: steel backing platen 240 x 180 x 46 + seat frame (4 x M12 per seat to the deck underside)", 2, "carbon steel",
     round(M["mould_seats"] * 0.6, 1), "make", "Duty section 3: steel backing platens around the graphite hot faces (DIETER1988 tool class)"],
    ["4", "Permanent-mould inserts x2, 160 x 120 x 110, open-top cavity 110 x 70 x 60 (0.462 L, about 3.7 kg Cu class)", 2, "fine graphite",
     M["mould_inserts"], "buy", "Duty section 3 (X-MAT-22): graphite hot face, chemically indifferent to the Cu melt (SCHACHT2004 ch. 8); change-out is the unit task 12 work order"],
    ["5", "Water-cooled jacket assemblies x2 (shell t6 + rear CW stubs toward the machine-side manifold)", 2, "carbon steel",
     round(M["mould_seats"] * 0.4, 1), "make",
     "Utility loop: no graph edge and no cooling rate; sized and commissioned at the task 12 first articles (params.json holds)"],
    ["6", "Melt path: refractory trough + steel base + trough head + distribution header + graphite bottom-fill risers x2 (D28) + drain well OD75", 1,
     "graphite + refractory ram in steel channel", M["launder_group"], "make",
     "Duty section 3 graphite launder class (SCHACHT2004 ch. 8); bottom fill is the registered layout choice (params.json layout_note); N1/N5 per the task-04 schedule"],
    ["7", "Pouring ladle 12 kg: shell OD280 x 240 t25 with two trunnion lugs + D115 x t25 refractory working lining (relining is a buy item)", 1,
     "carbon steel + alumina ram lining", round(M["pour_station"] * 0.55, 1), "make",
     "AQS-DUTY-072 section 3 (12 kg); hand tilt, no actuator; lining replaced at the task 12 traveller"],
    ["8", "Tilt post + arm + saddle on the deck, carriage-bolted to the shell lugs (2 x M16 T-bolts, fasteners.csv item 1)", 1, "carbon steel",
     round(M["pour_station"] * 0.45, 1), "make", "WORK_ORDER step 2; manual tilt bracket"],
    ["9", "Runout roller table 700 mm: 5 solid rollers D70 x 500 on D20 end shafts, press-fitted 2-bolt pillow blocks (25 mm bore class) + bearer rails + front guide rail on floor posts", 1,
     "carbon steel", M["roller_table"], "make",
     "Graph design row table_L_mm 700; hand-fed (0 kW node duty); the guide rail is the +Y face pick (params.json layout_note)"],
    ["10", "Static shear / stop block at the line end: CS pedestal to the floor + tool-steel knife insert + block head + strike bar", 1,
     "carbon steel + tool steel", M["shear_block"], "make",
     "Sprue/runner campaign-return prep (prior BOM basis); the shear campaign is a task 12 traveller item; also the +X face pick"],
    ["11", "Guards: rear hot-zone panel frame + mesh opening (AQS-BLD-012 class) on floor posts + channel, fixed knife cover", 1, "carbon steel + mesh",
     M["guards"], "make", "A-MACH: guard drawn; mesh fitted at fabrication"],
    ["12", "Vent hood plenum 500 x 200 over the pour zone + N6 DN15 Class 150 flanged tap at top z 800", 1, "carbon steel",
     round(M["vent_hood"] + M["n6_port"] * 0.4, 1), "make", "Task-04 schedule N6; ties to the plant vent header at detail design"],
    ["13", "Scheduled connection hardware: N1/N5/N6 DN15 Class 150 flanges OD95 + spigots (AQS-PIP-003 PIPING_CLASSES)", 1,
     "carbon steel", round(M["n1_port"] + M["n5_port"] + M["n6_port"] * 0.6, 1), "buy",
     "Ratings named from the task-04 schedule (A-MACH)"],
    ["14", "Mould-change gantry: 2 columns SHS 80 x 80 to 1500, top beam, trolley body, hook lug; SWL 250 kg manual chain hoist", 1,
     "carbon steel (gantry); hoist = purchase item", M["gantry"], "make (hoist: buy)",
     "Mould change-out is the unit task 12 work order; SWL 250 kg is a fit choice against the model seat mass, no load calc claimed"],
    ["15", "Bolt kit per fasteners.csv: item 1 M16 T-bolts x12, item 2 M12 anchors x6, M12 SHCS x28 (seats, pillow blocks, knife, trolley lug), M8 SHCS x8 (jacket covers)", 1,
     "steel fasteners", "", "buy", "A-core 7: every bolted joint holds a row; fasteners.csv is the unit record"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
