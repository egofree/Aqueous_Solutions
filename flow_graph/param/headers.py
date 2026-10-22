"""Unit task 02 for the header-class units (AQS-DUTY-075): the four gas headers HDR_H2, HDR_O2,
HDR_N2, HDR_CO2, the water headers HDR_UPW and Q4_BUS, the pyrolysis NCG header and the
afterburner flue junction. Bore from the concurrent design flow at a velocity limit (PERRY9
sec. 6: d = sqrt(4 Q / (pi v)), gas 8 m/s, water 1.5 m/s), not below the service minimum
(gas DN25 to seat take-off valves and instruments, water DN25, flue DN100 for draft and
condensate drainage - registered assumptions); manifold length = the longest routed run among
the header's present lines (docs-authority/iso/ISO_SHEETS.csv route_m, committed data), volume
and holdup from bore x length; material per service under AQS-STD-002 (O2 header oxygen-clean
per ASTM_G93). Q4_BUS flow follows the ladder rule: the winter concurrent case (life + HX-9 +
HX-10 + GHEX recharge + MAU_HX coil) on the 10 K loop swing (drivers heat_loop_dT_K); summer
(ADS_CHILL in place of MAU) is checked lower. No rates change on the graph.
Run: python3 -m flow_graph.param.headers [--write]"""
import csv, json, math, os, sys
from . import drivers as DR
from .refs import cite

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC = 'AQS-DUTY-075'
TAG = f'header sizing (flow_graph/param/headers.py, {DOC})'
HD = 'HDR.headers-train.'            # U4b: sizing literals single-sourced from drivers.json
# unit: (service, kind, min DN key, velocity key, density kg/m3 key or Q4_BUS marker, material, note)
SPEC = {
    'HDR_H2':  ('H2 header (EW cathode gas in, dryer and trim draws out)', 'gas', 'hdr_min_DN_gas', 'hdr_v_gas_m_s', 'hdr_rho_H2', 'PVC-U, bonded; wet acid H2 + sweep air per AQS-REV-H2-001 (M3, X-MAT-06)', None),
    'HDR_O2':  ('O2 header (ASU/receiver in; fuel cell, peroxide, genset, afterburner, product draws)', 'gas', 'hdr_min_DN_gas', 'hdr_v_gas_m_s', 'hdr_rho_air', '316L tube, oxygen-clean per ASTM_G93, socketless', None),
    'HDR_N2':  ('plant air / N2 header (receiver in; AHU, afterburner air, reagent sparge draws)', 'gas', 'hdr_min_DN_gas', 'hdr_v_gas_m_s', 'hdr_rho_air', '316L tube', None),
    'HDR_CO2': ('CO2 header (crew and cold-box in; farm and methanol-synthesis draws)', 'gas', 'hdr_min_DN_gas', 'hdr_v_gas_m_s', 'hdr_rho_CO2', '316L tube', None),
    'HDR_UPW': ('UPW distribution header (polish skid in; fab and hab draws)', 'liquid', 'hdr_min_DN_water', 'hdr_v_water_m_s', 'hdr_rho_water', 'PVDF SDR 21, fusion-welded (high-purity water, AQS-STD-002)', None),
    'Q4_BUS':  ('Q4 hot-water bus (Q4 batteries in; life, HX-9/HX-10 preheat, GHEX recharge, MAU/ADS branches)', 'liquid', 'hdr_min_DN_water', 'hdr_v_water_m_s', 'hdr_rho_water', 'PP-H SDR 11 (80 C class), fusion-welded', 'Q4_BUS'),
    'NCG_HEADER': ('pyrolysis non-condensable gas header (OIL_FRAC in; afterburner out)', 'gas', 'hdr_min_DN_gas', 'hdr_v_gas_m_s', 'hdr_rho_ncg', '304L, heat-traced (tar service)', None),
    'AFTERBURNER_FLUE': ('afterburner flue duct to the knock-out (flue gas at 200 C class)', 'flue', 'hdr_min_DN_flue', 'hdr_v_flue_m_s', 'hdr_rho_flue', 'CS Sch 40, insulated per AQS-THM-003', None),
}
DN_LIST = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500]
ID_OF = {dn: dn - 8 for dn in DN_LIST}       # Sch 40/SDR class bores on the DN grid, mm


def _flow_kg_s(g, u, mode):
    """Concurrent design flow through the header. Gas headers: the larger of total in and total out
    (all drops can run at once at the bounding assay). Q4_BUS: the winter concurrent branch sum."""
    kg_d = 0.0
    for e in g['edges']:
        if e.get('presence') != 'present' or (e.get('rate') or {}).get('unit') not in ('kg/d', 'kW'):
            continue
        if mode == 'Q4_BUS' and e['from_unit_id'] == u and e['to_unit_id'] in ('HABITATION', 'LEACH_CSTR_1', 'GLASS_DIGEST', 'GEO_GHEX', 'MAU_HX'):
            kg_d += float(e['rate']['value'] or 0)                                       # kW branches, winter set
    if mode == 'Q4_BUS':
        return 'kW', kg_d                                                                # thermal duty; converted below
    tin = tout = 0.0                                                                     # steady state: the larger side governs
    for e in g['edges']:
        if e.get('presence') == 'present' and (e.get('rate') or {}).get('unit') == 'kg/d' and u in (e['from_unit_id'], e['to_unit_id']):
            r = float(e['rate']['value'] or 0)
            if e['from_unit_id'] == u: tout += r
            else: tin += r
    return 'kg/d', max(tin, tout)


def design(d, g):
    v = lambda k: DR.val(d, k)
    iso = {}
    p = os.path.join(ROOT, 'docs-authority/iso/ISO_SHEETS.csv')
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            try: iso[r['line']] = max(iso.get(r['line'], 0.0), float(r['route_m'] or 0))
            except ValueError: pass
    out = {}
    for u, (svc, kind, mink, velk, rhok, mat, mode) in SPEC.items():
        unit_kind, x = _flow_kg_s(g, u, mode or kind)
        if kind == 'liquid':
            if mode == 'Q4_BUS':                        # kW -> kg/s on the loop swing
                m_kg_s = x * 1000.0 / (v(HD + 'hdr_cp_water_kJ_kgK') * 1000.0 * DR.val(d, 'heat_loop_dT_K')) if x else 0.0
                duty_kW = x
            else:
                m_kg_s = x / 86400.0; duty_kW = None
            rho = v(HD + 'hdr_rho_water'); Q = m_kg_s / rho
        else:
            m_kg_s = x / 86400.0; duty_kW = None
            rho = v(HD + rhok) if rhok.startswith('hdr_rho') else v(HD + rhok)
            Q = m_kg_s / rho
        vel = v(HD + velk); id_req = math.sqrt(4 * Q / (math.pi * vel)) * 1000 if Q else 0.0
        dn = next(dn for dn in DN_LIST if ID_OF[dn] >= max(id_req, 0.0) and dn >= v(HD + mink))
        runs = [iso[e['stream_id']] for e in g['edges'] if e.get('presence') == 'present'
                and u in (e['from_unit_id'], e['to_unit_id']) and e['stream_id'] in iso and (e.get('rate') or {}).get('unit') in ('kg/d', 'kW')]
        L = max(runs) if runs else v(HD + 'hdr_run_default_m')
        i_d = ID_OF[dn] / 1000.0
        vol_m3 = math.pi * i_d * i_d / 4 * L
        out[u] = dict(service=svc, kind=kind, flow_kg_s=round(m_kg_s, 6), duty_kW=duty_kW, rho_kg_m3=rho, Q_m3_s=round(Q, 6),
                      v_m_s=vel, id_req_mm=round(id_req, 1), DN=dn, length_m=round(L, 1), volume_m3=round(vol_m3, 4),
                      material=mat, hold_kg=round(vol_m3 * rho, 2),
                      connections=sum(1 for e in g['edges'] if e.get('presence') == 'present' and u in (e['from_unit_id'], e['to_unit_id'])
                                      and (e.get('rate') or {}).get('unit') in ('kg/d', 'kW')))
    return out


def write(g, R):
    N = {n['unit_id']: n for n in g['nodes']}
    for u, r in R.items():
        p = N[u].setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_note'] = f'DN{r["DN"]} manifold x {r["length_m"]:.0f} m run ({r["volume_m3"]:.3f} m3), {TAG}'
    open(GP, 'w').write(json.dumps(g, indent=2))


def write_doc(d, R):
    v = lambda k: DR.val(d, k)
    md = ['# Header and bus sizing', '', f'Document number: {DOC}', 'Revision: A', 'Date: 2026-10-20',
          'Authority: AQS-PLAN-007 unit tasks 02 (GAS/HAB/WTR/HEAT/OIL headers). Generated by `flow_graph/param/headers.py`. Study. Not a PE stamp.', '',
          f'Unit task 02 for {len(R)} header-class units. Bore from the concurrent design flow at the velocity limit '
          f'(gas {v(HD+"hdr_v_gas_m_s")} m/s, water {v(HD+"hdr_v_water_m_s")} m/s, flue {v(HD+"hdr_v_flue_m_s")} m/s; {cite("PERRY9")} sec. 6 '
          f'd = sqrt(4Q/(pi v))), not below the service minimums (gas DN{v(HD+"hdr_min_DN_gas")}, water DN{v(HD+"hdr_min_DN_water")}, flue '
          f'DN{v(HD+"hdr_min_DN_flue")} - registered basis: take-off seating, instrument taps, flue draft and condensate drainage). '
          f'Manifold length is the longest routed run of the header\'s lines in the issued isometrics (AQS-ISO-002 route table); volume and '
          f'standing holdup from bore x length. Q4_BUS flow follows AQS-HEAT-LADDER-001: the winter concurrent case (life 3.0 + HX-9 + HX-10 + '
          f'GHEX recharge + MAU coil) on the {DR.val(d, "heat_loop_dT_K")} K loop swing (drivers heat_loop_dT_K); the summer case (ADS_CHILL for '
          f'MAU) is lower and does not govern. Line classes, schedules and ratings of each connected line stay in AQS-PIP-003/-004.', '',
          '| Unit | Service | DN | ID req mm | Length m | Volume m3 | Hold kg | Connections | Material |', '|---|---|---|---|---|---|---|---|---|']
    for u, r in R.items():
        md.append(f"| {u} | {r['service']} | DN{r['DN']} | {r['id_req_mm']} | {r['length_m']} | {r['volume_m3']} | {r['hold_kg']} | {r['connections']} | {r['material']} |")
    md += ['', 'Q4_BUS design duty ' + (f"{R['Q4_BUS']['duty_kW']:.2f} kW winter concurrent" if R['Q4_BUS']['duty_kW'] else 'n/a') +
               f" -> {R['Q4_BUS']['flow_kg_s']:.3f} kg/s at {DR.val(d, 'heat_loop_dT_K')} K swing. Gas densities at header conditions "
               f"(H2 {v(HD+'hdr_rho_H2')}, air class {v(HD+'hdr_rho_air')}, CO2 {v(HD+'hdr_rho_CO2')}, NCG {v(HD+'hdr_rho_ncg')}, flue {v(HD+'hdr_rho_flue')} kg/m3, "
               f'{cite("NIST_WEBBOOK")} class). The O2 header is degreased and bagged per {cite("ASTM_G93")}; its take-offs carry the no-oil rule of '
               'AQS-STD-002. Open: hydraulic network verification (pressure drops at the governing draws) folds into the line list calculation as the '
               'connected line bores are re-derived at unit task 05.']
    open(os.path.join(ROOT, 'docs-authority/sizing/HEADERS.md'), 'w').write('\n'.join(md) + '\n')


def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, 'DN', r['DN'], 'x', r['length_m'], 'm', r['volume_m3'], 'm3,', r['connections'], 'connections')
    if '--write' in sys.argv: write(g, R); write_doc(d, R)


if __name__ == '__main__':
    main()
