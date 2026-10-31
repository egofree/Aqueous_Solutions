"""Rare-earth magnet recovery unit REE_RECOVER (X-END-02 route; Q-013 reopen; A-M-433).

Closes the Nd/Dy composition hold of the EOL matrix: the NdFeB magnets of the motor families
(AQS-INV-005: MF-01 2.8 g x 14, MF-02 28.7 g x 55 installed; MF-03/22/23 reserved variants)
were held 'recovery has no unit'. This module adds the recovery unit as a BATCH CAMPAIGN bench:

  Route (published short-product NdFeB recycling, ULLMANN_REE class):
    1. demagnetise       heat > 320 C (Nd2Fe14B Curie 310-320 C)
    2. HCl leach         Fe + RE dissolve (plant acid loop, BMED 30 wt% class); H2 to the vent header
    3. Fe removal        oxidise Fe(II)->Fe(III) (H2O2), Fe(OH)3 sweep at pH 3-3.5 (NaOH); cake to MET_MELT remnant
    4. RE oxalate        H2C2O4 precipitation at pH 1-2; RE2(C2O4)3 out, Na/Fe stay soluble
    5. calcine 900 C     RE2O3 concentrate (REO) - the tradeable product
  Filtrate is NaCl brine -> the BMED feed class (closes Cl and Na back into the plant loops).

  Campaign basis (A-M-433): one full motor-fleet retirement = 1.618 kg NdFeB
    (MF-01 14 x 2.8 g + MF-02 55 x 28.7 g); the reserved families (MF-22 104.7 g, MF-23 555.2 g)
    ride the same batch capacity. Campaign chemistry (bounding, study):
    magnets 1.618 kg (31 wt% RE / 67.8 % Fe / 1.2 % B) with HCl 30 % aq 6.0 kg, H2O2 30 % 1.11 kg,
    oxalic acid dihydrate 0.46 kg, NaOH 2.36 kg, wash water 10.0 kg ->
    REO 0.585 kg, Fe(OH)3 cake 2.10 kg, NaCl brine filtrate 18.8 kg (16.6 wt% NaCl), H2 0.040 kg.

  NO daily mass edges by design: magnet scrap arises at motor end-of-life, not per day - the
  daily mass graph stays untouched (the 94.4 % closure and the balance fixed point are unaffected).
  The unit is a bench-campaign unit in the MFG wet-chem row (MET_SYN class), continuous 0.3 kW study.

Run: python3 -m flow_graph.param.ree_recover [--write]
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
SP = os.path.join(ROOT, 'flow_graph/placement_seed.json')
TAG = 'A-M-433 X-END-02 rare-earth route (Q-013): REE_RECOVER batch campaign'

CAMPAIGN = dict(
    ndfeb_kg=1.618, re_pct=31.0, fe_pct=67.8, b_pct=1.2,
    hcl_30_kg=6.0, h2o2_30_kg=1.11, oxalic_kg=0.46, naoh_kg=2.36, wash_kg=10.0,
    reo_kg=0.585, fe_cake_kg=2.10, brine_kg=18.8, brine_nacl_pct=16.6, h2_kg=0.040,
    families='MF-01 14 x 2.8 g; MF-02 55 x 28.7 g installed; MF-03/22/23 reserved variants',
)


def build():
    g = json.load(open(GP))
    N = {n['unit_id']: n for n in g['nodes']}
    made = []
    if 'REE_RECOVER' not in N:
        g['nodes'].append({
            'unit_id': 'REE_RECOVER', 'sector_id': 'MFG', 'class': 'precip', 'presence': 'present',
            'enabled': True, 'tags': ['rare earth', 'eol'], 'electrical_role': None,
            'diagram_gap': None, 'modules': [],
            'notes': 'Rare-earth magnet recovery bench (batch campaign, X-END-02 route; Q-013). '
                     'No continuous mass edges: magnet scrap arises at motor retirement, not per day.',
            'continuous_kw': {'value': 0.3, 'unit': 'kW', 'status': 'study',
                              'note': f'{TAG}. muffle 0.25 kW + stirrer/pumps 0.05 kW; campaign duty, not continuous process load.'},
        })
        made.append('node')
    n = next(x for x in g['nodes'] if x['unit_id'] == 'REE_RECOVER')
    p = n.setdefault('params', {})
    if 'sizing' not in p or 'campaign' in p.get('sizing', {}):
        p['design'] = {
            'service': 'rare-earth magnet recovery (batch campaign): demag > 320 C, HCl leach, Fe removal, RE oxalate precipitation, 900 C calcine',
            'route': 'published short-product NdFeB recycling; HCl from the plant acid loop (BMED 30 wt% class)',
            'campaign': CAMPAIGN,
            'campaign_basis': 'largest installed-family campaign MF-02 55 x 28.7 g = 1.578 kg; full-fleet campaign 1.618 kg '
                              '(A-M-433); reserved families (MF-23 555.2 g/unit) ride the same batch capacity',
            'closures': 'Fe(OH)3 cake to MET_MELT remnant; NaCl brine filtrate to the BMED feed class; REO product exported',
        }
        p['sizing'] = {
            'campaign_kg': CAMPAIGN['ndfeb_kg'],
            'reo_kg_campaign': CAMPAIGN['reo_kg'],
            'reactor_L': 10.0,
            'power_kW': 0.3,
            'basis': 'bench campaign skid: 10 L glass-lined leach reactor + demag oven + filter + muffle; '
                     'largest installed-family campaign MF-02 1.578 kg (A-M-433)',
        }
        made.append('sizing')
    s3m = p.get('sec3_material')
    if not isinstance(s3m, dict) or not {'mat', 'basis', 'alt', 'note', 'task'} <= set(s3m):
        p['sec3_material'] = {
            'mat': 'glass-lined reactor, PTFE transfer, PP-H filter wetted (HCl service per AQS-STD-002 '
                   'thermoplastic rules; no metal wetted part below 60 C); 316L muffle shell (dry oxide, 900 C)',
            'basis': 'X-MAT-22 section-3 selection for the REE_RECOVER campaign bench: HCl leach at < 60 C '
                     '(thermoplastic/glass class per AQS-STD-002 M-rules); the 900 C muffle is dry oxide service (316L shell).',
            'alt': 'Hastelloy C-276 wetted parts if the campaign moves above 60 C (AQS-STD-002 metal-acid rule); '
                   'not required at the bench campaign scale',
            'note': 'X-MAT-22 issued selection for the campaign bench; thermoplastic/glass wetted class',
            'task': 'X-MAT-22',
        }
        made.append('material')
    if 'size_mm' not in p:
        p['size_mm'] = [800, 600, 1400]
        p['size_note'] = ('bench campaign skid: demag oven + 10 L leach reactor + filter + muffle on one frame '
                          f'(fume-hood class, MET_SYN row); {TAG}')
        made.append('size')
    json.dump(g, open(GP, 'w'), indent=2)
    return made


def seat():
    """Place the bench beside the MFG wet-chem row (MET_SYN), 800 mm clearance, first free spot east."""
    seed = json.load(open(SP))
    if any(u['unit_id'] == 'REE_RECOVER' for u in seed['units']):
        return 'already seated'
    met = next(u for u in seed['units'] if u['unit_id'] == 'MET_SYN')
    W, D, H = 800, 600, 1400
    x0, y0 = met['origin_mm'][0], met['origin_mm'][1]
    occupied = [(u['origin_mm'][0], u['origin_mm'][1],
                 u['origin_mm'][0] + u['size_mm'][0], u['origin_mm'][1] + u['size_mm'][1])
                for u in seed['units'] if u['level'] == met['level']]
    for step in range(60):   # march east, then north, until 800 mm clear
        x = x0 + 1500 + step * (W + 800)
        y = y0 + (300 * (step // 20) * (1 if step % 40 < 20 else -1))
        box = (x, y, x + W + 800, y + D + 800)
        if not any(not (box[2] < o[0] or box[0] > o[2] or box[3] < o[1] or box[1] > o[3]) for o in occupied):
            seed['units'].append({
                'unit_id': 'REE_RECOVER', 'level': met['level'], 'origin_mm': [x, y, 0], 'size_mm': [W, D, H],
                'source': f'{TAG}: bench campaign unit seated beside the MFG wet-chem row (MET_SYN), '
                          '800 mm clearance; no daily mass edges, so the process-adjacency refinement does not re-seat it.'})
            json.dump(seed, open(SP, 'w'), indent=1)
            return f'seated at {met["level"]} [{x}, {y}]'
    return 'no free seat found - placement needs a hand'


if __name__ == '__main__':
    made = build()
    seat_msg = seat()
    print('REE_RECOVER:', ', '.join(made) if made else 'graph current', '|', seat_msg)
