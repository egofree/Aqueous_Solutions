"""FOUNDRY train parametric CAD (CadQuery, X-MFG-30 pattern). Reads params.design + params.envelope on the graph
(written by flow_graph/param/foundry_poly.py, AQS-DUTY-072 Rev B D-DOCK feedstock program) and writes
models/mfg/<UNIT>/export/<unit>.step and .stl, bom.csv, fasteners.csv and WORK_ORDER.md per unit. Live trains
(scrap-remelt melt-and-cast + roll + stock staging; D-DOCK pot/cell molten-chloride electrolysis, Kroll Ti train,
investment casting on wax make-up + shell reclaim) get machine geometry; the standby_rated N+1 alternates (A-M-283)
keep the envelope box only as a presence-consistent PLACEHOLDER, marked in bom.csv and the work order.
Run: $CADQUERY_PYTHON models/mfg/foundry.py [UNIT ...]"""
import csv, json, math, os, sys
import cadquery as cq

UNITS = ['IND_MELT', 'CAST_LINE', 'CONT_CAST', 'ROLL', 'STOCK_OUT',
         'EXTRUDE', 'DRAW', 'FORGE', 'SINTER', 'VAC_IND', 'VAC_CAST', 'RF_HEAT', 'RES_HEAT', 'COMB_HEAT', 'FLUX_PREP',
         'AL_POT', 'MG_POT', 'CA_POT', 'TI_CELL', 'MO_CELL', 'CR_CELL',
         'WAX_PATTERN', 'SHELL_BUILD', 'SHELL_BURNOUT', 'INV_CAST', 'SHELL_BREAK']
DOC = 'AQS-DUTY-072'
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
    why = (N[U]['params'].get('sizing') or {}).get('status_note') or 'standby train (AQS-DUTY-072 section 4)'
    m = cq.Workplane('XY').box(L, W, H, centered=False)
    rows = [('1', f'PLACEHOLDER (standby, envelope-only): box {L} x {W} x {H} mm per params.envelope; '
                  f'no machine design until the feed lands', 1, 'n/a (massing only)', f'{DOC} section 4; {why}')]
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
    if style == 'pot_cell':                          # AL/MG/CA pots + Mo/Cr cells: molten-chloride electrolysis
        imm, nD, nc = d['anode_imm_mm'], d['anode_D_mm'], d['cathodes']
        A = d['busbar_mm2']
        bw = max(12, int(math.sqrt(A)) + 1); bh = max(4, -(-A // bw))               # busbar rail cross-section, mm
        gas = d.get('cl2_kg_d') or d.get('co2_kg_d') or d.get('co_kg_d') or 0.0
        dn = 150 if gas > 10 else (80 if gas > 1 else 50)
        if 'cl2_kg_d' in d:
            gasdesc = (f'{d["cl2_kg_d"]:g} kg/d Cl2 to the Kroll loop (AQS-BAL-KROLL)' if U == 'MG_POT'
                       else f'{d["cl2_kg_d"]:g} kg/d Cl2 dock export at the CRU (A-M-290 ruling)')
        else:
            gasdesc = f'anode-gas chlorine recycle, internal loop ({d.get("co2_kg_d", d.get("co_kg_d", 0)):g} kg/d COx, A-M-290)'
        m = box(0, 0, 0, 800, 800, 1000).cut(box(70, 70, 60, 660, 660, 940))        # lined rectangular cell shell
        for i in range(nc):                                                          # anode bank, one row
            ax = 160 + i * (480 / (nc - 1)) if nc > 1 else 400
            m = m.union(cyl_z(ax, 250, 820 - imm, nD / 2, imm + 300))
            m = m.union(box(ax - 8, 250, 1108, 16, 490, 8))                          # anode strap to the + rail
        for i in range(nc - 1):                                                      # cathode plates, interleaved
            cx = 160 + (i + 0.5) * (480 / (nc - 1)) if nc > 1 else 400
            m = m.union(box(cx - 55, 545, 700, 110, 12, 420))
            m = m.union(box(cx - 8, 55, 1108, 16, 490, 8))                            # cathode strap to the - rail
        m = m.union(box(70, 740, 1140, 660, bw, bh))                                  # anode rail (+)
        m = m.union(box(70, 55 - bw // 2, 1140, 660, bw, bh))                         # cathode rail (-)
        m = m.union(box(0, 0, 1000, 800, 800, 120).cut(box(40, 40, 1000, 720, 720, 120)))   # hood
        m = m.union(cyl_z(650, 400, 1120, dn / 2, 460))                               # gas offtake
        m = m.union(box(20, 80, 1000, 130, 170, 520))                                 # feed chute barrel
        m = m.union(cone_z(85, 165, 1520, 80, 35, 70))                                # feed hopper cone
        rows = [('1', f'Lined cell shell 800 x 800 x 1000 mm (70 mm casing + refractory), bath at {d["bath_T_C"]:.0f} C', 1,
                 'CS casing, ceramic-fibre + ram lining', f'{DOC} section 4; {d["service"]}'),
                ('2', f'Anode bank, {nc} x D{nD} mm graphite anodes at {imm} mm immersion', nc, 'graphite, chlorinated',
                 f'Faraday I = {d["I_A"]:.0f} A at CE 0.85 (A-M-282); {d["chemistry"]}'),
                ('3', f'Cathode plate set, {nc - 1} x 110 x 12 mm with product pocket', nc - 1, 'mild steel / clad',
                 f'{d["metal_kg_d"]:g} kg/d metal on the D-DOCK chloride import (A-M-284)'),
                ('4', f'Cu busbar ladder: 2 rails {bw} x {bh} mm ({A} mm2 class), straps and DC drops', 1, 'Cu ETP',
                 f'{d["I_A"]:.0f} A at {d["cell_V"]} V cell; {d["dc_kW"]:.3f} kW dc + {d["hold_kW"]} kW hold of {d["connected_kW"]} kW connected'),
                ('5', f'Hood with gas offtake DN{dn} and dip leg', 1, 'CS hood, Hastelloy C-276 dip leg', gasdesc),
                ('6', 'Feed chute with hopper cone and rotary seal', 1, 'CS + refractory throat',
                 f'{d["feed_kg_d"]:.3f} kg/d feed (A-M-284 feedstock ruling)'),
                ('7', f'Thyristor rectifier + bath hold heaters, {d["connected_kW"]} kW connected', 1, 'cabinet, IP54',
                 f'{DOC} section 4; A-M-282 current class')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M12 stud + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,10,anode clamp bars,study\n'
                '2,M10 x 30 hood bolts,ISO 898-1 8.8,16,hood rim flange,study\n'
                '3,M12 anchor,ISO 898-1 8.8,4,cell shell to slab,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). LIVE unit - D-DOCK feedstock program (A-M-284).\n\n'
              f'1. Fabricate the 800 x 800 x 1000 mm shell; line 70 mm (casing + ceramic fibre + ram) for {d["bath_T_C"]:.0f} C service.\n'
              f'2. Set the {nc - 1} cathode plates on the pocket wall; hang the {nc} x D{nD} mm anodes at {imm} mm immersion.\n'
              f'3. Fit the busbar ladder ({A} mm2 Cu class for {d["I_A"]:.0f} A) and the DC drops; torque and megger-check.\n'
              f'4. Mount the hood, DN{dn} offtake with dip leg, and the feed chute with rotary seal.\n'
              f'5. Wire the {d["connected_kW"]} kW rectifier; interlock hood draft, bath temperature and cover position.\n'
              f'6. Test: dry-out and melt-up curve, then trial electrolysis; route the off-gas per the Cl2 ruling ({gasdesc}).\n'
              f'7. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'kroll_train':                       # TI_CELL: chlorinator + condenser + reduction vessel trio
        m = cyl_z(170, 560, 240, 90, 640)                                            # chlorinator retort
        m = m.union(ring_z(170, 560, 260, 105, 90, 320))                             # chlorinator heater band
        m = m.union(cone_z(170, 560, 880, 80, 35, 70))                               # oxide + carbon charge hopper
        m = m.union(cyl_z(400, 560, 240, 70, 420))                                   # TiCl4 condenser
        m = m.union(ring_z(400, 560, 300, 85, 70, 200))                              # condenser water band
        m = m.union(cyl_z(660, 520, 200, 100, 520))                                  # Mg reduction retort
        m = m.union(box(560, 400, 60, 200, 240, 420))                                # reduction furnace box
        m = m.union(cyl_z(660, 520, 720, 20, 20))                                    # Mg hopper neck
        m = m.union(cyl_z(660, 520, 740, 55, 240))                                   # Mg charge hopper
        m = m.union(cyl_x(260, 560, 560, 12, 140))                                   # chlorinator -> condenser
        m = m.union(cyl_x(470, 560, 600, 12, 190))                                   # condenser -> reduction retort
        m = m.union(box(80, 60, 40, 640, 110, 90))                                   # MgCl2 drag-out trough
        rows = [('1', f'Chlorinator retort D180 x 640 mm with 320 mm heater band, {d["chlorinator_T_C"]:.0f} C', 1,
                 'Inconel 601 retort, CS shell', f'{DOC} section 4; TiO2 {d["tio2_kg_d"]:g} + C {d["c_kg_d"]:g} kg/d, Cl2 {d["cl2_kg_d"]:g} kg/d from MG_POT'),
                ('2', 'TiCl4 condenser D140 x 420 mm with water band', 1, 'Hastelloy C-276',
                 f'{DOC} section 4; AQS-BAL-KROLL TiCl4 pass'),
                ('3', f'Mg reduction retort D200 x 520 mm in furnace box, {d["retort_T_C"]:.0f} C', 1,
                 'Inconel 601 retort, argon-latched', f'{d["mg_kg_d"]:g} kg/d Mg at {d["batch_kg"]:g} kg Ti batch campaigns'),
                ('4', f'Mg charge hopper D110 with neck and metering valve', 1, 'CS',
                 f'{DOC} section 4; A-M-284 Mg-pot loop'),
                ('5', 'TiCl4 transfer lines DN25, chlorinator -> condenser -> retort', 2, 'Hastelloy C-276',
                 f'{DOC} section 4'),
                ('6', 'MgCl2 drag-out trough 640 x 110 x 90 mm, tapping spout', 1, 'CS, Monel-lined',
                 f'{d["mgcl2_gross_kg_d"]:g} kg/d gross MgCl2; drag-out to FLUX_PREP (A-M-284)'),
                ('7', f'Retort hold furnace + SCR, {d["hold_kW"]} kW', 1, 'resistance, PID', f'{DOC} section 4; CO {d["co_kg_d"]:g} kg/d off-gas to burn')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M16 stud + 2 nuts (ISO 4014 / ISO 4032),ISO 898-1 8.8,12,retort and hopper flanges,study\n'
                '2,M12 anchor,ISO 898-1 8.8,4,train stands to slab,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). LIVE unit - D-DOCK rutile + carbon (A-M-284).\n\n'
              f'1. Set the three-vessel train: chlorinator (800 C), TiCl4 condenser, Mg reduction retort (900 C) in its furnace box.\n'
              f'2. Fit the charge hopper (TiO2 + C), the Mg charge hopper, and the DN25 transfer lines.\n'
              f'3. Weld and Monel-line the MgCl2 drag-out trough; route it to FLUX_PREP.\n'
              f'4. Leak-check the train on argon (Kroll retorts run oxygen-free); commission the {d["hold_kW"]} kW hold furnace.\n'
              f'5. Test: one {d["batch_kg"]:g} kg Ti campaign; verify the Cl2 return balance to MG_POT (AQS-BAL-KROLL).\n'
              f'6. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'bench_prep':                        # WAX_PATTERN / FLUX_PREP: prep bench class
        m = box(0, 0, 860, 800, 600, 40)                                             # bench top
        for lx, ly in ((20, 20), (740, 20), (20, 540), (740, 540)):
            m = m.union(box(lx, ly, 0, 40, 40, 860))                                 # legs
        m = m.union(box(20, 20, 150, 760, 560, 25))                                  # lower shelf
        if U == 'WAX_PATTERN':
            m = m.union(cyl_z(180, 300, 900, 110, 260))                              # wax pot (10 L)
            m = m.union(box(520, 150, 900, 30, 30, 250))                             # injector posts
            m = m.union(box(520, 420, 900, 30, 30, 250))
            m = m.union(box(480, 120, 900, 260, 360, 16))                            # die plate
            m = m.union(cyl_z(600, 300, 920, 40, 230))                               # injector plunger
            m = m.union(box(480, 120, 1150, 260, 360, 30))                           # top platen
            m = m.union(box(40, 40, 175, 190, 200, 190))                             # reclaim wax melter
            rows = [('1', 'Prep bench 800 x 600 x 900 mm, CS frame, lower shelf', 1, 'CS weldment, SS top',
                     f'{DOC} section 4; {d["bench"]}'),
                    ('2', f'Wax pot D220 x 260 mm, {d["pot_L"]:.0f} L, thermostatted', 1, 'SS 304, jacketed',
                     f'{d["wax_kg_d"]:g} kg/d wax duty ({d["makeup_kg_d"]:g} make-up + {d["reclaim_kg_d"]:g} reclaim, A-M-286)'),
                    ('3', f'Pattern injector: 2-post frame, platen, plunger, die plate ({d["injector_kW"]} kW)', 1,
                     'CS frame, pneumatic cylinder', f'{DOC} section 4; A-M-286 wax loop'),
                    ('4', 'Reclaim-wax melter with filter bag, on the lower shelf', 1, 'SS 304',
                     'SHELL_BURNOUT condensate return, 90 % reclaim (A-M-286)')]
            fast = ('item,size,grade,qty,location,basis\n'
                    '1,M10 x 30 bench bolts,ISO 898-1 8.8,12,legs and platen,study\n'
                    '2,M12 anchor,ISO 898-1 8.8,4,bench feet to slab,study\n')
            wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). LIVE unit - wax make-up import + 90 % reclaim (A-M-286).\n\n'
                  f'1. Weld the bench; fit the SS top and lower shelf.\n'
                  f'2. Set the {d["pot_L"]:.0f} L wax pot with thermostat; plumb the reclaim melter beside it on the shelf.\n'
                  f'3. Build the injector frame; align plunger to die plate.\n'
                  f'4. Test: wax at temperature, 10 injection shots; check reclaim melt quality.\n'
                  f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
            return export(U, m, rows, fast, wo)
        m = m.union(cyl_z(400, 300, 900, 150, 283))                                  # salt hopper (20 L)
        m = m.union(cyl_z(400, 300, 1183, 158, 8))                                   # hopper lid
        m = m.union(box(640, 240, 1030, 120, 120, 160))                              # mixer motor
        m = m.union(cyl_x(540, 300, 1100, 10, 100))                                  # mixer shaft
        m = m.union(box(100, 120, 900, 170, 150, 110))                               # mixing tub
        m = m.union(box(560, 380, 175, 220, 180, 220))                               # salt day-bin
        rows = [('1', 'Prep bench 800 x 600 x 900 mm, CS frame, lower shelf', 1, 'CS weldment, SS top',
                 f'{DOC} section 4; {d["bench"]}'),
                ('2', f'Salt hopper D300 x 283 mm, {d["hopper_L"]:.0f} L, with lid', 1, 'SS 304',
                 f'{d["salt_kg_d"]:g} kg/d salt-flux cover (Kroll MgCl2-class drag-out, A-M-284)'),
                ('3', f'Side-entry mixer {d["mixer_kW"]} kW with shaft and gland', 1, 'SS 304, PTFE gland',
                 f'{DOC} section 4'),
                ('4', 'Mixing tub and salt day-bin (lower shelf)', 2, 'SS 304 / HDPE',
                 f'{DOC} section 4; batch cover for the Al-charged melt')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M10 x 30 bench bolts,ISO 898-1 8.8,12,legs and hopper bracket,study\n'
                '2,M12 anchor,ISO 898-1 8.8,4,bench feet to slab,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). Live unit: the Kroll drag-out stream is connected (A-M-284).\n\n'
              f'1. Weld the bench; fit the SS top and lower shelf.\n'
              f'2. Set the {d["hopper_L"]:.0f} L salt hopper with lid; mount the {d["mixer_kW"]} kW side-entry mixer.\n'
              f'3. Place the mixing tub and the day-bin on the shelf.\n'
              f'4. Test: one {d["salt_kg_d"]:g} kg/d salt-flux batch; check the cover quality on a trial melt.\n'
              f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
        return export(U, m, rows, fast, wo)
    if style == 'box_furnace':                       # box furnace class
        if U == 'SHELL_BURNOUT':                     # flash-dewax + shell fire furnace
            m = box(0, 0, 0, 1000, 640, 900).cut(box(60, 60, 80, 880, 520, 780))    # chamber + cavity
            m = m.union(box(200, 10, 200, 600, 50, 500))                             # door frame / face
            m = m.union(box(90, 90, 90, 820, 520, 50))                               # shell trolley deck
            m = m.union(cyl_z(250, 320, 900, 75, 540))                               # off-gas stack
            m = m.union(cyl_z(500, 320, 900, 60, 360))                               # wax condenser
            m = m.union(cyl_x(325, 320, 1150, 22, 115))                              # stack -> condenser cross-duct
            m = m.union(cyl_x(560, 320, 980, 12, 300))                               # condensate run
            m = m.union(cyl_y(860, 320, 980, 12, 320))                               # downcomer to corridor
            m = m.union(cyl_z(860, 700, 240, 12, 660))                               # drop leg
            m = m.union(box(790, 660, 0, 180, 200, 240))                             # condensate receiver
            m = m.union(box(0, 660, 0, 400, 320, 1100))                              # control cabinet
            rows = [('1', f'Flash-dewax + fire chamber 1000 x 640 x 900 mm, {d["T_C"]:.0f} C, 60 mm lined', 1,
                     'CS casing, ceramic fibre', f'{DOC} section 4; {d["service"]}'),
                    ('2', 'Shell trolley deck with casters and stop', 1, 'CS, heat-resistant wheels',
                     f'{d["shell_kg_d"]:g} kg/d fired shells (A-M-286)'),
                    ('3', 'Off-gas stack DN150 with dewax-air bias damper', 1, 'SA-240 304L',
                     f'{DOC} section 4; flash dewax stage'),
                    ('4', f'Wax condenser D120 x 360 mm with run, downcomer and receiver', 1, 'SA-240 304L, jacketed',
                     f'{d["wax_reclaim_kg_d"]:g} kg/d wax reclaim to WAX_PATTERN; {d["burned_wax_kg_d"]:g} kg/d burned (A-M-286)'),
                    ('5', f'Control cabinet, SCR and {d["kW"]} kW elements, 2-zone', 1, 'CS enclosure, IP54',
                     f'{DOC} section 4; {d["condenser"]}')]
            fast = ('item,size,grade,qty,location,basis\n'
                    '1,M16 stud + 2 nuts (ISO 4014 / ISO 4032),ISO 898-1 8.8,16,door frame and stack flange,study\n'
                    '2,M12 anchor,ISO 898-1 8.8,4,chamber and cabinet feet,study\n')
            wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). LIVE unit - IND_TO_INV castings train (A-M-286).\n\n'
                  f'1. Fabricate the chamber; line 60 mm for {d["T_C"]:.0f} C; fit the door frame and trolley deck.\n'
                  f'2. Mount the DN150 stack with bias damper; set the wax condenser, run, downcomer and receiver.\n'
                  f'3. Wire the {d["kW"]} kW SCR zones; interlock door-open and stack draft.\n'
                  f'4. Test: dewax burn-off curve, then fire 8 shells; verify wax condensate quality to WAX_PATTERN.\n'
                  f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
            return export(U, m, rows, fast, wo)
        Dc, Hc = d['crucible_D_mm'], d['crucible_H_mm']                              # IND_MELT: induction melt box furnace
        m = box(0, 0, 0, 660, W, 1100)                                              # chamber casing
        m = m.cut(box(130, 150, 200, 400, W - 300, 800))                            # lined cavity
        m = m.union(box(0, 0, 1100, 660, W, 50))                                    # lid
        m = m.union(cyl_z(330, W / 2, 350, Dc / 2, Hc))                             # crucible
        m = m.union(cyl_z(330, W / 2, 380, Dc / 2 + 40, 90).cut(cyl_z(330, W / 2, 380, Dc / 2 + 20, 90)))   # coil band
        m = m.union(cyl_z(200, W * 0.30, 1150, 75, 300))                            # stack (through the lid)
        m = m.union(box(660, 0, 0, 340, W * 0.5, 1400))                             # PSU / matchbox cabinet
        m = m.union(box(660, W * 0.70, 0, 340, W * 0.30, 500))                      # tilt-frame hydraulics
        rows = [('1', f'Chamber 660 x {W} x 1100 mm, 150 mm ceramic-fibre lined, 4 mm CS casing, tilt pour', 1,
                 'SA-240 304L casing over ceramic fibre', f'{DOC} section 3; {d["service"]}'),
                ('2', f"Crucible {d['crucible_kg']:.0f} kg, ID {Dc} x {Hc} mm, {d['heats_d']} heats/d", 1,
                 'fused SiO2 isostatic (Cu/Fe/Zn classes)', f'{DOC} section 3; melt {d["melt_kWh_d"]} kWh/d, peak {d["peak_kW"]} kW of {d["connected_kW"]} kW connected'),
                ('3', 'Induction coil, medium frequency, with cooled leads', 1, 'Cu tube, water-cooled', 'A-M-232 power basis'),
                ('4', 'Extraction stack DN150 with damper', 1, 'SA-240 304L', 'metal-dust off-gas to MET_SCRUB'),
                ('5', f"PSU / matchbox cabinet, {d['connected_kW']:.0f} kW connected", 1, 'CS enclosure, IP54', 'A-M-232'),
                ('6', 'Tilt-frame hydraulics with trunnions', 1, 'CS weldment', f'{DOC} section 3'),
                ('7', 'Slag/skimmings tote under the tilt axis', 1, 'mild steel', 'FOUNDRY_SLAG_TO_LEACH, A-M-262')]
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M16 stud + 2 nuts (ISO 4014 / ISO 4032),ISO 898-1 8.8,24,lid and coil hatch flanges,study\n'
                '2,M12 anchor,ISO 898-1 8.8,6,chamber and cabinet feet,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication; no bought furnace.\n\n'
              f'1. Fold and weld the 660 x {W} mm chamber casing; line with 150 mm ceramic fibre.\n'
              f'2. Fit the {d["crucible_kg"]:.0f} kg crucible (ID {Dc} x {Hc} mm) on the hearth; wind and set the coil band.\n'
              f'3. Mount the tilt frame, trunnions and hydraulics; fit the lid and DN150 stack with damper.\n'
              f'4. Wire the {d["connected_kW"]:.0f} kW PSU cabinet; interlock lid-open and coil water flow.\n'
              f'5. Test: dry-out heat-up curve, then 2 trial heats of the {d["crucible_kg"]:.0f} kg charge ({d["heats_d"]} heats/d duty).\n'
              f'6. Inspect against models/mfg/{U}/export/{U.lower()}.step; record dimensions on the traveller.\n')
        return export(U, m, rows, fast, wo)
    if style == 'line_machine':
        mach = d.get('machine', '')
        if U == 'CAST_LINE':                         # permanent-mould Cu cast line
            m = box(0, 150, 0, 700, 500, 900)                                         # mould table
            m = m.union(box(310, 250, 900, 80, 300, 120))                             # ladle bracket
            m = m.union(cyl_z(350, 400, 1020, 110, 260))                              # pouring ladle
            m = m.union(box(750, 320, 820, 700, 160, 80))                             # runout table
            m = m.union(box(780, 320, 0, 60, 160, 820))                               # legs
            m = m.union(box(1390, 320, 0, 60, 160, 820))
            m = m.union(box(1320, 290, 0, 160, 220, 420))                             # shear/stop block
            rows = [('1', 'Permanent-mould table, 2 mould seats, water-cooled inserts', 1, 'CS weldment, Cu inserts',
                     f'{DOC} section 3; pour {d["pour_kg_d"]} kg/d Cu class'),
                    ('2', 'Pouring ladle 12 kg with tilt bracket', 1, 'CS, refractory lined', f'{DOC} section 3'),
                    ('3', 'Runout roller table 700 mm with 2 legs', 1, 'CS rollers', f'{DOC} section 3'),
                    ('4', 'Static shear / stop block at the line end', 1, 'CS + tool steel knife', 'sprue/runner campaign returns')]
        elif U == 'CONT_CAST':                      # two-strand semi-continuous caster
            m = box(0, 0, 0, 500, W, 700)                                            # mould/water tank zone
            m = m.union(cyl_x(25, 200, 350, 65, W - 200))                            # strand tube 1
            m = m.union(cyl_x(25, 600, 350, 65, W - 200))                            # strand tube 2
            m = m.union(box(550, 0, 50, 250, W, 600))                                # withdrawal rolls
            m = m.union(box(820, 0, 480, 650, W, 80))                                # runout table
            m = m.union(box(850, 0, 0, 80, W, 480))                                  # table legs
            m = m.union(box(1390, 0, 0, 80, W, 480))
            m = m.union(box(1280, 0, 560, 150, W, 500))                              # torch shear
            rows = [('1', 'Water tank and mould zone, 2 strands', 1, 'SS 304 casing; Cu moulds', f'{DOC} section 3'),
                    ('2', f'Water-cooled copper moulds, {d["strands"]} strands (Fe billet {d["billet_kg_d"]} + Zn ingot {d["ingot_kg_d"]} kg/d)',
                     d['strands'], 'Cu, water-cooled', f'{d["mould"]} (AQS-SIZE-FOUNDRY)'),
                    ('3', 'Withdrawal/straightener roll stand', 1, 'CS frame, tool-steel rolls', f'{DOC} section 3'),
                    ('4', 'Runout table 650 mm with legs', 1, 'CS rollers', f'{DOC} section 3'),
                    ('5', 'Torch shear at the runout end', 1, 'CS gantry', 'billet cut lengths')]
        elif U == 'ROLL':                           # two-high bench mill
            m = box(500, 0, 250, 100, W, 1000)                                        # housing plate A
            m = m.union(box(900, 0, 250, 100, W, 1000))                               # housing plate B
            m = m.union(cyl_y(700, 0, 500, d['rolls_D_mm'] / 2, W))                   # bottom roll
            m = m.union(cyl_y(700, 0, 810, d['rolls_D_mm'] / 2, W))                   # top roll
            m = m.union(box(60, 50, 745, 400, 700, 60))                               # entry table
            m = m.union(box(1040, 50, 745, 400, 700, 60))                             # exit table
            m = m.union(cyl_y(1150, 250, 175, 125, 300))                              # drive motor
            m = m.union(box(1000, 250, 150, 200, 300, 300))                           # gearbox
            rows = [('1', f"Two-high housing, rolls stacked at 310 mm centres", 1, 'CS weldment',
                     f'{DOC} section 3; {d["rolled_kg_d"]} kg/d'),
                    ('2', f"Work rolls {d['rolls_D_mm']} dia x {d['roll_L_mm']} mm", 2, 'forged tool steel', f'{DOC} section 3'),
                    ('3', 'Entry and exit roller tables 400 mm', 2, 'CS rollers', f'{DOC} section 3'),
                    ('4', 'Geared drive with motor', 1, 'geared motor, IEC frame', f'{d["kWh_d"]} kWh/d (A-M-177 rolling class)')]
        elif U == 'SHELL_BREAK':                    # vibratory knock-out station + reclaim sieve
            m = box(100, 260, 720, 1000, 360, 70)                                    # knock-out grid table
            m = m.union(box(100, 260, 560, 1000, 360, 40))                           # base frame
            for sx, sy in ((150, 300), (1050, 300), (150, 580), (1050, 580)):
                m = m.union(cyl_z(sx, sy, 600, 25, 120))                             # isolation springs
            m = m.union(cyl_y(1150, 380, 600, 60, 200))                              # eccentric vibrator drive
            m = m.union(box(1120, 300, 560, 120, 160, 120))                          # belt guard
            m = m.union(box(150, 300, 60, 900, 360, 500))                            # breakout bin
            m = m.union(box(1140, 300, 360, 320, 300, 40))                           # reclaim sieve deck
            m = m.union(box(1140, 320, 280, 300, 260, 60))                           # fines pan
            m = m.union(box(100, 240, 790, 1000, 420, 50))                           # dust hood
            m = m.union(cyl_z(950, 450, 840, 60, 280))                               # dust offtake
            rows = [('1', 'Vibratory knock-out table 1000 x 360 mm on isolation springs', 1, 'CS deck, Mn liner',
                     f'{DOC} section 4; {d["machine"]}'),
                    ('2', f'Eccentric vibrator drive, {d["table_kW"]} kW, with belt guard', 1, 'geared motor',
                     f'{DOC} section 4; A-M-199 forming class'),
                    ('3', f'Breakout bin 900 x 360 x 500 mm under the grid', 1, 'CS, lined',
                     f'{d["spent_shell_kg_d"]:g} kg/d spent shells (A-M-286)'),
                    ('4', f'Reclaim sieve deck 320 x 300 mm with fines pan', 1, 'SS mesh, CS pan',
                     f'{d["reclaim_kg_d"]:g} kg/d reclaim to SHELL_BUILD; {d["export_kg_d"]:g} kg/d fines exported (A-M-286)'),
                    ('5', 'Dust hood with DN120 offtake', 1, 'CS', 'knock-out dust to the baghouse')]
        elif U == 'SHELL_BUILD':                    # dip-coat + stucco rainfall booth
            m = box(100, 280, 100, 520, 340, 300).cut(box(120, 300, 100, 480, 300, 300))   # slurry tank (40 L)
            m = m.union(box(700, 160, 100, 420, 480, 880))                           # rainfall booth
            m = m.union(box(700, 160, 980, 420, 480, 140))                           # booth hopper top
            m = m.union(box(1180, 200, 100, 180, 180, 240))                          # stucco blower
            m = m.union(box(200, 660, 400, 50, 50, 840))                             # gantry posts
            m = m.union(box(1150, 660, 400, 50, 50, 840))
            m = m.union(box(200, 660, 1240, 1000, 50, 60))                           # gantry beam
            m = m.union(box(700, 645, 1180, 120, 80, 60))                            # hoist trolley
            for rx, ry in ((1320, 140), (1440, 140), (1320, 620), (1440, 620)):
                m = m.union(box(rx, ry, 0, 40, 40, 1100))                            # drying rack posts
            for i in range(3):
                m = m.union(box(1300, 120, 300 + i * 250, 180, 560, 30))             # rack shelves
            rows = [('1', f'Dip slurry tank 480 x 300 x 300 mm ({d["slurry_L"]:.0f} L), binder + flour', 1,
                     'SS 304, agitated', f'{DOC} section 4; {d["machine"]}'),
                    ('2', 'Rainfall stucco booth 420 x 480 x 880 mm with hopper top', 1, 'CS, recycled-stucco circuit',
                     f'{d["dips"]} dips per shell at 4 kg/kg castings (A-M-286)'),
                    ('3', 'Stucco blower / conveyor module', 1, 'CS', f'{DOC} section 4'),
                    ('4', 'Mold-handling gantry, 1000 mm span beam + hoist trolley', 1, 'CS beam, chain hoist',
                     f'{DOC} section 4'),
                    ('5', '3-tier drying rack 180 x 560 mm', 1, 'CS angle + mesh',
                     f'{d["shell_kg_d"]:g} kg/d shells; silica make-up {d["silica_makeup_kg_d"]:g} + reclaim {d["reclaim_kg_d"]:g} kg/d (A-M-286)')]
        elif U == 'INV_CAST':                       # investment casting tilt-pour station
            m = box(180, 300, 0, 320, 320, 700)                                      # tilt pedestal
            m = m.union(box(300, 440, 700, 150, 60, 60))                             # tilt bracket
            m = m.union(cyl_z(340, 460, 700, 110, 190))                              # pouring ladle
            m = m.union(cyl_y(340, 260, 760, 25, 440))                               # trunnion
            m = m.union(box(640, 240, 700, 520, 420, 70))                            # mold table
            for mx in (700, 810, 920, 1030):
                for my in (330, 480):
                    m = m.union(cyl_z(mx, my, 770, 48, 130))                         # shell mold seats
            m = m.union(box(1180, 260, 0, 60, 60, 900))                              # rollover frame posts
            m = m.union(box(1180, 480, 0, 60, 60, 900))
            m = m.union(box(1160, 260, 880, 120, 280, 40))                           # rollover cross-beam
            m = m.union(box(1240, 300, 0, 200, 240, 300))                            # cool/quench bin
            m = m.union(box(1380, 300, 0, 110, 240, 1000))                           # control pedestal
            rows = [('1', 'Tilt-pour pedestal and bracket, 700 mm axis height', 1, 'CS weldment',
                     f'{DOC} section 4; {d["machine"]}'),
                    ('2', 'Pouring ladle D220 x 190 mm, trunnion-mounted', 1, 'CS, refractory lined',
                     f'{d["pour_kg_d"]:g} kg/d pour from IND_MELT (A-M-286)'),
                    ('3', f'Mold table with {d["molds_per_campaign"]} fired-shell seats', 1, 'CS, pinned',
                     f'{d["shell_kg_d"]:g} kg/d shells at 8/campaign (A-M-286)'),
                    ('4', 'Rollover frame and cross-beam for shell cooling', 1, 'CS', f'{DOC} section 4'),
                    ('5', 'Cool/quench bin and control pedestal', 2, 'CS / CS enclosure IP54', f'{DOC} section 4')]
        else:
            return placeholder(U)
        fast = ('item,size,grade,qty,location,basis\n'
                '1,M16 T-bolt + nut (ISO 4014 / ISO 4032),ISO 898-1 8.8,12,machine feet and clamps,study\n'
                '2,M12 anchor,ISO 898-1 8.8,6,bench to slab,study\n')
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication; no bought line machine.\n\n'
              f'1. Fabricate and level the bench/frame; set the machine envelope {L} x {W} x {H} mm.\n'
              f'2. Fit the line elements per bom.csv ({mach}).\n'
              f'3. Guard the moving parts (ISO 14122-2 access; guards per AQS-BLD-012 class).\n'
              f'4. Test: dry run, then trial feed pass; record dimensions on the traveller.\n'
              f'5. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
        return export(U, m, rows, fast, wo)
    if style == 'store_rack':                       # STOCK_OUT
        m = None
        for x, y in ((30, 30), (L - 90, 30), (30, W - 90), (L - 90, W - 90)):
            post = box(x, y, 0, 60, 60, H)
            m = post if m is None else m.union(post)
        for i in range(3):
            m = m.union(box(0, 0, 60 + i * 500, L, W, 40))                           # tier shelves
        rows = [('1', f'Three-tier staging rack {L} x {W} x {H} mm, 500 mm tier pitch', 1, 'CS angle + mesh shelves',
                 f'{DOC} section 3; {d["issue_kg_d"]} kg/d shop issue, {d["hold_d"]:.0f} d staging'),
                ('2', 'Bar/plate dividers and location stops', 4, 'CS angle', 'class separation Cu / Fe / Zn'),
                ('3', 'Bin tote for offcut returns to the melt', 1, 'mild steel', 'MFG_SCRAP_TO_IND loop')]
        fast = 'item,size,grade,qty,location,basis\n1,M12 anchor,ISO 898-1 8.8,4,rack feet to slab,study\n'
        wo = (f'# Work order {U}\n\nAuthority: {DOC} (X-MFG-30 pattern). In-house fabrication.\n\n'
              f'1. Cut and weld the rack frame {L} x {W} x {H} mm, 3 tiers at 500 mm pitch.\n'
              f'2. Fit mesh shelves, dividers and the offcut tote.\n'
              f'3. Anchor to the slab; load test to 2x the {d["issue_kg_d"]} kg/d daily issue.\n'
              f'4. Inspect against models/mfg/{U}/export/{U.lower()}.step.\n')
        return export(U, m, rows, fast, wo)
    return placeholder(U)


if __name__ == '__main__':
    for U in (sys.argv[1:] or UNITS):
        assert U in UNITS, U
        build(U)
