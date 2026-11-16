"""engine v2: the protection book (the physics half of the ledger section D
row protection — the reference writers docs-authority/_protection.py and
docs-authority/_grounding_study.py, AQS-ELEC-005/006).

The v1 stages compute a JSON book and print it: the grounding-grid resistance
of _grounding_study.py (IEEE Std 80-2013 Sverak equation 52 over the drivers'
ELEC.distribution-train.gnd_* basis and the converged building footprint, the
graph PV_ARRAY params.roof) and the coordination plus touch/step study of
_protection.py over the committed one-line table (inverter-limited fault,
thermal-magnetic or electronic-trip settings per feeder, the IEEE 80 mesh and
step voltages of equations 85-94 against the tolerable limits of equations 32
and 29). This module ports both as pure functions; the one-line rows enter
composed (the display values the v1 stage parsed out of the committed
ONE_LINE.md text — the landed render/electrical.py book formats exactly
those), so no document is parsed and no file is read.

The committed PROTECTION.md page is hand-authored (its figures predate the
current roof and inverter count; no writer exists in the tree), so the page
itself stays in the electrical wave's REMAINING census; this book is the
golden the eventual renderer and the owner's page refresh quote.

Golden equality: flow_graph/v2/test_safety_books.py runs the two v1 print-only
stages and compares their stdout books against these functions over the same
model and inputs.

Pure: no I/O, no wall-clock, no RNG, no float literals (the engine lint's
discipline; the drivers, the seed books and the one-line rows carry the
values).
"""
import math


def grounding_study(m, d):
    """The IEEE 80-2013 grid-resistance book of _grounding_study.py (Sverak
    equation 52, Rev B D75: the grid follows the converged building — graph
    PV_ARRAY params.roof — plus the 10 m west yard; mesh on every second 6 m
    column line; rods at the driver pitch on the ring, A-M-110)."""
    def v(k):
        return d[k]['value']

    rf = m.field('node', 'PV_ARRAY', 'params')['roof']
    x = rf['footprint_mm'][0] / 1000 + v('ELEC.distribution-train.gnd_west_yard_m')
    y = rf['footprint_mm'][1] / 1000                                    # m, building plus west yard
    h = v('ELEC.distribution-train.gnd_depth_m')
    mesh = v('ELEC.distribution-train.gnd_mesh_spacing_m')
    rho = v('ELEC.distribution-train.gnd_soil_rho_ohm_m')               # ohm m, soil resistivity (clay, AQS-SITE-002)
    lr = 2 * (x + y)
    rods = math.ceil(lr / v('ELEC.distribution-train.gnd_rod_pitch_m'))
    rod_l = v('ELEC.distribution-train.gnd_rod_L_m')
    lm = (math.floor(x / mesh) - 1) * y + (math.floor(y / mesh) - 1) * x
    a = x * y
    lt = lr + lm + rods * rod_l
    rg = rho * (1 / lt + 1 / math.sqrt(20 * a) * (1 + 1 / (1 + h * math.sqrt(20 / a))))
    return dict(rho=rho, A_m2=a, ring_m=lr, mesh_m=lm, rods=rods, LT_m=lt, Rg_ohm=round(rg, 3),
                target_ohm=v('ELEC.distribution-train.gnd_target_ohm'))


_MAIN_LADDER = (100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000, 1200, 1600, 2000,
                2500, 3000, 4000, 5000, 6000)                          # the main-breaker NEC ladder of _protection.py
V_BUS = 480                                                          # the main bus volts
PP_V = 208                                                           # the PP-1 panel volts


def protection_book(m, d, feeders, xf_kva, grid):
    """The coordination and IEEE 80 touch/step book of _protection.py.
    feeders: (bus, load, a, breaker) per one-line table row, with a and
    breaker exactly as the committed table displays them (the v1 stage parsed
    the two columns out of the ONE_LINE.md text). xf_kva: the T-1 transformer
    kVA (the one-line ladder pick). grid: the grounding_study() book."""
    def v(k):
        return d[k]['value']

    inv = m.field('node', 'SOL_ARK_60K', 'params')
    inv_kw = float(inv.get('kW', 60))
    kf = float('2.0')                                                   # inverter fault contribution 2 x rated (study)
    irated = inv_kw * 1000 / (math.sqrt(3) * V_BUS)
    ifault = kf * irated
    fe = []
    for bus, load, a, br in feeders:
        bus480 = '480' in bus
        f_if = ifault if bus480 else min(ifault * V_BUS / PP_V * float('0.95'),
                                         xf_kva * 1000 / (math.sqrt(3) * PP_V) / float('0.05'))  # T-1 5 % impedance (study)
        inst_tm = 5 * br                                                # thermal-magnetic low instantaneous 5x (study)
        if inst_tm <= f_if * float('0.8'):
            dev, setg = 'thermal-magnetic, instantaneous 5×', f'{inst_tm:.0f} A'
        else:
            dev, setg = 'electronic trip, short-time pickup 1.5×, 0.1 s', f"{float('1.5') * br:.0f} A"
        fe.append(dict(bus=bus.strip(), load=load.strip(), A=a, breaker=br, If=f_if, device=dev, setting=setg))
    main = dict(breaker=max((inv.get('sections') or {}).get('breaker_A', [0])) or
                next(b for b in _MAIN_LADDER if b >= float('1.25') * irated), If=ifault)
    # IEEE 80-2013 mesh and step voltage (equations 85-94), rectangular grid,
    # rods on the perimeter (Kii 1), 2/0 AWG (d 0.0105 m), h 0.75 m burial
    d_cond = float('0.0105')
    h = float('0.75')
    d_spacing = float('12.0')
    lc = grid['ring_m'] + grid['mesh_m']
    lr = grid['rods'] * float('3.0')
    a = grid['A_m2']
    lp = grid['ring_m']
    n_cond = (2 * lc / lp) * math.sqrt(lp / (4 * math.sqrt(a)))
    kh = math.sqrt(1 + h)
    km = 1 / (2 * math.pi) * (math.log(d_spacing ** 2 / (16 * h * d_cond) + (d_spacing + 2 * h) ** 2 / (8 * d_spacing * d_cond) - h / (4 * d_cond))
                              + 1 / kh * math.log(8 / (math.pi * (2 * n_cond - 1))))
    ki = float('0.644') + float('0.148') * n_cond
    ks = 1 / math.pi * (1 / (2 * h) + 1 / (d_spacing + h) + 1 / d_spacing * (1 - float('0.5') ** (n_cond - 2)))
    lm_total = lc + (float('1.55') + float('1.22') * (float('3.0') / math.sqrt(2 * a))) * lr
    gpr = ifault * grid['Rg_ohm']
    em = float('50.0') * km * ki * ifault / lm_total
    es = float('50.0') * ks * ki * ifault / (float('0.75') * lc + float('0.85') * lr)

    def cs(rho, rhos, hs):
        return 1 - float('0.09') * (1 - rho / rhos) / (2 * hs + float('0.09'))

    ts = float('0.5')                                                   # the clearing time, s
    rho = grid['rho']
    cases = {'bare soil': (rho, float('1.0')),
             'crushed rock 0.1 m, 3000 ohm m': (float('3000.0'), cs(rho, float('3000.0'), float('0.1')))}
    tolerable = {k: dict(touch=(1000 + float('1.5') * c * r) * float('0.116') / math.sqrt(ts),
                         step=(1000 + 6 * c * r) * float('0.116') / math.sqrt(ts)) for k, (r, c) in cases.items()}
    return dict(Irated=irated, Ifault=ifault, feeders=fe, main=main, Rg=grid['Rg_ohm'], GPR=gpr, Em=em, Es=es,
                n=n_cond, ts=ts, tolerable=tolerable)
