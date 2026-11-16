"""engine v2: the duty-sheet documentation wave (ledger section E, the doc
half of the `duty_basis` row - the manifest's largest doc producer).

Reference writer: docs-authority/_duty_basis.py. That stage is not a
whole-document generator. Every committed duty sheet is a hand-authored page
that the stage patches in place each run: the section 1 basis line is
re-rendered from the graph, the section 3 material line where it still
carries a default template, the envelope-hours fragment, the section 7
manufacturing pointer, and - for the nodes carrying a solved hvac or
cycling_thermal block - the whole section 2. A separate author() template
creates a sheet when none exists. The committed pages sit at that patch
fixpoint and carry hand/historical text the graph does not hold: the
`Graph Rev` header line frozen at authoring time (the patch path never
touches it), manufacturing-pointer suffix variants, hand-rewritten envelope
tails, and per-unit sections 4, 5 and 8. Verified at port time against the
committed census: author(current graph) reproduces zero committed pages, and
the generator's own fragments reproduce byte-exactly (section 1 on every
graph unit with a sheet, the issued section 3 lines, the hvac section 2, the
cycling_thermal section 2, and the envelope bullet where the node stamp and
page agree). The renderer registry's contract is byte-exact equality with
the committed file, so DOCS registers no whole page yet; the composer lane
that later declares the hand base text as data and stitches these generated
sections onto it registers there, and flow_graph/v2/test_render_duties.py
enforces byte-exactness for every DOCS entry automatically.

What migrated - the generator's generated content as pure functions over the
model (the seed carries every book; the v1 hidden reads enter as explicit
arguments instead of file I/O):

- render_section1(m, uid): the section 1 basis line, byte-exact on every
  graph unit with a committed sheet;
- render_duty_string(m, uid): the params.duty prefix the stage refreshes (in
  memory only, per the v1 comment, so three of the four committed node
  fields still carry older graph-lane values; EXT_HALL is at the fixpoint);
- render_envelope_line(m, uid): the section 2 envelope bullet (author
  template shape), byte-exact where the page and the node stamp agree;
- render_material_line_issued(m, uid): the section 3 line rendered from
  params.sec3_material (X-MAT-22), byte-exact on every unit that carries one;
- render_material_line_graph(m, uid): the section 3 default-template
  replacement line (X-MAT-06), byte-exact on every page the patch converged;
- render_hvac_section2(m, uid): the whole section 2 for a node with a solved
  hvac block (X-PAR-07/X-PAR-08), byte-exact on EXT_HALL;
- render_cycling_section2(m, uid, seed_block_mm): the whole section 2 for a
  node with a solved cycling_thermal block (X-THM-01 F-4), byte-exact on
  ZNBR2; seed_block_mm is the placement-seed block size (the v1 hidden read,
  injected);
- render_author_sheet(m, uid, facts): the create-lane AQS-STD-001 template,
  ported exactly; facts carries the sorted instrument loops, the STL
  existence flag and the manufacturing module name - the v1 function's
  hidden environment reads (INSTRUMENT_INDEX.csv, cad/stl and models/mfg
  globs), injected;
- FRAGMENTS(m, sheets, envelope_pages, placement_seed): the fragment
  registry - (page path, fragment id, render closure) per generator-owned
  fragment - the content rule flow_graph/v2/check.py holds against the
  hand-authored pages (each fragment must OCCUR in its page's bytes);
- apply_patch(page_text, fragment_text, fragment_id): the v1 patch idioms
  (the line and section-span replaces), the update-side of that rule.

REMAINING below is the explicit census of committed sheets not ported as
whole-page renderers: all of them, for the structural reason above. The
engine lint (flow_graph/v2/lint.py) walks the whole v2 package including
render/, so this module holds the discipline: no I/O, no float literals,
and `re` (a pure text transform) as its only import.
"""
import re


# Un-ported pages (the byte-exact whole-document census): every committed
# sheet in docs-authority/duties/. None is reproducible byte-exactly from the
# model and inputs alone - see the module docstring. The composer lane
# registers a page here as it lands.
REMAINING = [
    'ABE', 'ACETOX', 'ACEX', 'ACID_PLANT', 'ACID_POLISH_SCRUB', 'ADS_CHILL', 'AFTERBURNER',
    'AFTERBURNER_FLUE', 'AIR_RECEIVER', 'ALD', 'ALK_SCRUBBER', 'AL_POT', 'AMF', 'ANIMAL_PEN',
    'AQUA_TANK', 'AQUA_UV', 'ASH', 'ATMOS', 'AZOLLA', 'AZOLLA_BED', 'BACKUP_GEN', 'BAGHOUSE',
    'BEES', 'BEE_HIVE', 'BIOFILTER', 'BLACK_DIGEST', 'BLOW_MOLD', 'BMED_ACID', 'BMED_BASE',
    'BMED_UPW_POLISH', 'BOARD_MILL', 'BOUNDARY_EXPORT', 'BRINE_CRYS', 'BSFL', 'BSFL_BIN',
    'BUCL', 'BUOH_STILL', 'C29_RECYCLE', 'CAST_LINE', 'CATCH_TANK', 'CA_POT', 'CHICKENS',
    'CHICKEN_COOP', 'CLARIFIER', 'CLOVER', 'COLD_MILL', 'COMB_HEAT', 'COMMON_AREA', 'COMPOST',
    'COMPOST_MYC', 'COMPOST_TOILET', 'CONTINUOUS_RECYCLE', 'CONT_CAST', 'CRAYFISH', 'CROP_ALLIUM',
    'CROP_BASIL', 'CROP_CUCUMBER', 'CROP_KALE', 'CROP_LETTUCE', 'CROP_PEPPER', 'CROP_ROSEMARY',
    'CROP_SPINACH', 'CROP_TOMATO', 'CRU', 'CRYO_AHU', 'CRYO_AHU_COND_CONDENSABLE', 'CRYO_AR',
    'CRYO_ASU', 'CRYO_CO2', 'CRYO_DED_COOL', 'CRYO_H2', 'CRYO_HE', 'CRYO_HX_Q4', 'CRYO_KR',
    'CRYO_N2', 'CRYO_NE', 'CRYO_O2', 'CRYO_XE', 'CR_CELL', 'CURTAIL', 'DIGESTER', 'DRAW',
    'DRY_COOLER', 'DUAL_ROOT', 'DUCKWEED', 'DUCK_PEN', 'ELECTRODE_COAT', 'EMETH', 'ETOH_STILL',
    'EVAP_ACID', 'EVAP_ACID_VS', 'EVAP_BASE', 'EW_1', 'EW_2', 'EW_3', 'EW_4', 'EW_5', 'EW_6',
    'EW_7', 'EW_8', 'EW_9', 'EXPANDER', 'EXTRUDE', 'EXT_HALL', 'FAB_UPW_TANK', 'FEED_PREP',
    'FILM_CAST', 'FISH', 'FISH_SUMP', 'FLOAT_SINK', 'FLUE_KO', 'FLUX_PREP', 'FOOD_STORE',
    'FORGE', 'FORM', 'FRUIT_GUTTER', 'FUEL_CELL', 'F_RECOVER', 'GALLEY', 'GAS_ATOMIZER',
    'GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP', 'GEO_ORC', 'GLASS_BURNOUT', 'GLASS_DIGEST',
    'GLASS_MILL', 'GLASS_RINSE', 'GLYOXAL', 'GOATS', 'GREASE_CA', 'GREASE_LI', 'GREY_TREAT',
    'GROWBED_A', 'GROWBED_B', 'GROW_BED', 'GW_INTAKE', 'H2O_ELYZ', 'H2_DRYER', 'H2_PURIFIER',
    'HABITATION', 'HAB_GALLEY', 'HAB_MED', 'HAB_SLEEP', 'HAB_WASH', 'HDR_CO2', 'HDR_H2',
    'HDR_N2', 'HDR_O2', 'HDR_UPW', 'HEAT_SINK', 'HF_GEN', 'HNO3', 'HOPPER', 'HTC', 'HX8',
    'HYDRO_SET', 'IMID', 'IND_MELT', 'INV_CAST', 'IODIDE', 'LEACH_CSTR_1', 'LIGNO_PRE',
    'LITHO_ALIGN', 'LITHO_COAT', 'LITHO_DEV', 'LITHO_STUB', 'LI_RECOVER', 'LOAD_AGG',
    'MAU_HX', 'MEAM', 'MEDICAL', 'MEOH_COND', 'MEOH_FC', 'MEOH_FERM', 'MEOH_SYNTH',
    'MEOH_TANK', 'METAL_STORE', 'MET_AHU', 'MET_HX_Q4', 'MET_MELT', 'MET_SCRUB', 'MET_SYN',
    'MFG_SHOP', 'MG_POT', 'MISTER', 'MO_CELL', 'MUSHROOM', 'MUSH_BLOCK', 'MUSH_STRAW',
    'NAOH_PLANT', 'NCG_HEADER', 'NFIX_BED', 'NFT', 'NORTH_DOCK', 'NOX_SCRUB', 'NUTRIENT_DOSE',
    'NUT_AN', 'OIL_DRYER', 'OIL_FRAC', 'OIL_PYRO', 'PEANUT', 'PELLET', 'POLISH_BANK',
    'POLY_COND', 'POLY_F', 'POLY_FIBER', 'POLY_OLEFIN', 'POLY_STOCK', 'POWDER_RESIN',
    'PROD_C11_C18', 'PROD_C19_C28', 'PROD_C29', 'PROD_C5_C10', 'PROD_MEOH', 'PROD_O2',
    'PV_ARRAY', 'P_CA', 'Q1_A', 'Q1_B', 'Q2_A', 'Q2_B', 'Q3_A', 'Q3_B', 'Q4_A', 'Q4_B',
    'Q4_BUS', 'QUAIL_CAGE', 'QUAT', 'RABBIT_HUTCH', 'RECTIFIER', 'RECT_EW', 'REC_DAYROOM',
    'REE_RECOVER', 'RELIEF_CRYO', 'RELIEF_H2', 'REMIN', 'RESIST_SYN', 'RES_HEAT', 'RF_HEAT',
    'ROLL', 'ROOF_TANK', 'S13_CLASS_TREAT', 'SALT_FEED', 'SEED_BANK', 'SHELL_BREAK',
    'SHELL_BUILD', 'SHELL_BURNOUT', 'SIC_FURNACE', 'SINTER', 'SI_REDUCE', 'SI_REFINE',
    'SLEEP_QUARTERS', 'SOLAR_PV_CELL', 'SOLV_PLANT', 'SOL_ARK_60K', 'STOCK_OUT', 'STRUVITE',
    'SUNFLOWER', 'TERRACE_IRRIG', 'TFE_SYN', 'TI_CELL', 'VAC_CAST', 'VAC_IND', 'VCD_TRAIN',
    'VDF_SYN', 'VEG_BED', 'VERMI_BIN', 'WAFER_FAB', 'WASHROOM', 'WAX_PATTERN', 'WET_BENCH',
    'WIRE_DRAW', 'WORMS', 'WS_AMMONIA', 'WS_DOPE', 'WS_HF_ED', 'WS_KOH', 'WS_NITRIC',
    'WS_PEROX', 'WS_PHOS', 'WS_SLURRY', 'WS_SOLV', 'YEAST', 'ZNBR2', 'ZNBR2_BR2_REGEN',
]

# The whole-page registry entries. Empty: no duty sheet is byte-exactly
# renderable yet (hand-authored base text the graph does not carry - see the
# module docstring). Each future entry is (repo-relative path, render fn) and
# is held to byte-exact equality with the committed file by
# flow_graph/v2/test_render_duties.py, exactly like the sizing wave.
DOCS = []

# Envelope pages whose section 2 bullet is historical hand/page state and is
# therefore not a live fragment: the node stamp moved on after the page was
# authored (stale dimensions or volume print), the tail was hand-rewritten
# ('The box is the machine.', 'No mass throughput...', 'Flow ... is
# circulation.', the working-volume shell prose of the MeOH/water train
# pages), or the page predates the tail template. The v1 patch idiom
# never rewrites dimensions or hand text on these, so a fragment here would
# demand a patch v1 cannot perform - they are skipped, not checked.
ENVELOPE_SKIP = frozenset((
    'H2O_ELYZ', 'MEOH_COND', 'MEOH_FERM', 'MEOH_TANK', 'NOX_SCRUB', 'REMIN',
    'RELIEF_CRYO', 'VCD_TRAIN', 'WS_PHOS', 'GLASS_RINSE', 'GLASS_MILL', 'GLASS_BURNOUT',
    'LITHO_COAT', 'LITHO_ALIGN', 'LITHO_DEV', 'LITHO_STUB',
    'ELECTRODE_COAT', 'BLOW_MOLD', 'SOLAR_PV_CELL', 'GREASE_CA', 'P_CA', 'SI_REDUCE',
    'PROD_MEOH', 'FOOD_STORE', 'BIOFILTER', 'BEE_HIVE',
))


def FRAGMENTS(m, sheets, envelope_pages, placement_seed):
    """The fragment registry: (repo-relative page path, fragment id, render
    closure) for every generator-owned fragment of every duty page - the
    content rule the staleness check holds against the hand-authored pages.

    A factory, not a static list, because the census is graph-derived: the
    units come from the model and the I/O-side facts gate the kinds, so a
    new unit or stamp gains its fragment without this file being edited.
    Arguments are the facts the v1 stage read around its I/O boundary:
    - sheets: the committed sheet ids (docs-authority/duties/*.md); a unit
      without a sheet is a placeholder and keeps no fragments (the v1 rule);
    - envelope_pages: ids whose page carries the envelope bullet at all; the
      v1 patch idiom refreshes the bullet's hours in place and never adds a
      bullet, so a page predating its node stamp is not a live fragment;
    - placement_seed: the seed's {unit_id: block} records (the v1 hidden
      read), bound into the cycling fragment closure.

    Each closure takes (model, inputs) - the sizing-renderer payload
    convention - and returns the fragment bytes. Excluded by rule, not by
    oversight: the one-time section 3 default-template replacement (the v1
    patch fires only while the page line still carries a default, so a
    converged page freezes by design and is not re-rendered), the section 7
    pointer (append-once, page-state keyed), and render_duty_string (a graph
    field, not page content).
    """
    entries = []

    def bind(fn, *args):
        return lambda mm, ii: fn(mm, *args).encode('utf-8')

    for uid in sorted(m.nodes):
        if uid not in sheets:
            continue                                        # placeholder unit: v1 keeps no sheet
        page = 'docs-authority/duties/%s.md' % uid
        entries.append((page, 'section-1', bind(render_section1, uid)))
        prm = m.nodes[uid].get('params') or {}
        if (prm.get('sec3_material') or {}).get('mat'):
            entries.append((page, 'section-3-issued', bind(render_material_line_issued, uid)))
        if (prm.get('hvac') or {}).get('total_kW') is not None:
            entries.append((page, 'section-2-hvac', bind(render_hvac_section2, uid)))
        if prm.get('cycling_thermal'):
            if uid not in placement_seed:
                raise ValueError(f'cycling fragment for {uid} needs the placement seed block')
            entries.append((page, 'section-2-cycling',
                            bind(render_cycling_section2, uid, placement_seed[uid].get('size_mm'))))
        esz = (prm.get('envelope') or {}).get('size_mm') or prm.get('size_mm')
        if esz and uid in envelope_pages and uid not in ENVELOPE_SKIP:
            entries.append((page, 'section-2-envelope', bind(render_envelope_line, uid)))
    return entries


def apply_patch(page_text, fragment_text, fragment_id):
    """The v1 patch idiom for one fragment kind, applied to a page's text:
    replace the generator-owned span with the fresh fragment, touching
    nothing else (the hand prose around it is the author's). Returns the
    text unchanged when the span the idiom anchors on is absent - an
    unpatchable page stays stale loudly, for a hand or owner decision.
    - section-1: the basis line, replaced whole (the v1 re.sub idiom);
    - section-3-issued: the material line, replaced whole;
    - section-2-hvac / section-2-cycling: the whole `2. Size.` span up to
      section 3, replaced with the rendered block (the v1 span replace);
    - section-2-envelope: the bullet line, replaced whole. On the governed
      fragment set (dimensions and volume already agree with the node stamp)
      this lands the same bytes as the v1 hours-only recompute, which it
      replaces here because the recompute reads the page's own volume."""
    if fragment_id == 'section-1':
        return re.sub(r'^1\. Basis\..*$', lambda _m: fragment_text, page_text, count=1, flags=re.M)
    if fragment_id == 'section-3-issued':
        found = re.search(r'^3\. Material\..*$', page_text, flags=re.M)
        if not found:
            return page_text
        return page_text.replace(found.group(0), fragment_text, 1)
    if fragment_id in ('section-2-hvac', 'section-2-cycling'):
        found = re.search(r'^2\. Size\..*?(?=^3\. )', page_text, flags=re.M | re.S)
        if not found:
            return page_text
        return page_text.replace(found.group(0), fragment_text, 1)
    if fragment_id == 'section-2-envelope':
        found = re.search(r'^- Envelope [\d×]+ mm, [\d.]+ m³\..*$', page_text, flags=re.M)
        if not found:
            return page_text
        return page_text.replace(found.group(0), fragment_text, 1)
    raise ValueError(f'no patch idiom for fragment {fragment_id}')


_VESSEL_ZERO = ('kettle', 'precip', 'separator', 'store')   # utilities-only nozzle file where nothing is piped (kept in step with _nozzle_sched.py)


def f4(x):
    """The v1 significant-figure scalar format."""
    return f'{x:.4g}'


def lst(es):
    """The v1 edge-list summary: the first four streams, then a count."""
    s = '; '.join(f"{e['stream_id']} {f4(e['rate']['value'] or 0)} kg/d ({e.get('carries') or e['stream_id']})" for e in es[:4])
    return s + (f'; {len(es) - 4} more' if len(es) > 4 else '') if es else 'none'


def _scalars(d, skip=()):
    """The v1 flat-scalar line: scalars only, dicts and lists skipped."""
    out = []
    for k, v in (d or {}).items():
        if k in skip or isinstance(v, (dict, list)):
            continue
        out.append(f'{k} {v if isinstance(v, (str, bool, int)) else f4(v)}')
    return '; '.join(out)


def _dot(s):
    """The v1 sentence terminator (collapse trailing dots, keep exactly one)."""
    while s.endswith('..'):
        s = s[:-1]
    return s if s.endswith('.') else s + '.'


def _ins(m, uid):
    """Present mass inlets rated kg/d, in seed (file) order - the v1 selection."""
    return [e for e in m.data['edges'] if e['to_unit_id'] == uid and e['presence'] == 'present'
            and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']


def _outs(m, uid):
    """Present mass outlets rated kg/d, in seed (file) order - the v1 selection."""
    return [e for e in m.data['edges'] if e['from_unit_id'] == uid and e['presence'] == 'present'
            and 'mass' in (e.get('layers') or []) and e['rate'].get('unit') == 'kg/d']


def _kw(n):
    """The node's continuous electrical duty book (0 when the node books none)."""
    return ((n.get('continuous_kw') or {}).get('value') or 0) if isinstance(n.get('continuous_kw'), dict) else 0


def _basis_line(ins, outs, mi, mo, kw):
    """The shared section 1 sentence (identical text in the patch path and author())."""
    return (f'1. Basis. Mass in {f4(mi)} kg/d. Mass out {f4(mo)} kg/d. '
            f'Electrical duty {kw:.4f} kW. In: {lst(ins)}. Out: {lst(outs)}.')


def render_section1(m, uid):
    """The section 1 basis line, re-rendered from the model exactly as the v1
    patch path writes it every run. Byte-exact on every graph unit with a
    committed sheet (the patch fixpoint)."""
    n = m.nodes[uid]
    ins, outs = _ins(m, uid), _outs(m, uid)
    mi = sum(e['rate']['value'] or 0 for e in ins)
    mo = sum(e['rate']['value'] or 0 for e in outs)
    return _basis_line(ins, outs, mi, mo, _kw(n))


def render_duty_string(m, uid):
    """The params.duty prefix the v1 stage refreshes each run (in memory only:
    the committed node fields land through a graph-write lane, so all but
    EXT_HALL still carry older values - render_section1 is the current basis)."""
    n = m.nodes[uid]
    mi = sum(e['rate']['value'] or 0 for e in _ins(m, uid))
    mo = sum(e['rate']['value'] or 0 for e in _outs(m, uid))
    return f'In {mi:.3f} kg/d, out {mo:.3f} kg/d, {_kw(n):.3f} kW.'


def render_envelope_line(m, uid):
    """The section 2 envelope bullet, author() shape: dimensions and volume
    from the node stamp, the hours tail only where mass flows. Byte-exact
    where the page and the node stamp agree; pages authored from an older
    stamp (or with a hand-rewritten tail) keep their historical line - the
    patch path never rewrites dimensions or hand text."""
    p = m.nodes[uid].get('params') or {}
    esz = (p.get('envelope') or {}).get('size_mm') or p.get('size_mm')
    if not esz:
        return None
    L, W, H = esz
    V = L * W * H / 1000000000                                      # the v1 1e9 as an exact int
    mi = sum(e['rate']['value'] or 0 for e in _ins(m, uid))
    tail = ''
    if mi > 0:
        tail = f' That box over this flow would be {V * 1000 / mi * 24:.1f} h if it were full. It is not a residence time.'
    return f'- Envelope {L}×{W}×{H} mm, {f4(V)} m³.' + tail


def render_material_line_issued(m, uid):
    """The section 3 line rendered from the issued selection
    (params.sec3_material, X-MAT-22); None where the node issues none."""
    s3m = (m.nodes[uid].get('params') or {}).get('sec3_material') or {}
    if not s3m.get('mat'):
        return None
    return (f"3. Material. {s3m['mat']}. Basis: {s3m['basis']} "
            f"Alternative: {s3m['alt']}. {s3m['note']} ({s3m['task']})")


def render_material_line_graph(m, uid):
    """The section 3 line that replaces a default template from the node's
    design or storage material (X-MAT-06); None where the node books no
    material. Hand-written per-unit material texts are never overwritten."""
    p = m.nodes[uid].get('params') or {}
    ds = p.get('design') or {}
    sto = p.get('design_storage') or {}
    mat = ds.get('material') or sto.get('material')
    if not mat:
        return None
    return f'3. Material. {mat} (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.'


def render_hvac_section2(m, uid):
    """The whole section 2 for a node carrying a solved hvac block
    (X-PAR-07/X-PAR-08), re-rendered from the graph every pass, trailing
    blank line included - the v1 replacement span."""
    n = m.nodes[uid]
    hv = (n.get('params') or {}).get('hvac') or {}
    ck = n.get('continuous_kw') or {}
    return (
        '2. Size.\n'
        '- Envelope and loads are solved in the graph (X-PAR-07/X-PAR-08, A-M-104, A-M-112) from the '
        'location-neutral bounding climate of AQS-SITE-002 Rev C; a site design re-solves them.\n'
        f"- Electrical, average: lighting {hv.get('light_kW', 0):.2f} kW (IECC 2021 C405, 10 % lit), ventilation "
        f"{hv.get('vent_kW', 0):.2f} kW (ASHRAE 62.1-2025), envelope service {hv.get('envelope_kW', 0):.2f} kW; "
        f"total {float(ck.get('value') or hv.get('total_kW')):.2f} kW on the bus.\n"
        f"- Thermal, average: heating {hv.get('Qh_kW', 0):.2f} kW and cooling {hv.get('Qc_kW', 0):.2f} kW after internal "
        f"gains {hv.get('gains_kW', 0):.2f} kW and slab edge {hv.get('slab_kW', 0):.2f} kW (IECC C402 F-factor); "
        'heat pumps per ASHRAE 90.1-2025 Table 6.8.1-2, loop pumping '
        f"{hv.get('pump_kW', 0):.2f} kW.\n"
        f"- Peak block load: heating {hv.get('peak_h_kW', 0):.1f} kW, cooling {hv.get('peak_c_kW', 0):.1f} kW at the "
        'bounding design temperatures.\n\n')


def _znbr2_machine_lines(prm, seed_block_mm):
    """X-MFG-43 (A-M-456/457): the ZNBR2 machine next to the thermal block -
    the stack the booked electrode area fills, the electrolyte the store
    holds, and the placement-block consequence. Generator-owned: every figure
    reads the graph, none is hand-stated. seed_block_mm is the placement-seed
    block for the unit (the v1 hidden read, injected)."""
    ds = prm.get('design') or {}
    if not ds.get('modules'):
        return ''
    bsz = ' x '.join(str(v) for v in (seed_block_mm or []))
    sz = ' x '.join(str(v) for v in (prm.get('size_mm') or []))
    return (f"- Stack (X-MFG-43, A-M-456): {ds.get('modules')} module bays x {ds.get('plates_per_module')} bipolar plates of "
            f"{ds.get('plate_active_L_mm')} x {ds.get('plate_active_W_mm')} mm active at the 20 mA/cm2 book fill the booked "
            f"electrode area {ds.get('electrode_area_m2_booked')} m2 (purge basis); j.A = current closes at "
            f"{ds.get('stack_I_A')} A x {ds.get('stack_V_dc')} V DC and {ds.get('stack_charge_kw_dc')} kW charge per module.\n"
            f"- Electrolyte (A-M-457): {ds.get('zn_kg_per_module')} kg Zn cycled per module per day at {ds.get('electrolyte_M')} M ZnBr2 = "
            f"{ds.get('electrolyte_L_per_module')} L per module in a {ds.get('tank_mm')[0]} x {ds.get('tank_mm')[1]} x {ds.get('tank_mm')[2]} reservoir; "
            f"Br2 inventory {ds.get('br2_kg_per_module')} kg per module; cooler {ds.get('cooler_kw_per_module')} kW at the charge-window rate (A-M-455).\n"
            f"- Machine envelope {sz} mm (the X-MFG-43 rack hall, models/mfg/ZNBR2); the placement seed block ({bsz} mm) under-books it - "
            "the floor-space reservation is the named consequence (ZNBR2 WORK_ORDER W12).\n")


def render_cycling_section2(m, uid, seed_block_mm):
    """The whole section 2 for a node carrying a solved cycling_thermal block
    (X-THM-01 F-4), re-rendered from the graph every pass, trailing blank
    line included - the v1 replacement span. seed_block_mm: the placement
    seed's block size for the unit (the v1 hidden read, injected)."""
    n = m.nodes[uid]
    prm = n.get('params') or {}
    ct = prm.get('cycling_thermal') or {}
    ck = n.get('continuous_kw') or {}
    zn = _znbr2_machine_lines(prm, seed_block_mm)
    return (
        '2. Size.\n'
        '- Store and electrolyte thermal management are solved in the graph (X-ELS-02 / X-THM-01 F-4, A-M-455).\n'
        f"- Store: {ct.get('kwh_d_out', 0):.0f} kWh/d cycled at round trip {ct.get('round_trip', 0)} (A-M-062/179);"
        f" charge {ct.get('kwh_d_in', 0):.0f} kWh/d.\n"
        f"- Electrolyte thermal-management duty: cycling loss {ct.get('loss_kwh_d', 0):.0f} kWh/d ="
        f" {ct.get('avg_kW', 0):.1f} kW average thermal, rejected on IA-ZNBR-HEAT to the Q4 bus and the dry cooler.\n"
        f"- Charge-window sizing case: {ct.get('window_kW', 0):.1f} kW thermal over the {ct.get('window_h', 0):.0f} h"
        f" charge window; sizes the electrolyte cooling loop.\n"
        f"- Electrical: {float(ck.get('value') or 0):.4f} kW continuous discharge rating (storage; the charge draw rides IA-ESS-ZNBR2-CHG).\n"
        + zn + '\n')


def render_author_sheet(m, uid, facts=None):
    """The create-lane AQS-STD-001 sheet template, ported exactly from the v1
    author(): for a present unit whose sheet does not exist yet - graph facts
    quoted, gaps stated as pending, no invented content. facts injects the
    v1 function's hidden environment reads: 'loops' the unit's instrument
    loops (sorted in AQS-CTL-001 order), 'has_stl' whether the unit's CAD
    envelope STL is issued, 'mfg_module' the unit's manufacturing model file
    name (None when none is issued). Pure."""
    facts = facts or {}
    loops = sorted(facts.get('loops') or ())
    has_stl = bool(facts.get('has_stl'))
    mfg_module = facts.get('mfg_module')
    n = m.nodes[uid]
    p = n.get('params') or {}
    env = p.get('envelope') or {}
    ds = p.get('design') or {}
    sz = p.get('sizing') or {}
    sto = p.get('design_storage') or {}
    edges = [e for e in m.data['edges'] if uid in (e['from_unit_id'], e['to_unit_id'])]
    conns = [e for e in edges if e.get('presence') == 'present' and (('mass' in (e.get('layers') or []) and (e.get('rate') or {}).get('unit') == 'kg/d') or ((e.get('rate') or {}).get('unit') == 'kW' and (e['stream_id'].startswith('HL-') or 'thermal' in (e.get('layers') or [])) and e.get('phase') not in ('E', 'electric') and 'elec' not in (e.get('layers') or [])))]
    vents = [e for e in edges if e.get('presence') == 'present' and 'vent' in (e['stream_id'] + ' ' + str(e.get('carries') or '')).lower()]
    unrate = [e['stream_id'] for e in edges if e.get('presence') == 'present' and 'mass' in (e.get('layers') or []) and (e.get('rate') or {}).get('unit') != 'kg/d']
    ins, outs = _ins(m, uid), _outs(m, uid)
    mi = sum(e['rate']['value'] or 0 for e in ins)
    mo = sum(e['rate']['value'] or 0 for e in outs)
    kw = _kw(n)
    o = [f'# {uid}', '', f"Standard: AQS-STD-001 Rev A. Graph Rev {m.data.get('revision')}. Study. Not a PE stamp.", '',
         _basis_line(ins, outs, mi, mo, kw), '', '2. Size.']
    s2 = []
    esz = env.get('size_mm') or p.get('size_mm')
    if esz:
        L, W, H = esz
        V = L * W * H / 1000000000                                  # the v1 1e9 as an exact int
        s2.append(f'- Envelope {L}×{W}×{H} mm, {f4(V)} m³.' + (f' That box over this flow would be {V * 1000 / mi * 24:.1f} h if it were full. It is not a residence time.' if mi > 0 else ''))
        if env.get('basis'):
            s2.append(_dot(f'- Envelope basis (graph node): {env["basis"]}'))
        elif p.get('size_note'):
            s2.append(_dot(f'- Envelope: {p["size_note"]}'))
    if sto:
        s2.append(_dot(f'- Storage sizing (AQS-DUTY-064, graph design_storage): {_scalars(sto, skip=("material",))}'))
    if sz:
        s2.append(_dot(f'- Sizing study {sz.get("source", "pending")} ({sz.get("status", "study")}): {_scalars(sz, skip=("status", "source", "status_note"))}'))
    if ds:
        s2.append(_dot(f'- Graph design (AQS-PAR-001 sizing): {_scalars(ds, skip=("material",))}'))
    flat = _scalars({k: v for k, v in p.items() if k not in ('design', 'envelope', 'sizing', 'design_storage', 'size_mm', 'size_note', 'note', 'internals', 'presence', 'design_kPa', 'relief_mm', 'relief_basis', 'basis') and not isinstance(v, dict)})
    if flat:
        s2.append(_dot(f'- Node params (AQS-PAR-001): {flat}'))
    if p.get('note'):
        s2.append(_dot(f'- Node note: {p["note"]}'))
    if p.get('internals'):
        s2.append(_dot(f'- Internals (graph node): {p["internals"]}'))
    if p.get('basis'):
        s2.append(_dot(f'- Basis (graph node): {p["basis"]}'))
    if not (esz or sz or ds or sto or flat):
        s2.append('- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.')
    o += s2
    o += ['']
    mat = ds.get('material') or sto.get('material')
    s3m = p.get('sec3_material') or {}
    if s3m.get('mat'):   # X-MAT-22: the issued selection text, same composition as the refresh branch
        o.append(f"3. Material. {s3m['mat']}. Basis: {s3m['basis']} Alternative: {s3m['alt']}. "
                 f"{s3m['note']} ({s3m['task']})")
    else:
        o.append('3. Material. ' + (f'{mat} (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.' if mat else 'Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.'))
    if conns:
        n4 = f'4. Nozzles. Schedule at `nozzles/{uid}.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`.'
    elif n.get('class') in _VESSEL_ZERO:
        n4 = f'4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/{uid}.csv` carries only the drain and vent utilities.'
    else:
        n4 = '4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.'
    if conns or n.get('class') in _VESSEL_ZERO:
        n4 += ' Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).'
    o += ['', n4, '']
    o.append('5. Instruments. ' + (f"Loops {', '.join(loops)} in AQS-CTL-001. What trips is stated on the loop." if loops else 'No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.'))
    o += ['']
    if p.get('relief_basis'):
        rb = p['relief_basis']
        rbc = rb.get('case') if isinstance(rb, dict) else rb
        o.append(_dot('6. Relief. ' + f'Node relief basis: {rbc}' + (f'. Bore {p["relief_mm"]} mm.' if p.get('relief_mm') else '') + (f' Design {f4(p["design_kPa"])} kPa g (node design_kPa).' if p.get('design_kPa') else '')) + ' Not to the room.')
    elif vents:
        o.append('6. Relief. ' + f"Vent edge {' and '.join(e['stream_id'] for e in vents)} on the graph (to {' and '.join(sorted(set(e['to_unit_id'] for e in vents)))}). Atmospheric operation is not claimed beyond this edge. Not to the room.")
    else:
        o.append('6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.')
    pres = n.get('presence', 'present')   # the node IS the unit: presence is on it, not in a lookup table
    if pres == 'absent':
        stl = ' The unit is retired from the graph; no envelope is issued.'
    elif has_stl:
        stl = f' The envelope is `cad/stl/{uid}.stl` (a thick-walled tray at the claimed envelope; X-PAR-04).'
    else:
        stl = ' No CAD envelope issued yet.'
    mfg = ''
    if mfg_module:
        mfg = f' Manufacturing model `models/mfg/{uid}/{mfg_module}` (AQS-PLAN-006; build log and drawings in the same folder).'
    o += ['', f'7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule).{stl}{mfg}', '']
    oi = []
    if not (sz or sto):
        oi.append('Sizing calculation pending (unit task 02).')
    if not mat:
        oi.append('Material selection pending (unit task 09).')
    if not loops:
        oi.append('No instrument loop yet (unit task 08).')
    if not (p.get('relief_basis') or vents):
        oi.append('Relief case pending (unit task 07).')
    if unrate:
        oi.append(f"Edges {', '.join(unrate)} carry no kg/d rate yet; section 1 reads zero flow until the parametric model rates them.")
    if conns or n.get('class') in _VESSEL_ZERO:
        oi.append('Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).')
    o.append('8. Open items. ' + ' '.join(oi))
    return '\n'.join(o) + '\n'
