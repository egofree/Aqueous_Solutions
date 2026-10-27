"""FARM / HAB / POLY unit manufacturing models (X-FARM / X-HAB / X-POLY M3 roster, AQS-PLAN-006).

One shared builder per form class - tray/basin, tank, frame, hive, cabinet, room shell - reading
each unit's params.json (size_mm from the claimed graph envelope, the sec3 material class, the
driver-derived duty). Every mass is wall volume x the material density; no rate is claimed.
M3 roster acceptance: build + check.json + bom.csv + WORK_ORDER + build_log (the FLUX_PREP-class
acceptance; the 8-sheet drawing sets follow as their own pass).

Run: $CADQUERY_PYTHON models/mfg/farm_hab.py UNIT [UNIT ...]
"""
import csv, json, math, pathlib, sys
import cadquery as cq

HERE = pathlib.Path(__file__).parent
RHO = {'HDPE': 950.0, 'PP': 905.0, 'EPDM': 1150.0, 'steel': 7850.0, 'HDG_steel': 7850.0,
       'SS304': 8000.0, 'SS316': 8000.0, 'aluminium': 2700.0, 'pine': 500.0, 'FRP': 1800.0,
       'LECA': 450.0, 'acrylic': 1180.0}


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def shell_box(L, W, H, t, floor=None):
    """Thick-walled open-top box (X-PAR-04 tray class): floor t thick, four walls t thick."""
    fl = t if floor is None else floor
    outer = box(0, 0, 0, L, W, H)
    cav = box(t, t, fl, L - 2 * t, W - 2 * t, H - fl)
    return outer.cut(cav)


def parts_tray(P):
    L, W, H = P['size_mm']
    t = P.get('wall_mm', 10)
    parts = {'basin_shell': shell_box(L, W, H, t)}
    if P.get('liner_mm'):
        lt = P['liner_mm']
        parts['liner'] = box(t, t, t, L - 2 * t, W - 2 * t, lt)
    for i, (bx, by, bd) in enumerate(P.get('baffles_mm', [])):
        parts[f'baffle_{i + 1}'] = box(bx, by, t, bd, W - 2 * t, H * 0.6)
    return parts


def parts_tank(P):
    L, W, H = P['size_mm']
    t = P.get('wall_mm', 15)
    parts = {'vessel_shell': shell_box(L, W, H, t, floor=t)}
    parts['lid'] = box(0, 0, H - t, L, W, t)
    lt = P.get('liner_mm')
    if lt:
        parts['liner'] = box(t, t, t, L - 2 * t, W - 2 * t, H - 2 * t - 10)
    for i, (r, h, x, y, z) in enumerate(P.get('stubs_mm', [])):
        parts[f'stub_{i + 1}'] = (cq.Workplane(cq.Plane(origin=(x, y, z), xDir=(0, 1, 0), normal=(1, 0, 0)))
                                  .circle(r).extrude(h))
    return parts


def parts_frame(P):
    L, W, H = P['size_mm']
    leg, wire = 40.0, 5.0
    parts = {}
    fr = None
    for (px, py) in ((0, 0), (L - leg, 0), (0, W - leg), (L - leg, W - leg)):
        q = box(px, py, 0, leg, leg, H - 100)
        fr = q if fr is None else fr.union(q)
    parts['frame_legs'] = fr
    parts['drop_board'] = box(0, 0, 100, L, W, 3)                        # manure board, 3 mm sheet
    parts['floor_wire'] = box(leg, leg, 300, L - 2 * leg, W - 2 * leg, 1)
    parts['roof'] = box(0, 0, H - 100, L, W, 3)                          # 3 mm sheet roof
    panels = None
    for z in (300, H - 250):
        for (px, py, dx, dy) in ((0, 0, L, 1), (0, W - 1, L, 1), (0, 0, 1, W), (L - 1, 0, 1, W)):
            q = box(px, py, z, dx, dy, 250)
            panels = q if panels is None else panels.union(q)
    parts['wire_panels'] = panels   # 1 mm plate at the hardware-cloth class; the mesh open area
                                    # carries ~0.15 of the plate mass - carried on the BOM note
    for i, (bx, by, bz, dx, dy, dz, nm) in enumerate(P.get('extras_mm', [])):
        parts[nm] = box(bx, by, bz, dx, dy, dz)
    return parts


def parts_hive(P):
    L, W, H = P['size_mm']
    body_h = (H - 150) // 2
    parts = {'stand': box(0, 0, 0, L + 50, W + 50, 150)}
    parts['box_deep'] = box(25, 25, 150, L, W, body_h)
    parts['box_medium'] = box(25, 25, 150 + body_h + 10, L, W, body_h)
    parts['lid'] = box(0, 0, 150 + 2 * body_h + 20, L + 40, W + 40, 30)
    parts['screen_floor'] = box(25, 25, 140, L, W, 10)
    return parts


def parts_cabinet(P):
    L, W, H = P['size_mm']
    t = P.get('wall_mm', 30)
    parts = {'cabinet_shell': shell_box(L, W, H, t, floor=t)}
    parts['top'] = box(0, 0, H - t, L, W, t)
    for i, (bx, by, bz, dx, dy, dz, nm) in enumerate(P.get('extras_mm', [])):
        parts[nm] = box(bx, by, bz, dx, dy, dz).cut(box(bx + 5, by + 5, bz, dx - 10, dy - 10, dz - 5))
    return parts


def parts_room(P):
    L, W, H = P['size_mm']
    t = 15.0                                             # partition panel 15 mm
    H = H - 20                                           # deck finish floor 20 mm
    door_w, door_h = 900.0, 2100.0
    parts = {'floor': box(0, 0, 0, L, W, t)}
    wall_long = box(0, 0, t, L, t, H - t)
    wall_short = box(0, W - t, t, L, t, H - t)
    wall_end = box(0, t, t, t, W - 2 * t, H - t)
    # the -X end wall carries the door opening
    seg_h = (W - 2 * t - door_w) / 2
    door_wall = (box(0, t, t, t, seg_h, H - t)
                 .union(box(0, t + seg_h + door_w, t, t, seg_h, H - t))
                 .union(box(0, t + seg_h, t + door_h, t, door_w, H - t - door_h)))
    parts['wall_long_a'] = wall_long
    parts['wall_long_b'] = wall_short
    parts['wall_end_solid'] = wall_end
    parts['wall_end_door'] = door_wall
    return parts


FORMS = {'tray': parts_tray, 'tank': parts_tank, 'frame': parts_frame,
         'hive': parts_hive, 'cabinet': parts_cabinet, 'room': parts_room}


def default_material(P):
    return P.get('material_class', 'HDPE')


def build(unit):
    H = HERE / unit
    P = json.loads((H / 'params.json').read_text())
    form = P['form']
    parts = FORMS[form](P)
    body = None
    for k, v in parts.items():
        body = v if body is None else body.union(v)
    out = H / 'export'
    out.mkdir(exist_ok=True)
    lp = unit.lower()
    cq.exporters.export(body, str(out / f'{lp}.step'))
    body.val().exportStl(str(out / f'{lp}.stl'), 0.3, 0.3, True)

    # masses: wall volume x the sec3 class density
    rho = {k: RHO[P.get('material_map', {}).get(k, default_material(P))] for k in parts}
    mass = {k: round(v.val().Volume() * 1e-9 * rho[k], 1) for k, v in parts.items()}
    L, W, Hh = P['size_mm']
    bb = body.val().BoundingBox()
    check = {
        'shell_bbox_mm': [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
        'envelope_mm': [L, W, Hh],
        'inside_size_mm_shell': bb.xlen <= L + 0.5 and bb.ylen <= W + 0.5 and bb.zlen <= Hh + 0.5,
        'solids': len(body.solids().vals()),
        'all_parts_valid': all(p.val().isValid() for p in parts.values()),
        'material_class': default_material(P),
        'form': form,
        'mass_kg': mass,
        'empty_kg': round(sum(mass.values()), 1),
        'cad_stl_scope': 'envelope-true build solid, mm (X-PAR-04 class; M3 roster acceptance)',
    }
    (H / 'check.json').write_text(json.dumps(check, indent=2) + '\n')
    with (H / 'bom.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['item', 'part', 'qty', 'material', 'mass_kg', 'make_buy', 'note'])
        for i, (k, m) in enumerate(sorted(mass.items()), 1):
            w.writerow([i, k, 1, default_material(P), m, 'make', f'{form} class; {P.get("size_note", "")[:80]}'])
    (H / 'WORK_ORDER.md').write_text(
        f'# {unit} work order (M3 roster acceptance)\n\n'
        f'1. Cut and join the {form} shell per `models/mfg/{unit}/params.json` (size_mm {L} x {W} x {Hh}).\n'
        f'2. {P.get("size_note", "")}\n'
        f'3. Fit the sec3 material class ({default_material(P)}); liner per params where specified.\n'
        f'4. Acceptance: check.json (bbox inside the envelope, solids valid, empty mass {check["empty_kg"]} kg).\n')
    print(json.dumps({'unit': unit, 'form': form, 'solids': check['solids'],
                      'bbox': check['shell_bbox_mm'], 'empty_kg': check['empty_kg']}))


if __name__ == '__main__':
    for u in (sys.argv[1:] or []):
        build(u)
