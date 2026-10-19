"""FOUNDRY train parametric CAD (CadQuery, X-MFG-30 pattern). Reads params.design + params.envelope on the graph
(written by flow_graph/param/foundry_poly.py, AQS-DUTY-072) and writes models/mfg/<UNIT>/export/<unit>.step and .stl,
bom.csv, fasteners.csv and WORK_ORDER.md per unit. Live trains (scrap-remelt melt-and-cast + roll + stock staging)
get machine geometry; standby trains (pot/cell, investment casting, alternates, forming extras) get the envelope box
only as a presence-consistent PLACEHOLDER, marked in bom.csv and the work order.
Run: /tmp/cqvenv/bin/python models/mfg/foundry.py [UNIT ...]"""
import csv, json, os, sys
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
    if style == 'box_furnace':                     # IND_MELT: induction melt box furnace
        Dc, Hc = d['crucible_D_mm'], d['crucible_H_mm']
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
        if U == 'CAST_LINE':                        # permanent-mould Cu cast line
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
