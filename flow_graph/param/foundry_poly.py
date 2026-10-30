"""Foundry + polymers sizing transfer functions (AQS-DUTY-072 / AQS-DUTY-073, unit task 02 for the
FOUNDRY and POLYMERS sectors). Sizes the two sectors from need at the Rev AC bounding case.

Rev B (2026-10-19, D-DOCK foundry feedstock program): the FOUNDRY standby placeholders become real
full designs on dock-imported feedstocks (owner ruling D-DOCK: the dock imports any feedstock class -
landfill reclaim, mining waste, regolith; A-M-284). Live trains after this pass:

  pot/cell train   AL_POT (anhydrous AlCl3 import, molten-chloride electrolysis), MG_POT (Kroll Mg
                   recycle + CaCl2-MgCl2 brine make-up), CA_POT (brine import, grease-thickener Ca),
                   TI_CELL (TiO2-eq rutile + C + Mg-pot Cl2/Mg, AQS-BAL-KROLL), MO_CELL / CR_CELL
                   (oxide + C, carbochlorination with an internal anode-gas chlorine loop)
  investment train WAX_PATTERN .. SHELL_BREAK at 2 kg/d castings on wax make-up + foundry silica
                   imports, shell 87.5 % reclaimed, spent balance exported at the dock
  N+1 alternates   VAC_IND / VAC_CAST / RF_HEAT / RES_HEAT / COMB_HEAT / SINTER / FORGE / EXTRUDE /
                   DRAW sized at their backup duty (AGENTS.md redundancy rule, A-M-283), standby-zero
                   on the design day, electrical edges connected

Chlorine ruling (A-M-290): the EW anode gas is fully booked to the leach oxidation by the Faraday
balance (A-M-255 double-booking rule) - it stays the INITIAL chlorine inventory charge for the Kroll
loops only. Steady state: Ti chlorination Cl2 returns from MG_POT exactly (AQS-BAL-KROLL closure);
Mo/Cr cells recycle their anode gas internally; the AL_POT Cl2 byproduct (39.4 kg/d) and the CA_POT
share export at the dock as water-treatment-class product (the only spare chlorine sink - CRU closes
exactly on S66 = IA-CRU-01).

Demand-side notes unchanged: WAFER_FAB draws are 0 (A-M-257: the fab closes on UPW + slurry + N2
purge); WIRE_DRAW closes on S57 (MFG Cu wire line), so STOCK_TO_WIRE_DRAW = 0. The MFG_SHOP goods
loop is closed (IA-MFG-OUT 596.863 out = IA-WEAR return), so the shop's only live need is its
rounding remnant r0 (rated in - rated out) plus whatever the foundry stock loop and polymer draw feed
back through it. K now carries the full AQS-SIZE-FOUNDRY consumable-replacement table (25.9 kg/d,
A-M-261 rev): the Al 8 / stainless 1.5 / Ti 0.40 / casting 2 lines unblock with their feeds.

Polymers chain (AQS-DUTY-073) unchanged from Rev A: the fluoropolymer train stays F-blocked (no
fluorine source on site, AQS-BOM-SC-001 43 BOM lines Missing, Q-013) and POLY_COND waits on the
digester organic assay (AQS-DES-POLY). The live train is the polyolefin line: C5-C10 naphtha drawn at
the cut tank -> POLY_OLEFIN -> PELLET -> POLY_STOCK -> MFG_SHOP draw + wet-line reject.

Closure (exact, from the live graph; the pot metals are the stock loop's only net inlet, so at steady
state the loop passes them and the full pot output leaves as the dock metal export - the melt-loss
accounting keeps metals whole and charges the poly scrap to slag, the established Rev AC pattern):
  K     = foundry stock demand (drivers foundry_stock_demand_kg_d, full table)
  potm  = pot/cell metal charged to the melt (Al 10 + Ti 0.5 + Mo 0.0625 + Cr 0.25, line + 25 % export)
  f     = melt loss to slag/dross (drivers foundry_melt_loss_frac)
  flux  = Kroll MgCl2 drag-out to FLUX_PREP (foundry_kroll_dragout_frac x Kroll MgCl2 gross)
  rej   = polymer offcut to the wet line per kg issued (drivers poly_shop_reject_frac)
  P     = -r0 + f*K/(1-f)          polymer draw that closes the shop (A-M-257 by-difference pattern)
  S     = K + P + r0               shop scrap charge to IND_MELT
  slag  = f*S + flux               FOUNDRY_SLAG_TO_LEACH (dross + the salt flux pass-through)
  cont  = S + potm + flux - 3(Cu cast) - 2(inv) - slag    to CONT_CAST (by difference)
  stock = 13(rolled) + (cont - 10) + 2(castings) = K + potm = STOCK_TO_MFG + IA-METAL-SHIP

Run: python3 -m flow_graph.param.foundry_poly [--write]

stamp() also writes params.design + params.envelope (size_mm, style, live|standby_rated state) for the
36 units, read by models/mfg/foundry.py and models/mfg/polymers.py (X-MFG-30 CadQuery pattern); every
FOUNDRY unit gets machine geometry now (standby_rated = real equipment at a standby-zero design-day
rate; the polymers placeholders stay until their feeds land). cad/stl envelope boxes regenerate with
`python3 -m flow_graph.param.envelopes <units>` (test_envelopes.py gates the match).
"""
import json, math, os, sys
from . import drivers as DR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
DOC_F, DOC_P = 'AQS-DUTY-072', 'AQS-DUTY-073'
TAG = f'X-PAR-02 TF: foundry/polymers sizing ({DOC_F}/{DOC_P})'
F = 96485.0                                          # C/mol, CODATA2018 class (refs.CODATA2018)
MM = dict(Al=26.9815, Cl=35.453, Mg=24.305, Ca=40.078, Ti=47.867, O=15.9994, C=12.011,
          Mo=95.948, Cr=51.9962, H=1.008)            # GREENWOOD / CRC element mass table


def rate(v, note):
    return {'value': round(v, 6), 'unit': 'kg/d', 'status': 'study', 'note': note}


def faraday_A(kg_d, el, z, ce):
    """Cell current at kg/d metal, z electrons, current efficiency ce."""
    return kg_d * 1000.0 / MM[el] * z * F / 86400.0 / ce


def hold_kW(feed_kg, rho, T_C, tau=0.5):
    """Bath hold loss: cylinder at atm_HD of tau d feed, U 0.8 W/m2K (150 mm ceramic fibre, study),
    ambient 25 C. Vessel floored at DN150."""
    V = max(feed_kg * tau / rho, 0.15 ** 2 * math.pi / 4 * 0.225)
    D = (4 * V / (math.pi * 1.5)) ** (1 / 3)
    A = (math.pi * D * 1.5 * D + 2 * math.pi * D ** 2 / 4) * 1.4
    return 0.8 * A * (T_C - 25.0) / 1000.0


def solve(g=None):
    """Return the sizing dict; g loaded from the graph when not given."""
    if g is None:
        g = json.load(open(GP))
    d = DR.load()
    val = lambda k: DR.val(d, k)
    E = {e['stream_id']: e for e in g['edges']}

    def rated(k):
        r = E[k]['rate']
        return float(r['value'] or 0) if r.get('unit') == 'kg/d' else 0.0

    def resid(u, skip=()):
        r = 0.0
        for e in g['edges']:
            if e['presence'] == 'present' and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d' \
                    and e['stream_id'] not in skip:
                v = float(e['rate']['value'] or 0)
                r += v if e['to_unit_id'] == u else 0.0
                r -= v if e['from_unit_id'] == u else 0.0
        return r

    r0 = resid('MFG_SHOP', skip=('MFG_SCRAP_TO_IND', 'STOCK_TO_MFG', 'POLY_TO_MFG'))
    # ^ rated in - rated out at the shop, EXCLUDING this pass's own loop edges so the closure is
    #   idempotent (re-running on the written graph returns the same remnant, A-M-257 pattern)
    K = val('foundry_stock_demand_kg_d')         # full AQS-SIZE-FOUNDRY table (A-M-261 rev)
    f = val('foundry_melt_loss_frac')
    rej = val('poly_shop_reject_frac')
    P = -r0 + f * K / (1 - f)                    # polymer draw that closes the shop
    S = K + P + r0                               # scrap charge to IND_MELT

    # ---- pot / Kroll / investment algebra (A-M-280..284.283) -----------------------------------
    xf = val('foundry_pot_export_frac')
    al_i, ti_i, mo_i, cr_i = (val('foundry_al_line_kg_d'), val('foundry_ti_line_kg_d'),
                              val('foundry_mo_add_kg_d'), val('foundry_cr_add_kg_d'))
    al = al_i * (1 + xf)                          # 8 internal + 2 export
    ti = ti_i * (1 + xf)
    mo = mo_i * (1 + xf)
    cr = cr_i * (1 + xf)
    potm = al + ti + mo + cr                      # total pot-metal throughput (A-M-284 block)
    ca = val('foundry_ca_add_frac') * (K + potm)                # deoxidizer Ca on the melt charge
    alcl3 = al * (MM['Al'] + 3 * MM['Cl']) / MM['Al']
    al_cl2 = al * 3 * MM['Cl'] / MM['Al']
    cacl2 = ca * (MM['Ca'] + 2 * MM['Cl']) / MM['Ca']
    ca_cl2 = ca * 2 * MM['Cl'] / MM['Ca']
    tio2 = ti * (MM['Ti'] + 2 * MM['O']) / MM['Ti']
    c_ti = ti * 2 * MM['C'] / MM['Ti']
    cl2_ti = ti * 4 * MM['Cl'] / MM['Ti']
    mg_ti = ti * 2 * MM['Mg'] / MM['Ti']
    mgcl2_g = ti * 2 * (MM['Mg'] + 2 * MM['Cl']) / MM['Ti']
    co_ti = ti * 2 * (MM['C'] + MM['O']) / MM['Ti']
    kd = val('foundry_kroll_dragout_frac')
    kroll_flux = kd * mgcl2_g                     # MgCl2-class salt drag-out to FLUX_PREP
    mgcl2_ret = mgcl2_g - kroll_flux              # arrives at MG_POT
    mgcl2_mu = mg_ti + cl2_ti - mgcl2_ret         # brine make-up that restores the retort Mg need
    moo3 = mo * (MM['Mo'] + 3 * MM['O']) / MM['Mo']
    c_mo = mo * 1.5 * MM['C'] / MM['Mo']
    co2_mo = mo * 1.5 * (MM['C'] + 2 * MM['O']) / MM['Mo']
    cr2o3 = cr * (2 * MM['Cr'] + 3 * MM['O']) / (2 * MM['Cr'])
    c_cr = cr * 3 * MM['C'] / (2 * MM['Cr'])
    co_cr = cr * 3 * (MM['C'] + MM['O']) / (2 * MM['Cr'])
    potm = al + ti + mo + cr                      # pot metal charged to the melt
    flux = kroll_flux
    slag = f * S + flux + ca                      # dross + flux pass-through + deoxidizer Ca reports to slag (metal-equivalent)
    inv = val('foundry_inv_line_kg_d')
    cont = S + potm + ca + flux - 3.0 - inv - slag     # IND_TO_CONT by difference; ca enters and reports to slag (f*S = S-K identity closes the ledger)
    cont_roll, cont_stock = 10.0, cont - 10.0
    stock_in = 13.0 + cont_stock + inv            # = K + potm exactly
    assert abs(stock_in - (K + potm)) < 1e-9
    # investment loop (A-M-286)
    sh = val('foundry_inv_shell_kg_per_kg') * inv
    shr = val('foundry_inv_shell_reclaim_frac')
    sh_mu, sh_recl = sh * (1 - shr), sh * shr
    wx = val('foundry_inv_wax_kg_per_kg') * inv
    wr = val('foundry_inv_wax_reclaim_frac')
    wx_mu, wx_recl, wx_burn = wx * (1 - wr), wx * wr, wx * (1 - wr)

    # ---- electrical (Faraday at the pots/cells; A-M-282) ------------------------------------
    Vc = DR.val(d, 'foundry_pot_voltage_V')
    ce = DR.val(d, 'foundry_pot_ce')
    pot_e = {}
    for u, m, el, z, v in (('AL_POT', al, 'Al', 3, Vc['al']), ('MG_POT', mg_ti, 'Mg', 2, Vc['mg']),
                           ('CA_POT', ca, 'Ca', 2, Vc['ca']), ('MO_CELL', mo, 'Mo', 3, Vc['mo']),
                           ('CR_CELL', cr, 'Cr', 3, Vc['cr'])):
        i = faraday_A(m, el, z, ce)
        pot_e[u] = dict(I_A=round(i, 2), V=round(v, 2), dc_kW=round(i * v / 1000.0, 4),
                        hold_kW=round(hold_kW(m, 1800.0, 700.0), 4))
        pot_e[u]['kW'] = round(pot_e[u]['dc_kW'] + pot_e[u]['hold_kW'], 4)
    pot_e['TI_CELL'] = dict(I_A=0.0, V=0.0, dc_kW=0.0, hold_kW=0.5,
                            kW=0.5)               # thermochemical Kroll retort 900 C + chlorinator 800 C (study)

    # melt energy by metal class (X-MFG-37 method, A-M-177): (cp_s dT + L + cp_l superheat)/eta
    eta = val('melt_eta'); sup = val('melt_superheat_K')
    q = {}
    q['Cu'] = (val('melt_cp_solid_kJ_kgK') * (1084.62 - 25) + val('melt_L_kJ_kg') + val('melt_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Fe'] = (val('melt_fe_cp_solid_kJ_kgK') * (1538 - 25) + val('melt_fe_L_kJ_kg') + val('melt_fe_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Zn'] = (val('melt_zn_cp_solid_kJ_kgK') * (419.5 - 25) + val('melt_zn_L_kJ_kg') + val('melt_zn_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Al'] = (val('melt_al_cp_solid_kJ_kgK') * (660.3 - 25) + val('melt_al_L_kJ_kg') + val('melt_al_cp_liq_kJ_kgK') * sup) / eta / 3600
    q['Ti'] = (val('melt_ti_cp_solid_kJ_kgK') * (1668 - 25) + val('melt_ti_L_kJ_kg') + val('melt_ti_cp_liq_kJ_kgK') * sup) / eta / 3600   # bounding reactive/addition class (Ti > Mo, Cr)
    # melt charge by class: the recycled table return (K less the poly draw P) + the fresh pot metal;
    # the castings line rides the Fe class; the stainless Cr/Mo content rides the Ti (reactive) class;
    # the shop rounding remnant r0 (A-M-265) rides the Fe class (0.6 % of charge, energy-negligible)
    mix = {'Cu': 3.0, 'Fe': 10.0 + (val('foundry_ss_line_kg_d') - mo_i - cr_i) + inv + r0, 'Zn': 1.0,
           'Al': al + al_i, 'Ti': (ti + mo + cr) + (ti_i + mo_i + cr_i)}
    assert abs(sum(mix.values()) - (S - P + potm)) < 1e-9
    e_melt = sum(m * q[c] for c, m in mix.items()) + val('melt_hold_kW') * val('melt_time_h') * math.ceil((S + potm + flux) / val('melt_charge_kg'))
    kw_peak = math.ceil(val('melt_charge_kg') * max(q.values()) / val('melt_time_h') * 2) / 2   # largest cold heat
    e_roll = 0.032 * (mix['Cu'] + 10.0)                        # A-M-177 rolling 0.032 kWh/kg (bounding, cold class)
    c5 = rated('CUT-1') - rated('CUT-1-OUT') - P * (1 + rej)   # IA-C5-SHIP re-solve (make - burned - olefin)
    return dict(g=g, E=E, d=d, r0=r0, K=K, f=f, rej=rej, P=P, S=S, slag=slag, flux=flux, potm=potm,
                inv=inv, cont=cont, cont_roll=cont_roll, cont_stock=cont_stock, stock_in=stock_in,
                al=al, ti=ti, mo=mo, cr=cr, ca=ca, xf=xf, al_i=al_i, ti_i=ti_i, mo_i=mo_i, cr_i=cr_i,
                alcl3=alcl3, al_cl2=al_cl2, cacl2=cacl2,
                ca_cl2=ca_cl2, tio2=tio2, c_ti=c_ti, cl2_ti=cl2_ti, mg_ti=mg_ti, mgcl2_g=mgcl2_g,
                mgcl2_ret=mgcl2_ret, mgcl2_mu=mgcl2_mu, kroll_flux=kroll_flux, co_ti=co_ti, moo3=moo3,
                c_mo=c_mo, co2_mo=co2_mo, cr2o3=cr2o3, c_cr=c_cr, co_cr=co_cr, sh=sh, sh_mu=sh_mu,
                sh_recl=sh_recl, wx=wx, wx_mu=wx_mu, wx_recl=wx_recl, wx_burn=wx_burn, pot_e=pot_e,
                poly_feed=P * (1 + rej), poly_wet=rej * P, c5_ship=c5, q=q, mix=mix, e_melt=e_melt,
                kw_peak=kw_peak, e_roll=e_roll, heats=math.ceil((S + potm + flux) / val('melt_charge_kg')),
                charge=val('melt_charge_kg'))


def slag_term(S, f):
    return f * S


def apply(g=None, write=False):
    s = solve(g)
    g, E = s['g'], s['E']
    K, S, P = s['K'], s['S'], s['P']
    N = {n['unit_id']: n for n in g['nodes']}

    def put(k, v, note):
        assert k in E, k
        E[k]['rate'] = rate(v, note)

    def mk(sid, frm, to, tsec, phase, carries, v, note, layers=('mass',)):
        """Create-or-rate a foundry edge (idempotent; AQS-DUTY-072 owns these)."""
        if sid not in E:
            src = dict(E['IA-SOLV-MU'])
            src.update(stream_id=sid, from_unit_id=frm, to_unit_id=to, to_sector_id=tsec, phase=phase,
                       carries=carries, layers=list(layers), notes=None, composition=None, gap_flags=[], presence='present',
                       from_sector_id=N[frm]['sector_id'])
            g['edges'].append(src); E[sid] = src
        put(sid, v, note)

    # ---- foundry: live scrap-remelt loop + pot/cell/Kroll metal ----------------------------
    R = lambda x: round(x, 6)                     # write-grid; by-difference edges use rounded operands
    sP = R(s['P']); sS = R(K + sP + s['r0'])      # S from the rounded P so MFG_SHOP closes on the grid
    s['S'] = sS
    sflux, spotm, sca = R(s['flux']), R(s['potm']), R(s['ca'])
    sslag = R(s['f'] * sS) + sflux + sca          # deoxidizer Ca reports to the dross (metal-equivalent)
    s['slag'] = sslag
    put('MFG_SCRAP_TO_IND', sS,
        f'Shop scrap (charge) to the melt; closes MFG_SHOP on the store draws ({DOC_F}, A-M-261 rev). | {TAG}.')
    put('FOUNDRY_SLAG_TO_LEACH', sslag,
        f'Melt slag+dross {s["f"]:.0%} of charge plus the {s["flux"]:.4f} kg/d salt-flux pass-through by mass '
        f'conservation on the melt (INDUCT_SOCX 1-2 % band, A-M-262); returns to the leach. | {TAG}.')
    put('IND_MELT_TO_CAST', 3.0,
        f'Cu-class melt to the cast line: bus/winding stock (AQS-SIZE-FOUNDRY Cu 3 kg/d). | {TAG}.')
    put('IND_TO_CONT', R(sS + spotm + sca + sflux) - 3.0 - R(s['inv']) - sslag,
        f'Melt to the semi-continuous caster by difference on the melt: Fe 11.5 (10 low-alloy + 1.5 stainless base) '
        f'+ Zn 1 + pot metal {s["potm"]:.4f} (Al {s["al"]:.1f} / Ti {s["ti"]:.2f} / Mo {s["mo"]:.4f} / Cr {s["cr"]:.2f}, '
        f'A-M-261 rev table). | {TAG}.')
    put('CAST_SCRAP_TO_IND', 0.0,
        'Near-net permanent-mold pours at 3 kg/d; sprue/runner returns are campaign events, not a daily '
        f'continuous rate (the melt loop closes on MFG_SCRAP_TO_IND). | {TAG}.')
    put('CAST_TO_ROLL', 3.0, f'Cu cast stock to rolling (bus bar / winding strip, FOUNDRY_DESIGN machine table). | {TAG}.')
    put('CAST_TO_EXTRUDE', 0.0,
        'EXTRUDE is ROLL\'s N+1 alternate (A-M-283): standby-zero on the design day; the Cu line rolls. | {TAG}.')
    put('CONT_TO_ROLL', s['cont_roll'], f'Fe billet to rolling (AQS-SIZE-FOUNDRY Fe 10). | {TAG}.')
    put('CONT_TO_STOCK', R(sS + spotm + sca + sflux) - 3.0 - R(s['inv']) - sslag - s['cont_roll'],
        f'As-cast stock by difference: Zn 1 + stainless base 1.5 + pot metal {s["potm"]:.4f} ingot to stock. | {TAG}.')
    put('ROLL_TO_STOCK', 13.0, f'Rolled plate/sheet stock (Cu 3 + Fe 10). | {TAG}.')
    put('STOCK_TO_MFG', K,
        f'Formed stock to the shop = the foundry product demand: the full AQS-SIZE-FOUNDRY consumable-replacement '
        f'table Cu 3 + Fe 10 + Zn/EW 1 + Al 8 + stainless 1.5 + Ti 0.40 + investment castings 2 = {K:.1f} kg/d '
        f'(A-M-261 rev: the pot-blocked lines unblock on their dock feeds, A-M-284). | {TAG}.')
    put('STOCK_TO_WIRE_DRAW', 0.0,
        'WIRE_DRAW (MFG) closes on S57 Cu from MET_MELT (A-M-177 line); no foundry wire draw at the '
        f'bounding case (A-M-257 by-difference pattern). | {TAG}.')
    put('EXTRUDE_TO_STOCK', 0.0, f'EXTRUDE standby-zero: ROLL N+1 alternate (A-M-283), energized on a roll-stand outage. | {TAG}.')
    put('DRAW_TO_STOCK', 0.0, f'DRAW standby-zero: ROLL N+1 alternate (A-M-283); wire sizing is MFG WIRE_DRAW S57. | {TAG}.')
    put('SINTER_TO_STOCK', 0.0, f'SINTER standby-zero: consolidation N+1 alternate (A-M-283); powder path optional. | {TAG}.')
    put('ATOM_TO_STOCK', 0.0, f'Gas-atomizer powder path optional, not baseline (FOUNDRY_INTEGRATION). | {TAG}.')
    put('IND_TO_ATOM', 0.0, f'No powder demand on IND_MELT at the bounding case. | {TAG}.')
    # ---- pot cells: dock-imported chlorides (A-M-284) ---------------------------------------
    mk('IA-ALCL3-MU', 'NORTH_DOCK', 'AL_POT', 'FOUNDRY', 'S', 'anhydrous AlCl3 feed (mining-waste chloride class)',
       R(s['al']) + R(s['al_cl2']),
       f'D-DOCK feedstock import (A-M-284): {s["al"]:.1f} kg/d Al line 8 + {s["xf"]:.0%} export = '
       f'{s["alcl3"]:.3f} kg/d AlCl3 at {(MM["Al"] + 3 * MM["Cl"]) / MM["Al"]:.3f} kg/kg Al (GREENWOOD); by difference '
       f'on the pot. | {TAG}.')
    put('AL_POT_TO_IND', s['al'],
        f'Al metal to the melt: molten AlCl3-(NaCl-KCl) electrolysis 2AlCl3 -> 2Al + 3Cl2 at 700 C, '
        f'{s["pot_e"]["AL_POT"]["I_A"]:.0f} A at CE {DR.val(s["d"], "foundry_pot_ce")} (A-M-282); '
        f'{s["al_i"]:.0f} kg/d line + {s["al"] - s["al_i"]:.1f} export surplus (A-M-285). | {TAG}.')
    from flow_graph.param import si_refine as _sir
    _si_cl2 = _sir.design(s['d'])['cl2_kg_d']   # chlorine make-up of the on-site silicon loop, IA-CL2-SIREF (A-M-419)
    mk('IA-CL2-SHIP', 'AL_POT', 'NORTH_DOCK', 'DOCK', 'G', 'chlorine byproduct export (water-treatment class product)',
       s['al_cl2'] - _si_cl2,
       f'Pot Cl2 byproduct {3 * MM["Cl"] / MM["Al"]:.3f} kg/kg Al less the {_si_cl2:.4f} kg/d silicon-loop make-up on IA-CL2-SIREF (A-M-419) exports at the dock (D-DOCK outlet; CRU closes '
       f'exactly on S66 = IA-CRU-01 so it has no internal sink - A-M-290 chlorine ruling). | {TAG}.',
       layers=['mass', 'energy'])
    mk('IA-MGCL2-KROLL', 'TI_CELL', 'MG_POT', 'FOUNDRY', 'L', 'Kroll retort MgCl2 return (net of drag-out)',
       s['mgcl2_ret'],
       f'AQS-BAL-KROLL closure: {2 * (MM["Mg"] + 2 * MM["Cl"]) / MM["Ti"]:.3f} kg/kg Ti gross less the '
       f'{s["kroll_flux"]:.4f} kg/d drag-out to FLUX_PREP (A-M-284). | {TAG}.')
    mk('IA-KROLL-FLUX', 'TI_CELL', 'FLUX_PREP', 'FOUNDRY', 'S', 'MgCl2-class salt drag-out (flux cover source)',
       s['kroll_flux'],
       f'{DR.val(s["d"], "foundry_kroll_dragout_frac"):.0%} of the Kroll MgCl2 gross: the salt-flux cover for the '
       f'Al-charged melt (A-M-284); unblocks FLUX_PREP from the SALT_FEED stub. | {TAG}.')
    mk('IA-MGCL2-MU', 'NORTH_DOCK', 'MG_POT', 'FOUNDRY', 'L', 'CaCl2-MgCl2 brine concentrate (mining-waste class)',
       R(s['mg_ti']) + R(s['cl2_ti']) - R(s['mgcl2_ret']),
       f'D-DOCK feedstock import (A-M-284): restores the drag-out so MG_POT delivers the retort Mg exactly; '
       f'{s["mgcl2_mu"]:.4f} kg/d MgCl2-equivalent. | {TAG}.')
    mk('IA-MG-TI', 'MG_POT', 'TI_CELL', 'FOUNDRY', 'S', 'Mg reductant to the Kroll retort',
       s['mg_ti'],
       f'{2 * MM["Mg"] / MM["Ti"]:.3f} kg Mg per kg Ti (AQS-BAL-KROLL); MG_POT electrolysis of the returned MgCl2 at '
       f'{s["pot_e"]["MG_POT"]["I_A"]:.0f} A (A-M-282). | {TAG}.')
    mk('IA-CL2-MG-TI', 'MG_POT', 'TI_CELL', 'FOUNDRY', 'G', 'chlorine to the Kroll chlorinator',
       s['cl2_ti'],
       f'Chlorine closes internally (AQS-BAL-KROLL): MG_POT returns exactly the {4 * MM["Cl"] / MM["Ti"]:.3f} kg/kg Ti '
       f'the chlorination draws; the EW anode gas stays booked to the leach (Faraday balance, A-M-255 pattern; '
       f'A-M-284 ruling - it is the initial loop charge only). | {TAG}.')
    put('MG_POT_TO_IND', 0.0,
        f'MG_POT serves only the Kroll recycle at steady state (all Mg to the retort on IA-MG-TI); no Mg stock line '
        f'at the table. | {TAG}.')
    put('MG_POT_CL2', 0.0, f'Retired 2026-10-30: MG_POT makes exactly the chlorine the Kroll chlorinator draws (IA-CL2-MG-TI), '
        f'because both follow the same Ti rate, so the pot can never have a chlorine surplus for CRU. | {TAG}.')
    E['MG_POT_CL2']['presence'] = 'retired'
    mk('IA-CACL2-MU', 'NORTH_DOCK', 'CA_POT', 'FOUNDRY', 'L', 'CaCl2 brine concentrate (mining-waste class)',
       R(s['ca']) + R(s['ca_cl2']),
       f'D-DOCK feedstock import (A-M-284): Ca deoxidizer addition {s["ca"]:.4f} kg/d at '
       f'{DR.val(s["d"], "foundry_ca_add_frac"):.2%} of the melt charge; by difference on the pot. | {TAG}.')
    put('CA_POT_TO_IND', s['ca'],
        f'Ca deoxidizer/desulfurizer addition to the melt (steelmaking practice class); sized at '
        f'{DR.val(s["d"], "foundry_ca_add_frac"):.2%} of the melt charge - the same Ca line serves the grease-thickener '
        f'Ca(OH)2 draw (AQS-DUTY-GREASE) when the P_CA param pass rates the cake. | {TAG}.')
    mk('IA-CA-CL2-SHIP', 'CA_POT', 'NORTH_DOCK', 'DOCK', 'G', 'chlorine byproduct export (water-treatment class)',
       s['ca_cl2'],
       f'CA_POT Cl2 byproduct {2 * MM["Cl"] / MM["Ca"]:.3f} kg/kg Ca exports at the dock (A-M-290 chlorine ruling). | {TAG}.',
       layers=['mass', 'energy'])
    # ---- Kroll cells: dock oxide concentrates + carbon, internal chlorine (A-M-290) ---------
    mk('IA-TIO2-MU', 'NORTH_DOCK', 'TI_CELL', 'FOUNDRY', 'S', 'TiO2-equivalent rutile concentrate (dock import class)',
       s['tio2'],
       f'D-DOCK feedstock import (A-M-284): {(MM["Ti"] + 2 * MM["O"]) / MM["Ti"]:.3f} kg/kg Ti on the oxide-equivalent '
       f'basis (AQS-BAL-KROLL); concentrate grade envelope TiO2 90-97 wt%, design point 94 % (A-M-284 '
       f'needs_verification: XRF assay of the accepted lot). | {TAG}.')
    # Carbon reductant from the plant's own pyrolysis char (owner decision t58u: no imports except waste or raw ore; A-M-420).
    # The char carries char_fixed_C_frac fixed carbon; its volatiles and ash leave with the chlorinator gas on the design basis.
    _fc = DR.val(s['d'], 'char_fixed_C_frac'); CH = {k: s[k]/_fc for k in ('c_ti', 'c_mo', 'c_cr')}
    def _char(sid, cell, why):
        mk(sid, 'OIL_PYRO', cell, 'FOUNDRY', 'S', 'plant pyrolysis char reductant', CH[why[0]],
           f'{why[1]}: {s[why[0]]:.4f} kg/d carbon / char_fixed_C_frac {_fc:g} = {CH[why[0]]:.4f} kg/d of char from OIL_PYRO (A-M-420). | {TAG}.')
        E[sid].update(from_unit_id='OIL_PYRO', from_sector_id='OIL', carries='plant pyrolysis char reductant')
    _char('IA-C-TI', 'TI_CELL', ('c_ti', '2 C per TiO2 chlorinated (AQS-BAL-KROLL)'))
    put('METALS_TO_IND_MELT', s['ti'],
        f'Ti sponge to the melt under salt flux: {s["ti"]:.2f} kg/d = 0.40 line + export margin (A-M-285); the vacuum '
        f'consolidation path (VAC_IND_TI) is the N+1 quality route, standby-zero (A-M-283). | {TAG}.')
    put('TI_CELL_CL2_TO_CRU', 0.0, f'Kroll chlorine closes on the Mg pot loop (IA-CL2-MG-TI); the CRU tap is purge-only. | {TAG}.')
    mk('IA-KROLL-CO', 'TI_CELL', 'NORTH_DOCK', 'DOCK', 'G', 'chlorinator CO (fuel-gas class export)',
       R(s['tio2']) + R(CH['c_ti']) + R(s['cl2_ti']) + R(s['mg_ti']) - R(s['ti']) - R(s['mgcl2_ret']) - R(s['kroll_flux']),
       f'{2 * (MM["C"] + MM["O"]) / MM["Ti"]:.3f} kg/kg Ti chlorinator CO to the dock fuel-gas class (IA-N2-VENT '
       f'precedent; no spare burner capacity at Rev AC scope - burner routing is an integration follow-up). | {TAG}.')
    put('VAC_IND_TI', 0.0, f'VAC_IND is the N+1 diverse melt path (A-M-283): standby-zero on the design day. | {TAG}.')
    put('VAC_IND_TO_VAC_CAST', 0.0, f'VAC_CAST rides VAC_IND (N+1 pair, A-M-283): standby-zero. | {TAG}.')
    mk('IA-MOO3-MU', 'NORTH_DOCK', 'MO_CELL', 'FOUNDRY', 'S', 'MoO3-equivalent concentrate (dock import class)',
       s['moo3'],
       f'D-DOCK feedstock import (A-M-284): {(MM["Mo"] + 3 * MM["O"]) / MM["Mo"]:.3f} kg/kg Mo oxide-equivalent; '
       f'tech-oxide grade envelope 95-99 wt% MoO3, design 98 % (A-M-284 assay-verification task). | {TAG}.')
    _char('IA-C-MO', 'MO_CELL', ('c_mo', '1.5 C per MoO3 on the Mo(III) chloride route (A-M-284)'))
    put('MO_TO_IND', s['mo'],
        f'Mo metal to the melt: carbochlorination to MoCl3 then molten-salt electrolysis MoCl3 -> Mo + 1.5Cl2 with the '
        f'anode gas recycled to the chlorination (internal chlorine loop, A-M-290); {s["mo_i"]:.2f} kg/d 316-class '
        f'addition + export margin. | {TAG}.')
    put('MO_CELL_RAFFINATE', 0.0, 'Oxide feed has no liquor raffinate; the EW_9 stub stays retired (A-M-255). | {TAG}.')
    put('MO_CELL_ANODE_GAS_TO_CRU', 0.0, f'Anode gas recycles to the cell chlorination step (A-M-290); CRU tap purge-only. | {TAG}.')
    put('EW9_LIQUOR_TO_MO', 0.0,
        'A-M-255 alias retired: EW_9 liquor tail fully booked on IA-EW-09 to POLISH_BANK; the Mo feed is the dock '
        f'oxide import (IA-MOO3-MU, A-M-284). | {TAG}.')
    put('EW_METALS_TO_IND', 0.0,
        'A-M-255 alias retired: EW_9 metal harvest fully booked on IA-EW-MET-9 and IA-EW-SHEET; the melt is fed on '
        f'shop scrap + pot metal. | {TAG}.')
    mk('IA-MO-VENT', 'MO_CELL', 'NORTH_DOCK', 'DOCK', 'G', 'chlorinator CO2 (vent class)',
       R(s['moo3']) + R(CH['c_mo']) - R(s['mo']), f'1.5 CO2 per Mo on the carbochlorination net (A-M-284); dock vent class. | {TAG}.')
    mk('IA-CR2O3-MU', 'NORTH_DOCK', 'CR_CELL', 'FOUNDRY', 'S', 'Cr2O3-equivalent chromite concentrate (dock import class)',
       s['cr2o3'],
       f'D-DOCK feedstock import (A-M-284): {(2 * MM["Cr"] + 3 * MM["O"]) / (2 * MM["Cr"]):.3f} kg/kg Cr '
       f'oxide-equivalent; chromite class envelope 40-52 wt% Cr2O3, design 46 % (A-M-284 assay-verification task; the '
       f'Fe/Mg/Al gangue balance is the assay-day follow-up). | {TAG}.')
    _char('IA-C-CR', 'CR_CELL', ('c_cr', '3 C per Cr2O3 on the Cr(III) chloride route (A-M-284)'))
    put('CR_TO_IND', s['cr'],
        f'Cr metal to the melt: carbochlorination to CrCl3 then molten-salt electrolysis 2CrCl3 -> 2Cr + 3Cl2 with the '
        f'anode gas recycled internally (A-M-284); {s["cr_i"]:.2f} kg/d stainless addition + export margin. | {TAG}.')
    mk('IA-CR-VENT', 'CR_CELL', 'NORTH_DOCK', 'DOCK', 'G', 'chlorinator CO (fuel-gas class export)',
       R(s['cr2o3']) + R(CH['c_cr']) - R(s['cr']), f'3 CO per 2 Cr on the carbochlorination net (A-M-284); dock fuel-gas class. | {TAG}.')
    # ---- investment casting: wax make-up from the plant wax cut + foundry silica (A-M-286, A-M-424) ----
    # Owner decision t59u (no imports except waste or raw ore): the dewax reclaim covers foundry_inv_wax_reclaim_frac of
    # the pattern wax first (recovery first, t61u); the make-up is the paraffin of the plant's own C19-C28 pyrolysis
    # cut, drawn from PROD_C19_C28 before its surplus ships (ess_tf.py takes this draw off IA-C19-SHIP).
    mk('C19_TO_WAX', 'PROD_C19_C28', 'WAX_PATTERN', 'FOUNDRY', 'S', 'C19-C28 paraffin cut as the pattern wax make-up',
       s['wx_mu'],
       f'{1 - DR.val(s["d"], "foundry_inv_wax_reclaim_frac"):.0%} of the {s["wx"]:.1f} kg/d pattern wax, the share the '
       f'dewax reclaim ({s["wx_recl"]:.1f} kg/d) does not cover, from the plant C19-C28 paraffin cut (A-M-286, A-M-424). | {TAG}.')
    E['C19_TO_WAX']['composition'] = {'C19-C28': 1.0}
    if 'IA-WAX-MU' in E:
        E['IA-WAX-MU']['presence'] = 'retired'
        E['IA-WAX-MU']['rate'] = rate(0.0, 'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). '
                                      'The make-up is the plant C19-C28 paraffin cut on C19_TO_WAX (A-M-424).')
    mk('IA-SILICA-MU', 'NORTH_DOCK', 'SHELL_BUILD', 'FOUNDRY', 'S', 'foundry silica (flour/stucco/binder make-up)',
       s['sh_mu'],
       f'D-DOCK feedstock import (A-M-284): shell make-up {1 - DR.val(s["d"], "foundry_inv_shell_reclaim_frac"):.1%} of '
       f'the {s["sh"]:.1f} kg/d green shell (the 0.5 kg/kg-casting registered waste line, AQS-SIZE-FOUNDRY); GLASS_DIGEST '
       f'stays fully committed (IA-GLASS-03 30.0 = S08G 26.7 + IA-SIL-SRC 3.3). | {TAG}.')
    put('WAX_TO_SHELL', s['wx'], f'{s["wx"]:.1f} kg/d wax patterns at 1 kg/kg castings (A-M-286). | {TAG}.')
    put('SHELL_TO_BURNOUT', s['sh'] + s['wx'],
        f'Green shell {s["sh"]:.1f} kg/d (6-dip class, 4 kg/kg castings) + patterns {s["wx"]:.1f} (A-M-286). | {TAG}.')
    put('WAX_RECLAIM_TO_PATTERN', s['wx_recl'],
        f'Dewax condensate reclaim {DR.val(s["d"], "foundry_inv_wax_reclaim_frac"):.0%} of the pattern wax (A-M-286). | {TAG}.')
    put('WAX_TO_OIL', 0.0,
        f'Unrecovered wax ({s["wx_burn"]:.2f} kg/d) burns in the flash-dewax firebox (A-M-286); no oil-line draw. | {TAG}.')
    mk('IA-BURNOUT-VENT', 'SHELL_BURNOUT', 'NORTH_DOCK', 'DOCK', 'G', 'dewax/burnout off-gas (burned wax + steam)',
       s['wx_burn'], f'Balance of the pattern wax at the burnout firebox (A-M-286); dock vent class. | {TAG}.')
    put('BURNOUT_TO_CAST', s['sh'], f'Fired shell {s["sh"]:.1f} kg/d to the pour station (A-M-286). | {TAG}.')
    put('IND_TO_INV', s['inv'],
        f'Melt to the investment pour: the live melt output at the {s["inv"]:.1f} kg/d castings line '
        f'(AQS-SIZE-FOUNDRY; A-M-286). | {TAG}.')
    put('VAC_TO_INV', 0.0, f'VAC_IND N+1 pour path (A-M-283): standby-zero on the design day. | {TAG}.')
    put('INV_TO_BREAK', s['sh'] + s['inv'], f'Castings in shell to knock-out (A-M-286). | {TAG}.')
    put('BREAK_TO_STOCK', s['inv'], f'Investment castings {s["inv"]:.1f} kg/d to stock (A-M-286). | {TAG}.')
    mk('IA-SHELL-RECLAIM', 'SHELL_BREAK', 'SHELL_BUILD', 'FOUNDRY', 'S', 'reclaimed shell stucco/flour',
       s['sh_recl'], f'{DR.val(s["d"], "foundry_inv_shell_reclaim_frac"):.1%} of spent shell reclaimed to the backup '
       f'coats (A-M-286). | {TAG}.')
    mk('IA-SHELL-EXPORT', 'SHELL_BREAK', 'NORTH_DOCK', 'DOCK', 'S', 'spent foundry silica (solids return class)',
       s['sh_mu'], f'Spent-shell balance = the 0.5 kg/kg-casting make-up (AQS-SIZE-FOUNDRY registered waste line; '
       f'A-M-286); GLASS_MILL has no digest capacity (A-M-267). | {TAG}.')
    # bench solvent made on site, recovery first (A-M-428); takes its CO from IA-KROLL-CO rated above
    from . import solvent as _SV
    _SV.tf(g, E, s['d'])
    # recovery-first records (owner rule t61u, A-M-423; checked by flow_graph/param/recovery.py)
    from .recovery import frac as _fr
    _v = lambda k: float(E[k]['rate']['value'] or 0)
    E['IA-SHELL-EXPORT']['composition'] = {'SiO2': 1.0}
    si = _fr('SiO2', 'Si')
    N['SHELL_BUILD'].setdefault('params', {})['recovery'] = [dict(
        element='Si', use='investment shell silica', need_kg_d=(_v('IA-SHELL-RECLAIM') + _v('IA-SILICA-MU'))*si,
        recovered_kg_d=_v('IA-SHELL-RECLAIM')*si, recovered_from=['IA-SHELL-RECLAIM'], ore_streams=['IA-SILICA-MU'],
        unrecovered=[dict(stream='IA-SHELL-EXPORT', kg_d=_v('IA-SHELL-EXPORT')*si, recoverable=False,
                          basis='spent shell beyond foundry_inv_shell_reclaim_frac: fines and fired binder that the stucco cannot take back (A-M-286)')])]
    # Q-037 (A-M-427): the dense grit of FLOAT_SINK is the first source of the Ti, Mo and Cr oxides, as far as its assay
    # supports; the dock concentrate covers the rest and stays installed as the redundant source. The assay is a driver
    # input (grit_dense_frac and grit_<oxide>_wt, AQS-ASSAY-TI-MO); until it lands it is 0 and the grit feeds stand by.
    _d = s['d']; _gv = lambda k: DR.val(_d, k)
    _mode = _gv('grit_route_mode'); assert _mode in ('GRIT_FIRST', 'ORE_ONLY'), _mode
    _sk = E['IA-SINK-01']; _sc = _sk.get('composition') or {}
    _dry = _v('IA-SINK-01')*(1 - _sc.get('water', 0.0) - _sc.get('HCl', 0.0))
    _grit_avail = _dry*_gv('grit_dense_frac') if _mode == 'GRIT_FIRST' else 0.0
    _rec = _gv('grit_chlor_recovery_frac'); _drawn = 0.0
    for _sid, _u, _el, _f, _gsid, _ssid, _wk in (('IA-TIO2-MU', 'TI_CELL', 'Ti', 'TiO2', 'FLOAT_SINK_GRIT_TO_TI', 'TI_CELL_SLAG_RETURN', 'grit_TiO2_wt'),
                                               ('IA-MOO3-MU', 'MO_CELL', 'Mo', 'MoO3', 'FLOAT_SINK_GRIT_TO_MO', 'MO_CELL_SLAG_RETURN', 'grit_MoO3_wt'),
                                               ('IA-CR2O3-MU', 'CR_CELL', 'Cr', 'Cr2O3', 'FLOAT_SINK_GRIT_TO_CR', 'CR_CELL_SLAG_RETURN', 'grit_Cr2O3_wt')):
        _need = _v(_sid)                                   # oxide-equivalent need of the cell, kg/d
        _y = _gv(_wk)*_rec                                 # oxide taken up per kg of grit fed
        _left = max(0.0, _grit_avail - _drawn)
        _feed = min(_left, _need/_y) if _y > 0 else 0.0     # grit fed to this cell, kg/d (one grit pool, Ti first)
        _cov = _feed*_y; _drawn += _feed
        _why = (f'{_feed:.4f} kg/d of dense grit at {_gv(_wk):g} {_f} x grit_chlor_recovery_frac {_rec:g} covers {_cov:.4f} of the {_need:.4f} kg/d '
                f'{_f}-equivalent need (Q-037, A-M-427; assay input AQS-ASSAY-TI-MO, route {_mode})')
        mk(_gsid, 'FLOAT_SINK', _u, 'FOUNDRY', 'S', f'dense grit from the float-sink as the first {_f} source', R(_feed),
           f'{_why}. Standby at 0 until the assay drivers are set; the dock concentrate is the redundant source. | {TAG}.')
        mk(_ssid, _u, 'LEACH_CSTR_1', 'DIGESTER', 'S', 'grit gangue and unreacted oxide back to the leach', R(_feed - _cov),
           f'grit fed {_feed:.4f} less the oxide taken up {_cov:.4f} kg/d returns to the leach as slag (Q-037, A-M-427). | {TAG}.')
        put(_sid, R(_need - _cov), f'{E[_sid]["rate"]["note"]} Ore covers the shortfall after the grit: {_need:.4f} - {_cov:.4f} kg/d (Q-037, A-M-427).')
        N[_u].setdefault('params', {})['recovery'] = [dict(
            element=_el, use=f'{_u} metal', need_kg_d=_need*_fr(_f, _el), recovered_kg_d=_cov*_fr(_f, _el), recovered_from=[_gsid],
            ore_streams=[_sid], unrecovered=[],
            note=(f'the dense grit of FLOAT_SINK is the first source as far as its assay supports (grit_dense_frac, {_wk}; AQS-ASSAY-TI-MO); '
                  f'the dock concentrate covers the rest and stays installed as the redundant source (Q-037, A-M-427)'))]
    _wf = E['IA-WET-FLOAT-01']
    if _drawn > 0 or 'pre_grit_kg_d' in (_wf.get('params') or {}):
        _base = _wf.setdefault('params', {}).setdefault('pre_grit_kg_d', _v('IA-WET-FLOAT-01'))
        put('IA-WET-FLOAT-01', R(_base - _drawn),
            f'Float/sink liquor return {_base:.4f} kg/d less the dense grit drawn to the cells {_drawn:.4f} kg/d (Q-037, A-M-427). | {TAG}.')
    put('SHELL_TO_GLASS', 0.0,
        'Spent shell reclaims internally (IA-SHELL-RECLAIM) and exports the balance at the dock: GLASS_DIGEST is fully '
        f'committed (A-M-267) so the solids line has no digest capacity for it. | {TAG}.')
    # ---- alternates: N+1 standby-zero with rated envelopes (A-M-283) -----------------------
    put('COMB_OFFGAS', 0.0, 'COMB_HEAT is the fuel-fired N+1 alternate (A-M-283): standby-zero; off-gas routes to '
      f'MET_SCRUB only when the alternate is energized. | {TAG}.')
    put('FLUX_TO_IND', s['kroll_flux'],
        f'Salt-flux cover to the melt = the Kroll MgCl2-class drag-out (A-M-284); closes FLUX_PREP on '
        f'IA-KROLL-FLUX. | {TAG}.')
    put('SALT_TO_FLUX', 0.0, 'SALT_FEED stays a stub source: the flux feed is the Kroll drag-out (A-M-284). | {TAG}.')
    # ---- node continuous_kw + SF feeds ------------------------------------------------------
    def kw(u, v, note):
        N[u]['continuous_kw'] = {'value': round(v, 4), 'unit': 'kW', 'status': 'study', 'note': note}
        sid = f'SF-{u}'
        if sid not in E:
            src = dict(E['SF-HF_GEN'])
            src.update(stream_id=sid, to_unit_id=u, to_sector_id='FOUNDRY', notes='Foundry bus feed (AQS-DUTY-072).')
            src['rate'] = {'value': round(v, 4), 'unit': 'kW', 'status': 'study', 'note': f'Equals {u} continuous_kw ({DOC_F}).'}
            g['edges'].append(src); E[sid] = src
        else:
            E[sid]['rate'] = {'value': round(v, 4), 'unit': 'kW', 'status': 'study',
                              'note': f'Equals {u} continuous_kw ({DOC_F}).'}

    pe = s['pot_e']
    kw('AL_POT', pe['AL_POT']['kW'],
       f'{DOC_F} pot cell: Faraday {pe["AL_POT"]["I_A"]:.0f} A x {pe["AL_POT"]["V"]:.1f} V at CE '
       f'{DR.val(s["d"], "foundry_pot_ce")} = {pe["AL_POT"]["dc_kW"]:.2f} kW DC + bath hold '
       f'{pe["AL_POT"]["hold_kW"]:.2f} kW (150 mm fibre, study; A-M-282).')
    kw('MG_POT', pe['MG_POT']['kW'],
       f'{DOC_F} Kroll Mg recycle: {pe["MG_POT"]["I_A"]:.1f} A x {pe["MG_POT"]["V"]:.1f} V = '
       f'{pe["MG_POT"]["dc_kW"]:.3f} kW + hold {pe["MG_POT"]["hold_kW"]:.2f} kW (A-M-282).')
    kw('CA_POT', pe['CA_POT']['kW'],
       f'{DOC_F} grease-Ca pot: {pe["CA_POT"]["I_A"]:.2f} A x {pe["CA_POT"]["V"]:.1f} V = '
       f'{pe["CA_POT"]["dc_kW"]:.3f} kW + hold {pe["CA_POT"]["hold_kW"]:.2f} kW (A-M-282).')
    kw('TI_CELL', pe['TI_CELL']['kW'],
       f'{DOC_F} Kroll retort + chlorinator hold at 900/800 C under Ar (thermochemical reduction, no electrolysis; '
       f'A-M-284 study hold).')
    kw('MO_CELL', pe['MO_CELL']['kW'],
       f'{DOC_F} Mo(III) molten-salt cell: {pe["MO_CELL"]["I_A"]:.2f} A x {pe["MO_CELL"]["V"]:.1f} V = '
       f'{pe["MO_CELL"]["dc_kW"]:.3f} kW + hold {pe["MO_CELL"]["hold_kW"]:.2f} kW (A-M-282).')
    kw('CR_CELL', pe['CR_CELL']['kW'],
       f'{DOC_F} Cr(III) molten-salt cell: {pe["CR_CELL"]["I_A"]:.2f} A x {pe["CR_CELL"]["V"]:.1f} V = '
       f'{pe["CR_CELL"]["dc_kW"]:.3f} kW + hold {pe["CR_CELL"]["hold_kW"]:.2f} kW (A-M-282).')
    kw('FLUX_PREP', 0.1, f'{DOC_F} flux bench agitator/mixer at the {s["kroll_flux"]:.3f} kg/d salt duty (study).')
    kw('WAX_PATTERN', 0.5, f'{DOC_F} pattern injector + wax conditioning pot at {s["wx"]:.1f} kg/d patterns (A-M-286 study).')
    kw('SHELL_BUILD', 0.3, f'{DOC_F} slurry mixer + stucco rainfall at {s["sh"]:.1f} kg/d shell (A-M-286 study).')
    kw('SHELL_BURNOUT', 0.25,
       f'{DOC_F} dewax/firebox at 900 C: shell sensible {s["sh"]:.1f} kg/d offset by the {s["wx_burn"]:.2f} kg/d wax '
       f'fire credit; 0.25 kW hold class (A-M-286 study).')
    kw('INV_CAST', 0.15, f'{DOC_F} tilt-pour station at {s["inv"]:.1f} kg/d castings (study).')
    kw('SHELL_BREAK', 0.4, f'{DOC_F} vibratory knock-out table at {s["sh"]:.1f} kg/d spent shell (study).')
    for u, why in (('VAC_CAST', 'N+1 of CAST_LINE/CONT_CAST (vacuum tilt-pour, A-M-283)'),
                   ('RES_HEAT', 'N+1 diverse heat of SHELL_BURNOUT/SINTER (resistance radiant, A-M-283)'),
                   ('SINTER', 'N+1 consolidation of ROLL (press-and-sinter P/M route, A-M-283)'),
                   ('FORGE', 'N+1 former of ROLL (open-die press, A-M-283)'),
                   ('EXTRUDE', 'N+1 former of ROLL (profile press, A-M-283)'),
                   ('DRAW', 'N+1 former of ROLL (wire/rod bench, A-M-283)')):
        kw(u, 0.0, f'standby-zero on the design day: {why}; connected rating in params.design.')
    kw('COMB_HEAT', 0.05,
       'standby-zero on the design day: N+1 fuel-fired heat of IND_MELT (A-M-283); 0.05 kW controls/blower '
       'parasitic, fuel on the C5-C10 class when energized.')
    # ---- polymers --------------------------------------------------------------------------
    spf = R(sP * (1 + s['rej']))                 # grid-consistent naphtha feed from the rounded P
    put('OIL_TO_OLEFIN', 0.0,
        'Fractionator draw 0: the olefin feed draws as naphtha at the cut tank (IA-C5-POLY); the recovered-wax '
        f'path (WAX_TO_OIL) is 0 with the wax loop closing on reclaim (A-M-286). OIL_FRAC closes. | {TAG}.')
    put('MEOH_TO_OLEFIN', 0.0,
        'Methanol committed to the tank/ship balance (X-PAR-12 TF on S75); the olefin carbon source is the '
        f'on-site C5-C10 naphtha cut (AQS-DES-POLY: carbon source on site). | {TAG}.')
    put('OLEFIN_TO_PELLET', spf,
        f'Polyolefin resin = naphtha feed {spf:.4f} kg/d (mass-conserving oligomerization, '
        f'AQS-SIZE-OIL-POLY POLY_OLEFIN 150-250 C / 1-5 MPa). | {TAG}.')
    put('PELLET_TO_STOCK', spf, f'Pellet line passes the resin to stock. | {TAG}.')
    put('POLY_TO_MFG', sP,
        f'Shop polymer draw by difference on the shop closure (A-M-257 pattern): -r0 {s["r0"]:+.6f} + melt loss '
        f'term f*K/(1-f); molded articles ride BLOW_MOLD (IA-BLOW-OUT 8.407). | {TAG}.')
    put('POLY_TO_WET', R(s['rej'] * sP),
        f'Shop polymer offcut to the wet line, {s["rej"]:.0%} of the issue (the S58/S59/S60 10 % shop-loss '
        f'class, AQS-DUTY-010; A-M-263). | {TAG}.')
    put('POWDER_TO_STOCK', 0.0, 'Fluoropolymer powder blocked (no F source on site, AQS-BOM-SC-001, Q-011/Q-013). | {TAG}.')
    put('FILM_TO_STOCK', 0.0, 'FILM_CAST has no feed edge at Rev AC; film/sheet rides the pellet line when a die study issues it. | {TAG}.')
    for k, why in [
        ('F_RECOVER_TO_HF_GEN', 'F_RECOVER (DIGESTER) has no in-edge at Rev AC; no fluorine source on site '
         '(AQS-BOM-SC-001 43 lines Missing, Q-013).'),
        ('HF_GEN_TO_VDF', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013); design case 0.5 kg/d HF in ' + DOC_P + '.'),
        ('HF_GEN_TO_TFE', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('VDF_TO_POLY_F', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('TFE_TO_POLY_F', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('POLYF_TO_PELLET', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('POLYF_TO_POWDER', 'Fluoropolymer train F-blocked (AQS-BOM-SC-001, Q-013).'),
        ('CRU_TO_VDF', 'No monomer chlorination draw: fluoropolymer train F-blocked (Q-013).'),
        ('CRU_TO_TFE', 'No monomer chlorination draw: fluoropolymer train F-blocked (Q-013).'),
        ('DIGEST_TO_POLY', 'POLY_COND recipe waits on the digester organic assay (AQS-DES-POLY / AQS-SIZE-OIL-POLY: '
         'no rate treated as design); BLACK_DIGEST closes on IA-BLK-GREY.'),
    ]:
        put(k, 0.0, f'{why} | {TAG}.')
    # naphtha feed edge + ship re-solve
    if 'IA-C5-POLY' not in E:
        src = dict(E['IA-C5-SHIP'])
        src.update(stream_id='IA-C5-POLY', to_unit_id='POLY_OLEFIN', to_sector_id='POLYMERS', phase='L',
                   carries='C5-C10 naphtha olefin feed',
                   notes='Created by the polymers sizing pass: the olefin feed draws as naphtha at the cut tank '
                         '(AQS-SIZE-OIL-POLY); the fractionator-side OIL_TO_OLEFIN stays 0 so OIL_FRAC closes.',
                   open_boundary=False)
        src['rate'] = rate(spf,
                           f'Olefin feed to POLY_OLEFIN = shop polymer draw x (1 + reject) = {spf:.4f} kg/d '
                           f'({DOC_P}, A-M-264). | {TAG}.')
        g['edges'].append(src)
        E['IA-C5-POLY'] = src
    else:
        put('IA-C5-POLY', spf, f'Polyolefin naphtha feed ({DOC_P}, A-M-264). | {TAG}.')
    cut1_out = float(s['E']['CUT-1-OUT']['rate']['value'] or 0)
    put('IA-C5-SHIP', R(float(s['E']['CUT-1']['rate']['value'] or 0)) - cut1_out - spf,
        f'X-PAR-12 TF (AQS-PAR-005): C5-C10 make less the plant draws - genset {cut1_out:.4f} and the '
        f'olefin feed {s["poly_feed"]:.4f} (this pass, {DOC_P}); shipped at the dock. | {TAG}.')
    # ---- dock metal export + goods statement ------------------------------------------------
    if 'IA-METAL-SHIP' not in E:
        src = dict(E['IA-O2-SHIP'])
        src.update(stream_id='IA-METAL-SHIP', from_unit_id='METAL_STORE', from_sector_id='MFG',
                   to_unit_id='NORTH_DOCK', to_sector_id='DOCK', phase='S',
                   carries='surplus foundry metal export (pot-line product, dispatch campaign)',
                   notes='Created by the foundry sizing pass: the pot/cell metal is the stock loop\'s only net inlet, '
                         'so at steady state the loop passes it and the full pot output leaves as the dock metal '
                         'export (A-M-285).')
        g['edges'].append(src); E['IA-METAL-SHIP'] = src
    put('IA-METAL-SHIP', s['potm'],
        f'Pot-line metal export {s["potm"]:.4f} kg/d (Al {s["al"]:.1f} + Ti {s["ti"]:.2f} + Mo {s["mo"]:.4f} + Cr '
        f'{s["cr"]:.2f}): the stock loop is the only net inlet, so the loop passes it to the METAL_STORE dispatch '
        f'(A-M-270 buffer) and the dock exports it (D-DOCK outlet; A-M-285). | {TAG}.')
    # ---- goods balance ---------------------------------------------------------------------
    # SF-HF_GEN: electrical feed of the F-blocked standby unit (0 duty; the power rollup sums 0)
    if 'SF-HF_GEN' in E:
        E['SF-HF_GEN']['rate'] = {'value': 0.0, 'unit': 'kW', 'status': 'study',
                                  'note': f'HF_GEN standby at 0 duty (fluoropolymer train F-blocked, Q-013; '
                                          f'feed 0 on F_RECOVER_TO_HF_GEN). | {TAG}.'}
        if 'HF_GEN' in N:
            N['HF_GEN']['continuous_kw'] = {'value': 0.0, 'unit': 'kW', 'status': 'study',
                                            'note': f'standby, 0 duty at the bounding case ({DOC_P} sec. 3). | {TAG}.'}
    put('DOCK_EXPORT_TBD', 0.0,
        'Goods balance (A-M-265 rev): the accounting placeholder stays 0.0 - the real surplus exports ride their own '
        'dock edges: foundry pot metal IA-METAL-SHIP ' f'{s["potm"]:.4f} kg/d + pot chlorine IA-CL2-SHIP/IA-CA-CL2-SHIP '
        f'{s["al_cl2"] + s["ca_cl2"]:.3f} kg/d (A-M-285) on top of the shipped products (O2, MeOH, oil cuts); mfg goods '
        'surplus net 0 (IA-MFG-OUT 596.863 = IA-WEAR worn return). THIS IS THE PLANT SURPLUS STATEMENT at Rev AC scope '
        'with the foundry feedstock program live: the plant is a net exporter of metal and chlorine through the dock.')
    E['DOCK_EXPORT_TBD']['rate']['note'] = (E['DOCK_EXPORT_TBD']['rate']['note'].split(f' | {TAG}')[0]) + f' | {TAG}.'
    stamp(g, s)
    # retire this pass's own Rev B interim edge (Ca routed via the melt; P_CA stays the DIGESTER lane's unrated stub)
    g['edges'] = [e for e in g['edges'] if e['stream_id'] != 'IA-CA-TO-PCA']
    # document the remaining blocked edges (idempotent: one entry, replaced in place)
    gap = {'id': 'FOUNDRY_POLY_MISSING_EDGES', 'severity': 'low',
           'detail': 'Foundry/polymers sizing pass Rev B (AQS-DUTY-072/073): the D-DOCK feedstock program unblocked the '
                     'pot/cell, Kroll and investment trains (A-M-284.285). Remaining absent/blocked: DRAW feed '
                     '(CAST/ROLL->DRAW) and FORGE edges (both N+1 alternates at standby-zero, A-M-283), FILM_CAST feed, '
                     'POLY_COND outlet to PELLET, SALT_FEED source (flux now fed from the Kroll drag-out), F_RECOVER '
                     'feed (F recovery, Q-013). The Kroll gangue/Fe terms wait on the concentrate assays (A-M-284).'}
    g['gaps'] = [x for x in g.get('gaps', []) if x.get('id') != gap['id']] + [gap]
    if write:
        open(GP, 'w').write(json.dumps(g, indent=2) + '\n')
    return s


def stamp(g, s):
    N = {n['unit_id']: n for n in g['nodes']}
    src_f, src_p = DOC_F, DOC_P

    def st(u, **kw):
        p = N[u].setdefault('params', {})
        p['sizing'] = dict(status='study', source=kw.pop('source'), **kw)

    q, mix = s['q'], s['mix']
    st('IND_MELT', source=src_f, charge_kg_d=round(s['S'] + s['potm'] + s['flux'], 4), stock_out_kg_d=s['K'],
       slag_kg_d=round(s['slag'], 4), crucible_kg=s['charge'], heats_d=s['heats'], melt_kWh_d=round(s['e_melt'], 3),
       avg_kW=round(s['e_melt'] / 24, 4), peak_kW=s['kw_peak'], connected_kW=25.0,
       kWh_per_kg={k: round(v, 4) for k, v in q.items()},
       basis='scrap remelt + pot metal; class energies (cp_s dT + L + cp_l superheat)/eta per A-M-177 method, '
             'CRC_CU/CRC_FE/CRC_ZN/CRC_AL/CRC_TI (reactive/addition class bounding at Ti)')
    st('CAST_LINE', source=src_f, pour_kg_d=mix['Cu'], products='Cu ingot/billet, permanent mold', scrap_return_kg_d=0.0)
    st('CONT_CAST', source=src_f, feed_kg_d=round(s['cont'], 4), billet_kg_d=10.0, ingot_kg_d=round(s['cont_stock'], 4),
       mold='water-cooled copper, horizontal (AQS-SIZE-FOUNDRY)',
       basis='pot metal + Zn + stainless base to the ingot line; Fe 10 rolled')
    st('ROLL', source=src_f, rolled_kg_d=round(mix['Cu'] + 10.0, 4), kWh_d=round(s['e_roll'], 4),
       basis='0.032 kWh/kg cold-rolling class (A-M-177 DIETER1988); hot rolling cheaper')
    st('STOCK_OUT', source=src_f, stock_out_kg_d=round(s['stock_in'], 4), draws=dict(MFG=s['K'], FAB=0.0, WIRE_DRAW=0.0),
       export_kg_d=round(s['potm'], 4))
    # pots / Kroll cells: live designs (A-M-280..284.283)
    pe = s['pot_e']
    st('AL_POT', source=src_f, al_kg_d=s['al'], line_kg_d=s['al_i'], export_kg_d=round(s['al'] - s['al_i'], 4),
       alcl3_kg_d=round(s['alcl3'], 4), cl2_kg_d=round(s['al_cl2'], 4), chemistry='2 AlCl3 -> 2 Al + 3 Cl2, 700 C '
       'NaCl-KCl-AlCl3 bath (GREENWOOD stoichiometry)', **pe['AL_POT'],
       basis='D-DOCK anhydrous AlCl3 import; Faraday at CE 0.85 (A-M-282); A-M-284 feedstock ruling')
    st('MG_POT', source=src_f, mg_kg_d=round(s['mg_ti'], 4), mgcl2_return_kg_d=round(s['mgcl2_ret'], 4),
       mgcl2_makeup_kg_d=round(s['mgcl2_mu'], 4), cl2_kg_d=round(s['cl2_ti'], 4), chemistry='MgCl2 -> Mg + Cl2, '
       '700 C (AQS-BAL-KROLL closure)', **pe['MG_POT'],
       basis='Kroll Mg recycle at the 0.50 kg/d Ti line; CaCl2-MgCl2 brine make-up covers the drag-out (A-M-284)')
    st('CA_POT', source=src_f, ca_kg_d=round(s['ca'], 6), cacl2_kg_d=round(s['cacl2'], 6), cl2_kg_d=round(s['ca_cl2'], 6),
       chemistry='CaCl2 -> Ca + Cl2, 700 C', **pe['CA_POT'],
       basis='grease-thickener Ca line (AQS-DUTY-GREASE 0.1 kg/d Ca(OH)2); brine import per A-M-284')
    st('TI_CELL', source=src_f, ti_kg_d=s['ti'], tio2_kg_d=round(s['tio2'], 4), c_kg_d=round(s['c_ti'], 4),
       cl2_kg_d=round(s['cl2_ti'], 4), mg_kg_d=round(s['mg_ti'], 4), mgcl2_gross_kg_d=round(s['mgcl2_g'], 4),
       co_kg_d=round(s['co_ti'], 4), chemistry='TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL)',
       **pe['TI_CELL'], basis='dock rutile-equivalent + carbon + Mg-pot loop; A-M-284 (assay envelope on the concentrate)')
    st('MO_CELL', source=src_f, mo_kg_d=s['mo'], moo3_kg_d=round(s['moo3'], 4), c_kg_d=round(s['c_mo'], 4),
       co2_kg_d=round(s['co2_mo'], 4), chemistry='MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2 '
       '(anode gas recycled)', **pe['MO_CELL'],
       basis='dock tech-oxide import; internal chlorine loop; A-M-290 (grade envelope 95-99 % MoO3)')
    st('CR_CELL', source=src_f, cr_kg_d=s['cr'], cr2o3_kg_d=round(s['cr2o3'], 4), c_kg_d=round(s['c_cr'], 4),
       co_kg_d=round(s['co_cr'], 4), chemistry='Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2 '
       '(anode gas recycled)', **pe['CR_CELL'],
       basis='dock chromite-equivalent import; internal chlorine loop; A-M-290 (grade envelope 40-52 % Cr2O3)')
    st('FLUX_PREP', source=src_f, salt_kg_d=round(s['kroll_flux'], 4),
       basis='Kroll MgCl2-class drag-out (A-M-284); salt-flux cover for the Al-charged melt')
    # investment train: live (A-M-286)
    st('WAX_PATTERN', source=src_f, wax_kg_d=round(s['wx'], 4), makeup_kg_d=round(s['wx_mu'], 4),
       reclaim_kg_d=round(s['wx_recl'], 4), basis='1 kg wax per kg castings, 90 % reclaim (A-M-286)')
    st('SHELL_BUILD', source=src_f, shell_kg_d=round(s['sh'], 4), silica_makeup_kg_d=round(s['sh_mu'], 4),
       reclaim_kg_d=round(s['sh_recl'], 4), basis='6-dip shell 4 kg/kg castings, 87.5 % reclaim (A-M-286)')
    st('SHELL_BURNOUT', source=src_f, shell_kg_d=round(s['sh'], 4), wax_reclaim_kg_d=round(s['wx_recl'], 4),
       burned_wax_kg_d=round(s['wx_burn'], 4), T_C=900.0, basis='flash dewax + fire at 900 C (A-M-286)')
    st('INV_CAST', source=src_f, pour_kg_d=s['inv'], shell_kg_d=round(s['sh'], 4),
       basis='live melt output 2 kg/d through the fired shell (A-M-286)')
    st('SHELL_BREAK', source=src_f, castings_kg_d=s['inv'], spent_shell_kg_d=round(s['sh'], 4),
       reclaim_kg_d=round(s['sh_recl'], 4), export_kg_d=round(s['sh_mu'], 4), basis='A-M-286 knock-out split')
    # N+1 alternates: standby-zero with rated envelopes (A-M-283)
    st('VAC_IND', source=src_f, rate_kg_d=0.0, connected_kW=15.0, backup_of='IND_MELT (diverse: vacuum induction '
       'skull melt)', outage_basis='IND_MELT relining/repair outage 2 d (crucible life 20-50 heats, AQS-SIZE-FOUNDRY '
       'sec. Crucibles; AGENTS.md redundancy rule)', design_case='2 kg ISM skull melt (AQS-SIZE-FOUNDRY)')
    st('VAC_CAST', source=src_f, rate_kg_d=0.0, connected_kW=7.5, backup_of='CAST_LINE / CONT_CAST (vacuum tilt-pour)',
       outage_basis='cast-line stoppage during the VAC_IND outage window (A-M-282)')
    st('RF_HEAT', source=src_f, duty_kg_d=0.0, connected_kW=5.0, backup_of='IND_MELT (N+1 at equal melt duty)',
       outage_basis='IND_MELT coil/PSU outage; 100-400 kHz through-coil at the 10 kg crucible class (A-M-232 rating '
       'held; A-M-283 N+1 envelope)')
    st('RES_HEAT', source=src_f, rate_kg_d=0.0, connected_kW=12.0, backup_of='SHELL_BURNOUT / SINTER heating duty '
       '(resistance radiant)', outage_basis='burnout-element outage during a shell campaign (A-M-282)')
    st('COMB_HEAT', source=src_f, rate_kg_d=0.0, connected_kW=30.0, backup_of='IND_MELT (tertiary, fuel-fired '
       'C5-C10 class)', outage_basis='long IND_MELT outage with both electric alternates unavailable (A-M-282); '
       'off-gas to MET_SCRUB when energized')
    st('SINTER', source=src_f, rate_kg_d=0.0, connected_kW=8.0, backup_of='ROLL consolidation (press-and-sinter P/M '
       'route at the 0.5 kg/d powder class)', outage_basis='roll-stand outage at the powder-class lots (A-M-282)')
    st('FORGE', source=src_f, rate_kg_d=0.0, connected_kW=11.0, backup_of='ROLL (open-die press)', outage_basis='roll-'
       'stand outage at the 10 kg/d bar class (A-M-282)')
    st('EXTRUDE', source=src_f, rate_kg_d=0.0, connected_kW=15.0, backup_of='ROLL (profile press at the Al/Cu profile '
       'class)', outage_basis='roll-stand outage on profile-class lots (A-M-282)')
    st('DRAW', source=src_f, rate_kg_d=0.0, connected_kW=3.0, backup_of='ROLL (wire/rod bench at the 3 kg/d class)',
       outage_basis='roll-stand outage on wire-class lots; wire sizing stays MFG WIRE_DRAW S57 (A-M-282)')
    # polymers
    st('POLY_OLEFIN', source=src_p, feed_kg_d=round(s['poly_feed'], 6), feed='C5-C10 naphtha at the cut tank (IA-C5-POLY)',
       T_C='150-250', P_MPa='1-5', heat_W=round(s['poly_feed'] * 2.1 * 175 / 86400, 4),
       basis='AQS-SIZE-OIL-POLY POLY_OLEFIN reactor; feed heating 25->200 C at 2.1 kJ/kg K, exotherm neglected (study)')
    st('PELLET', source=src_p, pellet_kg_d=round(s['poly_feed'], 6), form='2-4 mm pellets (AQS-DES-POLY)')
    st('POWDER_RESIN', source=src_p, rate_kg_d=0.0, status_note='live via fluoro_train (Q-013 reopened on dock fluorspar, A-M-289); rates re-stamped by the fluoro stage each pass')
    st('FILM_CAST', source=src_p, rate_kg_d=0.0, status_note='live via fluoro_train (A-M-289); PVDF film rates re-stamped by the fluoro stage')
    st('POLY_STOCK', source=src_p, out_kg_d=round(s['P'], 6), to_wet_kg_d=round(s['poly_wet'], 6), to_fab_kg_d=0.0)
    fp = dict(hf_kg_d=0.5, vdf_kg_d=0.15, tfe_kg_d=0.10, pvdf_kg_d=0.14, ptfE_kg_d=0.09, source='AQS-RATE-FP-MET design case')
    for u in ('HF_GEN', 'VDF_SYN', 'TFE_SYN', 'POLY_F'):
        st(u, source=src_p, rate_kg_d=0.0, design_case=fp, status_note='live via fluoro_train (Q-013 reopened, A-M-289); rates re-stamped by the fluoro stage')
    st('POLY_COND', source=src_p, rate_kg_d=0.0, status_note='recipe waits on the digester organic assay (AQS-DES-POLY)')

    # ---- CAD stamps (X-MFG-30 pattern): params.design + params.envelope per unit, read by
    # models/mfg/foundry.py and models/mfg/polymers.py. Envelope = hold-up box grown at the class
    # minimum (the A-M-199 method: cylinder at atm_HD, +300 mm plan access, +500 mm head). The
    # melt/forming/thermal minimums and the 7000/2000 kg/m3 densities are registered (A-M-199,
    # AQS-DUTY-064); cell minimums are study values from the AQS-DUTY-072 design cases (A-M-277).
    # state: 'live' = fed machine geometry; 'standby_rated' = real equipment at a standby-zero
    # design-day rate (N+1 alternates, A-M-283). Only the POLYMERS placeholders remain (A-M-277 rev).
    HD = DR.val(s['d'], 'atm_HD')
    MIN = {'melt': (1000, 1000, 1500), 'forming': (1500, 800, 1500), 'thermal': (600, 600, 1200),   # A-M-199
           'cell': (800, 800, 1600), 'reactor': (600, 600, 1200), 'prep': (800, 600, 1200),
           'rack': (1200, 800, 1500), 'bin': (600, 400, 800)}                                       # study, this pass

    def D_hold(kg, rho, tau=1.0):
        V = kg * tau / rho
        return (4 * V / (math.pi * HD)) ** (1 / 3) * 1000 if V > 0 else 0.0

    def ebox(mn, D):
        return [int(round(max(mn[0], D + 300), -1)), int(round(max(mn[1], D + 300), -1)), int(round(max(mn[2], D * HD + 500), -1))]

    def hoop(P_MPa, D_mm):
        return round(max(3.0, P_MPa * (D_mm / 2) / (115.0 - 0.6 * P_MPa)) + 0.49, 1)   # ASME VIII-1 UG-27 class, S 115 MPa (AQS-DUTY-064 method)

    def cad(u, style, mn, D, design, state, why):
        size = ebox(MIN[mn], D)
        p = N[u]['params']; p['design'] = design; p['envelope'] = dict(size_mm=size, style=style, state=state, basis=why)
        p['sizing']['size_mm'] = size

    # foundry: live scrap-remelt train
    Dc = round(D_hold(s['charge'], 7000.0), -1); Hc = round(Dc * HD)   # the melt_charge_kg crucible at the A-M-199 melt density
    cad('IND_MELT', 'box_furnace', 'melt', Dc,
        dict(service='Cu/Fe/Zn/Al scrap + pot-metal remelt; medium-frequency coreless induction, tilt pour',
             crucible_kg=s['charge'], crucible_D_mm=Dc, crucible_H_mm=Hc, heats_d=s['heats'], connected_kW=25.0,
             peak_kW=s['kw_peak'], melt_kWh_d=round(s['e_melt'], 3),
             lining='ceramic-fibre hot face 150 mm + 4 mm CS casing (study)'),
        'live', 'A-M-199 melt class: crucible melt_charge_kg at 7000 kg/m3, H/D atm_HD, +300/+500 allowances; box furnace at the connected load')
    cad('CAST_LINE', 'line_machine', 'forming', D_hold(mix['Cu'], 7000.0, 1 / 24),
        dict(machine='permanent-mould cast line', pour_kg_d=mix['Cu'], moulds=2, table_L_mm=700),
        'live', 'A-M-199 forming class; 1 h hold-up of the Cu pour is below the class minimum')
    cad('CONT_CAST', 'line_machine', 'forming', D_hold(s['cont'], 7000.0, 1 / 24),
        dict(machine='two-strand horizontal semi-continuous caster', feed_kg_d=round(s['cont'], 4),
             billet_kg_d=mix['Fe'], ingot_kg_d=round(s['cont_stock'], 4), strands=2,
             mould='water-cooled copper (AQS-SIZE-FOUNDRY)'),
        'live', 'A-M-199 forming class; hold-up of the cont feed is below the class minimum')
    cad('ROLL', 'line_machine', 'forming', D_hold(mix['Cu'] + 10.0, 7000.0, 1 / 24),
        dict(machine='two-high bench rolling mill', rolled_kg_d=round(mix['Cu'] + 10.0, 4), rolls_D_mm=300,
             roll_L_mm=640, kWh_d=round(s['e_roll'], 4)),
        'live', 'A-M-199 forming class; hold-up of the 13 kg/d charge is below the class minimum')
    cad('STOCK_OUT', 'store_rack', 'rack', D_hold(s['stock_in'], 2000.0),
        dict(rack='three-tier bar/plate/ingot staging rack', issue_kg_d=s['K'], export_kg_d=round(s['potm'], 4),
             hold_d=1.0),
        'live', '1 d shop issue K at the 2000 kg/m3 staged-metal density (AQS-DUTY-064 METAL_STORE row; A-M-261 loop)')
    # foundry: pot cells (molten-chloride electrolysis, live on dock chloride imports)
    for u, dc in [
        ('AL_POT', dict(service='molten AlCl3-(NaCl-KCl) electrolysis cell, 700 C', chemistry='2 AlCl3 -> 2 Al + 3 Cl2',
                        feed_kg_d=round(s['alcl3'], 4), metal_kg_d=s['al'], cl2_kg_d=round(s['al_cl2'], 4),
                        I_A=pe['AL_POT']['I_A'], cell_V=pe['AL_POT']['V'], dc_kW=pe['AL_POT']['dc_kW'],
                        hold_kW=pe['AL_POT']['hold_kW'], connected_kW=math.ceil(pe['AL_POT']['kW'] + 0.5),
                        bath_T_C=700.0, anode_D_mm=75, anode_imm_mm=400, cathodes=5,
                        busbar_mm2=int(math.ceil(pe['AL_POT']['I_A'] / 1.5 / 25) * 25))),
        ('MG_POT', dict(service='molten MgCl2 electrolysis cell (Kroll Mg recycle), 700 C', chemistry='MgCl2 -> Mg + Cl2',
                        feed_kg_d=round(s['mgcl2_ret'] + s['mgcl2_mu'], 4), metal_kg_d=round(s['mg_ti'], 4),
                        cl2_kg_d=round(s['cl2_ti'], 4), I_A=pe['MG_POT']['I_A'], cell_V=pe['MG_POT']['V'],
                        dc_kW=pe['MG_POT']['dc_kW'], hold_kW=pe['MG_POT']['hold_kW'],
                        connected_kW=math.ceil(pe['MG_POT']['kW'] + 0.5), bath_T_C=700.0, anode_D_mm=50,
                        anode_imm_mm=300, cathodes=4, busbar_mm2=int(math.ceil(pe['MG_POT']['I_A'] / 1.5 / 25) * 25) or 25)),
        ('CA_POT', dict(service='molten CaCl2 electrolysis cell, 700 C', chemistry='CaCl2 -> Ca + Cl2',
                        feed_kg_d=round(s['cacl2'], 4), metal_kg_d=round(s['ca'], 4), cl2_kg_d=round(s['ca_cl2'], 4),
                        I_A=pe['CA_POT']['I_A'], cell_V=pe['CA_POT']['V'], dc_kW=pe['CA_POT']['dc_kW'],
                        hold_kW=pe['CA_POT']['hold_kW'], connected_kW=math.ceil(pe['CA_POT']['kW'] + 0.5),
                        bath_T_C=700.0, anode_D_mm=50, anode_imm_mm=250, cathodes=3,
                        busbar_mm2=int(math.ceil(pe['CA_POT']['I_A'] / 1.5 / 25) * 25) or 25)),
        ('MO_CELL', dict(service='Mo(III) molten-salt electrolysis cell with carbochlorination loop, 650 C',
                         chemistry='MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2',
                         feed_kg_d=round(s['moo3'] + s['c_mo'], 4), metal_kg_d=s['mo'], co2_kg_d=round(s['co2_mo'], 4),
                         I_A=pe['MO_CELL']['I_A'], cell_V=pe['MO_CELL']['V'], dc_kW=pe['MO_CELL']['dc_kW'],
                         hold_kW=pe['MO_CELL']['hold_kW'], connected_kW=math.ceil(pe['MO_CELL']['kW'] + 0.5),
                         bath_T_C=650.0, anode_D_mm=50, anode_imm_mm=250, cathodes=3,
                         busbar_mm2=int(math.ceil(pe['MO_CELL']['I_A'] / 1.5 / 25) * 25) or 25)),
        ('CR_CELL', dict(service='Cr(III) molten-salt electrolysis cell with carbochlorination loop, 700 C',
                         chemistry='Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2',
                         feed_kg_d=round(s['cr2o3'] + s['c_cr'], 4), metal_kg_d=s['cr'], co_kg_d=round(s['co_cr'], 4),
                         I_A=pe['CR_CELL']['I_A'], cell_V=pe['CR_CELL']['V'], dc_kW=pe['CR_CELL']['dc_kW'],
                         hold_kW=pe['CR_CELL']['hold_kW'], connected_kW=math.ceil(pe['CR_CELL']['kW'] + 0.5),
                         bath_T_C=700.0, anode_D_mm=50, anode_imm_mm=250, cathodes=3,
                         busbar_mm2=int(math.ceil(pe['CR_CELL']['I_A'] / 1.5 / 25) * 25) or 25)),
    ]:
        rho_feed = 1800.0
        cad(u, 'pot_cell', 'cell', D_hold(dc['feed_kg_d'], rho_feed, 0.5), dc, 'live',
            f'cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at '
            f'{rho_feed:.0f} kg/m3, electrodes and busbar from the Faraday current (A-M-282)')
    # foundry: Kroll train (chlorinator + retort, live)
    cad('TI_CELL', 'kroll_train', 'cell', D_hold(s['tio2'] + s['c_ti'], 1800.0, 1.0),
        dict(service='Kroll chlorinator + Mg-reduction retort train', chemistry='TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; '
        'TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL)', tio2_kg_d=round(s['tio2'], 4), c_kg_d=round(s['c_ti'], 4),
        ti_kg_d=s['ti'], mg_kg_d=round(s['mg_ti'], 4), cl2_kg_d=round(s['cl2_ti'], 4),
        mgcl2_gross_kg_d=round(s['mgcl2_g'], 4), co_kg_d=round(s['co_ti'], 4), retort_T_C=900.0,
        chlorinator_T_C=800.0, hold_kW=pe['TI_CELL']['hold_kW'], batch_kg=1.0,
        basis='batch retort campaigns at the 0.5 kg/d Ti scale'),
        'live', 'cell-class study minimum; live on the D-DOCK rutile + carbon imports with the Mg-pot loop (A-M-284)')
    # foundry: investment train (live)
    cad('WAX_PATTERN', 'bench_prep', 'prep', D_hold(s['wx'], 1000.0, 1.0),
        dict(bench='wax pattern injection bench', wax_kg_d=round(s['wx'], 4), makeup_kg_d=round(s['wx_mu'], 4),
             reclaim_kg_d=round(s['wx_recl'], 4), injector_kW=0.5, pot_L=10),
        'live', 'prep-class study minimum; live on the C19-C28 wax make-up (A-M-424) + 90 % reclaim (A-M-286)')
    cad('SHELL_BUILD', 'line_machine', 'forming', D_hold(s['sh'], 1600.0, 1.0),
        dict(machine='dip-coat + stucco rainfall shell-building booth', shell_kg_d=round(s['sh'], 4),
             silica_makeup_kg_d=round(s['sh_mu'], 4), reclaim_kg_d=round(s['sh_recl'], 4), dips=6, slurry_L=40),
        'live', 'A-M-199 forming class at the 4 kg/kg shell duty (A-M-286); 1 d slurry/flour staging at 1600 kg/m3')
    cad('SHELL_BURNOUT', 'box_furnace', 'melt', D_hold(s['sh'], 2500.0, 1.0),
        dict(service='flash-dewax + shell fire furnace, 900 C', shell_kg_d=round(s['sh'], 4),
             wax_reclaim_kg_d=round(s['wx_recl'], 4), burned_wax_kg_d=round(s['wx_burn'], 4), T_C=900.0,
             kW=0.25, condenser='wax condensate to WAX_PATTERN'),
        'live', 'A-M-199 melt class at the fired-shell duty (A-M-286)')
    cad('INV_CAST', 'line_machine', 'forming', D_hold(s['inv'], 7000.0, 1 / 24),
        dict(machine='investment casting tilt-pour station', pour_kg_d=s['inv'], shell_kg_d=round(s['sh'], 4),
             molds_per_campaign=8),
        'live', 'A-M-199 forming class; live on IND_TO_INV (A-M-286)')
    cad('SHELL_BREAK', 'line_machine', 'forming', D_hold(s['sh'], 1600.0, 1.0),
        dict(machine='vibratory shell knock-out station with reclaim sieve', spent_shell_kg_d=round(s['sh'], 4),
             reclaim_kg_d=round(s['sh_recl'], 4), export_kg_d=round(s['sh_mu'], 4), table_kW=0.4),
        'live', 'A-M-199 forming class at the spent-shell duty (A-M-286)')
    cad('FLUX_PREP', 'bench_prep', 'prep', D_hold(s['kroll_flux'], 1800.0, 2.0),
        dict(bench='salt flux cover preparation bench', salt_kg_d=round(s['kroll_flux'], 4), hopper_L=20,
             mixer_kW=0.1),
        'live', 'prep-class study minimum; live on the Kroll drag-out (A-M-284)')
    # foundry: N+1 alternates (real equipment, standby-zero design-day rate; A-M-283)
    cad('VAC_IND', 'box_furnace', 'melt', round(D_hold(2.0, 7000.0), -1),
        dict(service='vacuum induction skull melt (ISM), N+1 diverse of IND_MELT', design_case_kg=2.0,
             connected_kW=15.0, backup_of='IND_MELT', outage_d=2.0,
             duty_note='equal-duty backup of the 25 kW melt at the 2 kg ISM batch class (A-M-283)'),
        'standby_rated', 'A-M-199 melt class; N+1 rated envelope (A-M-283): real machine, standby-zero design-day rate')
    cad('VAC_CAST', 'line_machine', 'forming', D_hold(3.0, 7000.0, 1 / 24),
        dict(machine='vacuum tilt-pour casting station, N+1 of CAST_LINE', connected_kW=7.5, backup_of='CAST_LINE',
             outage_d=2.0, design_case_kg_d=3.0),
        'standby_rated', 'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    cad('RF_HEAT', 'box_furnace', 'melt', round(D_hold(s['charge'], 7000.0), -1),
        dict(service='RF preheat/hold unit, N+1 at equal melt duty of IND_MELT', connected_kW=5.0,
             backup_of='IND_MELT', outage_d=2.0, crucible_kg=s['charge'], freq_kHz='100-400',
             duty_note='equal-duty backup of the 10 kg crucible class (A-M-283; A-M-232 rating held)'),
        'standby_rated', 'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    cad('RES_HEAT', 'box_furnace', 'melt', D_hold(s['sh'] + 1.0, 2500.0, 1.0),
        dict(service='resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating', connected_kW=12.0,
             backup_of='SHELL_BURNOUT/SINTER', outage_d=2.0, T_C=900.0),
        'standby_rated', 'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    cad('COMB_HEAT', 'box_furnace', 'melt', round(D_hold(s['charge'], 7000.0), -1),
        dict(service='combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT',
             connected_kW=0.05, thermal_kW=30.0, backup_of='IND_MELT', outage_d=2.0,
             offgas='to MET_SCRUB when energized (COMB_OFFGAS)'),
        'standby_rated', 'A-M-199 melt class; N+1 rated envelope (A-M-283)')
    cad('SINTER', 'box_furnace', 'melt', round(D_hold(0.5, 3000.0), -1),
        dict(service='Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL', connected_kW=8.0,
             backup_of='ROLL', outage_d=2.0, design_case_kg_d=0.5, T_C=1300.0),
        'standby_rated', 'A-M-199 melt class at the powder-bulk density 3000 kg/m3 (study); N+1 rated envelope (A-M-283)')
    cad('FORGE', 'line_machine', 'forming', 0.0,
        dict(machine='open-die hydraulic press, N+1 former of ROLL', connected_kW=11.0, backup_of='ROLL',
             outage_d=2.0, press_t=25, ram_mm=200),
        'standby_rated', 'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    cad('EXTRUDE', 'line_machine', 'forming', 0.0,
        dict(machine='horizontal profile press, N+1 former of ROLL', connected_kW=15.0, backup_of='ROLL',
             outage_d=2.0, press_t=50, container_mm=60),
        'standby_rated', 'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    cad('DRAW', 'line_machine', 'forming', 0.0,
        dict(machine='bench wire/rod draw bench, N+1 former of ROLL', connected_kW=3.0, backup_of='ROLL',
             outage_d=2.0, bench_mm=1200, dies=6),
        'standby_rated', 'A-M-199 forming class; N+1 rated envelope (A-M-283)')
    # polymers: live polyolefin line
    Dp = max(150.0, D_hold(s['poly_feed'], 750.0))   # DN150 vessel minimum (house ABE precedent, AQS-DUTY-062)
    cad('POLY_OLEFIN', 'reactor', 'reactor', Dp,
        dict(vessel='vertical cylindrical oligomerization reactor', D_mm=150, H_mm=round(150 * HD), wall_mm=hoop(5.0, 150.0),
             T_C=250.0, P_MPa=5.0, op_window='150-250 C at 1-5 MPa (AQS-SIZE-OIL-POLY)', feed_kg_d=round(s['poly_feed'], 6),
             heat_W=round(s['poly_feed'] * 2.1 * 175 / 86400, 4), material='SA-240 316L, welded (ASME IX)'),
        'live', 'reactor-class study minimum; DN150 at 1 d hold-up of the naphtha feed at 750 kg/m3 melt density; wall by ASME VIII-1 UG-27 at 5 MPa')
    cad('PELLET', 'line_machine', 'forming', D_hold(s['poly_feed'], 500.0, 1 / 24),
        dict(machine='underwater die-face pelletizer', rate_kg_d=round(s['poly_feed'], 6), pellet_mm='2-4'),
        'live', 'A-M-199 forming class; hold-up of the resin stream is below the class minimum')
    cad('POLY_STOCK', 'store_bin', 'bin', D_hold(s['poly_feed'], 500.0),
        dict(bin='pellet tote bin', issue_kg_d=round(s['P'], 6), to_wet_kg_d=round(s['poly_wet'], 6), hold_d=1.0),
        'live', '1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (study; A-M-264)')
    # polymers: standby trains (reactors from design-case duty, formers as line machines)
    for u, design, note in [('POLY_COND', dict(vessel='condensation resin kettle', D_mm=150, H_mm=225, design_case_kg_d=0.5),
                              'reactor-class study minimum; standby envelope (recipe waits on the digester organic assay)'),
                             ('HF_GEN', dict(vessel='HF generation train', D_mm=150, H_mm=225, design_case_kg_d=0.5,
                                             material='carbon steel, dry HF service (PERRY9_MAT)'),
                              'reactor-class study minimum; standby envelope (F-blocked, Q-013)'),
                             ('VDF_SYN', dict(vessel='VDF monomer synthesis', D_mm=150, H_mm=225, design_case_kg_d=0.15),
                              'reactor-class study minimum; standby envelope (F-blocked, Q-013)'),
                             ('TFE_SYN', dict(vessel='TFE monomer synthesis', D_mm=150, H_mm=225, design_case_kg_d=0.10),
                              'reactor-class study minimum; standby envelope (F-blocked, Q-013)'),
                             ('POLY_F', dict(vessel='fluoropolymer polymerization kettle', D_mm=150, H_mm=225,
                                             design_case_kg_d=0.23, design_case='PVDF 0.14 + PTFE 0.09 kg/d'),
                              'reactor-class study minimum; standby envelope (monomers 0, Q-013)')]:
        cad(u, 'reactor', 'reactor', 150.0, design, 'standby', note)
    cad('POWDER_RESIN', 'line_machine', 'forming', 0.0, dict(machine='powder mill / classifier line', design_case_kg_d=0.15),
        'standby', 'A-M-199 forming class; standby envelope (fluoropolymer feed blocked)')
    cad('FILM_CAST', 'line_machine', 'forming', 0.0, dict(machine='cast film line'),
        'standby', 'A-M-199 forming class; standby envelope (no feed edge at Rev AC)')


def main():
    s = apply(write='--write' in sys.argv)
    out = {k: v for k, v in s.items() if k not in ('g', 'E', 'd')}
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()
