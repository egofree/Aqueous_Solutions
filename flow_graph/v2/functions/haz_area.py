"""engine v2: the hazardous-area release census (the graph-derived half of the
ledger section D row haz_area — the reference writer
docs-authority/_haz_area.py, AQS-ELEC-009).

The v1 stage derives the release sources from the graph alone (present edges
carrying a classified flammable substance above the driver thresholds, phase
liquid or gas, biological hydrocarbon excluded, header/boundary/building/dock/
relief units excluded) and classifies each source per IEC 60079-10-1 with the
gas class table from the drivers (A-M-210). The Instruments and Motors-and-
pumps counts of its rows read INSTRUMENT_INDEX.csv and OTHER_INVENTORY.csv —
the instrument and other census families, not landed — so the document half
and the HAZ_AREA.csv sidecar wait on those; this module ports the graph-derived
book as one pure function.

Golden equality: flow_graph/v2/test_safety_books.py compares every graph-
derived field of the rows against the committed
docs-authority/inventory/HAZ_AREA.csv (the committed doc fields; the two
census-count columns are excluded, they belong to the unlanded families).

Pure: no I/O, no wall-clock, no RNG, no float literals (the engine lint's
discipline; the gas classes and thresholds ride the drivers).
"""


def _v(d, k):
    return d[k]['value']


def release_rows(m, d):
    """The release-source rows of _haz_area.py minus the two inventory-count
    columns: one row per source unit with its substances, the summed
    flammable flow, the worst-case gas group and temperature class, and the
    Zone 1 / Zone 2 extents (A-M-210: H2 R1 1.0 m / R2 1.5 m, vapours R1
    1.5 m / R2 3.0 m to floor), sorted by unit id (the v1 iteration order)."""
    ga_st = _v(d, 'ELEC.distribution-train.haz_gas_classes')
    gas = {x: (c['group'], c['T_class'], c['AIT_C'], c['R1_m'], c['R2_m'], c['kind']) for x, c in ga_st.items()}
    min_h2 = _v(d, 'ELEC.distribution-train.haz_min_frac_H2')
    min_vap = _v(d, 'ELEC.distribution-train.haz_min_frac_vap')
    src = {}
    for e in m.data['edges']:
        if e['presence'] != 'present' or not (e['rate'].get('value') or 0) > 0:
            continue
        for x, f in (e.get('composition') or {}).items():
            if x not in gas or not (f or 0) > (min_h2 if x == 'H2' else min_vap):
                continue
            if e.get('phase') not in ('L', 'G'):
                continue
            if x == 'hydrocarbon' and {(m.nodes.get(e['from_unit_id']) or {}).get('sector_id'),
                                       (m.nodes.get(e['to_unit_id']) or {}).get('sector_id')} & {'FARM', 'HAB', 'WTR'}:
                continue                                           # biological 'hydrocarbon' (biomass) is not a vapour source
            for u in (e['from_unit_id'], e['to_unit_id']):
                n = m.nodes.get(u) or {}
                if n.get('class') not in ('header', 'boundary', 'building', 'dock', 'relief'):
                    src.setdefault(u, {})
                    src[u][x] = max(src[u].get(x, 0), e['rate']['value'] * f)
    rows = []
    for u in sorted(src):
        sp = src[u]
        worst = max(sp, key=lambda x: (gas[x][0].startswith('IIC'), -gas[x][2]))
        grp, tc, _ait, r1, r2, kind = gas[worst]
        if any(gas[x][1] == 'T3' for x in sp):
            tc = 'T3'
        rlf = ((m.nodes[u].get('params') or {}).get('relief_mm') or 0) > 0
        rows.append(dict(unit=u, sector=m.nodes[u].get('sector_id'), substances=' '.join(sorted(sp)),
                         kg_d=round(sum(sp.values()), 3), group=grp, T_class=tc, zone0='inside vessel',
                         zone1=f'{r1} m around relief/vent outlet' if rlf else 'none (no vent on the unit)',
                         zone2=f'{r2} m around the envelope' + (', to floor' if kind.startswith('vapour') else ', upward bias'),
                         protection=f'Zone 1: Ex d/e or Ex ia {grp.split()[0]} {tc}; Zone 2: Ex ec/nA {grp.split()[0]} {tc}'))
    return rows
