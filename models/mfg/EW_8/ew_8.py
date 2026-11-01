"""EW_8 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AC. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the design and layout blocks beside them are builder-owned). Built on the
EW_1 pattern per its WORK_ORDER recipe: every number is the EW_8 row of
AQS-DUTY-051 section 2 with duty section 9 (Rev B basis), the EW_8 rows of
docs-authority/nozzles/EW_8.csv and AQS-BUS-001, never a copy of EW_1 figures.

Placement frame: x along 470 mm, y along 720 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Tank inside 450 x 700 x 750 mm at wall 10 mm (AQS-DUTY-051 section 1: length =
  cathodes x 100 + 2 x 75 ends, width = plate 600 + 2 x 50, depth = 150 sump +
  420 plate + 100 cover + 80 freeboard), so the shell fills the graph envelope
  470 x 720 x 760 exactly. The tank is open-topped. PVC-U: the liquor arrives at
  55 C (EW_1 duty section 3 records the split; AQS-STD-002 M5 PVC-U limit 60 C),
  where EW_1 at 77.5 C runs CPVC.
- 3 cathodes / 4 anodes at 100 mm pitch (50 mm cathode-to-anode), plate
  immersed 0.60 x 0.42 m, both faces 0.504 m2 (AQS-DUTY-051 section 1; duty
  section 9: bounding 209 A at 138 A/m2). Cathode titanium Grade 2 t3, anode
  titanium mesh t1.5 MMO coated, drawn as its sheet envelope (AQS-PLAN-006 rule 6;
  AQS-STD-002 section 9). PVC-U edge strips on the cathodes so the sheet peels.
- Bus per pole is the published AQS-BUS-001 EW-8 pack, 1 x 20.0 x 6.3 mm flat copper
  C101 flat spaced one thickness apart; go and return run as a pair on FRP
  standoffs, nothing touches a tank lip (AQS-STD-002 section 11). Copper sits above
  the liquor line; every contact is the Ti tab against the Cu bar (AQS-STD-002
  section 9). Published at 178 A; the duty section 9 bounding current is a
  named hold (WORK_ORDER W12), re-sizing belongs to docs-authority/_ew_busbar.py.
- Nozzle hardware is drawn flush at the envelope faces - the house idiom of
  lib/nozzles.place_on_face - so the build keeps the bounding box the graph states.
  Atmospheric joints are hose barbs (duty section 4); a rectifier service row would
  be a conductor gland, not a hose. Solids rows are drawn at DN15 and labeled
  "bore not calculated" per AQS-PLAN-006 W4. Styles and x positions classify from
  the tracker-written schedule rows, so the build follows EW_8's own schedule.

Materials per docs-authority/duties/EW_8.md section 3 (via the EW_1 page 55 C
split): tank and racks PVC-U; corrosion allowance 0 mm on the titanium and none on
polymers (AQS-STD-001 shop rule). No measured rate is claimed anywhere.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = P["size_mm"]                                    # 470 x 720 x 760
REV = P["graph_revision"]

# ------------------------------------------------------------------ cited constants
T_WALL = 10.0            # AQS-DUTY-051 section 1 (matches the issued envelope)
SUMP, PLATE_Z, COVER, FREE = 150.0, 420.0, 100.0, 80.0    # inside depth zones, AQS-DUTY-051
Z_FLOOR = T_WALL                                          # inner floor top
Z_PLATE0 = Z_FLOOR + SUMP                                 # 160
Z_PLATE1 = Z_PLATE0 + PLATE_Z                             # 580  (plate top)
Z_LIQ = Z_FLOOR + SUMP + PLATE_Z + COVER                  # 680  (0.211 m3 fill line)
N_CAT, N_AN = 3, 4                           # AQS-DUTY-051 section 2 row EW_8
PITCH = 100.0                                             # cathode pitch, AQS-DUTY-051
PLATE_W, PLATE_H = 600.0, PLATE_Z                         # immersed plate face
T_CAT, T_AN = 3.0, 1.5                                    # duty section 3
I_BOUND, V_CELL = 209.0, 2.12                             # duty section 9 (Rev B basis)
DC_KW, CHAN_KW = 0.44, 0.51                         # cell / channel DC, duty section 9
J_DUTY = 138                                            # AQS-DUTY-051 section 2
LIQ_M3 = 0.211                                          # sizing fill, AQS-DUTY-051 section 2
BUS_PACK = (1, 20.0, 6.3)                       # AQS-BUS-001 Rev C EW-8 row
BUS_PUB = {"A": 178, "A_cm2": 1.3, "J": 141}
METAL = "Cd"                                       # plated metal, AQS-DUTY-051 section 2
RHO = {"PVC_U": materials.density("PVC-U"), "Ti_G2": materials.density("Ti G2"),
       "Cu": materials.density("Cu"), "FRP": materials.density("FRP")}
CA = materials.ca_for("PVC-U")                            # 0.0, polymers: AQS-STD-001 rule

x_an = [85.0 + k * PITCH for k in range(N_AN)]            # 75 mm off each end wall
x_cat = [135.0 + k * PITCH for k in range(N_CAT)]
BAR_X0, BAR_X1 = x_cat[0], x_cat[-1]                      # bus runs over the cathode row
X_DIS = BAR_X1 - 35.0 if L >= 900 else float(L - 70)      # discharge-end connections
X_VENT = 5.0 * round((L / 2) / 5.0)                       # rim bridge at mid-length
y_lo, y_hi = 60.0, 660.0                                  # plate width 600 inside 700
TAB_W, TAB_TOP = 120.0, 691.0                             # Ti tab, y 300..420, top laps the bar


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


def r5(v):
    return 5.0 * round(v / 5.0)


def spread(lo, hi, n):
    """n study x positions across [lo, hi], rounded to 5 mm."""
    if n <= 0:
        return []
    if n == 1:
        return [r5((lo + hi) / 2)]
    step = (hi - lo) / (n - 1)
    return [r5(lo + k * step) for k in range(n)]


parts = {}

# ---------------------------------------------------------------- tank: PVC-U shell
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
    lug = box(25.0, y0, BAR_Z[0][0], 110.0, y1 - y0, bus_t)  # rectifier lug, overlap = bar width
    bus = bus.union(lug)
    for xb in BEAM_X:
        pad = box(xb - 5.0, y0, 683.0, 10.0, y1 - y0, 8.0)
        pads = pad if pads is None else pads.union(pad)
parts["bus_bars"] = bus
parts["standoff_pads"] = pads                # FRP (glass-polyester) per AQS-STD-002 section 11
beams = None
for xb in BEAM_X:                            # PVC-U cross beams under the pads, bolted to the walls
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
    if row["face"] == "bottom":
        return "drain"
    if row["face"] == "top":
        return "vent"
    if row["size"] == "solids":
        return "solids"
    if "rectifier" in (row.get("service") or ""):
        return "gland"
    return "hose"


# tag: (style, dn, face, height_mm, x, y), classified from the unit's own schedule rows.
# Along-face x: one pool per face, overflow pinned at the discharge end, slots rounded to
# 5 mm, and any two rows on a face kept apart by (od_a + od_b) / 2 + 15 mm of wall web.
rows = sorted(P["nozzles"], key=lambda r: int(r["tag"][1:]))
GEO_FACE = {"inlet": "-Y", "outlet": "+Y", "bottom": "bottom", "top": "top"}
ovf = next(r["tag"] for r in rows
           if r["face"] == "outlet" and r["size"] == "DN50" and r["height_mm"] == 487)


def nat(t):
    return int(t[1:])


xs = {}
small = L < 900
for face in ("-Y", "+Y"):
    pool = [r["tag"] for r in rows if GEO_FACE[r["face"]] == face]
    pool = sorted(pool, key=nat)
    if face == "+Y":
        pool = sorted((t for t in pool if t != ovf), key=nat) + [ovf]   # discharge end last
    lo, hi = (70.0, float(L - 70)) if small else              ((0.15 * L, 0.30 * L) if face == "-Y" else (0.15 * L, X_DIS))
    xs.update(dict(zip(pool, spread(lo, hi, len(pool)))))
LAYOUT = {}
for r in rows:
    st = style_of(r)
    dnl = "DN15" if st == "solids" else r["size"]
    face = GEO_FACE[r["face"]]
    if face in ("-Y", "+Y"):
        x = xs[r["tag"]]
        assert 45.0 <= x <= L - 45.0, (r["tag"], x)
    elif face == "bottom":
        x = X_DIS
    else:
        x = X_VENT
    LAYOUT[r["tag"]] = (st, dnl, face, r["height_mm"], x, 360.0)
for f in ("-Y", "+Y"):
    col = sorted((v[4], t) for t, v in LAYOUT.items() if v[2] == f)
    for (a, ta), (b, tb) in zip(col, col[1:]):
        need = (dn.pipe_od(LAYOUT[ta][1]) + dn.pipe_od(LAYOUT[tb][1])) / 2 + 15.0
        assert b - a >= need, ((ta, tb), a, b, need)    # wall webs survive the bores
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
    drawn[tag] = {"style": style, "dn": dnl, "face": face, "height_mm": h, "x_mm": x,
                  "note": SOLIDS_NOTE if style == "solids" else
                  ("conductor gland, not a hose (duty section 4)" if style == "gland" else
                   "atmospheric hose joint at the face (duty section 4)" if style == "hose" else
                   ("drain stub, boss to the 50 datum" if style == "drain" else
                    "vent stub hung to its 650 datum on the rim bridge"))}
parts["nozzles"] = noz

# vent support: two posts on the inner walls and a rim bridge (schedule face "top" on an
# open tank); the vent stub hangs from the bridge down to its 650 mm datum.
posts = box(X_VENT - 15.0, T_WALL, 660.0, 30.0, 30.0, 100.0).union(
    box(X_VENT - 15.0, W - T_WALL - 30.0, 660.0, 30.0, 30.0, 100.0))
bridge = box(X_VENT - 30.0, T_WALL, H - 10.0, 60.0, W - 2 * T_WALL, 10.0)
vent_dn = next(t["size"] for t in rows if t["face"] == "top")
bridge = bridge.cut(rod(dn.pipe_od(vent_dn) / 2, (X_VENT, 360.0, H - 11.0), "Z", 12.0))
parts["vent_support"] = posts.union(bridge)

tank = tank.cut(holes)
parts["tank"] = tank

# ---------------------------------------------------------------- process inventory (not a BOM part)
liq = box(T_WALL, T_WALL, Z_FLOOR, L - 2 * T_WALL, W - 2 * T_WALL, Z_LIQ - Z_FLOOR)
for k in ("cathodes", "anodes", "edge_strips", "support_beams", "nozzles"):
    liq = liq.cut(parts[k])
inv = {"liquor": liq}                        # 0.211 m3 fill line, AQS-DUTY-051 section 2

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="EW_8")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "ew_8.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "ew_8.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "EW_8.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [float(v) for v in (L, W, H)]))
active_m2 = N_CAT * 2 * (PLATE_W / 1000) * (PLATE_H / 1000)
j_drawn = I_BOUND / active_m2
a_cm2 = n_bars * (bus_w * bus_t) / 100.0
v_liq = inv["liquor"].val().Volume() / 1e9
rho = {"tank": "PVC_U", "cathodes": "Ti_G2", "anodes": "Ti_G2", "edge_strips": "PVC_U",
       "bus_bars": "Cu", "standoff_pads": "FRP", "support_beams": "PVC_U",
       "vent_support": "PVC_U", "nozzles": "PVC_U"}
mass = {k: round(v.val().Volume() * RHO[rho[k]] / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H], "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "cathodes": {"count": N_CAT, "sheet_mm": [PLATE_W, PLATE_H, T_CAT], "pitch_mm": PITCH,
                 "active_m2_each": 0.504, "active_m2_bank": round(active_m2, 2),
                 "duty_basis": f"AQS-DUTY-051 section 1; {I_BOUND:g} A at {J_DUTY} A/m2 = "
                               f"{I_BOUND / J_DUTY:.2f} m2 against the {active_m2:.2f} m2 bank "
                               f"({abs(j_drawn - J_DUTY) / J_DUTY * 100:.1f} % rounding, drawn bank governs)"},
    "anodes": {"count": N_AN, "sheet_envelope_mm": [PLATE_W, PLATE_H, T_AN],
               "basis": "Ti mesh t1.5 MMO, drawn as its sheet envelope (AQS-PLAN-006 rule 6)"},
    "bus": {"pack": f"{n_bars} x {bus_w:g} x {bus_t:g} mm per pole", "section_cm2": round(a_cm2, 1),
            "A_cm2_at_bound": round(I_BOUND / a_cm2, 1),
            "published_A_cm2": BUS_PUB["J"], "published_current_A": BUS_PUB["A"],
            "note": f"pack verbatim from the published AQS-BUS-001 EW-8 row ({BUS_PUB['A']} A "
                    f"basis, {BUS_PUB['J']} A/cm2 published). At the duty section 9 bounding "
                    f"{I_BOUND:g} A the same pack runs {I_BOUND / a_cm2:.0f} A/cm2; the bus "
                    "standard regenerates from the duty current in docs-authority/_ew_busbar.py - "
                    "re-sizing is that generator's run, not the model's (named hold, WORK_ORDER W12)."},
    "liquor_m3": round(v_liq, 3), "liquor_fill_basis_m3": LIQ_M3,
    "nozzles_drawn": drawn,
    "nozzle_idiom": "hardware flush at the envelope faces (lib/nozzles.place_on_face default); "
                    "external hose makeup at the face plane",
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
n_anchors = max(4, 2 * round(L / 670.0))
rows_bom = [
    ["1", f"PVC-U tank shell, outside {L} x {W} x {H} mm, wall {T_WALL:g} mm, open top "
          f"(inside {L - 2 * T_WALL:g} x 700 x 750: sump 150 + plate 420 + cover 100 + freeboard 80)",
     1, "PVC-U", mass["tank"], "make",
     "AQS-DUTY-051 section 1 wall 10 mm and zone stack; duty section 3 via the EW_1 page: 55 C "
     "liquor stays PVC-U (AQS-STD-002 M5, limit 60 C); CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"PVC-U support set: {len(BEAM_X)} cross beams 60 x 10 x 700 under the bus pads + vent "
          f"bridge 60 x 10 x 700 + 2 posts 30 x 30 x 100", 1, "PVC-U",
     round(mass["support_beams"] + mass["vent_support"], 1), "make",
     "duty section 3 racks PVC-U; AQS-STD-002 section 11 (no busbar touches a tank lip); CA 0 mm"],
    ["3", f"Cathode set: {N_CAT} sheets {PLATE_W:g} x {PLATE_H:g} x {T_CAT:g} mm Ti Grade 2 + "
          f"{N_CAT} hanger tabs 120 x {TAB_TOP - Z_PLATE1:g} x {T_CAT:g}, at {PITCH:g} mm pitch",
     N_CAT, "titanium Grade 2 (ASTM B265)", mass["cathodes"], "make",
     "AQS-DUTY-051 section 1 (plate 0.60 x 0.42, 0.504 m2 both faces); AQS-STD-002 section 9; "
     "CA 0 mm on titanium (duty section 3); annealed, no cold forming after anneal"],
    ["4", f"Anode set: {N_AN} meshes {PLATE_W:g} x {PLATE_H:g} x {T_AN:g} mm Ti + "
          f"{N_AN} hanger tabs 120 x {TAB_TOP - Z_PLATE1:g} x {T_AN:g}, MMO coated (RuO2-IrO2-TiO2)",
     N_AN, "titanium mesh, MMO coated", mass["anodes"], "buy",
     "duty section 3; AQS-STD-002 section 9; drawn as its sheet envelope (AQS-PLAN-006 rule 6); "
     "coat life is a vendor figure at the cell current density"],
    ["5", f"PVC-U edge strip clips, 9 x 20 x 420, slot 3 x 12, 2 per cathode", 2 * N_CAT,
     "PVC-U", "", "buy",
     "AQS-STD-002 section 9 (plastic edge strip so the sheet peels); cut-to-length stock, "
     "density per the supplier TDS at order"],
    ["6", f"Bus pack, go and return: 2 x ({n_bars} flat {bus_w:g} x {bus_t:g} x "
          f"{BAR_X1 - BAR_X0:g} mm, spaced one thickness) + 2 rectifier lugs 110 x {bus_w:g} x "
          f"{bus_t:g}", 1, "copper C101, painted", round(mass["bus_bars"], 1), "make",
     f"AQS-BUS-001 Rev C EW-8 row ({BUS_PUB['A_cm2']} cm2 class, published at {BUS_PUB['A']} A); "
     "pair per AQS-STD-002 section 11; copper above the liquor, contacts Ti-clad (section 9); "
     "CA 0 mm"],
    ["7", f"Standoff pads 10 x {bus_w:g} x 8 under the bus packs, one per pack per beam station",
     2 * len(BEAM_X), "FRP (glass-polyester)", mass["standoff_pads"], "buy",
     "AQS-STD-002 section 11 non-conductive standoffs"],
    ["8", f"Nozzle set, set-in PVC-U per docs-authority/nozzles/EW_8.csv: {hose_txt}"
          + (f"; {extra_txt}" if extra_txt else ""), len(LAYOUT), "PVC-U",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric joints are hose (duty section 4); "
     + SOLIDS_TXT + "barb profile is a study proportion (lib/nozzles.py)"],
    ["9", f"Rectifier, {CHAN_KW} kW cell channel on IA-DC-EW_8 (floating, insulation monitor, "
          "protection current on trip)", 1, "purchase item", "", "buy",
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
    "I_A": I_BOUND, "cell_V": V_CELL, "dc_kW": DC_KW, "channel_dc_kW": CHAN_KW,
    "j_A_m2": J_DUTY, "cathodes": N_CAT, "anodes": N_AN, "pitch_mm": PITCH,
    "plate_immersed_mm": [PLATE_W, PLATE_H], "active_m2_per_cathode": 0.504,
    "tank_inside_mm": [L - 2 * T_WALL, W - 2 * T_WALL, H - T_WALL], "wall_mm": T_WALL,
    "liquor_m3": LIQ_M3, "liquor_density_kg_m3": 1100,
    "bus_pack": f"{n_bars} x {bus_w:g} x {bus_t:g} mm Cu C101 per pole (AQS-BUS-001 Rev C EW-8 row)",
    "basis": "AQS-DUTY-051 Rev C section 1 and the EW_8 row of its section 2; duty section 9 "
             "supersedes the 2.5 V / CE 1.0 figures (Rev B basis: CE 0.85, 2.12 V); channel DC "
             f"on IA-DC-EW_8 {CHAN_KW} kW with the 0.3 V bus drop.",
}
p["layout"] = {
    "frame": f"origin at the envelope corner; x along {L}, y along 720, z up",
    "electrodes": f"anodes at x 85 + 100k ({N_AN}), cathodes at x 135 + 100k ({N_CAT}); sheets "
                  "y 60..660, z 160..580; tabs 120 wide rise to z 691 (study contact arrangement, "
                  "AQS-STD-002 section 9: Ti tab against the Cu bar above the liquor line)",
    "bus": f"pack pair over the tab line: + y {350.0 - bus_w:g}..350, - y 370..{370.0 + bus_w:g} "
           "(20 mm creepage gap, AQS-STD-002 section 11); bars x "
           f"{BAR_X0:g}..{BAR_X1:g} on FRP pads at beam stations x "
           f"{'/'.join(f'{xb:g}' for xb in BEAM_X)}; rectifier lugs at the -X bar ends",
    "nozzle_spread": "the schedule gives face and height only; the along-face x positions are "
                     "this layout's study choice (overflow at the discharge end x "
                     f"{X_DIS:g}, vent bridge at x {X_VENT:g}, the rest spread clear of the "
                     "largest bore), recorded per tag in check.nozzles_drawn",
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

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "liquor_m3", "part_mass_kg")}))
