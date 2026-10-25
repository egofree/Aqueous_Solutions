"""AQS-DUTY-064 storage and holdup sizing (unit task 02 for storage-class units; A-M-225).
Working volume V = Q x t_hold / rho with Q = max(design capacity, duty in) kg/d (X-RSZ-07 bounding case where present);
nominal volume = V / 0.80 fill (20 % freeboard and dead volume). Upright cylinder, H/D = 1.5 (nominal), D rounded up to 50 mm.
Wall: rotomoulded or fabricated PE, hoop T = P OD / (2 SD), P = rho g H, SD 4.14 MPa, minimum 4.75 mm [ASTM_D1998]. Densities [PERRY9].
Hold times are the A-M-225 basis (resupply interval or batch decoupling per service). Writes docs-authority/sizing/STORAGE_HOLDUP.md
and docs-authority/inventory/STORAGE_HOLDUP.json."""
import json, math, re, os, sys
sys.path.insert(0, '.')
from flow_graph.param import drivers as DR
from flow_graph.param.refs import cite
_d = DR.load()   # U4b: hold times, densities and vessel rules single-sourced from drivers.json
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
G = 9.80665
SD = DR.val(_d,'storage_pe_sd_MPa'); TMIN = DR.val(_d,'storage_pe_min_wall_mm'); FILL = DR.val(_d,'storage_tank_fill_frac'); HD = DR.val(_d,'storage_tank_HD')
SS = DR.val(_d,'storage_steel_allow_MPa'); TMIN_S = DR.val(_d,'storage_steel_min_wall_mm')
# unit: (dotted tree path, service, phase); hold days (A-M-225) and density (PERRY9) per unit in drivers.json
B = {'FAB_UPW_TANK': ('FAB.wet-reagent-train.bench.FAB_UPW_TANK', 'UPW buffer to the fab (1 d limits TOC pickup)', 'L'),
     'MEOH_TANK': ('MEOH.synthesis-train.MEOH_TANK', 'methanol day store, 14 d campaign', 'L'),
     'REMIN': ('WTR.potable-upw-train.REMIN', 'remineralisation contact, 1 d buffer', 'L'),
     'WS_AMMONIA': ('FAB.wet-reagent-train.reagents.WS_AMMONIA', 'aqueous NH3 25 %, 30 d resupply', 'L'),
     'WS_DOPE': ('FAB.wet-reagent-train.reagents.WS_DOPE', 'dopant solution, 30 d resupply', 'L'),
     'WS_HF_ED': ('FAB.wet-reagent-train.reagents.WS_HF_ED', 'HF etch 49 %, 30 d resupply', 'L'),
     'WS_KOH': ('FAB.wet-reagent-train.reagents.WS_KOH', 'KOH 45 %, 30 d resupply', 'L'),
     'WS_NITRIC': ('FAB.wet-reagent-train.reagents.WS_NITRIC', 'HNO3 65 %, 30 d resupply', 'L'),
     'WS_PEROX': ('FAB.wet-reagent-train.reagents.WS_PEROX', 'H2O2 30 %, 30 d resupply', 'L'),
     'WS_SLURRY': ('FAB.wet-reagent-train.reagents.WS_SLURRY', 'CMP slurry, 30 d resupply', 'L'),
     'WS_SOLV': ('FAB.wet-reagent-train.reagents.WS_SOLV', 'solvent (IPA), 30 d resupply', 'L'),
     'WS_PHOS': ('FAB.wet-reagent-train.reagents.WS_PHOS', 'H3PO4 85 %, 30 d resupply', 'L'),
     'PROD_C5_C10': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C5_C10', 'naphtha cut, 14 d to dispatch', 'L'),
     'PROD_C11_C18': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C11_C18', 'middle distillate cut, 14 d', 'L'),
     'PROD_C19_C28': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C19_C28', 'heavy distillate cut, 14 d', 'L'),
     'PROD_C29': ('OIL.pyro-fractionation-train.cuts-and-headers.PROD_C29', 'C29+ to recycle, 3 d buffer', 'L'),
     'NUTRIENT_DOSE': ('NUT.dosing-train.NUTRIENT_DOSE', 'dosing solution day tank, 1 d (stock concentrate is stored dry)', 'L'),
     'HOPPER': ('OIL.pyro-fractionation-train.pyro-frac.HOPPER', 'shredded feed, 1 d (bulk density)', 'S'),
     'FOOD_STORE': ('FARM.grow-bed-train.FOOD_STORE', 'D-DOCK food buffer: fresh harvest pass-through + X-RED-08 80 d dry reserve (A-M-270)', 'S'),
     'METAL_STORE': ('FOUNDRY.form-train.METAL_STORE', 'D-DOCK metal product buffer, 14 d dispatch campaign (A-M-270)', 'S'),
     'AIR_RECEIVER': ('CRYO.cold-box-asu-recovery-train.cold-box.AIR_RECEIVER', 'D-DOCK plant-air receiver on the cold-box N2 delivery, 1 d of the ASU/vent margin (A-M-270)', 'G'),
     'PROD_O2': ('CRYO.cold-box-asu-recovery-train.feed-and-recovery.PROD_O2', 'D-DOCK surplus-O2 product bank, cylinder-bank equivalent volume, 14 d dispatch campaign (A-M-278)', 'G'),
     'PROD_MEOH': ('CRYO.cold-box-asu-recovery-train.feed-and-recovery.PROD_MEOH', 'D-DOCK methanol product store, 14 d dispatch campaign (A-M-278)', 'L')}
def qin(n):
    p = n.get('params') or {}; m = re.search(r'In ([\d.]+) kg/d', p.get('duty') or '')
    return max((p.get('design_capacity_kg_d') or {}).get('value') or 0, float(m[1]) if m else 0)
EV = {e['stream_id']: float(e['rate']['value'] or 0) for e in g['edges'] if e['presence'] == 'present'}
# D-DOCK product buffers (A-M-270): Q is derived from the feed/draw edges, not a duty sheet - the stores pass their
# feeds at steady state, so the sized hold is the standing inventory each buffer must carry:
#   FOOD_STORE: the X-RED-08 dry-matter draw (crew food S14 fresh x 6 % DM; the 80 d hold is the crop-failure reserve)
#   METAL_STORE: the foundry product dispatch (sum of the STOCK_TO_* draws from the store)
#   AIR_RECEIVER: the ASU/vent margin (IA-N2-VENT, the cold-box N2 surplus over header draws) banked for one draw cycle
#   PROD_O2 / PROD_MEOH (A-M-278): the shipped-product dispatch edges out of the header / day store to NORTH_DOCK
GRAPH_Q = {
    'FOOD_STORE': round(EV.get('S14', 0.0)*0.06, 4),
    'METAL_STORE': round(sum(EV[k] for k in ('STOCK_TO_MFG', 'STOCK_TO_FAB', 'STOCK_TO_WIRE_DRAW') if k in EV), 4),
    'AIR_RECEIVER': round(EV.get('IA-N2-VENT', 0.0), 4),
    'PROD_O2': round(EV.get('IA-O2-PROD', 0.0), 4),
    'PROD_MEOH': round(EV.get('IA-MEOH-PROD', 0.0), 4),
}
GAS_STEEL = {'AIR_RECEIVER', 'PROD_O2'}   # compressed-gas service: steel at the working pressure (not hydrostatic PE)
FLAM = {'MEOH_TANK', 'WS_SOLV', 'PROD_C5_C10', 'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29', 'PROD_MEOH'}   # flammable / combustible: steel per NFPA 30 ch. 21
rows = []
for u, (path, svc, ph) in B.items():
    n = N[u]; Q = GRAPH_Q.get(u, 0.0) or qin(n); td = DR.val(_d, path + '.hold_d'); rho = DR.val(_d, path + '.rho_kg_m3'); V = Q*td/rho; Vn = max(V/FILL, 0.02)
    D = math.ceil((4*Vn/(math.pi*HD))**(1/3)*1000/50)*50; H = math.ceil(Vn/(math.pi*(D/1000)**2/4)*1000/50)*50
    P = DR.val(_d, path + '.P_MPa') if u in GAS_STEEL else (rho*G*H/1000*1e-6 if ph == 'L' else 0.0)
    steel = u in FLAM or u in GAS_STEEL
    t = max(P*(D/2)/(SS - 0.6*P), TMIN_S) if steel else max(P*D/(2*SD), TMIN)
    mat = 'SA-240 304L, welded' if steel else 'PE (rotomoulded / fabricated)'
    s = open(f'docs-authority/duties/{u}.md').read() if os.path.exists(f'docs-authority/duties/{u}.md') else ''
    m = re.search(r'Size (\d+) [×x] (\d+) [×x] (\d+)', s); env = [int(x) for x in m.groups()] if m else None
    fits = bool(env) and D <= min(env[0], env[1]) and H <= env[2]   # against the issued duty-sheet envelope
    rows.append(dict(unit=u, service=svc, Q_kg_d=round(Q, 3), hold_d=td, rho=rho, V_work_m3=round(V, 4), V_nom_m3=round(Vn, 4), D_mm=D, H_mm=H, wall_mm=round(t, 2), material=mat, envelope_mm=env, fits_envelope=fits))
json.dump(rows, open('docs-authority/inventory/STORAGE_HOLDUP.json', 'w'), indent=1)
if '--write' in sys.argv:   # sized vessel + 300 mm access on plan, + 300 mm on height becomes the unit envelope
    for r in rows:
        p = N[r['unit']].setdefault('params', {})
        p['size_mm'] = [r['D_mm'] + DR.val(_d,'storage_envelope_allowance_mm'), r['D_mm'] + DR.val(_d,'storage_envelope_allowance_mm'), r['H_mm'] + DR.val(_d,'storage_envelope_allowance_mm')]; p['size_note'] = 'L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064)'
        p['design_storage'] = {k: r[k] for k in ('hold_d', 'V_nom_m3', 'D_mm', 'H_mm', 'wall_mm', 'material')}
    open('flow_graph/plant_flow_graph.json', 'w').write(json.dumps(g, indent=2))
L = [f"""# Storage and holdup sizing

Document number: AQS-DUTY-064
Revision: A
Date: 2026-10-16
Authority: graph; X-RSZ-07 design capacities. Generated by `docs-authority/_storage_sizing.py`. Study. Not a PE stamp.

Unit task 02 for {len(rows)} storage-class units. Method: working volume = Q x hold / rho; nominal = working / {FILL}; upright cylinder H/D {HD}; PE wall by hoop stress T = P OD / (2 SD), SD {SD} MPa, minimum {TMIN} mm ({cite('ASTM_D1998')}). Flammable and combustible services (methanol, IPA, hydrocarbon cuts) are welded SA-240 304L ({cite('NFPA30_2027')}), wall t = P R / (S - 0.6 P), S 115 MPa, E 1.0, minimum 3.0 mm ({cite('ASME_VIII_1_UG27')}). Densities at 20 C ({cite('PERRY9')}). Hold times: A-M-225. Q is the larger of the X-RSZ-07 design capacity and the graph duty.

| Unit | Service | Q kg/d | Hold d | rho kg/m3 | V work m3 | V nom m3 | D mm | H mm | Material | Wall mm | Envelope mm | Fits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"""]
for r in rows:
    L.append(f"| {r['unit']} | {r['service']} | {r['Q_kg_d']} | {r['hold_d']} | {r['rho']} | {r['V_work_m3']} | {r['V_nom_m3']} | {r['D_mm']} | {r['H_mm']} | {r['material']} | {r['wall_mm']} | {' x '.join(map(str, r['envelope_mm'])) if r['envelope_mm'] else '—'} | {'yes' if r['fits_envelope'] else 'no' if r['envelope_mm'] else 'no envelope'} |")
bad = [r['unit'] for r in rows if r['envelope_mm'] and not r['fits_envelope']]
L.append(f"\nResult. {sum(r['fits_envelope'] for r in rows)} of {len(rows)} fit their graph envelope. Over envelope: {', '.join(bad) or 'none'}. Units without an envelope get the sized vessel as their envelope at the next GA build. Not covered here (sized elsewhere or no flow): CATCH_TANK and ROOF_TANK (`flow_graph/param/water_tower.py`), LIGNO_PRE (a pretreatment step, sized with its reactor). PROD_O2 and PROD_MEOH joined as A-M-278 shipped-product rows (2026-10-19); the PROD_O2 wall is the thin-wall equivalent-vessel number - the 200 bar seamless cylinder bank governs (CRYO_O2 storage_mode basis).\n")
open('docs-authority/sizing/STORAGE_HOLDUP.md', 'w').write('\n'.join(L))
print(len(rows), bad)
