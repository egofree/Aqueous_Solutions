"""POLYMERS train parametric CAD (CadQuery, X-MFG-30 pattern). Reads params.design + params.envelope on the graph
(written by flow_graph/param/foundry_poly.py AQS-DUTY-073 and fluoro_train.py A-M-289) and writes
models/mfg/<UNIT>/export/<unit>.step and .stl, bom.csv, fasteners.csv and WORK_ORDER.md per unit. Live trains
(polyolefin line; fluoro train: HF kiln, VDF/TFE synthesis skids, PVDF/PTFE polymerization kettle, film/powder
formers) get machine geometry. POLY_COND stays standby (assay-gated, AQS-DES-POLY): envelope box only as a
presence-consistent PLACEHOLDER, marked in bom.csv and the work order. Liveness is read from BOTH stamps:
envelope.state, or live throughput rates in params.design (fluoro_train A-M-289 restamped units live whose older
foundry_poly sizing notes still say F-blocked - the design rates win; the graph is authority and is not edited here).
Run: $CADQUERY_PYTHON models/mfg/polymers.py [UNIT ...]"""
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


def cyl_y(x, y, z, r, h):
    return cq.Workplane('XY').circle(r).extrude(h).rotate((0, 0, 0), (1, 0, 0), -90).translate((x, y, z))


def ring_z(x, y, z, r_out, r_in, h):
    return cq.Workplane('XY').circle(r_out).circle(r_in).extrude(h).translate((x, y, z))


def cone_z(x, y, z, r_bot, r_top, h):
    return cq.Workplane('XY').circle(r_bot).workplane(offset=h).circle(r_top).loft(ruled=True).translate((x, y, z))


def box(x, y, z, L, W, H):
    return cq.Workplane('XY').box(L, W, H, centered=False).translate((x, y, z))


def _live_rates(d):
    """True when params.design carries live throughput rates (fluoro_train A-M-289 stamps these; the older
    foundry_poly sizing.status_note may still read 'F-blocked' / 'installed standby' for the same unit).
    A design_case_* key is a design case, not a live rate - POLY_COND stays standby on it."""
    return any(k.endswith('_kg_d') and isinstance(v, (int, float)) and v > 0 and k != 'design_case_kg_d'
               for k, v in (d or {}).items())


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
    note = (N[U]['params'].get('sizing') or {}).get('status_note')
    why = note if note and not _live_rates(N[U]['params'].get('design')) else (note or e['basis'])
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
    # POLY_COND (X-MFG-31): assay-gated standby, but its design-case chamber IS issued (AQS-DUTY-073
    # sec. 4: design case 0.5 kg/d condensation resin; foundry_poly stamps the kettle design), so it
    # gets real geometry at the design case and a standby-marked BOM/WO - not an envelope placeholder.
    if e['state'] != 'live' and not _live_rates(d) and U != 'POLY_COND':
        return placeholder(U)
    L, W, H = e['size_mm']; style = e['style']
    if style == 'reactor' and U == 'POLY_OLEFIN':    # DN150 vertical oligomerization reactor
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
    if style == 'reactor' and U == 'POLY_F':         # PVDF/PTFE emulsion polymerization kettle
        D, Hv = d['D_mm'], d['H_mm']
        cx, cy = L / 2, W / 2
        t = 6                                                                         # study-min wall at DN150 (wall key is POLY_OLEFIN's)
        m = ring_z(cx, cy, 640, D / 2, D / 2 - t, Hv)                                 # kettle shell
        m = m.union(cq.Workplane('XY').circle(D / 2).extrude(t).translate((cx, cy, 640 - t)))                       # bottom
        m = m.union(ring_z(cx, cy, 640 + Hv, D / 2 + 20, D / 2 - t, t + 4))                                        # lid flange
        m = m.union(cq.Workplane('XY').circle(D / 2 + 5).extrude(6).translate((cx, cy, 640 + Hv + t + 4)))         # lid
        m = m.union(ring_z(cx, cy, 655, D / 2 + 18, D / 2 + 2, Hv - 25))             # hot-water jacket (60 C)
        m = m.union(cyl_z(cx, cy, 640 + Hv + t + 10, 45, 130))                       # agitator / mixer motor
        m = m.union(cyl_z(cx + 50, cy, 640 + Hv + t + 10, 12, 80))                   # relief valve
        m = m.union(cyl_x(cx + D / 2, cy, 700, 8, 50))                               # monomer feed nozzle
        for lx, ly in ((150, 150), (420, 150), (150, 420), (420, 420)):
            m = m.union(box(lx, ly, 0, 30, 30, 640 - t))                             # frame legs
        m = m.union(cyl_z(80, 80, 80, 55, 400))                                      # VDF feed receiver
        m = m.union(cyl_z(520, 80, 80, 55, 400))                                     # TFE feed receiver
        m = m.union(box(470, 400, 0, 110, 150, 240))                                 # reclaim pump module
        rows = [('1', f'Kettle shell DN{D} x {Hv} mm, {t} mm wall, {d["T_C"]} C emulsion service', 1,
                 d['material'], f'{DOC} fluoro train; {d["vessel"]}'),
                ('2', f'Hot-water jacket band at {d["T_C"]} C with PID', 1, 'SS 304 jacket',
                 f'{DOC} fluoro train; duty {d["duty_kW"]} kW'),
                ('3', 'Top-entry agitator with variable-speed drive and gland', 1, 'Hastelloy C-276 shaft, PTFE gland',
                 f'{d["initiator"]}'),
                ('4', f'Monomer feed receivers, 2 x D110 x 400 mm, with metering heads', 2, 'SS 316L, PTFE',
                 f'VDF {d["vdf_kg_d"]:g} + TFE {d["tfe_kg_d"]:g} kg/d from the synthesis skids'),
                ('5', f'Reclaim pump module: transfer of unreacted monomer ({d["reclaim_kg_d"]:g} kg/d to F_RECOVER)', 1,
                 'PVDF pump, PTFE line', f'{DOC} fluoro train; F recovery closure'),
                ('6', 'Relief: rupture disc DN25 to the vent scrubber', 1, 'Hastelloy / graphite',
                 'blocked-outlet case, API 520 class'),
                ('7', 'Frame, 4 legs 30 x 30 mm with foot plates', 4, 'SS 304', 'study')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M10 x 40 lid bolt with nut and washers,ISO 3506 A4-80,12,lid flange at 80 mm pitch,study\n'
                '2,M10 clamp,ISO 3506 A4-70,8,receiver bottle heads,study\n'
                '3,M12 anchor,ISO 3506 A4-80,4,frame feet,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} fluoro train (Q-013 reopened; A-M-289). LIVE unit - feed landed.\n\n'
              f'1. Fabricate the DN{D} x {Hv} mm kettle in {d["material"]}; fit the jacket band and 4-leg frame.\n'
              f'2. Set the agitator gland, the rupture disc seat and the monomer feed nozzle; drill the lid for 12 M10 bolts.\n'
              f'3. Plumb the VDF/TFE receiver heads with metering valves; set the reclaim pump to F_RECOVER.\n'
              f'4. Test: inert pressure hold, jacket circulation at {d["T_C"]} C, then a water batch.\n'
              f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'line_machine':                      # forming line machines
        if U == 'PELLET':                            # die-face pelletizer line
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
        if U == 'FILM_CAST':                         # PVDF cast film/sheet line: extruder + chill roll + winder
            m = box(0, 280, 480, 240, 240, 340)                                       # drive + gearbox
            m = m.union(cyl_x(240, 400, 640, 35, 430))                                # extruder barrel (D25 screw)
            m = m.union(cyl_z(390, 400, 675, 45, 170))                                # feed hopper
            m = m.union(box(670, 280, 600, 90, 240, 80))                              # coat hanger die, 200 mm
            m = m.union(cyl_y(840, 250, 615, d['chill_roll_D_mm'] / 2, 300))          # chill roll D150
            m = m.union(cyl_y(840, 250, 470, 40, 300))                                # idler / pull roll
            m = m.union(box(1060, 240, 0, 40, 320, 950))                              # winder posts
            m = m.union(box(1420, 240, 0, 40, 320, 950))
            m = m.union(cyl_y(1120, 250, 600, 95, 300))                               # wind roll, station 1
            m = m.union(cyl_y(1120, 250, 600, 25, 300))                               # wind shaft
            m = m.union(cyl_y(1280, 250, 600, 25, 300))                               # shaft, station 2
            m = m.union(cyl_y(1200, 250, 730, 45, 300))                               # lay-on roll
            m = m.union(box(1440, 250, 0, 60, 300, 1150))                             # control panel
            rows = [('1', f"Extruder D{d['extruder_D_mm']} with D70 x 430 mm barrel, L/D 24 class", 1,
                     d['material'], f'{DOC} fluoro train; {d["pvdf_kg_d"]:g} kg/d PVDF at {d["melt_C"]} C melt'),
                    ('2', 'Feed hopper D90 with dryer sleeve', 1, '316L', f'{DOC} fluoro train'),
                    ('3', f"Coat-hanger die, {d['die_mm']} mm width slot", 1, 'Hastelloy C-276',
                     f'{DOC} fluoro train; {d["product"]}'),
                    ('4', f"Chill roll D{d['chill_roll_D_mm']} x 300 mm with idler/pull roll", 2, 'CS cored, chrome plated',
                     f'{DOC} fluoro train; duty {d["duty_kW"]} kW'),
                    ('5', 'Double-station surface winder with lay-on roll', 1, 'CS frame, pneumatic shafts',
                     f'{DOC} fluoro train; gasket/lining sheet to MFG'),
                    ('6', 'Control panel with heat and speed loops', 1, 'CS enclosure, IP54', 'study')]
            fast = ('item,size,grade,qty,location,basis\n'
                    '1,M12 anchor,ISO 898-1 8.8,8,line feet to slab,study\n'
                    '2,M10 x 30 guard screws,ISO 3506 A4-70,16,guard covers,study\n')
            wo = (f'# Work order {U}\n\nAuthority: {DOC} fluoro train (Q-013 reopened; A-M-289). LIVE unit - feed landed.\n\n'
                  f'1. Set the drive/extruder bed; align the D{d["extruder_D_mm"]} barrel to the {d["die_mm"]} mm die.\n'
                  f'2. Fit the D{d["chill_roll_D_mm"]} chill roll and pull roll with water circuits.\n'
                  f'3. Build the winder frame; set both shafts and the lay-on roll.\n'
                  f'4. Wire the panel; interlock heater overtemp and nip guards.\n'
                  f'5. Test: heat-up to {d["melt_C"]} C, then a PVDF trial pass at {d["pvdf_kg_d"]:g} kg/d; check gauge.\n'
                  f'6. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
            return export(U, m, rows, fast, wo)
        if U == 'POWDER_RESIN':                      # PTFE powder line: pin mill + cyclone classifier + collector
            m = cyl_z(200, 400, 700, 130, 300)                                       # pin mill body
            m = m.union(cyl_z(200, 400, 520, 80, 180))                               # mill motor
            m = m.union(box(150, 320, 560, 100, 160, 140))                           # belt guard
            m = m.union(cyl_z(200, 400, 1000, 70, 240))                              # feed hopper
            m = m.union(cyl_x(330, 400, 880, 25, 110))                               # mill -> cyclone duct
            m = m.union(cone_z(550, 400, 620, 110, 35, 130))                         # cyclone cone
            m = m.union(cyl_z(550, 400, 750, 110, 280))                              # cyclone body
            m = m.union(cyl_z(550, 400, 1030, 30, 160))                              # vortex outlet
            m = m.union(cyl_z(550, 400, 500, 30, 120))                               # fines drop
            m = m.union(box(420, 270, 80, 260, 260, 380))                            # PE-lined collector bin
            m = m.union(box(1000, 300, 80, 180, 200, 240))                           # blower / oversize return
            m = m.union(cyl_x(680, 400, 900, 25, 300))                               # oversize return duct
            m = m.union(box(1300, 300, 0, 160, 300, 1100))                           # control panel
            rows = [('1', f"Pin mill D260 x 300 mm with vertical spindle", 1, d['material'],
                     f'{DOC} fluoro train; {d["ptfe_kg_d"]:g} kg/d PTFE at {d["mill_kWh_kg"]} kWh/kg ({d["duty_kW"]} kW)'),
                    ('2', 'Mill motor D160 with belt guard', 1, 'IEC frame', f'{DOC} fluoro train'),
                    ('3', 'Feed hopper D140 x 240 mm with metering screw', 1, '316L', f'{DOC} fluoro train'),
                    ('4', 'Cyclone classifier D220 with vortex outlet and fines drop', 1, '316L',
                     f'{DOC} fluoro train; fine-cut classification'),
                    ('5', 'PE-lined collector bin 260 x 260 x 380 mm', 1, '316L shell, PE liner',
                     f'{d["product"]}'),
                    ('6', 'Blower with oversize-return duct to the hopper', 1, '316L fan', f'{DOC} fluoro train'),
                    ('7', 'Control panel with interlocks', 1, 'CS enclosure, IP54', 'study')]
            fast = ('item,size,grade,qty,location,basis\n'
                    '1,M12 anchor,ISO 898-1 8.8,6,frame feet to slab,study\n'
                    '2,M10 x 30 guard screws,ISO 3506 A4-70,12,guard covers,study\n')
            wo = (f'# Work order {U}\n\nAuthority: {DOC} fluoro train (Q-013 reopened; A-M-289). LIVE unit - feed landed.\n\n'
                  f'1. Set the pin mill on its motor base; align the belt; guard it.\n'
                  f'2. Mount the cyclone classifier; connect the mill duct, fines drop and collector bin (PE liner).\n'
                  f'3. Fit the blower and oversize-return duct; wire the panel with interlocks.\n'
                  f'4. Test: dry run, then a PTFE trial at {d["ptfe_kg_d"]:g} kg/d; check the cut on a sieve assay.\n'
                  f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
            return export(U, m, rows, fast, wo)
        return placeholder(U)
    if style == 'rotary_kiln':                       # HF_GEN: indirectly heated rotary kiln
        Dt, Lt = d['tube_D_mm'], d['tube_L_mm']
        slope = d['slope_deg']
        tl = Lt - 8                                                                   # tube fitted between the end hoods
        zh = 861                                                                      # feed-end (high) axis height
        m = cq.Workplane('YZ').circle(Dt / 2).circle(Dt / 2 - 8).extrude(tl)          # kiln tube, 8 mm wall
        m = m.rotate((0, 0, 0), (0, 1, 0), slope).translate((4, W / 2, zh))
        m = m.union(box(250, 140, 640, 700, 420, 340))                                # indirect furnace chamber
        m = m.union(cyl_z(90, W / 2, 1060, 70, 300))                                  # spar feed hopper
        m = m.union(box(40, W / 2 - 40, 960, 110, 80, 100))                           # feed chute
        m = m.union(box(1060, 200, 600, 140, 300, 380))                               # discharge hood
        m = m.union(cyl_z(1130, W / 2, 980, 55, 420))                                 # kiln gas offtake
        m = m.union(box(1090, W / 2 - 50, 320, 110, 100, 280))                        # cake chute
        m = m.union(box(990, 260, 0, 210, 180, 300))                                  # gypsum cake bin
        m = m.union(box(120, 290, 600, 80, 120, 155))                                 # trunnion pedestal, feed end
        m = m.union(box(990, 290, 600, 80, 120, 126))                                 # trunnion pedestal, discharge end
        m = m.union(box(200, 580, 600, 200, 90, 180))                                 # drive gearbox + motor
        m = m.union(cyl_z(100, 120, 0, 80, 300))                                      # acid day tank
        m = m.union(box(190, 90, 0, 80, 110, 150))                                    # metering pump
        rows = [('1', f'Kiln tube D{Dt} x {tl} mm, 8 mm wall, {slope:g} deg slope, {d["rpm"]} rpm', 1,
                 d['material'], f'{DOC} fluoro train; {d["machine"]}'),
                ('2', f'Indirect furnace chamber 700 x 420 x 340 mm, {d["T_C"]:.0f} C', 1, 'CS casing, ceramic fibre',
                 f'{DOC} fluoro train; residence {d["residence_min"]:.0f} min'),
                ('3', 'Spar feed hopper D140 with chute and rotary valve', 1, 'CS, Monel trim',
                 f'spar {d["spar_kg_d"]:.3f} kg/d + F_RECOVER concentrate ({d["feed"]})'),
                ('4', 'Acid day tank D160 x 300 mm with metering pump', 1, 'SS 316L, PTFE pump head',
                 f'acid {d["acid_kg_d"]:.3f} kg/d (98 wt% H2SO4)'),
                ('5', 'Discharge hood with cake chute and bin', 1, 'CS, Monel-lined',
                 f'cake {d["cake_kg_d"]:.3f} kg/d'),
                ('6', 'Kiln gas offtake DN110 to the dissolution/absorption tank', 1, 'CS, PTFE-lined',
                 f'HF {d["hf_kg_d"]:.3f} kg/d product gas'),
                ('7', f'Trunnion riding rings + 2 pedestals, drive {d["drive_kW"]} kW', 1,
                 'CS pedestals, Monel inserts (PERRY9_MAT)', f'duty {d["duty_kW"]} kW; {slope:g} deg x {d["rpm"]} rpm')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M16 stud + 2 nuts (ISO 4014 / ISO 4032),ISO 898-1 8.8,12,hatch and hood flanges,study\n'
                '2,M12 anchor,ISO 898-1 8.8,6,pedestals and chamber feet,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} fluoro train (A-M-289). LIVE unit - dock acid-spar landed.\n\n'
              f'1. Set the trunnion pedestals and drive; roll and load the D{Dt} tube at {slope:g} deg ({d["rpm"]} rpm).\n'
              f'2. Build the indirect furnace chamber around the tube; cure the lining.\n'
              f'3. Fit the spar hopper/rotary valve and the acid day tank with metering pump.\n'
              f'4. Mount the discharge hood, cake bin and the DN110 gas offtake to the absorption tank.\n'
              f'5. Test: dry rotation and heat-up to {d["T_C"]:.0f} C, then a spar campaign at {d["spar_kg_d"]:.2f} kg/d.\n'
              f'6. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'reactor':                           # VDF_SYN / TFE_SYN: synthesis skid (duty-based, envelope-sized)
        D = min(L, W) - 240; Hv = H - 760; t = 8
        cx, cy = L / 2, W / 2
        m = ring_z(cx, cy, 400, D / 2, D / 2 - t, Hv)                                # reactor shell
        m = m.union(cq.Workplane('XY').circle(D / 2).extrude(t).translate((cx, cy, 400)))                  # bottom
        m = m.union(ring_z(cx, cy, 400 + Hv, D / 2 + 20, D / 2 - t, t + 5))                                # lid flange
        m = m.union(ring_z(cx - D / 4, cy, 400 + Hv + t + 5, 90, 70, 220))                                 # feed hopper
        m = m.union(ring_z(cx, cy, 520, D / 2 + 10, D / 2, 80))                                            # heater band
        m = m.union(box(0, 0, 0, L, 50, H))                                          # skid rail y-min
        m = m.union(box(0, W - 50, 0, L, 50, H))                                     # skid rail y-max
        m = m.union(box(10, W - 230, 0, 180, 180, 380))                              # HCl return pump module
        m = m.union(box(L - 170, 10, 0, 160, 160, 480))                              # control cabinet
        rows = [('1', f'Synthesis reactor shell D{D} x {Hv} mm, wall {t} mm, jacketed', 1,
                 '316L shell, PTFE-lined heads (fluorocarbon service)',
                 f'{DOC} fluoro train; duty {d.get("duty_kW", "TBD")} kW; '
                 f'{d.get("machine", {}).get("route", "AQS-SEL-FP route") if isinstance(d.get("machine"), dict) else "AQS-SEL-FP route"}'),
                ('2', 'Catalyst charge port and dip leg', 1, '316L / PTFE',
                 str(d.get('catalyst', 'catalyst per route'))),
                ('3', 'Chlorination / pyrolysis heater circuit with SCR control', 1, 'Inconel 600 sheath',
                 f'stage temperatures per {DOC} route table'),
                ('4', 'Dilute-HCl return pump and transfer line to CRU', 1, 'PVDF pump + PTFE line',
                 f'HCl return {d.get("hcl_return_kg_d", "rated")} kg/d'),
                ('5', 'Scrub/catch pot with caustic charge', 1, 'PP-H / PVDF', 'vent scrub per AQS-SEL-FP'),
                ('6', 'Skid frame rails and module tie-ins', 1, 'CS, HDG', f'envelope {L} x {W} x {H} mm'),
                ('7', 'Control cabinet with interlocks (high-T, high-P, low-flow)', 1, 'CS enclosure IP54', 'study')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M12 anchor,ISO 898-1 8.8,6,skid rails to slab,study\n'
                '2,M10 x 30 jacket screws,ISO 3506 A4-70,16,jacketed heads,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} fluoro train (Q-013 reopened; A-M-289). LIVE unit - feed landed.\n\n'
              f'1. Fabricate the D{D} jacketed shell; line the heads in PTFE (fluorocarbon service).\n'
              f'2. Fit the heater circuit, dip leg and the HCl-return pump skid module.\n'
              f'3. Wire interlocks: high-T, high-P, low circulation flow.\n'
              f'4. Test: inert pressure hold, then the route trial per {DOC}.\n'
              f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
        return export(U, m, rows, fast, wo)
    if style == 'store_bin':                         # POLY_STOCK: pellet tote bin
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
