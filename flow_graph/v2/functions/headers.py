"""The header and bus sizing family (family migration; reference writer
flow_graph/param/headers.py `--write`, ledger row `sizing_headers`, section B,
MIXED: split sizing -> this function, the sizing doc HEADERS.md
(docs-authority/sizing/HEADERS.md, AQS-DUTY-075) -> the renderer lane). The
eight header-class units - the gas headers HDR_H2, HDR_O2, HDR_N2, HDR_CO2,
the water headers HDR_UPW and Q4_BUS, the pyrolysis NCG header and the
afterburner flue junction. Bore from the concurrent design flow at the
velocity limit (PERRY9 sec. 6: d = sqrt(4 Q / (pi v)); gas 8 m/s, water
1.5 m/s, flue 8 m/s - drivers), not below the service minimum (gas DN25 to
seat take-off valves and instruments, water DN25, flue DN100 for draft and
condensate drainage - A-M-303/A-M-304); manifold length = the longest routed
run among the header's present lines (route refinements retired with the
auto-router 2026-10-27), volume and holdup from bore x length; material per
service under AQS-STD-002 (the O2 header oxygen-clean per ASTM_G93); the
reservation cross-section covers the largest issued branch hardware
(AQS-PIP-004). Q4_BUS flow follows the ladder rule: the winter concurrent
case (life + HX-9 + HX-10 + GHEX recharge + MAU_HX coil) on the loop swing
(driver heat_loop_dT_K; AQS-HEAT-LADDER-001). No rates change on the graph.
The committed graph carries every field this family stamps; that committed
state is the golden this module reproduces.

Grid doctrine (owner ruling 2026-11-15): driver and seed values cross the
boundary through dec() (the exact Decimal of the decimal repr); quantise
points emit through book()/unbook() - the integer count of 10^-dp units,
half-even, with the dimension and scale cited at every call. The DN ladder
and its DN-minus-8 clearance (the Sch 40/SDR class bore table) run as native
integers, as do the connections census and the modelled layout length.
Dimensionless and physical constants port as integer scaled pairs or exact
decimal strings: 86400 s/d (the 24 h day), 1000 mm/m and 1000 W/kW, the
EN-rounded OD series (213/10 mm ... 1143/10 mm), R_GAS 8.314462618 J/(mol K)
[CODATA2018], 273.15 K absolute-zero offset, and the shell molar masses.
No float literals; the lint holds this.

THE RAW-FLOAT DESIGN BOOKS. v1 stored params.design as its own rounded
float chain - the concurrent flow and stream at 6 dp, the required bore at
1 dp, volume at 4 dp, holdup at 2 dp, then the writer's blanket 4 dp store
over every float - and the chain behind it runs through sqrt, pi and the
site atmosphere. An exact-Decimal book floats a ulp away from the committed
repr and would read as an edit on every raw field, so - the foundry-family
precedent (flow_graph/v2/functions/foundry.py, module docstring) - the
stored design numerics stay v1 float books: float replicas of the reference
writer's expressions over the same boundary inputs, constants entering as
floats of their exact decimals by flo(), every quantise point through
book()/unbook(), whose float path converts through the exact binary value
(Fraction) so it is Python round()'s own tie rule - the rounding the v1
writer used. The exact-Decimal audit books of the same chain (the
velocity-limit bore identity, the Q4_BUS duty book, the volume and holdup
identities) live in the family test as independent re-derivations.

Disposition of the chains around this family (the strangler bridge):
- ISO_SHEETS.csv (docs-authority/iso/ISO_SHEETS.csv, the placement_routes
  product; the route source retired with the auto-router rejection): the v1
  read is dead code (`if False and os.path.exists`), so the only branch that
  ever ran is the empty-route default - manifold length = the
  hdr_run_default_m driver (A-M-306). Ported as an inputs-declared payload:
  inputs['iso_sheets'] may carry the sheet rows ({'line', 'route_m'}); when
  absent or empty the function takes the v1 default branch. No file is
  opened.
- The branch-hardware schedule (docs-authority/nozzles/<unit>.csv, the
  nozzle_sched product the v1 writer opened exists-guarded for the
  reservation cross-section) ports as inputs['nozzles'] ({unit: [size
  strings]}); a unit absent from the payload takes the v1 absent-file branch
  - the cross-section covers the manifold OD alone. No file is opened.
- SITE PROFILE: the air-class density (HDR_N2 and HDR_O2, at the A-M-384
  header gas temperature driver) comes from inputs['site_profile'] (the
  geo_loop-family idiom): the open-air branch (ideal gas at the profile
  atmosphere) and the shell branch (process pressure from
  shell_pressure_kPa, molar mass from the shell composition) both port.
- params.size_note on AFTERBURNER_FLUE: the v1 writer stamped it, but the
  CAD envelope read-back re-stamps the study envelope note later in the pass
  and the committed graph carries that - one writer per field: the flue
  junction's design book is this family's; its envelope note is not (the
  geo_loop-family precedent).
- params.size_mm[0], the modelled segment length, is layout state: read from
  the seed, carried through unchanged as an integer book; a seed without
  size_mm takes the v1 2000 mm default.
A solve without the driver payload or the profile records nothing, so the
bridge solve and the check stay byte-faithful to the seed.
"""
import math
from decimal import Decimal
from fractions import Fraction

from flow_graph.v2.registry import fn

STAGES = 'sizing_headers'                                      # ledger row, section B
TAG = 'header sizing (flow_graph/param/headers.py, AQS-DUTY-075)'
HD = 'HDR.headers-train.'                                      # the header sizing driver prefix (U4b)
REF_BORE = 'PERRY9'                                            # d = sqrt(4Q/(pi v)), sec. 6
REF_RES = 'AQS-PIP-004'
F0 = Decimal(0)


def dec(value):
    """A v1 float/int/str -> exact Decimal at the boundary (decimal repr)."""
    return Decimal(str(value))


def flo(value):
    """The documented float-lane conversion: the float of an exact book or
    decimal - identical bits to the JSON literal it came from."""
    if isinstance(value, Fraction):
        return value.numerator / value.denominator
    return float(str(value))


def book(x, dp, cite):
    """The integer book: exact value -> count of 10^-dp units, half-even.
    A float input converts through its exact binary value, so this is Python
    round()'s own tie rule - the rounding the v1 writer used at this point.
    `cite` names the dimension and the schema scale at the call site."""
    if isinstance(x, (float, Decimal)):
        x = Fraction(x)
    m = 10 ** dp
    a, b = x.numerator * m, x.denominator
    sign = -1 if a < 0 else 1
    q, r = divmod(abs(a), b)
    if 2 * r > b or (2 * r == b and q % 2 == 1):
        q += 1
    return sign * q


def unbook(cnt, dp):
    """Render an integer book count as the exact JSON number of its decimal
    (no signed zeros - the v1 design book carries none)."""
    f = float(Decimal(cnt) / (Decimal(10) ** dp))
    return float(0) if f == 0 else f


DAY_S = 86400                                                  # s/d: the 24 h design day (24x60x60)
MM_PER_M = 1000                                                # mm/m: the bore book (ID grid)
W_PER_KW = 1000                                                # W/kW: the duty -> flow book
K0 = flo('273.15')                                             # K, absolute zero (ideal-gas law)
R_GAS = flo('8.314462618')                                     # J/(mol K) [CODATA2018]
SHELL_M = {'N2': flo('28.0134'), 'O2': flo('31.9988'),          # kg/kmol [CODATA2018]
           'Ar': flo('39.948'), 'CO2': flo('44.0095')}
DN_LIST = (15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500)
ID_OF = {dn: dn - 8 for dn in DN_LIST}                         # Sch 40/SDR class bores, DN-minus-8, mm
DN_OD = {'DN15': flo('21.3'), 'DN20': flo('26.9'), 'DN25': flo('33.7'), 'DN32': flo('42.4'),
         'DN40': flo('48.3'), 'DN50': flo('60.3'), 'DN65': flo('76.1'), 'DN80': flo('88.9'),
         'DN100': flo('114.3')}                                # EN-rounded OD series, B36.19M/B36.10M
LAY_MM = 2000                                                  # the v1 default modelled segment, mm
CITE_FLOW = 'mass-flow kg/s: the concurrent flow book at 6 dp (the v1 design rounding)'
CITE_Q = 'volume-flow m3/s: the stream book at 6 dp (the v1 design rounding)'
CITE_BORE = 'length mm: the velocity-limit required bore at 1 dp (PERRY9 sec. 6, d = sqrt(4Q/(pi v)))'
CITE_VOL = 'volume m3: the manifold volume book at 4 dp (bore x length)'
CITE_HOLD = 'mass kg: the standing holdup book at 2 dp (volume x density)'
CITE_STORE = 'the design book blanket 4 dp store (the schema scale the writer applied to every float)'
CITE_LENGTH = 'length mm: the modelled segment length, the layout book (carried through)'
CITE_CROSS = 'length mm: the reservation cross-section book at 1 dp (AQS-PIP-004)'

# unit: (service, kind, min DN key, velocity key, density kg/m3 key or Q4_BUS marker, material, mode)
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
RESERVATION = ('HDR_H2', 'HDR_N2', 'HDR_O2', 'HDR_CO2', 'HDR_UPW',
               'Q4_BUS', 'NCG_HEADER')                         # every header the stage reserves
BUS_DRAWS = ('HABITATION', 'LEACH_CSTR_1', 'GLASS_DIGEST', 'GEO_GHEX', 'MAU_HX')   # winter set


def _atm(prof, key):
    """A profile atmosphere entry value (the site.val('atmosphere.<key>') read)."""
    return prof['groups']['atmosphere']['entries'][key]['value']


def air_density(T_C, prof):
    """site.air_density port [A-M-384 class]: ideal gas at the profile
    atmosphere, kg/m3 (the reference writer's own float book)."""
    p = flo(dec(_atm(prof, 'pressure_Pa')))                    # Pa, external absolute
    M = flo(dec(_atm(prof, 'molar_mass_kg_kmol')))             # kg/kmol
    return p * M / 1000 / (R_GAS * (T_C + K0))


def process_air_density(T_C, prof):
    """site.process_air_density port: the shell interior where the profile
    states one (process pressure, shell-composition molar mass), else the
    external atmosphere (open-air sites have no shell entries)."""
    grp = prof['groups'].get('atmosphere') or {}
    e = (grp.get('entries') or {}).get('shell_composition_mole_fraction')
    if e:
        M = sum([x * SHELL_M[gas] for gas, x in e['value'].items() if gas in SHELL_M])
        p = flo(dec(grp['entries']['shell_pressure_kPa']['value'])) * 1000   # kPa -> Pa
        return p * M / 1000 / (R_GAS * (T_C + K0))
    return air_density(T_C, prof)


def flow_book(b, uid, mode):
    """The v1 _flow_kg_s port: the concurrent design flow through the header,
    summed in edge-list order. Gas headers: the larger of total in and total
    out (all drops can run at once at the bounding assay). Q4_BUS: the winter
    concurrent branch sum. Returns (unit, value)."""
    kg_d = 0
    for e in b.data['edges']:
        if e.get('presence') != 'present' or (e.get('rate') or {}).get('unit') not in ('kg/d', 'kW'):
            continue
        if mode == 'Q4_BUS' and e['from_unit_id'] == uid and e['to_unit_id'] in BUS_DRAWS:
            kg_d += flo(dec(e['rate'].get('value') or 0))      # kW branches, winter set
    if mode == 'Q4_BUS':
        return 'kW', kg_d                                      # thermal duty; converted below
    tin = 0
    tout = 0                                                   # steady state: the larger side governs
    for e in b.data['edges']:
        if e.get('presence') == 'present' and (e.get('rate') or {}).get('unit') == 'kg/d' \
                and uid in (e['from_unit_id'], e['to_unit_id']):
            r = flo(dec(e['rate'].get('value') or 0))
            if e['from_unit_id'] == uid:
                tout += r
            else:
                tin += r
    return 'kg/d', max(tin, tout)


def iso_routes(inputs):
    """The ISO_SHEETS.csv payload port: longest route per line id, rows whose
    route does not parse skipped (the v1 csv.DictReader walk). An absent or
    empty payload is the committed route state - the v1 default branch (the
    source retired with the auto-router rejection)."""
    iso = {}
    for r in inputs.get('iso_sheets') or []:
        try:
            iso[r['line']] = max(iso.get(r['line'], flo(F0)), flo(dec(r['route_m'] or 0)))
        except (KeyError, TypeError, ValueError, ArithmeticError):
            pass
    return iso


def design_row(b, u, drv, prof, iso):
    """The v1 headers.design() row for one unit - the float replica (see the
    module docstring) - in the v1 key order."""
    svc, kind, mink, velk, rhok, mat, mode = SPEC[u]
    _unit, x = flow_book(b, u, mode or kind)
    duty = None
    if kind == 'liquid':
        if mode == 'Q4_BUS':                                   # kW -> kg/s on the loop swing
            cp = flo(dec(drv[HD + 'hdr_cp_water_kJ_kgK']['value']))   # kJ/kg K, IAPWS_IF97
            dT = flo(dec(drv['heat_loop_dT_K']['value']))             # K, AQS-HEAT-LADDER-001
            m = x * W_PER_KW / (cp * W_PER_KW * dT) if x else flo(F0)
            duty = x
        else:
            m = x / DAY_S
        rho = drv[HD + 'hdr_rho_water']['value']               # as written (int book stays int)
    else:
        m = x / DAY_S
        rho = process_air_density(flo(dec(drv[HD + 'hdr_air_T_C']['value'])), prof) \
            if rhok == 'hdr_rho_air' else drv[HD + rhok]['value']
    Q = m / rho                                                # m3/s at header conditions
    vel = flo(dec(drv[HD + velk]['value']))                    # m/s, the velocity limit
    id_req = math.sqrt(4 * Q / (math.pi * vel)) * MM_PER_M if Q else flo(F0)
    min_dn = int(dec(drv[HD + mink]['value']))                 # service minimum, A-M-303/A-M-304
    dn = next(d for d in DN_LIST if ID_OF[d] >= max(id_req, flo(F0)) and d >= min_dn)
    runs = [iso[e['stream_id']] for e in b.data['edges'] if e.get('presence') == 'present'
            and u in (e['from_unit_id'], e['to_unit_id']) and e['stream_id'] in iso
            and (e.get('rate') or {}).get('unit') in ('kg/d', 'kW')]
    L = max(runs) if runs else drv[HD + 'hdr_run_default_m']['value']   # A-M-306 fallback
    i_d = ID_OF[dn] / MM_PER_M                                 # m, the class bore on the DN grid
    vol = math.pi * i_d * i_d / 4 * L
    return dict(service=svc, kind=kind, flow_kg_s=unbook(book(m, 6, CITE_FLOW), 6), duty_kW=duty,
                rho_kg_m3=rho, Q_m3_s=unbook(book(Q, 6, CITE_Q), 6), v_m_s=vel,
                id_req_mm=unbook(book(id_req, 1, CITE_BORE), 1), DN=dn, length_m=round(L, 1),
                volume_m3=unbook(book(vol, 4, CITE_VOL), 4), material=mat,
                hold_kg=unbook(book(vol * rho, 2, CITE_HOLD), 2),
                connections=sum(1 for e in b.data['edges'] if e.get('presence') == 'present'
                                and u in (e['from_unit_id'], e['to_unit_id'])
                                and (e.get('rate') or {}).get('unit') in ('kg/d', 'kW')))


def blanket4(row):
    """The v1 write() store: every float of the design book quantised at
    4 dp (the schema scale); ints, strings and None as written."""
    return {k: (unbook(book(x, 4, CITE_STORE), 4) if isinstance(x, float) else x)
            for k, x in row.items()}


def reservation_books(b, u, row, sizes):
    """The v1 write() reservation port: the modelled manifold segment keeps
    its study length; the cross-section is the larger of the sized manifold
    OD and the largest branch OD the issued schedule carries (the EN-rounded
    millimetre OD series, ASME B36.19M/B36.10M). Returns (size_mm, note,
    basis)."""
    branch = [flo(F0)] + [DN_OD.get(s, flo(F0)) for s in (sizes or [])]
    cross = unbook(book(max(DN_OD.get('DN' + str(row['DN']), flo(F0)), max(branch)), 1, CITE_CROSS), 1)
    prev = (b.nodes[u].get('params') or {}).get('size_mm')
    length_mm = book(flo(dec((prev or [LAY_MM])[0])), 0, CITE_LENGTH)
    basis = (f'{TAG}: manifold DN{row["DN"]} segment (modelled length {length_mm} mm, layout) with the '
             f'cross-section covering the largest issued branch hardware ({cross:g} mm, EN-rounded '
             'OD series, AQS-PIP-004)')
    note = f'DN{row["DN"]} manifold x {row["length_m"]:.0f} m run ({row["volume_m3"]:.3f} m3), {TAG}'
    return [length_mm, cross, cross], note, basis


def _prov(basis, ref=None):
    from flow_graph.v2.model import Prov
    return Prov(STAGES, basis, ref)


def _set(b, uid, path, value, basis, ref=None):
    b.set_node_field(uid, path, value, _prov(basis, ref))


@fn('headers_bore', 'AQS-DUTY-075 header-class units: bore from the concurrent design flow at the velocity '
    'limit (PERRY9 sec. 6, d = sqrt(4Q/(pi v))), not below the service minimum (A-M-303/A-M-304), '
    'reservation cross-section per AQS-PIP-004; no rates change')
def headers_bore(b, inputs):
    drv = inputs.get('drivers')
    prof = inputs.get('site_profile')
    if drv is None or prof is None:
        return                                                 # the bridge contract: no payload, no stamps
    missing = [u for u in SPEC if u not in b.nodes]
    assert not missing, f'headers_bore: the seed lacks header-class units {missing} (builder topology)'
    iso = iso_routes(inputs)
    nozzles = inputs.get('nozzles') or {}
    basis = ('AQS-DUTY-075 header sizing (flow_graph/param/headers.py port): bore from the concurrent '
             'design flow at the velocity limit (PERRY9 sec. 6, d = sqrt(4Q/(pi v))), not below the service '
             'minimum (gas/water DN25 A-M-303, flue DN100 A-M-304); densities at header conditions '
             '(NIST_WEBBOOK class, air class A-M-384 at the hdr_air_T_C driver, NCG and flue A-M-305); '
             'manifold run per A-M-306, route refinements retired with the auto-router 2026-10-27')
    q4_basis = basis + '; Q4_BUS flow on the AQS-HEAT-LADDER-001 winter concurrent case (life + HX-9 + ' \
        'HX-10 + GHEX recharge + MAU_HX coil) over the heat_loop_dT_K loop swing'
    res_basis = ('AQS-PIP-004 reservation (flow_graph/param/headers.py port): the modelled manifold segment '
                 'keeps its layout length; the cross-section covers the larger of the sized manifold OD and '
                 'the largest branch OD the issued nozzle schedule carries (EN-rounded OD series, ASME '
                 'B36.19M/B36.10M)')
    for u in SPEC:
        row = blanket4(design_row(b, u, drv, prof, iso))
        _set(b, u, 'params.design', row, q4_basis if u == 'Q4_BUS' else basis, REF_BORE)
        if u in RESERVATION:
            size_mm, note, r_basis = reservation_books(b, u, row, nozzles.get(u))
            _set(b, u, 'params.size_note', note, res_basis, REF_RES)
            _set(b, u, 'params.size_mm', size_mm, res_basis, REF_RES)
            _set(b, u, 'params.size_basis', r_basis, res_basis, REF_RES)
