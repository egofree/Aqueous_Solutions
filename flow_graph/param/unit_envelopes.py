"""Need-based envelopes for units that had no graph size (A-M-199). Envelope = max(hold-up box, task minimum box).
Hold-up box: inflow (kg/d) x residence (d) / bulk density, vertical H/D = atm_HD, plus 300 mm access on plan and 500 mm head.
Task minimum box: the smallest frame that does the stated task at this scale (A-M-199 table below), not a catalogue item.
HABITATION is a room, not equipment: its plan comes from the crew area (params.py HAB_X/Y), loaded as floor live load in AQS-BLD."""
from . import drivers as DR
# class: (residence d, bulk density kg/m3, minimum L, W, H mm, basis)
RULE = {'hopper':    (1.0, 1500, (1000, 1000, 1500), 'one day of feed buffer ahead of the shredder'),
        'feed':      (7.0, 1200, (800, 600, 1200), 'one week of salt make-up'),
        'separator': (1/24, 1300, (1200, 800, 1500), 'float-sink bath, 1 h hold-up, two dewatering screens'),
        'dryer':     (1/24, 900, (800, 600, 1200), '1 h hold-up, heated chamber'),
        'baghouse':  (0.0, 1, (800, 800, 2000), 'filter bags 2 m long, hopper below'),
        'ahu':       (0.0, 1, (1500, 900, 1200), 'fan, coil and filter bank in series at the duty air flow'),
        'cool':      (0.0, 1, (800, 600, 1200), 'dedicated chiller module'),
        'cold_box':  (0.0, 1, (800, 800, 2500), 'packed column in a vacuum jacket'),
        'forming':   (0.0, 1, (1500, 800, 1500), 'bench forming machine with guards'),
        'melt':      (1/24, 7000, (1000, 1000, 1500), 'induction crucible and pouring frame'),
        'thermal':   (0.0, 1, (600, 600, 1200), 'chamber ID 200 x 600 mm plus refractory and burner'),
        'hydro':     (0.0, 1, (1200, 800, 1200), 'pump-turbine, generator and inlet valve on one bedplate')}
def size(unit, node, inflow_kg_d):
    p = (node or {}).get('params') or {}; c = (node or {}).get('class')
    if c == 'hab': return None, 'room: floor live load (AQS-BLD-014)'
    if c not in RULE: return None, 'no rule'
    tau, rho, mn, basis = RULE[c]; d = DR.load(); HD = DR.val(d, 'atm_HD')
    V = inflow_kg_d*tau/rho if tau else 0.0
    D = (4*V/(3.1416*HD))**(1/3)*1000 if V > 0 else 0.0
    z = [max(mn[0], D + 300), max(mn[1], D + 300), max(mn[2], D*HD + 500)]
    return [round(x, -1) for x in z], f'A-M-199 {c}: {basis}; hold-up {V:.2f} m3'
