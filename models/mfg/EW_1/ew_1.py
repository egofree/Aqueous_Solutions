"""EW_1 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared reader
(models/mfg/lib/graph_node.py): the tank comes from the node sizing stamp written by
write_graph power() (AQS-DUTY-051 Rev F element-envelope sizing), the electrode counts and
currents are that stamp's outputs, the bus pack comes from docs-authority/BUSBAR.json
(AQS-BUS-001 Rev D), and the nozzle schedule is the unit's own CSV. The design and layout
blocks written back to params.json are builder-owned. This is the pattern builder: the
other EW cells follow its structure and never its figures.

Placement frame: x along the tank length, y along 720 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Tank inside (L - 20) x 700 x 750 mm at wall 10 mm (AQS-DUTY-051 Rev F section 1:
  length = cathodes x 100 + 2 x 75 ends, width = plate 600 + 2 x 50, depth = 150 sump +
  420 plate + 100 cover + 80 freeboard), so the shell fills the graph envelope exactly.
  The tank is open-topped. CPVC: EW_1 duty section 3 records the liquor at 77.5 C, above
  the AQS-STD-002 M5 PVC-U limit 60 C that the cooler EW cells meet at 55 C, so tank and
  racks run CPVC (X-MAT-09, M5).
- The cathode/anode counts, the bounding current and the current density are the
  AQS-DUTY-051 Rev F sizing outputs (graph params.sizing): the element-envelope current of
  this cell at current efficiency 0.85. Cathode titanium Grade 2 t3, anode titanium mesh
  t1.5 MMO coated, drawn as its sheet envelope (AQS-PLAN-006 rule 6; AQS-STD-002 section 9).
  PVC-U edge strips on the cathodes so the sheet peels.
- Bus per pole is the AQS-BUS-001 Rev D pack of this cell (docs-authority/BUSBAR.json,
  regenerated at the element-envelope current), go and return as a pair on FRP standoffs,
  nothing touches a tank lip (AQS-STD-002 section 11). Copper sits above the liquor line;
  every contact is the Ti tab against the Cu bar (AQS-STD-002 section 9).
- Nozzle hardware is drawn flush at the envelope faces - the house idiom of
  lib/nozzles.place_on_face - so the build keeps the bounding box the graph states.
  Face connections re-base into the cover gas zone band (z 690-748) in OD-aware slots:
  the issued datums (487/600/650) predate the Rev F zone stack, the re-basing is a named
  hold (WORK_ORDER W12), and the schedule datums stay in the CSV. A wall that runs out
  of slots re-faces its rest to the +X discharge-end wall with full hardware. The
  overflow discharge sits at the 680 fill line (the launder datum); the drain and the
  vent keep their issued datums. Atmospheric joints are hose barbs (duty section 4);
  the rectifier row is a conductor gland, not a hose (duty section 4).

Materials per docs-authority/duties/EW_1.md section 3: tank and racks CPVC; corrosion allowance 0 mm on the titanium and none on
polymers (AQS-STD-001 shop rule). No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
sys.path.insert(0, str(HERE.parents[2]))                  # the repository root, for the graph reader
from lib import dn, fasteners, materials, nozzles, graph_node  # noqa: E402

UNIT = "EW_1"
GN = graph_node.graph_node(UNIT)                          # the plant graph is the sole authority
S = GN.params.get("sizing") or {}
assert S.get("cathodes"), f"{UNIT}: no sizing stamp on the graph node (run the regeneration)"

P = json.loads((HERE / "params.json").read_text())   # the tracker-merged unit params (draw scripts read it)

# ------------------------------------------------------------------ cited constants
T_WALL = 10.0            # AQS-DUTY-051 section 1 (matches the issued envelope)
SUMP, PLATE_Z, COVER, FREE = 150.0, 420.0, 100.0, 80.0    # inside depth zones, AQS-DUTY-051
Z_FLOOR = T_WALL                                          # inner floor top
Z_PLATE0 = Z_FLOOR + SUMP                                 # 160
Z_PLATE1 = Z_PLATE0 + PLATE_Z                             # 580  (plate top)
Z_LIQ = Z_FLOOR + SUMP + PLATE_Z + COVER                  # 680  (fill line)
L, W, H = (float(v) for v in S["size_mm"])                # the sized tank (element envelope)
N_CAT, N_AN = int(S["cathodes"]), int(S["anodes"])        # AQS-DUTY-051 Rev F sizing outputs
I_BOUND = float(S["I_bounding_A"])                        # element-envelope bounding current
J_DUTY = float(S["j_A_m2"])                               # drawn current density at the bank
P_DC = float(S["P_dc_kW"])                                # cell DC at 2.12 V
V_LIQ_S = float(S["V_liq_m3"])                            # sizing fill
V_CELL = 2.12                                             # drivers ew_cell_voltage_V (USBM_CL_EW)
PITCH = 100.0                                             # cathode pitch, AQS-DUTY-051
PLATE_W, PLATE_H = 600.0, PLATE_Z                         # immersed plate face
T_CAT, T_AN = 3.0, 1.5                                    # duty section 3
END = 75.0                                                # inside end margin, AQS-DUTY-051
METAL = "Au"                                       # plated metal, AQS-DUTY-051 section 2
RHO = {"CPVC": materials.density("CPVC"), "Ti_G2": materials.density("Ti G2"),
       "Cu": materials.density("Cu"), "FRP": materials.density("FRP"),
       "PVC_U": materials.density("PVC_U")}
CA = materials.ca_for("CPVC")                            # 0.0, polymers: AQS-STD-001 rule

# channel DC on IA-DC-EW_n: the graph edge write_graph power() owns (cell + 0.3 V bus drop)
CHAN_KW = float(next(e['rate']['value'] for e in GN.graph['edges']
                     if e['stream_id'] == f'IA-DC-{UNIT}'))
# bus pack: the AQS-BUS-001 Rev D row of this cell (docs-authority/BUSBAR.json)
_bb = json.loads((HERE.parents[2] / "docs-authority" / "BUSBAR.json").read_text())
_bus_row = next(r for r in _bb["rows"] if r["cell"] == UNIT.replace('_', '-'))
BUS_A = int(_bus_row["A"])
BUS_PACK = (int(_bus_row["pack"].split(" x ")[0]), float(_bus_row["pack"].split(" x ")[1]), 6.3)

x_an = [T_WALL + END + k * PITCH for k in range(N_AN)]    # 75 mm off each inside end wall
x_cat = [x + PITCH / 2 for x in x_an[:N_CAT]]             # cathodes mid-gap, one per gap
y_lo, y_hi = 60.0, 660.0                                  # plate width 600 inside 700
TAB_W, TAB_TOP = 120.0, 691.0                             # Ti tab, y 300..420, top laps the bar
BAR_X0, BAR_X1 = x_cat[0], max(x_cat[-1] + T_CAT / 2, x_cat[0] + TAB_W)   # at least one tab width of copper
assert BAR_X1 > BAR_X0, (UNIT, BAR_X0, BAR_X1)
X_DIS = BAR_X1 - 35.0 if L >= 900 else float(L - 70)      # discharge-end connections
X_VENT = 5.0 * round((L / 2) / 5.0)                       # rim bridge at mid-length
assert x_an[-1] <= L - T_WALL - END + 0.1, (UNIT, x_an[-1], L)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


def r5(v):
    return 5.0 * round(v / 5.0)


parts = {}

# ---------------------------------------------------------------- tank: CPVC shell
tank = box(0, 0, 0, L, W, H).cut(box(T_WALL, T_WALL, Z_FLOOR, L - 2 * T_WALL,
                                     W - 2 * T_WALL, H - Z_FLOOR))
parts["tank"] = tank

# ---------------------------------------------------------------- electrode bank
cat, strips = None, None
for xc in x_cat:
    sheet = box(xc - T_CAT / 2, y_lo, Z_PLATE0, T_CAT, PLATE_W, PLATE_H)
    tab = box(xc - T_CAT / 2, 300.0, Z_PLATE1, T_CAT, TAB_W, TAB_TOP - Z_PLATE1)
    e = sheet.union(tab)
    cat = e if cat is None else cat.union(e)
    for ye in (48.0, 652.0):                              # PVC-U clip, 3 wall, 3 slot for t3
        clip = (box(xc - 4.5, ye, Z_PLATE0, 9.0, 20.0, PLATE_H)
                .cut(box(xc - 1.5, ye + 4.0, Z_PLATE0, 3.0, 12.0, PLATE_H)))
        strips = clip if strips is None else strips.union(clip)
parts["cathodes"] = cat
parts["edge_strips"] = strips
an = None
for xc in x_an:
    sheet = box(xc - T_AN / 2, y_lo, Z_PLATE0, T_AN, PLATE_W, PLATE_H)
    tab = box(xc - T_AN / 2, 300.0, Z_PLATE1, T_AN, TAB_W, TAB_TOP - Z_PLATE1)
    e = sheet.union(tab)
    an = e if an is None else an.union(e)
parts["anodes"] = an          # MMO mesh drawn as its sheet envelope (plan rule 6)

# ---------------------------------------------------------------- bus: AQS-BUS-001 pack pair
n_bars, bus_w, bus_t = BUS_PACK
PACK = {"+": (350.0 - bus_w, 350.0), "-": (370.0, 370.0 + bus_w)}   # pair, 20 mm creepage gap
BAR_Z = [(TAB_TOP + 2 * i * bus_t, TAB_TOP + (2 * i + 1) * bus_t)
         for i in range(n_bars)]                           # flats spaced one thickness apart
BEAM_X = []                                                # support stations along the bar
_k = 0
while 110.0 + 750.0 * _k <= BAR_X1 - 25.0:
    BEAM_X.append(110.0 + 750.0 * _k)
    _k += 1
if len(BEAM_X) == 1 and BAR_X1 - BAR_X0 > 100.0:
    BEAM_X.append(BAR_X1 - 35.0)                           # short tanks still get two seats
bus, pads = None, None
for pole, (y0, y1) in PACK.items():
    for (z0, z1) in BAR_Z:
        b = box(BAR_X0, y0, z0, BAR_X1 - BAR_X0, y1 - y0, bus_t)
        bus = b if bus is None else bus.union(b)
    for xb in BEAM_X:
        pad = box(xb - 5.0, y0, 683.0, 10.0, y1 - y0, 8.0)
        pads = pad if pads is None else pads.union(pad)
parts["bus_bars"] = bus
parts["standoff_pads"] = pads                # FRP (glass-polyester) per AQS-STD-002 section 11
beams = None
for xb in BEAM_X:                            # CPVC cross beams under the pads, bolted to the walls
    bm = box(xb - 30.0, T_WALL, 673.0, 60.0, W - 2 * T_WALL, 10.0)
    beams = bm if beams is None else beams.union(bm)
parts["support_beams"] = beams

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}           # barb lengths, study proportions
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"


def hose_id(dn_label):
    od, wall = dn.pipe_od(dn_label), dn.pipe_wall(dn_label)
    return round(od - 2 * wall, 2)                          # the pipe bore from the cited table


def style_of(row):
    if row["size"] == "cable":
        return "cable"                                      # power terminal: carried, never drawn
    if row["face"] == "bottom":
        return "drain"
    if row["face"] == "top":
        return "vent"
    if row["size"] == "solids":
        return "solids"
    if row["size"] == "cable":
        return "cable"
    if "rectifier" in (row.get("service") or ""):
        return "gland"
    return "hose"


GEO_FACE = {"inlet": "-Y", "outlet": "+Y", "bottom": "bottom", "top": "top"}
rows = sorted(GN.nozzles, key=lambda r: int(r["tag"][1:]))
ISSUED_H = {r["tag"]: r["height_mm"] for r in rows}
CARRIED = {r["tag"]: r for r in rows if style_of(r) == "cable"}
# along-face stations: every face connection re-bases into the cover gas zone band above
# the 680 mm fill line in OD-aware z slots (the issued datums 487/600/650 predate the Rev F
# zone stack - the re-basing is a named hold, WORK_ORDER W12; the schedule datums stay in
# the CSV). A wall that runs out of slots spills its rest to the +X discharge-end wall,
# where each spilled row takes a y/z slot of its own. The overflow discharge is the
# launder datum: it sits at the fill line on its issued face at the discharge end. The
# drain and the vent keep their issued bottom/top datums.
_clamped = {}
GAS_Z0, GAS_Z1 = 690.0, 748.0     # the cover gas zone band above the 680 fill line
LAYOUT = {}
END_WALL = []                     # spill rows: hardware re-faces to the +X discharge end
END_TAKEN = []                    # (y, z, r) slots already taken on the discharge end
_ovf = next((r for r in rows if r["face"] == "outlet"
             and "overflow" in (r.get("service") or "")), None)
for face in ("-Y", "+Y"):
    pool = [r for r in rows if GEO_FACE[r["face"]] == face and style_of(r) != "cable"
            and r is not _ovf]
    pool.sort(key=lambda r: int(r["tag"][1:]))
    n = len(pool)
    step = (X_DIS - 0.15 * L) / (n - 1) if n > 1 else 0.0
    taken = []                                    # (z centre, bore radius) slots on this wall
    for k, r in enumerate(pool):
        st = style_of(r)
        dnl = "DN15" if st == "solids" else r["size"]
        rb = dn.pipe_od(dnl) / 2.0
        z = None
        for cand in (GAS_Z0 + rb, GAS_Z0 + rb + 29.0, GAS_Z0 + rb + 58.0):
            if cand + rb <= GAS_Z1 + 0.1 and all(abs(cand - zt) >= rb + rt + 2.0
                                                 for zt, rt in taken):
                z = cand
                break
        x = (0.15 * L) + k * step
        if z is None:                             # the wall is full: the +X discharge-end wall
            for yc in (240.0, 360.0, 480.0, 120.0, 600.0):
                for zc in (GAS_Z0 + rb, GAS_Z0 + rb + 29.0, GAS_Z0 + rb - 29.0):
                    if zc - rb < 680.0 or zc + rb > 755.0:
                        continue
                    if all(abs(zc - zt) >= rb + rt + 2.0 or abs(yc - yt) >= rb + rt + 2.0
                           for yt, zt, rt in END_TAKEN):
                        END_TAKEN.append((yc, zc, rb))
                        END_WALL.append(dict(tag=r["tag"], style=st, dnl=dnl, y=yc, z=zc,
                                             issued=float(r["height_mm"])))
                        break
                else:
                    continue
                break
            else:
                raise SystemExit(f'{UNIT}: the +X discharge-end wall cannot take '
                                 f'{r["tag"]}; the schedule needs a design pass')
            continue
        taken.append((z, rb))
        LAYOUT[r["tag"]] = (st, dnl, face, z, x, 360.0)
# the overflow is the launder datum: it sits at the fill line on its issued face, at the
# discharge-end station
if _ovf is not None:
    _ovf_st = style_of(_ovf)
    LAYOUT[_ovf["tag"]] = (_ovf_st, "DN15" if _ovf_st == "solids" else _ovf["size"],
                           GEO_FACE[_ovf["face"]], 680.0, X_DIS, 360.0)
# the drain and the vent keep their issued bottom/top datum rows
_dr = next(r for r in rows if r["face"] == "bottom")
_dr_st = style_of(_dr)
LAYOUT[_dr["tag"]] = (_dr_st, _dr["size"], "bottom", float(_dr["height_mm"]), X_DIS, 360.0)
_ve = next(r for r in rows if r["face"] == "top" and style_of(r) != "cable")
LAYOUT[_ve["tag"]] = (style_of(_ve), _ve["size"], "top", float(_ve["height_mm"]), X_VENT, 360.0)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}   # duty section 4: inlets -Y face center, outlets +Y
noz, holes = None, None
drawn = {}
for tag, (style, dnl, face, h, x, y) in LAYOUT.items():
    row = next(r for r in rows if r["tag"] == tag)
    want = FACE_OF.get(row["face"], row["face"])
    assert want == face, (tag, row["face"], face)   # schedule face mapped per duty section 4
    if style in ("hose", "solids"):
        if style == "hose":
            s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=dn.pipe_od(dnl))
        else:
            s = nozzles.stub(dnl, 40.0)                     # solids: stub at DN15, labeled
    elif style == "gland":
        s = rod(16.0, (0, 0, 0), "Z", 40.0)                 # conductor gland boss
        s = s.cut(rod(dn.pipe_od(dnl) / 2 - dn.pipe_wall(dnl), (0, 0, -1), "Z", 42.0))
    elif style == "drain":
        s = nozzles.stub(dnl, 50.0)
    else:                                                   # vent: hangs to its 650 datum
        s = nozzles.stub(dnl, H - h)
    s = nozzles.place_on_face(s, face, float(h), (x, y if y is not None else 360.0), (L, W, H))
    noz = s if noz is None else noz.union(s)
    hr = dn.pipe_od(dnl) / 2
    if face == "-Y":
        holes = rod(hr, (x, -1.0, h), "Y", 12.0) if holes is None else holes.union(
            rod(hr, (x, -1.0, h), "Y", 12.0))
    elif face == "+Y":
        holes = rod(hr, (x, W - 11.0, h), "Y", 12.0) if holes is None else holes.union(
            rod(hr, (x, W - 11.0, h), "Y", 12.0))
    elif face == "bottom":
        holes = rod(hr, (x, y, -1.0), "Z", 12.0) if holes is None else holes.union(
            rod(hr, (x, y, -1.0), "Z", 12.0))
    elif face == "+X":
        holes = rod(hr, (L + 1.0, x, h), "X", 12.0) if holes is None else holes.union(
            rod(hr, (L + 1.0, x, h), "X", 12.0))
    clamp_note = (f"; issued height {ISSUED_H[tag]:g} clamped to {h:g} for the wall webs (W12)"
                  if h != ISSUED_H[tag] else "")
    drawn[tag] = {"style": style, "dn": dnl, "face": face, "height_mm": h,
                  "issued_height_mm": ISSUED_H[tag], "x_mm": x,
                  "note": SOLIDS_NOTE if style == "solids" else
                  ("conductor gland, not a hose (duty section 4)" if style == "gland" else
                   "atmospheric hose joint at the face (duty section 4)" if style == "hose" else
                   ("drain stub, boss to the 50 datum" if style == "drain" else
                    "vent stub hung to its 650 datum on the rim bridge")) + clamp_note}
for w in END_WALL:
    st, dnl = w["style"], w["dnl"]
    if st == "hose":
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=dn.pipe_od(dnl))
    elif st == "solids":
        s = nozzles.stub(dnl, 40.0)                     # solids: stub at DN15, labeled
    elif st == "gland":
        s = rod(16.0, (0, 0, 0), "Z", 40.0)             # conductor gland boss
        s = s.cut(rod(dn.pipe_od(dnl) / 2 - dn.pipe_wall(dnl), (0, 0, -1), "Z", 42.0))
    else:
        raise SystemExit(f"{UNIT}: unexpected spill style {st}")
    s = nozzles.place_on_face(s, "+X", w["z"], (0.0, w["y"]), (L, W, H))
    noz = s if noz is None else noz.union(s)
    hr = dn.pipe_od(w["dnl"]) / 2
    holes = rod(hr, (L + 1.0, w["y"], w["z"]), "X", 12.0) if holes is None else holes.union(
        rod(hr, (L + 1.0, w["y"], w["z"]), "X", 12.0))
    drawn[w["tag"]] = {"style": st, "dn": dnl, "face": "+X",
                       "height_mm": w["z"], "issued_height_mm": w["issued"],
                       "y_mm": w["y"],
                       "note": f"issued height {w['issued']:g} predates the Rev F zone stack; "
                               "the bore re-faces to the +X discharge-end wall in the cover "
                               "gas zone with its hardware (W12)"}
for tag, row in CARRIED.items():
    drawn[tag] = {"style": "carried", "dn": row["size"], "face": row["face"],
                  "height_mm": row["height_mm"], "schedule_rating": row["rating"],
                  "service": row["service"],
                  "note": "power terminal row (IA-DC-EW_n, DC bus bar) - a cable schedule row: "
                          "carried verbatim, never drawn"}
assert set(drawn) == {r["tag"] for r in rows}, \
    (UNIT, "schedule rows not all drawn or carried")
parts["nozzles"] = noz

# vent support: two posts on the inner walls and a rim bridge (schedule face "top" on an
# open tank); the vent stub hangs from the bridge down to its 650 mm datum.
posts = box(X_VENT - 15.0, T_WALL, 660.0, 30.0, 30.0, 100.0).union(
    box(X_VENT - 15.0, W - T_WALL - 30.0, 660.0, 30.0, 30.0, 100.0))
bridge = box(X_VENT - 30.0, T_WALL, H - 10.0, 60.0, W - 2 * T_WALL, 10.0)
vent_dn = next(t["size"] for t in rows if t["face"] == "top" and t["size"] != "cable")
bridge = bridge.cut(rod(dn.pipe_od(vent_dn) / 2, (X_VENT, 360.0, H - 11.0), "Z", 12.0))
parts["vent_support"] = posts.union(bridge)

tank = tank.cut(holes)
parts["tank"] = tank

# ---------------------------------------------------------------- process inventory (not a BOM part)
liq = box(T_WALL, T_WALL, Z_FLOOR, L - 2 * T_WALL, W - 2 * T_WALL, Z_LIQ - Z_FLOOR)
for k in ("cathodes", "anodes", "edge_strips", "support_beams", "nozzles"):
    liq = liq.cut(parts[k])
inv = {"liquor": liq}                        # fill line at the sized liquor volume

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / f"{UNIT.lower()}.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / f"{UNIT.lower()}.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / f"{UNIT}.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
active_m2 = N_CAT * 2 * (PLATE_W / 1000) * (PLATE_H / 1000)
j_drawn = I_BOUND / active_m2
a_cm2 = n_bars * (bus_w * bus_t) / 100.0
v_liq = inv["liquor"].val().Volume() / 1e9
rho = {"tank": "CPVC", "cathodes": "Ti_G2", "anodes": "Ti_G2", "edge_strips": "PVC_U",
       "bus_bars": "Cu", "standoff_pads": "FRP", "support_beams": "CPVC",
       "vent_support": "CPVC", "nozzles": "CPVC"}
mass = {k: round(v.val().Volume() * RHO[rho[k]] / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H], "graph_revision": GN.graph_revision,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "cathodes": {"count": N_CAT, "sheet_mm": [PLATE_W, PLATE_H, T_CAT], "pitch_mm": PITCH,
                 "active_m2_each": 0.504, "active_m2_bank": round(active_m2, 2),
                 "duty_basis": f"AQS-DUTY-051 Rev F section 2 row {UNIT}: the element-envelope "
                               f"current {I_BOUND:g} A needs {I_BOUND / 200.0:.3f} m2 at the duty "
                               f"density; the bank is {active_m2:.2f} m2 (the one-plate commercial "
                               f"minimum where the envelope current is smaller), drawn j "
                               f"{j_drawn:.1f} A/m2"},
    "anodes": {"count": N_AN, "sheet_envelope_mm": [PLATE_W, PLATE_H, T_AN],
               "basis": "Ti mesh t1.5 MMO, drawn as its sheet envelope (AQS-PLAN-006 rule 6)"},
    "bus": {"pack": f"{n_bars} x {bus_w:g} x {bus_t:g} mm per pole", "section_cm2": round(a_cm2, 1),
            "A_cm2_at_bound": round(I_BOUND / a_cm2, 1),
            "basis": f"pack verbatim from AQS-BUS-001 Rev D ({BUS_A} A basis, "
                     "docs-authority/BUSBAR.json), regenerated at the element-envelope current; "
                     "the same generator sizes this pack - not a model hold"},
    "liquor_m3": round(v_liq, 3), "liquor_fill_basis_m3": V_LIQ_S,
    "nozzles_drawn": drawn,
    "nozzle_clamped": sorted(_clamped),
    "nozzle_idiom": "hardware flush at the envelope faces (lib/nozzles.place_on_face default); "
                    "external hose makeup at the face plane; the power terminal row is a cable "
                    "schedule row, carried verbatim and never drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
by_style = {}
for tag, (style, dnl, *_r) in LAYOUT.items():
    by_style.setdefault((style, dnl), []).append(tag)
def _cnt(d, ts, word):
    return f"{len(ts)} x {d} {word}{'' if len(ts) == 1 else 's'} ({'/'.join(ts)})"


hose_txt = ", ".join(_cnt(d, ts, "barb")
                     for (st, d), ts in sorted(by_style.items()) if st == "hose")
extra_txt = ", ".join(_cnt(d, ts, "solids port" if st == "solids" else st)
                      for (st, d), ts in sorted(by_style.items()) if st not in ("hose",))
SOLIDS_TXT = ("solids at DN15 labeled bore not calculated (AQS-PLAN-006 W4); "
              if any(st == "solids" for st, _d in by_style) else "")
CABLE_TXT = ("the power terminal is a cable schedule row, carried verbatim and never drawn; "
             if CARRIED else "")
n_anchors = max(4, 2 * round(L / 670.0))
rows_bom = [
    ["1", f"CPVC tank shell, outside {L:g} x {W:g} x {H:g} mm, wall {T_WALL:g} mm, open top "
          f"(inside {L - 2 * T_WALL:g} x 700 x 750: sump 150 + plate 420 + cover 100 + freeboard 80)",
     1, "CPVC", mass["tank"], "make",
     "AQS-DUTY-051 Rev F section 1 wall 10 mm and zone stack; duty section 3 via the EW_1 page: "
     "77.5 C liquor runs CPVC (X-MAT-09; AQS-STD-002 M5 CPVC class); CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"CPVC support set: {len(BEAM_X)} cross beams 60 x 10 x 700 under the bus pads + vent "
          f"bridge 60 x 10 x 700 + 2 posts 30 x 30 x 100", 1, "CPVC",
     round(mass["support_beams"] + mass["vent_support"], 1), "make",
     "duty section 3 racks CPVC (X-MAT-09); AQS-STD-002 section 11 (no busbar touches a tank lip); CA 0 mm"],
    ["3", f"Cathode set: {N_CAT} sheets {PLATE_W:g} x {PLATE_H:g} x {T_CAT:g} mm Ti Grade 2 + "
          f"{N_CAT} hanger tabs 120 x {TAB_TOP - Z_PLATE1:g} x {T_CAT:g}, at {PITCH:g} mm pitch",
     N_CAT, "titanium Grade 2 (ASTM B265)", mass["cathodes"], "make",
     "AQS-DUTY-051 Rev F section 2 (plate 0.60 x 0.42, 0.504 m2 both faces); AQS-STD-002 "
     "section 9; CA 0 mm on titanium (duty section 3); annealed, no cold forming after anneal"],
    ["4", f"Anode set: {N_AN} meshes {PLATE_W:g} x {PLATE_H:g} x {T_AN:g} mm Ti + "
          f"{N_AN} hanger tabs 120 x {TAB_TOP - Z_PLATE1:g} x {T_AN:g}, MMO coated (RuO2-IrO2-TiO2)",
     N_AN, "titanium mesh, MMO coated", mass["anodes"], "buy",
     "duty section 3; AQS-STD-002 section 9; drawn as its sheet envelope (AQS-PLAN-006 rule 6); "
     "coat life is a vendor figure at the cell current density"],
    ["5", f"PVC-U edge strip clips, 9 x 20 x 420, slot 3 x 12, 2 per cathode", 2 * N_CAT,
     "PVC-U", "", "buy",
     "AQS-STD-002 section 9 (plastic edge strip so the sheet peels); cut-to-length stock, "
     "density per the supplier TDS at order"],
    ["6", f"Bus packs, go and return: 2 x ({n_bars} flats {bus_w:g} x {bus_t:g} x "
          f"{BAR_X1 - BAR_X0:g} mm, spaced one thickness) + 2 rectifier lugs 110 x {bus_w:g} x "
          f"{bus_t:g}", 1, "copper C101, painted", round(mass["bus_bars"], 1), "make",
     f"AQS-BUS-001 Rev D {UNIT.replace('_', '-')} row ({BUS_A} A basis, "
     "docs-authority/BUSBAR.json); pair per AQS-STD-002 section 11; copper above the liquor, "
     "contacts Ti-clad (section 9); CA 0 mm"],
    ["7", f"Standoff pads 10 x {bus_w:g} x 8 under the bus packs, one per pack per beam station",
     2 * len(BEAM_X), "FRP (glass-polyester)", mass["standoff_pads"], "buy",
     "AQS-STD-002 section 11 non-conductive standoffs"],
    ["8", f"Nozzle set, set-in PVC-U per docs-authority/nozzles/{UNIT}.csv: {hose_txt}"
          + (f"; {extra_txt}" if extra_txt else ""), len(LAYOUT), "CPVC",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric joints are hose (duty section 4); "
     + CABLE_TXT + SOLIDS_TXT + "barb profile is a study proportion (lib/nozzles.py)"],
    ["9", f"Rectifier, {CHAN_KW:.2f} kW cell channel on IA-DC-{UNIT} (floating, insulation "
          "monitor, protection current on trip)", 1, "purchase item", "", "buy",
     "duty sections 3 and 9, channel DC with the 0.3 V bus drop (AQS-STD-002 section 11); "
     "mass per the purchase datasheet at order"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows_bom)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 x 30 wedge anchor", fasteners.grade_for("PVC-U"), n_anchors, "tank to slab",
     "polymer-joint rule of AQS-PLAN-006 W5 (A4-70); supplier rule named per the plan"],
    [None, "M8 x 40", fasteners.grade_for("PVC-U"), 2 * len(BEAM_X),
     "support beams to the inner walls (2 per beam station)",
     "polymer-joint rule; study count, torque per the PVC-U supplier rule"],
    [None, "M8 x 40", fasteners.grade_for("PVC-U"), 4, "vent posts to the inner walls",
     "polymer-joint rule"],
    [None, "M6 x 25", fasteners.grade_for("PVC-U"), N_CAT + N_AN,
     "electrode tab clamps, one per tab through the Ti tab and the bus bar",
     "Ti-Cu lap per AQS-STD-002 sections 9 and 11; wet-aisle stainless; count from the model"],
    [None, "M10 x 35", fasteners.grade_for("PVC-U"), 6, "rectifier lugs, 3 per pole",
     "AQS-BUS-001 section 4 (bolted at the cell bus, overlap at least the bar width)"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["design"] = {
    "service": f"electrowinning cell, {METAL} cathode product; chloride liquor 55 C in / "
               "cell-to-cell launder out",
    "I_A": I_BOUND, "cell_V": V_CELL, "dc_kW": P_DC, "channel_dc_kW": CHAN_KW,
    "j_A_m2": J_DUTY, "cathodes": N_CAT, "anodes": N_AN, "pitch_mm": PITCH,
    "plate_immersed_mm": [PLATE_W, PLATE_H], "active_m2_per_cathode": 0.504,
    "tank_inside_mm": [L - 2 * T_WALL, W - 2 * T_WALL, H - T_WALL], "wall_mm": T_WALL,
    "liquor_m3": V_LIQ_S, "liquor_density_kg_m3": 1100,
    "bus_pack": f"{n_bars} x {bus_w:g} x {bus_t:g} mm Cu C101 per pole "
                f"(AQS-BUS-001 Rev D {UNIT.replace('_', '-')} row)",
    "basis": "AQS-DUTY-051 Rev F section 1 and the row of its section 2 for this cell "
             "(the element-envelope current at CE 0.85, 2.12 V); channel DC on "
             f"IA-DC-{UNIT} {CHAN_KW:.2f} kW with the 0.3 V bus drop.",
}
p["layout"] = {
    "frame": f"origin at the envelope corner; x along {L:g}, y along 720, z up",
    "electrodes": f"anodes at x {x_an[0]:g} + 100k ({N_AN}), cathodes at x {x_cat[0]:g} + 100k "
                  f"({N_CAT}); sheets y 60..660, z 160..580; tabs 120 wide rise to z 691 "
                  "(study contact arrangement, AQS-STD-002 section 9: Ti tab against the Cu bar "
                  "above the liquor line)",
    "bus": f"pack pair over the tab line: + y {350.0 - bus_w:g}..350, - y 370..{370.0 + bus_w:g} "
           "(20 mm creepage gap, AQS-STD-002 section 11); bars x "
           f"{BAR_X0:g}..{BAR_X1:g} on FRP pads at beam stations x "
           f"{'/'.join(f'{xb:g}' for xb in BEAM_X)}; rectifier lugs at the -X bar ends",
    "nozzle_spread": "the schedule gives face and height; the stations run in height order "
                     "along the wall, OD-aware (wall webs survive the bores between "
                     "z-overlapping bores, rounded down to 5 mm), vent bridge at x "
                     f"{X_VENT:g}, recorded per tag in check.nozzles_drawn with any "
                     "height clamp named",
    "vent_support": "the schedule vent is face top on an open tank: two PVC-U posts on the inner "
                    "walls carry a rim bridge at z 750..760; the stub hangs to its 650 datum",
    "drain": f"drain at the discharge-end sump (x {X_DIS:g}), flush at z 0, boss top at the 50 datum",
    "solids_ports": "solids rows drawn at DN15 and labeled bore not calculated (AQS-PLAN-006 W4); "
                    "hand/bin transfer interface" if any(v[0] == "solids" for v in LAYOUT.values())
                    else "none in this schedule",
    "hardware_idiom": "connection hardware flush at the envelope faces "
                      "(lib/nozzles.place_on_face default); nothing protrudes, bbox = size_mm",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids", "part_mass_kg")}))
