"""Standby feed routes sized for the case that puts them in service (owner decision 2026-10-29, X-RTE, A-M-418).

A standby route carries no flow on the design day. It is finished when it carries the rate of the case that puts it in
service (its rated case), so that the tool it feeds, its source unit and its line are sized for that case. Each row of
ROUTES names the standby route, the primary route it stands in for, and the case. The rated rate is the design-day rate of
the primary route, because the tool downstream needs the same feed whichever route brings it. On the design day the route
stays at zero, which the balance keeps.

The outage a standby route covers lasts standby_outage_d days, the N+1 outage basis of the foundry melt backups (A-M-283).
A route drawn from a store makes the store hold the rated rate for that outage on top of its own holding (the hold_kg
parameter, read by docs-authority/_storage_sizing.py). A route drawn from a melt furnace makes the furnace run the extra
heats for the rated rate during the outage (the heats parameters); the furnace rating is unchanged because each heat is the
same charge, and the energy of the extra heats replaces the melt energy of the primary furnace that is out.

Batch 43 (A-M-433) extends the table to the standby and site-mode routes of the X-RTE grouped sets, each with the case that
puts it in service, and retires the routes that duplicate another route or have no source (RETIRE). A row whose rated rate is
not the rate of one primary edge names a function of the graph instead. Only a store that is named to hold the feed holds
the rated rate for the outage; a melt furnace runs the extra heats.

Run: python3 -m flow_graph.param.standby_routes"""
import json, math
from . import drivers as DR
from . import site as SITE

TAG = 'X-RTE TF (A-M-418)'
RHO_W = 1000.0           # kg/m3, fresh water at the reservoir temperature (density to 0.3 % from 4 to 30 C, NIST_WEBBOOK)
H_FG = 2.454e6           # J/kg, latent heat of water at 20 C (NIST_WEBBOOK), the basis balance.py uses for the spray charge

def _mo_anode_cl2(g, E, N, d):
    """MO_CELL electrolyses MoCl3: 1.5 Cl2 per Mo leaves the anode and is drawn back by the carbochlorination step (A-M-290)."""
    from .foundry_poly import MM as AW
    mo = float(E['MO_TO_IND']['rate']['value'] or 0)
    return mo/AW['Mo']*1.5*2*AW['Cl'], 'the MO_CELL anode chlorine, 1.5 Cl2 per Mo of MO_TO_IND'

def _hydro(g, E, N, d):
    bb = N['HYDRO_SET']['params']['backup_basis']
    return float(bb['upper_reservoir_m3'])*RHO_W, f"the full {bb['upper_reservoir_m3']:g} m3 upper reservoir in one day"

def _spray(g, E, N, d):
    kw = float(N['DRY_COOLER']['params']['rated_kW'])
    return kw*86400.0*1000.0/H_FG, f'the DRY_COOLER rated {kw:g} kW rejected by evaporation'

def _nit_vent(g, E, N, d):
    """API 2000 normal out-breathing of the nitric tank: thermal on the nominal volume plus the pump-in displacement over the
    transfer window (flow_graph/param/sizing/vent.py), held for the whole day, as air at 0 C and the site pressure."""
    from .sizing import vent as VT
    V = float(N['WS_NITRIC']['params']['design_storage']['V_nom_m3'])
    qi = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['to_unit_id'] == 'WS_NITRIC' and e.get('phase') == 'L'
             and e.get('presence') == 'present' and e['rate'].get('unit') == 'kg/d')/RHO_W/DR.val(d, 'vent_transfer_h')
    nm3_h = VT.out_breathing_Nm3_h(V, qi, DR.val(d, 'api2000_Y'))
    return nm3_h*24*SITE.air_density(0.0), f'the API 2000 out-breathing {nm3_h:.4f} Nm3/h of the {V:g} m3 tank for 24 h'

def _gen_cut(g, E, N, d):
    """BACKUP_GEN fallback fuel: the C5-C10 reserve held in PROD_C5_C10 (backup_fuel.py) burned over the critical-autonomy period."""
    res = float(N['PROD_C5_C10']['params']['genset_reserve_kg']); aut = DR.val(d, 'crit_autonomy_d')
    return res/aut, f'the {res:g} kg cut reserve over crit_autonomy_d {aut:g} d'

# (standby route, primary route it stands in for or a rate function, rated case, store holds the outage feed)
ROUTES = (
    ('STOCK_TO_WIRE_DRAW', 'S57', 'MET_MELT is out of service and copper rod from the METAL_STORE dock buffer feeds the wire drawer', True),
    ('IND_TO_ATOM', 'IA-MELT-ATOM', 'MET_MELT is out of service and the foundry melt IND_MELT pours the atomiser charge', False),
    ('CAST_TO_EXTRUDE', 'CAST_TO_ROLL', 'ROLL is out of service and the cast-line billet is extruded instead (EXTRUDE is the N+1 alternate, A-M-283)', False),
    ('EXTRUDE_TO_STOCK', 'CAST_TO_ROLL', 'ROLL is out of service and EXTRUDE sends the extruded cast-line stock to STOCK_OUT', False),
    ('VAC_IND_TI', 'METALS_TO_IND_MELT', 'IND_MELT is out of service and the titanium sponge is melted in the VAC_IND skull furnace (A-M-283)', False),
    ('VAC_TO_INV', 'METALS_TO_IND_MELT', 'IND_MELT is out of service and the VAC_IND titanium melt pours to the investment line', False),
    ('TI_CELL_CL2_TO_CRU', 'IA-CL2-MG-TI', 'the Kroll chlorinator is out of service while MG_POT runs down, and the pot chlorine goes to CRU', False),
    ('MO_CELL_ANODE_GAS_TO_CRU', _mo_anode_cl2, 'the MO_CELL carbochlorination step is out of service while the cell runs down, and its anode chlorine goes to CRU', False),
    ('IA-ESS-HYDRO-DIS', _hydro, 'ZNBR2 is lost and the reservoir discharges through the turbine over the night class hours (A-M-145)', False),
    ('IA-ESS-HYDRO-CHG', _hydro, 'after a discharge the reservoir is pumped back up on the PV surplus (A-M-145)', False),
    ('IA-DC-SPRAY', _spray, 'the site heat-rejection mode is evaporative and the cooler rejects its rated duty on spray (X-LOC-13)', False),
    ('IA-DC-EVAP', _spray, 'the site heat-rejection mode is evaporative and the sprayed water evaporates at the cooler (X-LOC-13)', False),
    ('CUT-1-OUT', _gen_cut, 'the hydrogen store is empty in an outage and BACKUP_GEN carries the critical list on the C5-C10 cut (A-M-435)', False),
    ('IA-NIT-VENT', _nit_vent, 'the nitric tank breathes out at its API 2000 normal venting rate (API2000_2020)', False),
)

# Routes retired: they duplicate another route or have no source that can ever give them flow (A-M-433)
RETIRE = {
    'DRAW_TO_STOCK': 'DRAW has no feed route, and wire is drawn by the MFG wire drawer on S57 with STOCK_TO_WIRE_DRAW as its standby',
    'SINTER_TO_STOCK': 'SINTER has no feed route, and the atomiser powder S60 goes to MFG_SHOP, its only consumer',
    'ATOM_TO_STOCK': 'the atomiser powder S60 goes to MFG_SHOP, its only consumer, so a powder stock route duplicates it',
    'COMB_OFFGAS': 'COMB_HEAT has no fuel route, so it can make no off-gas; a fuel-fired alternate needs a fuel route first (X-RTE-COMB-HEAT-FUEL)',
    'VAC_IND_TO_VAC_CAST': 'VAC_CAST has no product route, so its casting could go nowhere; the vacuum titanium melt pours to INV_CAST on VAC_TO_INV',
    'IA-N2-RET': 'the air and nitrogen header is fed by AIR_RECEIVER and holds its pressure by the receiver supply, so it never returns gas to the cold box',
    # batch 44a, gas and hydrogen routes (A-M-434)
    'IA-EW1-H2': ('the EW_1 cathode hydrogen leaves on IA-HDR-H2-01 by Faraday, so this hood stub duplicates it', 'A-M-434'),
    'IA-EW2-H2': ('the EW_2 cathode hydrogen leaves on IA-HDR-H2-03 by Faraday, so this hood stub duplicates it', 'A-M-434'),
    'IA-FC-EXH': ('the methanol cell burns its fuel completely on stoichiometric oxygen, and its products leave as water on S81 and carbon dioxide on S82, so no exhaust remains', 'A-M-434'),
    'IA-H2-AIR': ('H2_DRYER is fed only by header hydrogen on IA-HDR-H2-02, so it has no sweep air to pass; hood sweep air is kept out of the hydrogen line', 'A-M-434'),
    'IA-LEACH-ASU': ('the leach has no degasser or compressor to send dissolved gas to the cold box, and its T5 closure solves to zero', 'A-M-434'),
    # batch 44b, polymer and foundry routes (A-M-435)
    'DIGEST_TO_POLY': ('POLY_COND has no product route, so digester organics sent to it could go nowhere; the digester closes on IA-BLK-GREY, IA-BLK-CAKE and IA-BLK-GAS', 'A-M-435'),
    'GLASS_MILL_TO_DIGEST': ('the milled solids reach GLASS_DIGEST through GLASS_BURNOUT on IA-GLASS-02 and IA-GLASS-03, so a direct mill route duplicates them', 'A-M-435'),
    'SHELL_TO_GLASS': ('the reusable spent shell is reclaimed as stucco on IA-SHELL-RECLAIM, and GLASS_DIGEST has no free capacity for the fines (A-M-267), which leave on IA-SHELL-EXPORT', 'A-M-435'),
    'WAX_TO_OIL': ('the drainable wax returns to the patterns on WAX_RECLAIM_TO_PATTERN, and the wax left soaked in the shell burns in place in the burnout, so no wax remains to send to OIL_FRAC', 'A-M-435'),
    'OIL_TO_OLEFIN': ('the olefin feed is drawn as naphtha at the cut tank on IA-C5-POLY, so a fractionator draw duplicates it', 'A-M-435'),
    'POLYF_TO_PELLET': ('the fluoropolymers go to FILM_CAST and POWDER_RESIN by the demand table (A-M-289), and PELLET is the polyolefin line', 'A-M-435'),
    'SALT_TO_FLUX': ('SALT_FEED has no feed route, and the flux is the Kroll salt drag-out on IA-KROLL-FLUX', 'A-M-435'),
    'S18': ('the afterburner carbon dioxide reaches the cold box on S67 and S67B through FLUE_KO, so this claim id duplicates them', 'A-M-434'),
}

# Routes that wait on a measurement: zero until the measured value is set (listed under X-RTE-ASSAY)
WAIT = {'POLISH_TO_LI': 'X-RTE waits on assay: the lithium tenor of the polish liquor (notes/DIGESTER_LI.md) sets the lithium that LI_RECOVER can take for the LI grease thickener (A-M-429, A-M-435)'}

def design(g, d=None):
    d = d or DR.load(); od = DR.val(d, 'standby_outage_d')
    E = {e['stream_id']: e for e in g['edges']}; N = {n['unit_id']: n for n in g['nodes']}
    out = {}
    for sid, prim, case, hold in ROUTES:
        if sid not in E or E[sid].get('presence') != 'present': continue
        e = E[sid]; src = N[e['from_unit_id']]
        if callable(prim): rated, backs = prim(g, E, N, d)
        else: rated, backs = float(E[prim]['rate']['value'] or 0), f'the {prim} rate'
        row = dict(rated_kg_d=rated, outage_d=od, backs_up=backs, case=case, source=src['unit_id'])
        sz = (src.get('params') or {}).get('sizing') or {}
        if isinstance(sz, dict) and sz.get('crucible_kg'):   # a melt furnace: extra heats in the outage
            row['heats_d'] = math.ceil(((sz.get('charge_kg_d') or 0) + rated)/sz['crucible_kg']); row['heats_d_normal'] = sz.get('heats_d')
        elif hold:                  # a store: hold the rated feed for the outage
            row['hold_kg'] = rated*od
        out[sid] = row
    return out

def tf(g, d=None):
    r = design(g, d); E = {e['stream_id']: e for e in g['edges']}
    for sid, row in r.items():
        e = E[sid]
        p = dict(rate_normal_kg_d=0.0, rate_rated_kg_d=round(row['rated_kg_d'], 4), rated_case=row['case'], backs_up=row['backs_up'],
                 outage_d=row['outage_d'], basis='A-M-418; A-M-433; flow_graph/param/standby_routes.py')
        if 'hold_kg' in row: p['hold_kg'] = round(row['hold_kg'], 4)
        if 'heats_d' in row: p.update(source_heats_d_normal=row['heats_d_normal'], source_heats_d_in_outage=row['heats_d'])
        e['params'] = p
        e['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study',
                     'note': f"{TAG}: zero on the design day; rated {row['rated_kg_d']:.4f} kg/d ({row['backs_up']}) when {row['case']}, for {row['outage_d']:g} d (standby_routes.py)."}
    for sid, why in WAIT.items():
        if sid in E and E[sid].get('presence') == 'present':
            E[sid]['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': why + '.'}
    for sid, why in RETIRE.items():
        why, am = why if isinstance(why, tuple) else (why, 'A-M-433')
        if sid in E:
            e = E[sid]; e['presence'] = 'retired'
            e['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': f'X-RTE retired 2026-10-30 ({am}): {why}.'}
    return r

if __name__ == '__main__':
    import os
    R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    g = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
    print(json.dumps(design(g), default=str))
