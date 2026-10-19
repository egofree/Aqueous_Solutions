"""POLYMERS train parametric CAD (CadQuery, X-MFG-30 pattern). Reads params.design + params.envelope on the graph
(written by flow_graph/param/foundry_poly.py, AQS-DUTY-073) and writes models/mfg/<UNIT>/export/<unit>.step and .stl,
bom.csv, fasteners.csv and WORK_ORDER.md per unit. The live polyolefin line (POLY_OLEFIN -> PELLET -> POLY_STOCK)
gets machine geometry; the standby trains (fluoropolymer F-blocked Q-013, POLY_COND assay-gated, film/powder formers)
get the envelope box only as a presence-consistent PLACEHOLDER, marked in bom.csv and the work order.
Run: /tmp/cqvenv/bin/python models/mfg/polymers.py [UNIT ...]"""
import csv, json, math, os, sys
import cadquery as cq

UNITS = ['POLY_OLEFIN', 'PELLET', 'POLY_STOCK', 'POLY_COND', 'HF_GEN', 'VDF_SYN', 'TFE_SYN', 'POLY_F',
         'POWDER_RESIN', 'FILM_CAST']
DOC = 'AQS-DUTY-073'
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}


def cyl_z(x, y, z, r, h):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x, y, z))


def cyl_x(x, y, z, r, h):
    return cq.Workplane('YZ').circle(r).extrude(h).translate((x, y, z))


def box(x, y, z, L, W, H):
    return cq.Workplane('XY').box(L, W, H, centered=False).translate((x, y, z))


def export(U, m, rows, fast, wo):
    e = N[U]['params']['envelope']; L, W, H = e['size_mm']
    bb = m.val().BoundingBox()
    assert bb.xmin >= -0.5 and bb.ymin >= -0.5 and bb.zmin >= -0.5 and bb.xmax <= L + 0.5 and bb.ymax <= W + 0.5 \
        and bb.zmax <= H + 0.5, (U, (round(bb.xmin), round(bb.xmax), round(bb.ymin), round(bb.ymax), round(bb.zmin), round(bb.zmax)), (L, W, H))
    out = f'models/mfg/{U}/export'; os.makedirs(out, exist_ok=True)
    cq.exporters.export(m, f'{out}/{U.lower()}.step'); cq.exporters.export(m, f'{out}/{U.lower()}.stl')
    csv.writer(open(f'models/mfg/{U}/bom.csv', 'w', newline='')).writerows(
        [('item', 'description', 'qty', 'material', 'basis')] + [tuple(r) for r in rows])   # quoted: materials carry commas
    open(f'models/mfg/{U}/fasteners.csv', 'w').write(fast)
    open(f'models/mfg/{U}/WORK_ORDER.md', 'w').write(wo)
    print(f'{U}: {e["style"]} {e["state"]} bbox {round(bb.xlen)} x {round(bb.ylen)} x {round(bb.zlen)} of {L} x {W} x {H}')


def placeholder(U):
    e = N[U]['params']['envelope']; L, W, H = e['size_mm']
    why = (N[U]['params'].get('sizing') or {}).get('status_note') or 'standby train (AQS-DUTY-073 sections 3-4)'
    m = cq.Workplane('XY').box(L, W, H, centered=False)
    rows = [('1', f'PLACEHOLDER (standby, envelope-only): box {L} x {W} x {H} mm per params.envelope; '
                  f'no machine design until the feed lands', 1, 'n/a (massing only)', f'{DOC} sections 3-4; {why}')]
    export(U, m, rows, 'item,size,grade,qty,location,basis\n'
                       '1,M12 anchor,ISO 898-1 8.8,4,footprint bolting to the envelope layout,study\n',
           f'# Work order {U}\n\nAuthority: {DOC} (foundry_poly.py stamps). STANDBY UNIT - DO NOT FABRICATE.\n\n'
           f'Envelope-only placeholder ({L} x {W} x {H} mm). {why}.\nThis model exists so the unit is '
           f'presence-consistent on the layout and the plant BOM; the machine is designed at its unit task when the '
           f'feed lands. Inspect against models/mfg/{U}/export/{U.lower()}.step for the reserved volume only.\n')


def build(U):
    p = N[U]['params']; e = p['envelope']; d = p['design']
    if e['state'] != 'live':
        return placeholder(U)
    L, W, H = e['size_mm']; style = e['style']
    if style == 'reactor':                          # POLY_OLEFIN: DN150 vertical oligomerization reactor
        D, Hv, t = d['D_mm'], d['H_mm'], d['wall_mm']
        m = cq.Workplane('XY').circle(D / 2).circle(D / 2 - t).extrude(Hv).translate((L / 2, W / 2, 600))    # shell
        m = m.union(cq.Workplane('XY').circle(D / 2).extrude(t).translate((L / 2, W / 2, 600)))              # bottom
        m = m.union(cq.Workplane('XY').workplane(offset=600 + Hv).circle(D / 2 + 25).circle(D / 2 - t).extrude(t + 6)
                    .translate((L / 2, W / 2, 0)))                                                          # lid flange
        for i in range(3):                                                                                   # legs
            a = 2 * math.pi * i / 3
            m = m.union(box(L / 2 + (D / 2 - 10) * math.cos(a) - 20, W / 2 + (D / 2 - 10) * math.sin(a) - 20, 0, 40, 40, 600))
        m = m.union(box(L / 2 - 60, W / 2 - 60, 600 + Hv + t + 6, 120, 120, 150))                            # agitator/mixer motor
        m = m.union(cyl_x(L / 2 - 30, W / 2, 700, 12, 60))                                                   # feed nozzle
        m = m.union(cyl_z(L / 2, W / 2, 600, D / 2 + 15, 50))                                                # heater band
        rows = [('1', f"Shell DN{D} x {Hv} mm, {t} mm wall, {d['T_C']} C / {d['P_MPa']} MPa design", 1,
                 d['material'], f'{DOC} section 2; wall ASME VIII-1 UG-27 class'),
                ('2', 'Bolted flat lid with gasket and mixer gland', 1, d['material'], f'{DOC} section 2'),
                ('3', 'Top-entry agitator with variable-speed drive', 1, '316L shaft, PTFE gland', f'{DOC} section 2 (oligomerization, study)'),
                ('4', 'Feed and product nozzles DN25', 2, d['material'], 'IA-C5-POLY in; resin out to PELLET'),
                ('5', f"Heater jacket band, {max(5, round(d['heat_W'] * 2))} W with thermostat", 1, 'silicone / mica', f'{DOC} section 2; {d["heat_W"]} W feed heating'),
                ('6', 'Relief: rupture disc DN25 to the vent header', 1, '316L / graphite', 'blocked-outlet case, API 520 class'),
                ('7', 'Three legs 40 x 40 x 600 mm with foot plates', 3, d['material'], 'study')]
        bolts = max(8, int(3.14159 * (D + 50) / 80) // 4 * 4)
        fast = (f'item,size,grade,qty,location,basis\n'
                f'1,M10 x 40 lid bolt with nut and washers,ISO 3506 A4-80,{bolts},lid flange at 80 mm pitch,study\n'
                f'2,M12 anchor,ISO 3506 A4-80,3,leg feet,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication; no bought reactor.\n\n'
              f'1. Roll and weld the DN{D} shell, {t} mm wall, height {Hv} mm; cut the bottom and lid discs ({d["material"]}).\n'
              f'2. Weld the longitudinal seam and the bottom; drill the lid for {bolts} M10 bolts.\n'
              f'3. Set 2 DN25 nozzles (feed at the side, product at the bottom) and the rupture disc seat.\n'
              f'4. Weld 3 legs; fit the agitator gland and the heater band.\n'
              f'5. Test: hydrostatic to 1.3 x {d["P_MPa"]} design (ASME VIII-1 UG-99 class intent); dry the heater circuit.\n'
              f'6. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'line_machine':                     # PELLET: die-face pelletizer line
        if U == 'PELLET':
            m = box(0, 275, 525, 250, 250, 350)                                       # gearbox
            m = m.union(cyl_x(125, 400, 700, 45, 600))                                # extruder barrel
            m = m.union(box(725, 325, 625, 150, 150, 150))                            # die head
            m = m.union(box(875, 250, 550, 300, 300, 300))                            # pelletizer water box
            m = m.union(box(1050, 250, 0, 400, 300, 250))                             # collector/dryer
            m = m.union(box(0, 0, 0, 150, 150, 600))                                  # control panel
            rows = [('1', 'Extruder barrel D90 x 600 mm with L/D 6 feed screw', 1, '316L barrel, nitrided screw',
                     f'{DOC} section 2; {d["rate_kg_d"]} kg/d resin'),
                    ('2', 'Gearbox and drive with variable speed', 1, 'geared motor, IEC frame', f'{DOC} section 2'),
                    ('3', f'Die head, {d["pellet_mm"]} mm pellet holes', 1, '316L',
                     f'{d["pellet_mm"]} mm pellets (AQS-DES-POLY)'),
                    ('4', 'Underwater die-face pelletizer with water box', 1, '316L wetted', f'{DOC} section 2'),
                    ('5', 'Collector/dryer centrifugal basket', 1, '316L', f'{DOC} section 2'),
                    ('6', 'Control panel with heater and speed loops', 1, 'CS enclosure, IP54', 'study')]
            fast = ('item,size,grade,qty,location,basis\n'
                    '1,M12 anchor,ISO 898-1 8.8,6,line feet to slab,study\n'
                    '2,M10 x 30 guard screws,ISO 3506 A4-70,16,guard covers,study\n')
            wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication; no bought pellet line.\n\n'
                  f'1. Set the gearbox/extruder bed; align the D90 barrel and {d["pellet_mm"]} mm die head.\n'
                  f'2. Fit the underwater pelletizer box and the collector/dryer basket.\n'
                  f'3. Wire the control panel; interlock the water flow and the cutter guard.\n'
                  f'4. Test: water run, then trial resin pass; check pellet size {d["pellet_mm"]} mm.\n'
                  f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
            return export(U, m, rows, fast, wo)
        return placeholder(U)
    if style == 'store_bin':                        # POLY_STOCK: pellet tote bin
        m = box(20, 20, 0, L - 40, W - 40, H - 100)                                   # bin body
        m = m.union(box(0, 0, H - 100, L, W, 30))                                     # lid rim
        m = m.union(cyl_z(L / 2 - 60, W / 2, H - 70, 25, 40))                         # lid vent
        rows = [('1', f'Pellet tote bin {L - 40} x {W - 40} x {H - 100} mm with lid rim', 1, 'HDPE PE100 sheet (DVS 2207-4)',
                 f'{DOC} section 2; issue {d["issue_kg_d"]} kg/d + offcut {d["to_wet_kg_d"]} kg/d, {d["hold_d"]:.0f} d staging'),
                ('2', 'Butterfly valve DN25 at the outlet', 1, 'PP-H / EPDM', 'metered draw to BLOW_MOLD / MFG'),
                ('3', 'Lid with vent filter (pellet dust)', 1, 'HDPE + PP filter', 'study')]
        fast = 'item,size,grade,qty,location,basis\n1,M10 clamp,ISO 3506 A4-70,4,lid clamps,study\n'
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication.\n\n'
              f'1. Cut, roll and weld the PE100 bin body {L - 40} x {W - 40} x {H - 100} mm (DVS 2207-4).\n'
              f'2. Fit the lid rim, vent filter and the DN25 outlet valve.\n'
              f'3. Test: fill to the brim, 24 h, no leak (DVS 2205).\n'
              f'4. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
        return export(U, m, rows, fast, wo)
    return placeholder(U)


if __name__ == '__main__':
    for U in (sys.argv[1:] or UNITS):
        assert U in UNITS, U
        build(U)
