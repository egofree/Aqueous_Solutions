"""Shared close-out builder for the X-FARM unit manufacturing models (AQS-PLAN-006
section 2 work order; section 5 acceptance A-core, A-FARM).

One shared exporter, twelve thin per-unit sources. Each `models/mfg/<UNIT>/<unit>.py`
carries that unit's SPEC (the solids the node and duty name beside the form-class
shell, the make-or-buy rows, the fastener rows) and a `parts(P)` function; this module
draws the schedule nozzles, exports, checks and writes. Conventions are the accepted
ones:

- Geometry: the Oct-31 form-class build (farm_hab FORMS) is confirmed by the rebuild;
  the parts the duty section 3 or the node design block name are drawn beside it
  (media envelopes, ramps, screens, the purchased lamp and drier envelopes per plan
  rule 6). Nothing is resized: a build that leaves `size_mm` is reported (plan rule 3).
- Nozzles: every row of `docs-authority/nozzles/<UNIT>.csv` is drawn at tag, face,
  height and bore as an atmospheric open-bore tube stub flush at the envelope face
  (duty section 4: DN15/DN50, no flange class, atmospheric tube or hose; no flange is
  drawn - the W4 110 % rule; the schedule rating column is carried verbatim as text).
  A schedule datum above the build is drawn flush at the envelope top with the
  stale-datum note (the GLASS_BURNOUT idiom); the drain is flush at the envelope
  bottom; the vent is flush at the envelope top.
- Exports: STEP assembly and a closed, manifold STL (mm) under `export/`;
  `cad/stl/<UNIT>.stl` replaced from the build solid, ASCII metres (X-PAR-04
  envelope registry; the CRYO_ASU treatment where the build leaves the node box).
- WORK_ORDER.md is the hand-authored W1-W12 item beside the model (AQS-PLAN-006
  section 2); no builder writes it, so a rebuild never clobbers the work order.

Run: $CADQUERY_PYTHON models/mfg/<UNIT>/<unit>.py
"""
import csv
import json
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))                 # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))      # repo root: models.*

from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                     # noqa: E402
from models.mfg import farm_hab                     # noqa: E402

FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 50.0                                     # side-wall stub set-in length
VENT_LEN = 40.0                                     # top/bottom flush stub length


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def od_of(row):
    return dn.pipe_od(row["size"]) if row["size"].startswith("DN") else dn.pipe_od("DN15")


def liner_bag(P, top_clearance=0.0):
    """The sec3 liner as the sheet the params name: floor plate plus four wall plates
    (the GROW_BED ponded-zone idiom), not the Oct-31 solid block. `top_clearance`
    hangs the bag top below the rim (tank class, clear of the lid)."""
    L, W, H = (float(v) for v in P["size_mm"])
    t = float(P.get("wall_mm", 10))
    lt = float(P.get("liner_mm") or 0)
    if lt <= 0:
        return None
    ix, iy = L - 2 * t, W - 2 * t
    hb = H - 2 * t - top_clearance
    bag = box(t, t, t, ix, iy, lt)
    bag = bag.union(box(t, t, t + lt, ix, lt, hb - lt))                       # -Y wall
    bag = bag.union(box(t, t + iy - lt, t + lt, ix, lt, hb - lt))             # +Y wall
    bag = bag.union(box(t, t + lt, t + lt, lt, iy - 2 * lt, hb - lt))         # -X wall
    bag = bag.union(box(t + ix - lt, t + lt, t + lt, lt, iy - 2 * lt, hb - lt))
    return bag


def draw_nozzles(P, spec):
    """All schedule rows as flush tube stubs; returns (union, drawn record)."""
    L, W, H = (float(v) for v in P["size_mm"])
    schedule = P["nozzles"]
    groups = {}
    for r in schedule:
        face = FACE_OF.get(r["face"], r["face"])
        if face in ("-Y", "+Y"):
            groups.setdefault((face, float(r["height_mm"])), []).append(r)
    layout_x = {}
    for (face, z), rows in sorted(groups.items()):
        rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
        span = sum(od_of(r) + 8.0 for r in rows) - 8.0
        assert span <= L - 120.0, (face, z, span)
        x = max(80.0, (L - span) / 2)
        for r in rows:
            w = od_of(r) / 2
            layout_x[r["tag"]] = round(x + w, 1)
            x += 2 * w + 8.0
    noz, drawn = None, {}
    for r in schedule:
        tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
        face = FACE_OF.get(r["face"], r["face"])
        od = od_of(r)
        note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
        if r["face"] == "bottom":                          # drain: flush at the base
            s = tube_z("DN15", STUB_LEN)
            s = nozzles.place_on_face(s, "bottom", 0.0,
                                      spec.get("drain_xy", (L / 2, W / 2)), (L, W, H))
            note = ("drain flush at the envelope bottom; the 50 datum is the schedule "
                    "placeholder at the base")
            drawn_h = 0.0
        elif r["face"] == "top":                           # vent: flush at the top face
            s = tube_z("DN15", VENT_LEN)
            s = nozzles.place_on_face(s, "top", 0.0,
                                      spec.get("vent_xy", (L / 2, W / 2)), (L, W, H))
            if abs(h - H) > 1.0:
                note += (f"; the schedule datum z {h:g} predates the build height "
                         f"{H:g} - drawn flush at the envelope top (hold, W12)")
            drawn_h = H
        else:
            z_draw = h
            if h + od / 2 > H - 5.0:                       # stale datum above the build
                z_draw = H - od / 2                        # top of the stub flush at H
                note += (f"; the schedule datum z {h:g} sits at or above the "
                         f"build height {H:g} - drawn flush at the envelope top "
                         "(hold, WORK_ORDER W12)")
            s = tube_z(dnl if dnl.startswith("DN") else "DN15", STUB_LEN)
            s = nozzles.place_on_face(s, face, z_draw, (layout_x[tag], W / 2), (L, W, H))
            drawn_h = z_draw
        noz = s if noz is None else noz.union(s)
        drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
                      "drawn_height_mm": drawn_h,
                      "xy_mm": [layout_x.get(tag), round(float(W) / 2, 1)]
                      if layout_x.get(tag) is not None else list(spec.get("drain_xy", (L / 2, W / 2))),
                      "schedule_rating": r["rating"], "service": r["service"],
                      "note": note}
    return noz, drawn


def unit_parts(P, spec):
    """The full part dict: form-class shell + spec extras + liner + media + nozzles."""
    build_P = {k: v for k, v in P.items() if k not in spec.get("drop_keys", ())}
    parts = dict(farm_hab.FORMS[P["form"]](build_P))
    if spec.get("liner_bag"):
        bag = liner_bag(build_P, spec.get("liner_top_clearance", 0.0))
        if bag is not None:
            parts["liner"] = bag
    for name, fn in spec.get("extras", {}).items():
        parts[name] = fn(build_P)
    noz, _ = draw_nozzles(build_P, spec)
    if noz is not None:
        parts["nozzles"] = noz
    return parts


def _masses(P, spec, parts):
    default = P.get("material_class", "HDPE")
    rho_map = spec.get("rho_map", {})
    mass = {}
    for k, v in parts.items():
        label = rho_map.get(k, default)
        rho = materials.density(label)
        mass[k] = round(v.val().Volume() * 1e-9 * rho, 1) if rho else 0.0
    return mass


def build_and_export(here, spec):
    """The shared close-out pass for one unit (bench_prep idiom)."""
    here = pathlib.Path(here)
    UNIT = spec["unit"]
    GN = graph_node.graph_node(UNIT)   # the plant graph is the sole authority
    P = GN.as_params()               # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
    P.update({k: v for k, v in json.loads((here / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned form keys only (form/material class/wall do not live on the graph)
    L, W, H = (float(v) for v in P["size_mm"])
    parts = unit_parts(P, spec)

    asm = cq.Assembly(name=UNIT)
    for k, v in parts.items():
        asm.add(v, name=k)
    out = here / "export"
    out.mkdir(exist_ok=True)
    step_export.export_step(asm, str(out / f"{UNIT.lower()}.step"))

    solid = None
    for k, v in parts.items():
        solid = v if solid is None else solid.union(v)
    solid_val = solid.val()
    solid_val.exportStl(str(out / f"{UNIT.lower()}.stl"), tolerance=0.5,
                        angularTolerance=0.4, ascii=True)
    # cad/stl is the envelope registry in metres (X-PAR-04): replaced from the build
    # solid - UNLESS the build leaves the node box and no in-envelope module fills it,
    # in which case the registry keeps the study envelope box (the X-PAR-04 gate: the
    # registry bbox matches size_mm within 1 mm) and the full build lives in export/
    # and the STEP, the misfit section-7-reported
    if not spec.get("cad_stl_envelope_box"):
        solid_val.scale(0.001).exportStl(str(here.parents[2] / "cad" / "stl" / f"{UNIT}.stl"),
                                         tolerance=0.0005, angularTolerance=0.4, ascii=True)

    dims = stl_bbox_mm(str(out / f"{UNIT.lower()}.stl"))
    inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
    reg_path = here.parents[2] / "cad" / "stl" / f"{UNIT}.stl"
    reg_dims = stl_bbox_mm(str(reg_path))
    drawn_report = draw_nozzles(P, spec)[1]
    mass = _masses(P, spec, parts)
    report = {
        "bbox_mm": dims, "inside_size_mm": inside,
        "size_mm": [L, W, H], "size_basis": P.get("size_basis"),
        "graph_revision": P.get("graph_revision"),
        "solids": len(solid_val.Solids()),
        "all_parts_valid": all(v.val().isValid() for v in parts.values()),
        "cad_stl_scope": spec["cad_stl_scope"],
        "cad_stl_bbox_mm": reg_dims,
        "machine": spec["machine"](P, dims, mass),
        "nozzles_drawn": drawn_report,
        "nozzle_count_schedule": len(P["nozzles"]),
        "nozzle_idiom": spec["nozzle_idiom"],
        "part_mass_kg": mass, "cadquery": cq.__version__,
    }
    (here / "check.json").write_text(json.dumps(report, indent=2) + "\n")

    rows = spec["bom"](P, mass, dims)
    with (here / "bom.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "description", "qty", "material", "mass_kg",
                    "make_or_buy", "basis"])
        w.writerows(rows)
    fasteners.write_fasteners(here / "fasteners.csv", spec["fastener_rows"](P))

    # builder-owned params blocks pass through the tracker merge; the stale form keys
    # the rebuild supersedes leave the file here
    p = json.loads((here / "params.json").read_text())
    for k in spec.get("drop_keys", ()):
        p.pop(k, None)
    p["envelope"] = spec["envelope_block"](P, dims)
    p["layout"] = spec["layout_block"](P)
    (here / "params.json").write_text(json.dumps(p, indent=1) + "\n")

    print(json.dumps({k: report[k] for k in
                      ("bbox_mm", "inside_size_mm", "solids", "nozzle_count_schedule")}),
          flush=True)
    return report
