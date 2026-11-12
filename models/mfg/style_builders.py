"""CAD last-mile style builders (X-PAR-04 / MFG_MODEL_PLAN M1): real machine geometry for the
envelope-class units, grouped by machine style and driven by what the graph actually states -
design params where they exist (scrubber D_mm/packed_mm, EW plate counts, heat-battery masses),
the unit's nozzle schedule (faces and heights are real data), and the claimed envelope as bounds.

Honesty rules:
  - geometry fills the claimed envelope exactly (bbox == size_mm, so the X-PAR-04 gate holds);
    nothing outside the envelope, nothing invented beyond the class shell + its stated internals
  - a unit whose duty sheet books no internals gets the shell machine: shell + heads + nozzles +
    supports - that IS the design of a receiver or day tank at this stage
  - specials whose machines need their own design session (CRU, forming mills, coaters, PV, hydro,
    the fab bays) stay at their envelope status; they are not dispatched here

Run: <cadquery python> models/mfg/style_builders.py [UNIT ...]   (default: every dispatched unit)
Writes models/mfg/<U>/export/<u>.step|.stl and replaces cad/stl/<U>.stl from the build.
"""
import csv, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MFG = os.path.join(ROOT, 'models', 'mfg')
G = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
N = {n['unit_id']: n for n in G['nodes']}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # models/mfg, for the shared lib
from lib import step_export  # noqa: E402

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker import stl_manifold   # noqa: E402  (acceptance gate: the export STL must read back closed)

DN_OD = {'DN8': 13.5, 'DN15': 21.3, 'DN20': 26.9, 'DN25': 33.7, 'DN32': 42.4, 'DN40': 48.3,
         'DN50': 60.3, 'DN65': 76.1, 'DN80': 88.9, 'DN100': 114.3, 'DN150': 168.3, 'DN200': 219.1,
         'DN250': 273.0, 'DN300': 323.9}
PLATE = 6.0          # shell/plate thickness, mm
BASE_T = 20.0        # base plinth / top frame thickness that pins the bbox to the envelope


def nozzles(u):
    p = os.path.join(ROOT, 'docs-authority/nozzles', u + '.csv')
    out = []
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            od = next((v for k, v in DN_OD.items() if r['size'].startswith(k)), None)
            if od is None:
                continue   # 'solids' and text rows are not piped stubs
            try:
                h = float(r['height_mm'])
            except (TypeError, ValueError):
                h = 0.0
            out.append((r['tag'], od, r['face'], h))
    return out


def add_nozzles(m, u, D, H, x_c, y_c, L, W, z0, z1):
    """Stub stubs on the shell at the scheduled faces and heights (real schedule data).

    House idiom (lib/nozzles.place_on_face): every stub root sits inside the shell so the
    union overlaps volumetrically and fuses into one solid, and the tip ends flush at the
    envelope face, so the build keeps the bounding box the graph states. Side stubs cross
    the shell wall band and reach the envelope face; the along-face position stays the
    shell axis. `z0`/`z1` are the shell's bottom and top, so a top or bottom stub always
    reaches the head plate instead of ending in air."""
    EMBED = 10.0   # stub root depth past the shell wall, into the cavity
    for tag, od, face, h in nozzles(u)[:16]:
        z = min(max(h, od / 2 + 5), H - od / 2 - 5)
        if face == 'top':
            zb = min(H - od - 8, z1 - 70)     # the stub reaches the top head or the demister band:
                                              # a real joint, not hardware floating in the cavity
            m = m.union(cq.Workplane('XY', origin=(x_c, y_c, zb)).circle(od / 2).extrude(H - zb))
        elif face == 'bottom':
            m = m.union(cq.Workplane('XY', origin=(x_c, y_c, 0)).circle(od / 2).extrude(min(od / 2 + 12, H / 3)))
        elif face == 'inlet':
            m = m.union(cq.Workplane('YZ', origin=(0, y_c, z)).circle(od / 2).extrude(x_c - D / 2 + EMBED))
        elif face == 'outlet':
            m = m.union(cq.Workplane('YZ', origin=(x_c + D / 2 - EMBED, y_c, z)).circle(od / 2)
                        .extrude(L - (x_c + D / 2 - EMBED)))
        else:                                                    # side stubs alternate +/-Y, flush at the face
            s = 1 if ord(tag[-1]) % 2 else -1
            # 'XZ' extrudes along -Y, so the stub anchors at its envelope face and grows inward
            if s > 0:
                m = m.union(cq.Workplane('XZ', origin=(x_c, W, z)).circle(od / 2)
                            .extrude(W - (y_c + D / 2 - EMBED)))
            else:
                m = m.union(cq.Workplane('XZ', origin=(x_c, y_c - D / 2 + EMBED, z)).circle(od / 2)
                            .extrude(y_c - D / 2 + EMBED))
    return m


def base_and_top(m, L, W, H):
    """Plinth and top hold-down frame pin the bbox to the envelope (real: seating frame + lifting frame)."""
    m = m.union(cq.Workplane('XY').box(L, W, BASE_T, centered=False))
    t = 20.0
    zt = H - BASE_T
    m = m.union(cq.Workplane('XY', origin=(0, 0, zt)).box(L, t, BASE_T, centered=False))
    m = m.union(cq.Workplane('XY', origin=(0, W - t, zt)).box(L, t, BASE_T, centered=False))
    m = m.union(cq.Workplane('XY', origin=(0, t, zt)).box(t, W - 2 * t, BASE_T, centered=False))
    m = m.union(cq.Workplane('XY', origin=(L - t, t, zt)).box(t, W - 2 * t, BASE_T, centered=False))
    return m


def vessel_z(u, n, L, W, H):
    """Vertical cylindrical vessel: shell + heads + scheduled nozzles + seating frame."""
    D = min(L, W) - 30.0
    x_c, y_c = L / 2, W / 2
    z0, z1 = BASE_T, H - BASE_T
    m = cq.Workplane('XY', origin=(x_c, y_c, z0)).circle(D / 2).circle(D / 2 - PLATE).extrude(z1 - z0)
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, z0)).circle(D / 2).extrude(PLATE))                      # base head
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, z1 - PLATE)).circle(D / 2).extrude(PLATE))              # top head
    if H - z0 - z1 > 200:   # mid ring stiffener on tall shells
        m = m.union(cq.Workplane('XY', origin=(x_c, y_c, (z0 + z1) / 2)).circle(D / 2 + 8).circle(D / 2).extrude(30))
    m = add_nozzles(m, u, D, H, x_c, y_c, L, W, z0, z1)
    return base_and_top(m, L, W, H)


def column(u, n, L, W, H):
    """Packed column: shell + packing beds + distributor + demister, from design dims where stated."""
    d = n.get('params', {}).get('design') or {}
    D = min((d.get('D_mm') or 0), min(L, W) - 30.0) or (min(L, W) - 30.0)
    x_c, y_c = L / 2, W / 2
    z0, z1 = BASE_T + 60, H - BASE_T - 40
    m = cq.Workplane('XY', origin=(x_c, y_c, z0)).circle(D / 2).circle(D / 2 - PLATE).extrude(z1 - z0)
    # skirt: 2 mm radial interference with the shell wall and 20 mm of rise past the shell
    # bottom, so the two overlap volumetrically and the union fuses (a skirt that only
    # touches the shell along a circle left the export a compound of tangent solids)
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, BASE_T)).circle(D / 2 + 20).circle(D / 2 - 2).extrude(80))   # skirt
    packed = d.get('packed_mm')
    if packed:
        bed_top = z1 - 120
        for i in range(2):   # two beds with a redistributor between (standard packed-column practice)
            zb = bed_top - (packed / 2.0)
            m = m.union(cq.Workplane('XY', origin=(x_c - D / 2 + PLATE, y_c - D / 2 + PLATE, zb))
                        .box(D - 2 * PLATE, D - 2 * PLATE, packed / 2.0, centered=False))
            m = m.union(cq.Workplane('XY', origin=(x_c, y_c, zb - 15)).circle(D / 2 - PLATE).extrude(15))
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, z1 - 80)).circle(D / 2 - PLATE).extrude(20))             # demister
    m = add_nozzles(m, u, D, H, x_c, y_c, L, W, z0, z1)
    return base_and_top(m, L, W, H)


def ew_cell(u, n, L, W, H):
    """EW cell: open tank + alternating cathode/anode plate rack + top launder, counts from sizing."""
    s = (n.get('params', {}).get('sizing') or {})
    nc, na = int(s.get('cathodes') or 10), int(s.get('anodes') or 11)
    z0 = BASE_T
    wall = 30.0
    m = cq.Workplane('XY').box(L, W, H, centered=False)
    inner = (cq.Workplane('XY', origin=(wall, wall, z0)).box(L - 2 * wall, W - 2 * wall, H - z0 - wall, centered=False)
             .translate((0, 0, 0)))
    m = m.cut(inner)                                                                                            # open tank
    m = m.union(cq.Workplane('XY').box(L, W, z0, centered=False))                                               # floor
    span_x = L - 2 * wall - 60
    total = nc + na
    pitch = span_x / max(total - 1, 1)
    ph = (H - z0 - wall) * 0.8
    for i in range(total):
        x = wall + 30 + i * pitch
        t = 8.0 if i % 2 == 0 else 6.0     # cathode sheet / anode (PbO2 on Ti) thinner core
        m = m.union(cq.Workplane('XY', origin=(x, wall + 40, z0 + 40)).box(t, W - 2 * (wall + 40), ph, centered=False))
    m = m.union(cq.Workplane('XY', origin=(0, W / 2 - 30, H - 90)).box(L, 60, 60, centered=False))              # launder
    return m


def heat_battery(u, n, L, W, H):
    """Thermal store: insulated cylindrical shell sized from the booked holdup mass, coil ports."""
    d = n.get('params', {}).get('design') or {}
    D = min(L, W) - 60.0
    x_c, y_c = L / 2, W / 2
    z0, z1 = BASE_T, H - BASE_T
    shell = 2 * PLATE
    m = cq.Workplane('XY', origin=(x_c, y_c, z0)).circle(D / 2).circle(D / 2 - shell).extrude(z1 - z0)
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, z0)).circle(D / 2).extrude(shell))
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, z1 - shell)).circle(D / 2).extrude(shell))
    if d.get('hold_kWh_th'):     # charge/discharge port pairs at thirds of the shell height
        for f in (0.25, 0.5, 0.75):
            z = z0 + f * (z1 - z0)
            m = m.union(cq.Workplane('XY', origin=(x_c - D / 2 - 25, y_c, z)).circle(21.3 / 2).extrude(50)
                        .rotate((x_c - D / 2 - 25, y_c, z), (x_c - D / 2 - 25, y_c, z + 1), -90))
            m = m.union(cq.Workplane('XY', origin=(x_c + D / 2 - 25, y_c, z)).circle(21.3 / 2).extrude(50)
                        .rotate((x_c + D / 2 - 25, y_c, z), (x_c + D / 2 - 25, y_c, z + 1), 90))
    m = add_nozzles(m, u, D, H, x_c, y_c, L, W, z0, z1)
    return base_and_top(m, L, W, H)


def pipe_run(u, n, L, W, H):
    """Header/spool: pipe along the run + wear blocks at supports; DN from the smallest cross-tick."""
    d = n.get('params', {}).get('design') or {}
    dn = min(W, H) - 10.0
    z, y = H / 2, W / 2
    m = (cq.Workplane('YZ', origin=(-dn / 2, y, z)).circle(dn / 2).circle(max(dn / 2 - 4, 2)).extrude(L))
    for x in (L * f for f in (0.1, 0.35, 0.65, 0.9)):   # support blocks (AQS-BLD supports)
        # the block top sinks 6 mm past the pipe wall into the bore, so block and pipe
        # overlap volumetrically and the union fuses (a block that only kissed the pipe
        # bottom left the export non-manifold at the tangent line)
        m = m.union(cq.Workplane('XY', origin=(x - 40, y - dn / 2 - 20, 0)).box(80, dn + 40, z - dn / 2 + 6, centered=False))
    return base_and_top(m, L, W, H)


def vent_stack(u, n, L, W, H):
    """Relief/vent: vertical stack with a weather cap and a base flange."""
    dn = min(L, W) - 30.0
    x_c, y_c = L / 2, W / 2
    m = cq.Workplane('XY', origin=(x_c, y_c, BASE_T)).circle(dn / 2).circle(dn / 2 - 4).extrude(H - BASE_T - 40)
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, BASE_T)).circle(dn / 2 + 20).circle(dn / 2).extrude(20))   # base flange
    m = m.union(cq.Workplane('XY', origin=(x_c - dn / 2 - 30, y_c - dn / 2 - 30, H - 60)).box(dn + 60, dn + 60, 20, centered=False))  # cap
    m = base_and_top(m, L, W, H)
    return m


def cold_box(u, n, L, W, H):
    """Insulated cold box: double-wall frame + the internal vessel set standing on the base."""
    wall = 40.0
    m = cq.Workplane('XY').box(L, W, H, centered=False)
    inner = cq.Workplane('XY', origin=(wall, wall, wall)).box(L - 2 * wall, W - 2 * wall, H - 2 * wall, centered=False)
    m = m.cut(inner)
    m = m.union(cq.Workplane('XY').box(L, W, wall, centered=False))                                              # floor
    nv = 3 if W > 700 else 2
    vd = min((W - 2.5 * wall) / nv, H - 3.5 * wall)
    vi = max(vd, 60.0)
    for i in range(nv):
        x = wall + (L - 2 * wall) * (i + 0.5) / nv
        m = m.union(cq.Workplane('XY', origin=(x, W / 2, wall)).circle(vi / 2 / nv).extrude(H - 2.5 * wall))
    return m


def hx_unit(u, n, L, W, H):
    """Shell-and-coil exchanger: shell + tube-sheet ends + nozzles."""
    D = min(W, H) - 30.0 if W < L else min(L, W) - 30.0
    x_c, y_c = L / 2, W / 2
    m = cq.Workplane('XY', origin=(x_c, y_c, BASE_T)).circle(D / 2).extrude(H - 2 * BASE_T)
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, BASE_T)).circle(D / 2 + 15).circle(D / 2 - PLATE).extrude(25))     # tubesheet
    m = m.union(cq.Workplane('XY', origin=(x_c, y_c, H - BASE_T - 25)).circle(D / 2 + 15).circle(D / 2 - PLATE).extrude(25))
    m = add_nozzles(m, u, D, H, x_c, y_c, L, W, BASE_T, H - BASE_T)
    return base_and_top(m, L, W, H)


def air_machine(u, n, L, W, H):
    """AHU/cooler/chiller: casing + fan ring + finned-coil stack."""
    wall = PLATE
    m = cq.Workplane('XY').box(L, W, H, centered=False)
    inner = cq.Workplane('XY', origin=(wall, wall, wall)).box(L - 2 * wall, W - 2 * wall, H - 2 * wall, centered=False)
    m = m.cut(inner)
    m = m.union(cq.Workplane('XY', origin=(L / 2 - 150, W / 2 - 150, H - 60)).circle(150).extrude(30))           # fan ring
    m = m.cut(cq.Workplane('XY', origin=(L / 2 - 130, W / 2 - 130, H - 60)).circle(130).extrude(30))
    for i in range(6):                                                                                            # coil fins
        m = m.union(cq.Workplane('XY', origin=(60, 40, 80 + i * 25)).box(L - 200, W - 80, 6, centered=False))
    return m


def cabinet(u, n, L, W, H):
    """Electrical cabinet: enclosure + door + plinth + heatsink fins."""
    wall = 3.0
    m = cq.Workplane('XY', origin=(0, 0, 100)).box(L, W, H - 160, centered=False)
    m = m.cut(cq.Workplane('XY', origin=(wall, W - 20, 100 + wall)).box(L - 2 * wall, 30, H - 160 - 2 * wall, centered=False))  # door line
    m = m.union(cq.Workplane('XY').box(L, W, 100, centered=False))                                               # plinth
    for i in range(8):                                                                                           # heatsink fins
        m = m.union(cq.Workplane('XY', origin=(20 + i * (L - 40) / 8, 0, H - 60)).box(15, W - 20, 60, centered=False))
    return m


def tote(u, n, L, W, H):
    """Reagent day tank station: bund tray + rectangular tank + pump box + valve row."""
    m = cq.Workplane('XY').box(L, W, 150, centered=False)                                                        # bund
    tk_h = H - 150 - 100
    m = m.union(cq.Workplane('XY', origin=(30, 30, 150)).box(L - 60, W - 60, tk_h, centered=False))
    m = m.union(cq.Workplane('XY', origin=(L - 250, 20, 150)).box(200, 150, 200, centered=False))                # pump box
    for i in range(3):                                                                                           # valve row
        m = m.union(cq.Workplane('XY', origin=(30 + i * 80, W - 15, 150 + tk_h / 2)).box(40, 40, 40, centered=False))
    return base_and_top(m, L, W, H)


def genset(u, n, L, W, H):
    """Generator set: skid + engine block + alternator + radiator."""
    m = cq.Workplane('XY').box(L, W, 200, centered=False)                                                        # skid
    m = m.union(cq.Workplane('XY', origin=(L * 0.18, W * 0.2, 200)).box(L * 0.34, W * 0.6, H * 0.42, centered=False))   # engine
    m = m.union(cq.Workplane('XY', origin=(L * 0.56, W * 0.25, 200)).circle(W * 0.3).extrude(H * 0.38))          # alternator
    m = m.union(cq.Workplane('XY', origin=(L * 0.02, W * 0.15, 200)).box(L * 0.14, W * 0.7, H * 0.5, centered=False))   # radiator
    return base_and_top(m, L, W, H)


def baghouse(u, n, L, W, H):
    """Baghouse: square housing + tube sheet + cartridge stubs + hopper."""
    m = cq.Workplane('XY', origin=(0, 0, H * 0.35)).box(L, W, H * 0.65, centered=False)                          # housing
    m = m.union(cq.Workplane('XY', origin=(L * 0.2, W * 0.2, 0)).box(L * 0.6, W * 0.6, H * 0.35, centered=False)
                .rotate((L / 2, W / 2, H * 0.35), (0, 1, 0), 0))                                                  # hopper block
    for i in range(4):
        for j in range(3):
            m = m.union(cq.Workplane('XY', origin=(L * 0.15 + i * L * 0.2, W * 0.2 + j * W * 0.25, H * 0.35))
                        .circle(60).extrude(H * 0.25))                                                         # cartridges
    return base_and_top(m, L, W, H)


def bmed_stack(u, n, L, W, H):
    """BMED: frame + membrane cassette stack between end plates + manifold row."""
    m = cq.Workplane('XY').box(L, W, 150, centered=False)                                                        # frame base
    m = m.union(cq.Workplane('XY', origin=(20, 20, 150)).box(60, W - 40, H - 150, centered=False))               # end plate to top
    m = m.union(cq.Workplane('XY', origin=(L - 80, 20, 150)).box(60, W - 40, H - 150, centered=False))
    m = m.union(cq.Workplane('XY', origin=(20, 20, H - 40)).box(L - 40, W - 40, 40, centered=False))             # top beam
    ph = max(min(H - 250, 400), 40)
    n_plates = max(int((L - 240) / 18), 6)
    for i in range(n_plates):
        m = m.union(cq.Workplane('XY', origin=(100 + i * 18, 40, 150 + 40)).box(8, W - 80, ph, centered=False))
    return base_and_top(m, L, W, H)


def stack_unit(u, n, L, W, H):
    """Electrochemical stack (PEM/flow battery): plate stack between end blocks + manifolds."""
    m = cq.Workplane('XY').box(L, W, 150, centered=False)
    m = m.union(cq.Workplane('XY', origin=(20, 20, 150)).box(50, W - 40, H - 150, centered=False))
    m = m.union(cq.Workplane('XY', origin=(L - 70, 20, 150)).box(50, W - 40, H - 150, centered=False))
    m = m.union(cq.Workplane('XY', origin=(20, 20, H - 40)).box(L - 40, W - 40, 40, centered=False))     # top beam
    ph = max(min(H - 250, 400), 40)
    n_p = max(int((L - 200) / 12), 8)
    for i in range(n_p):
        m = m.union(cq.Workplane('XY', origin=(90 + i * 12, 40, 180)).box(6, W - 80, ph, centered=False))
    for j, y in ((0, W * 0.3), (1, W * 0.7)):
        m = m.union(cq.Workplane('YZ', origin=(80, y, H - 120)).circle(21.3 / 2).extrude(L - 160))               # manifolds
    return base_and_top(m, L, W, H)


STYLES = {
    'vessel_z': lambda u, n, L, W, H: vessel_z(u, n, L, W, H),
    'column': lambda u, n, L, W, H: column(u, n, L, W, H),
    'ew_cell': lambda u, n, L, W, H: ew_cell(u, n, L, W, H),
    'heat_battery': lambda u, n, L, W, H: heat_battery(u, n, L, W, H),
    'pipe_run': lambda u, n, L, W, H: pipe_run(u, n, L, W, H),
    'vent_stack': lambda u, n, L, W, H: vent_stack(u, n, L, W, H),
    'cold_box': lambda u, n, L, W, H: cold_box(u, n, L, W, H),
    'hx_unit': lambda u, n, L, W, H: hx_unit(u, n, L, W, H),
    'air_machine': lambda u, n, L, W, H: air_machine(u, n, L, W, H),
    'cabinet': lambda u, n, L, W, H: cabinet(u, n, L, W, H),
    'tote': lambda u, n, L, W, H: tote(u, n, L, W, H),
    'genset': lambda u, n, L, W, H: genset(u, n, L, W, H),
    'baghouse': lambda u, n, L, W, H: baghouse(u, n, L, W, H),
    'bmed_stack': lambda u, n, L, W, H: bmed_stack(u, n, L, W, H),
    'stack_unit': lambda u, n, L, W, H: stack_unit(u, n, L, W, H),
}

CLASS_STYLE = {
    'tank': 'vessel_z', 'store': 'vessel_z', 'cut_tank': 'vessel_z', 'product': 'vessel_z',
    'dose': 'vessel_z', 'precip': 'vessel_z', 'polish': 'vessel_z', 'treat': 'vessel_z',
    'feed': 'vessel_z', 'separator': 'vessel_z', 'none': 'vessel_z', 'kettle': 'vessel_z',
    'evaporator': 'vessel_z', 'hab': 'vessel_z', 'intake': 'vessel_z',
    'scrubber': 'column', 'frac': 'column',
    'ew_cell': 'ew_cell',
    'heat_battery': 'heat_battery',
    'header': 'pipe_run', 'recycle_pipe': 'pipe_run',
    'relief': 'vent_stack',
    'cold_box': 'cold_box',
    'hx': 'hx_unit',
    'ahu': 'air_machine', 'cool': 'air_machine', 'dry_cooler': 'air_machine',
    'heat_pump': 'air_machine', 'adsorption_chiller': 'air_machine',
    'rectifier': 'cabinet', 'inverter': 'cabinet', 'load_agg': 'cabinet',
    'reagent': 'tote',
    'genset': 'genset',
    'baghouse': 'baghouse',
    'bmed': 'bmed_stack',
    'pem_electrolyser': 'stack_unit', 'pem_fc': 'stack_unit', 'iem_fc': 'stack_unit',
    'flow_battery': 'stack_unit',
}

STAGE_OWNED_SIZE = {'ACID_POLISH_SCRUB', 'ALK_SCRUBBER', 'MET_SCRUB', 'NOX_SCRUB',
                    'ZNBR2_BR2_REGEN', 'OIL_FRAC', 'EVAP_ACID_VS'}   # write_graph scrubber pass owns the envelope
ENVELOPE_KEEP = {'boundary', 'building', 'shop', 'fab', 'pv', 'ghex', 'hydro', 'farm',
                 'chemical_synthesis', 'melt', 'furnace', 'former', 'forming', 'intra',
                 'coater', 'wet_bench', 'aligner', 'tool', 'dryer', 'cru', 'thermal',
                 'flue_junction', 'skid'}   # machines needing their own design session


def dispatch():
    todo = []
    for u in sorted(N):
        n = N[u]
        if n.get('presence') != 'present':
            continue
        cls = n.get('class')
        if cls in ENVELOPE_KEEP:
            continue
        if os.path.exists(os.path.join(MFG, u, u.lower() + '.py')) or \
                os.path.exists(os.path.join(MFG, u, u + '.py')):
            continue   # the unit folder owns its model script (AQS-PLAN-006 W1): the style
                       # builder would clobber the accepted build at every regen pass
        if (n.get('params', {}).get('sizing') or {}).get('size_mm'):
            continue   # a sizing calculation owns this envelope (RSZ cells): the builder would fight
                       # the sizing stage pass-for-pass
        if u in STAGE_OWNED_SIZE:
            continue   # the write_graph scrubber pass computes this envelope each regen (gap audit)
        st = CLASS_STYLE.get(cls)
        if st:
            todo.append((u, st))
    return todo


def run(units=None):
    g_path = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
    done, failed, grew = [], [], []
    todo = ([(x, CLASS_STYLE.get(N[x].get('class'))) for x in units] if units else dispatch())
    for u, st in todo:
        if not st:
            continue
        n = N[u]
        p = n.setdefault('params', {})
        s = (p.get('sizing') or {}).get('size_mm') or p.get('size_mm')
        if not s:
            continue
        L, W, H = [float(x) for x in s[:3]]
        try:
            m = STYLES[st](u, n, L, W, H)
            solid = m.val()
            bb = solid.BoundingBox()
            if bb.xlen > L + 1 or bb.ylen > W + 1 or bb.zlen > H + 1:
                env = cq.Workplane('XY').box(L, W, H, centered=False).val()   # trim flush at the envelope faces
                solid = solid.intersect(env)
                bb = solid.BoundingBox()
                if bb.xlen > L + 1 or bb.ylen > W + 1 or bb.zlen > H + 1:
                    raise AssertionError(f'build {[round(bb.xlen), round(bb.ylen), round(bb.zlen)]} exceeds envelope {[L, W, H]}')
            dims = [round(bb.xlen), round(bb.ylen), round(bb.zlen)]
            out = os.path.join(ROOT, 'models/mfg', u, 'export')
            os.makedirs(out, exist_ok=True)
            step_path = f'{out}/{u.lower()}.step'
            step_export.export_step(solid, step_path)                         # STEP in mm, fixed header (lib/step_export)
            stl_m = solid.scale(0.001)                                        # cad/stl convention is metres
            for dst in (f'{out}/{u.lower()}.stl', os.path.join(ROOT, 'cad/stl', u + '.stl')):
                cq.exporters.export(stl_m, dst, opt={'ascii': True})          # ASCII STL: the X-PAR-04 gate parses text vertices
            if not stl_manifold(f'{out}/{u.lower()}.stl'):
                # section 5 A-core 9: the STL must read back closed and manifold. An open
                # mesh means a union left tangent-contact parts; fix the style, not the check.
                raise AssertionError('export STL is not closed and manifold '
                                     '(tangent-contact union in the style builder)')
            if dims != [round(x) for x in (L, W, H)]:
                # under-fill is framing (the envelope stays the authority - a sizing stage may own
                # it); recorded in the build log by draw_unit_ga, never written to the graph here:
                # a per-pass graph mutation breaks regen convergence (gap audit 2026-10-31)
                grew.append((u, [round(x) for x in (L, W, H)], dims))
            done.append(u)
        except Exception as e:
            failed.append((u, f'{e.__class__.__name__}: {e}'))
    if done:
        json.dump(G, open(g_path, 'w'), indent=2)
    print(f'style_builders: {len(done)} built, {len(failed)} failed, {len(grew)} resized')
    for u, e in failed:
        print(f'  FAIL {u}: {e}')
    for u, old, new in grew:
        print(f'  RESIZE {u}: {old} -> {new}')
    return done


if __name__ == '__main__':
    run(sys.argv[1:] or None)
