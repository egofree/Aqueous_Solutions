"""Unit task 02 for the two unsized methanol-train units (AQS-DUTY-077): MEOH_COND (water
recovery condenser / knock-out pot on the synthesis-loop and fuel-cell water streams to
ROOF_TANK) and MEOH_FC (the indirect-methanol fuel cell: installed 1.0 kW_e stack, continuous
book 0.5 kW_e per the Q-039 owner ruling, 2026-11-13).
MEOH_COND: condense the water vapour carried by IA-MEOH-H2O (synthesis loop, 19.47 kg/d) and
S81 (fuel-cell water, 7.25 kg/d) at the loop dew point; duty = sensible + latent (IAPWS_IF97
latent 2257 kJ/kg class at near-atmospheric dew); area at U 1.2 kW/m2 K (water-vapour
condensing on water, PERRY9 sec. 11) with a 17 K LMTD at cooling water 25/35 C against
60/40 C condensation; vessel = knock-out pot ahead of the condensate drain (30 s vapour residence for
entrainment or one day of condensate, whichever is larger; H/D 2, DN grid). MEOH_FC: stack from the installed
rating at a cell
point (0.60 V, 0.30 A/cm2, IEC62282_3_100 module class; registered), reformer + aftercooler
from the methanol draw (5.0 kg/d, PERRY9 properties); envelope unchanged (issued). No rates
change on the graph. Run: python3 -m flow_graph.param.meoh_train [--write]"""
import json, math, os, sys
from . import drivers as DR
from .refs import cite

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC = 'AQS-DUTY-077'
TAG = f'methanol train residual sizing (flow_graph/param/meoh_train.py, {DOC})'
MK = 'MEOH.synthesis-train.'          # U4b: sizing literals single-sourced from drivers.json


def design(d, g):
    v = lambda k: DR.val(d, k)
    E = {e['stream_id']: e for e in g['edges']}
    ev = lambda sid: float((E.get(sid) or {}).get('rate', {}).get('value') or 0)
    # ---- MEOH_COND -----------------------------------------------------------------------------
    m_h2o = ev('IA-MEOH-H2O') + ev('S81')                                            # kg/d water to recover
    m_s = m_h2o / 86400.0
    lat = v(MK + 'MEOH_COND.latent_kJ_kg'); dT_sh = v(MK + 'MEOH_COND.subcool_K')
    q = m_s * (v(MK + 'MEOH_COND.cp_vap_kJ_kgK') * dT_sh + lat) * 1000.0             # W sensible+latent
    lmtd = ((60.0 - 35.0) - (40.0 - 25.0)) / math.log((60.0 - 35.0) / (40.0 - 25.0))
    A = q / 1000.0 / (v(MK + 'MEOH_COND.U_kW_m2K') * lmtd)
    rho_v = 0.13                                                                     # kg/m3 water vapour at 50 C class
    qv = m_s / rho_v                                                                 # m3/s vapour
    vdrum = max(qv * 30, m_h2o / 1000.0, 0.002)                                      # 30 s vapour residence (entrainment) or the daily condensate, >= 2 L
    D = math.ceil((4 * vdrum / (math.pi * v(MK + 'MEOH_COND.drum_HD'))) ** (1 / 3) * 1000 / 50) * 50
    H = math.ceil(vdrum / (math.pi * (D / 1000) ** 2 / 4) * 1000 / 50) * 50
    cond = dict(water_kg_d=round(m_h2o, 4), sources='IA-MEOH-H2O (synthesis loop) + S81 (fuel cell)',
                condensing_kW=round(q / 1000.0, 4), U_kW_m2K=v(MK + 'MEOH_COND.U_kW_m2K'), LMTD_K=round(lmtd, 1),
                area_m2=round(A, 4), tube=f'{math.ceil(A / 0.10)} x 10 mm x 1 m coil',
                drum_L=round(vdrum * 1000, 2), D_mm=D, H_mm=H, to='condensate to ROOF_TANK (IA-MEOH-COND)',
                material='316L shell and coil (methanol/water traces)', note='knock-out pot + condenser on the same skid')
    # ---- MEOH_FC -------------------------------------------------------------------------------
    # Q-039 owner ruling (2026-11-13): the continuous book re-locks at the fuel-supported class.
    # S79 carries 0.5 kW electric at the settled S76 feed (5.0 kg/d x 19.9 MJ/kg LHV x 0.5085
    # voltage efficiency at the A-M-312 0.6 V/cell point = 0.586 kW supported on S76 alone; 0.735 kW
    # on the full 6.28 kg/d burn). The installed stack stays the 1.0 kW / 28-cell hardware rating
    # (2 x 0.5 kW SI-DMFC-01 bank modules, AQS-REQ-KW-001) as standby capability; the 1-2-module
    # peak headroom is dispatch, not a continuous fuel book. The stack is sized from the installed
    # rating; the continuous book rides S79.
    p_cont = ev('S79')                   # kW_e continuous book, fuel-supported class (Q-039)
    installed_kWe = 1.0                  # installed hardware class (owner lock, Q-039; SI-DMFC-01 bank 2 x 0.5 kW)
    n_cells = math.ceil(installed_kWe * 1000.0 / (v(MK + 'MEOH_FC.cell_V') * v(MK + 'MEOH_FC.cell_A_cm2') * v(MK + 'MEOH_FC.j_A_cm2')))
    a_stack = v(MK + 'MEOH_FC.cell_A_cm2') / 10000.0
    meoh = ev('S76')                                                                 # kg/d methanol draw
    lhv = v(MK + 'MEOH_FC.meoh_LHV_MJ_kg')
    fc = dict(rated_kWe=installed_kWe, continuous_kW=p_cont,
              methanol_kg_d=meoh, air_O2_kg_d=round(ev('IA-FC-AIR'), 4),
              water_kg_d=round(ev('S81'), 4), CO2_kg_d=round(ev('S82'), 4),
              heat_kW=round(ev('S80'), 4), n_cells=n_cells, cell_V=v(MK + 'MEOH_FC.cell_V'),
              j_A_cm2=v(MK + 'MEOH_FC.j_A_cm2'), cell_A_cm2=v(MK + 'MEOH_FC.cell_A_cm2'),
              stack_area_m2=round(n_cells * a_stack, 4), methanol_energy_kW=round(meoh * lhv / 86.4, 3),
              basis=f'installed stack {installed_kWe} kW (SI-DMFC-01 bank, 2 x 0.5 kW modules, standby per the '
                    f'Q-039 owner ruling 2026-11-13); cell point {v(MK + "MEOH_FC.cell_V")} V at {v(MK + "MEOH_FC.j_A_cm2")} A/cm2, '
                    f'{v(MK + "MEOH_FC.cell_A_cm2")} cm2 cells ({cite("IEC62282_3_100")} module class); methanol LHV {lhv} MJ/kg ({cite("PERRY9")})',
              material='PEM stack, 316L reformer shell (Cu/ZnO class catalyst), PTFE gaskets',
              note='skid at the issued 1800 x 800 x 1600 mm envelope; the continuous book is 0.5 kW_e on S79 '
                   '(Q-039 owner ruling 2026-11-13, fuel-limited at the settled S76 feed) and the installed 1.0 kW rating '
                   'is standby capability, so the skid runs at part load on the dispatch schedule; '
                   'the species edges (O2, CO2, water) close on the graph')
    return {'MEOH_COND': cond, 'MEOH_FC': fc}


def write(g, R):
    N = {n['unit_id']: n for n in g['nodes']}
    for u, r in R.items():
        p = N[u].setdefault('params', {})
        p['design'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()}
        p['size_note'] = f'sized from the issued graph duties, {TAG}'
    open(GP, 'w').write(json.dumps(g, indent=2))


def write_doc(d, R):
    c, f = R['MEOH_COND'], R['MEOH_FC']
    v_lat = DR.val(d, MK + 'MEOH_COND.latent_kJ_kg'); d_sub = DR.val(d, MK + 'MEOH_COND.subcool_K')
    d_hd = DR.val(d, MK + 'MEOH_COND.drum_HD')
    md = ['# Methanol train residual sizing', '', f'Document number: {DOC}', 'Revision: A', 'Date: 2026-10-20',
          'Authority: AQS-PLAN-007 unit tasks (MEOH)-02; MEOH_SYNTH and MEOH_FERM are sized in AQS-DUTY-062 (`docs-authority/sizing/REACTOR_DESIGN.md`), '
          'MEOH_TANK in AQS-DUTY-064. Generated by `flow_graph/param/meoh_train.py`. Study. Not a PE stamp.', '',
          '## MEOH_COND - water-recovery condenser and knock-out pot', '',
          f'Recovers {c["water_kg_d"]} kg/d water ({c["sources"]}) to ROOF_TANK on IA-MEOH-COND. Duty = m (cp dT + latent) with '
          f'latent {v_lat} kJ/kg ({cite("IAPWS_IF97")} class at the near-atmospheric dew) and {d_sub} K subcool: '
          f'{c["condensing_kW"]} kW. Area at U {c["U_kW_m2K"]} kW/m2 K (water vapour on water, {cite("PERRY9")} sec. 11) and LMTD {c["LMTD_K"]} K '
          f'(60/40 C condensing against 25/35 C cooling water): {c["area_m2"]} m2 = {c["tube"]}. Knock-out pot {c["drum_L"]} L (30 s vapour residence or the daily condensate, {cite("PERRY9")} entrainment class), '
          f'D{c["D_mm"]} x {c["H_mm"]} mm (H/D {d_hd}). {c["note"]}.', '',
          '## MEOH_FC - indirect methanol fuel cell', '',
          f'The installed stack is {f["rated_kWe"]} kW_e: {f["n_cells"]} cells of {f["cell_A_cm2"]} cm2 at {f["cell_V"]} V and {f["j_A_cm2"]} A/cm2 '
          f'({f["n_cells"] * f["cell_A_cm2"] / 10000.0:.3f} m2 active); {f["basis"]}. The continuous book is {f["continuous_kW"]} kW_e on S79 '
          f'(Q-039 owner ruling 2026-11-13): the methanol draw of {f["methanol_kg_d"]} kg/d (S76) carries {f["methanol_energy_kW"]} kW thermal (LHV), '
          f'which at the cell point supports 0.586 kW electric on S76 alone and 0.735 kW on the full 6.28 kg/d burn, so the installed rating runs at '
          f'part load on the dispatch schedule and its headroom is standby capability, not a continuous fuel book. At the booked point the cell draws '
          f'O2 {f["air_O2_kg_d"]} kg/d, water {f["water_kg_d"]} kg/d, CO2 {f["CO2_kg_d"]} kg/d return and reject heat {f["heat_kW"]} kW to Q4_BUS (S80); '
          f'{f["note"]}.', '',
          'Both units sit on the methanol skid row (AQS-PLACE-SEED-001); no graph rate changes. Open: the fuel-cell stack polarisation follows the '
          'issued duty; a bench polarisation set replaces the cell-point assumption at the first article (registered).']
    v_lat = lambda d: DR.val(d, MK + 'MEOH_COND.latent_kJ_kg'); d_sub = lambda d: DR.val(d, MK + 'MEOH_COND.subcool_K')
    d_hd = lambda d: DR.val(d, MK + 'MEOH_COND.drum_HD')
    open(os.path.join(ROOT, 'docs-authority/sizing/MEOH_TRAIN.md'), 'w').write('\n'.join(md) + '\n')


def main():
    d = DR.load(); g = json.load(open(GP)); R = design(d, g)
    for u, r in R.items(): print(u, json.dumps(r)[:220])
    if '--write' in sys.argv: write(g, R); write_doc(d, R)


if __name__ == '__main__':
    main()
