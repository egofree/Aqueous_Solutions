"""BACKUP_GEN fuel selection and fallback-fuel reserve (owner decision 2026-10-24: redundancy is the point; the generator
stays as the backup, hydrogen first, another plant fuel when hydrogen is short).

Fuel priority, modelled on the graph as BACKUP_GEN params['fuel_selection']:
  1. hydrogen, stream S45 from CRYO_H2, used whenever the store holds hydrogen. The NFPA 110 8.4.2 monthly exercise runs on it.
  2. C5-C10 cut, stream CUT-1-OUT from PROD_C5_C10, used when hydrogen is short. PROD_C5_C10 holds a reserve that is never
     shipped, sized for the edge case: the hydrogen store empty when an outage starts, the generator carrying the whole
     critical list for the critical-autonomy period (driver crit_autonomy_d, AQS-ELEC-007).
Methanol (MEOH_TANK) and digester gas are further plant fuels; neither is piped to the generator.

critical_list() is the single source of the critical-load list; docs-authority/_power_sizing.py reads it too."""
from flow_graph.param import drivers as DR
K = 'ELEC.generation-train.BACKUP_GEN.'
def critical_list(gc, d):
    """Critical loads (kW) the generator carries in an outage, from drivers and the graph (AQS-ELEC-007)."""
    crit = {'HABITATION': DR.val(d, K + 'crit_HABITATION_kW'),
            'CRYO_H2': round(gc['CRYO_H2']['params'].get('compressor_design', {}).get('P_peak_kW', 4.0), 2)}   # CRYO_H2 peak (AQS-DUTY-067)
    if 'CRYO_ASU' in gc: crit['CRYO_ASU'] = round(gc['CRYO_ASU']['continuous_kw']['value'], 2)   # AQS-DUTY-069 duty (A-M-238)
    if 'GROW_BED' in gc: crit['GROW_BED'] = DR.val(d, K + 'crit_GROW_BED_kW')
    crit['controls and instruments'] = DR.val(d, K + 'crit_controls_kW')
    return crit
def plan(gc, d, e_ex_kWh_d):
    """Daily exercise fuel by priority and the fallback reserve held in PROD_C5_C10."""
    eta_c, lhv_c = DR.val(d, K + 'eta'), DR.val(d, K + 'fuel_lhv_kWh_kg')
    eta_h, lhv_h = DR.val(d, K + 'eta_h2'), DR.val(d, K + 'h2_lhv_kWh_kg')
    aut = DR.val(d, 'crit_autonomy_d')
    crit = critical_list(gc, d); crit_kw = sum(crit.values())
    e_out = crit_kw * 24.0 * aut                                     # kWh the generator must supply in the edge case
    return dict(
        h2_kg_d=e_ex_kWh_d / (eta_h * lhv_h), cut_kg_d=0.0,
        reserve_cut_kg=e_out / (eta_c * lhv_c), reserve_h2_equiv_kg=e_out / (eta_h * lhv_h),
        crit_kW=crit_kw, outage_kWh=e_out, autonomy_d=aut, eta_cut=eta_c, lhv_cut=lhv_c, eta_h2=eta_h, lhv_h2=lhv_h)
def selection(p):
    """The fuel-selection record written on BACKUP_GEN params."""
    return [
        {'priority': 1, 'fuel': 'hydrogen', 'stream': 'S45', 'from': 'CRYO_H2',
         'rule': 'used whenever CRYO_H2 holds hydrogen; the monthly NFPA 110 exercise runs on it',
         'normal_kg_d': round(p['h2_kg_d'], 6)},
        {'priority': 2, 'fuel': 'C5-C10 cut', 'stream': 'CUT-1-OUT', 'from': 'PROD_C5_C10',
         'rule': 'used when hydrogen is short; PROD_C5_C10 keeps a reserve that is not shipped',
         'normal_kg_d': 0.0, 'reserve_kg': round(p['reserve_cut_kg'], 1),
         'reserve_basis': f"critical list {p['crit_kW']:.1f} kW x 24 h x crit_autonomy_d {p['autonomy_d']:g} d = {p['outage_kWh']:.0f} kWh, at engine efficiency {p['eta_cut']:.0%} on {p['lhv_cut']} kWh/kg; edge case: hydrogen store empty at the start of the outage"},
        {'priority': 3, 'fuel': 'methanol or digester gas', 'stream': None, 'from': 'MEOH_TANK / sanitation digester',
         'rule': 'not piped to the generator; candidates if both fuels above are short'}]
