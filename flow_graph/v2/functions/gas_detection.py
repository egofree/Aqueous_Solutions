"""engine v2: the gas-detection book (the detector census of the ledger
section H row doc_gas_det — the reference writer docs-authority/_gas_det.py).

The v1 script embeds the detector book (species match patterns, detector
types, mountings and the NFPA 2 / NFPA 69 / OSHA 1910.146 / ACGIH TLV set
points) and censuses the graph's present gas-phase edges into per-unit source
rows: two detectors per source unit (one failed head still covers it — the
redundancy rule), three where a SIF votes 2oo3 on them (AQS-CTL-003). This
module carries that book and the census as one pure function over the model.

Golden equality: flow_graph/v2/test_safety_books.py compares the rows against
the committed docs-authority/inventory/GAS_DETECTORS.csv (the doc_gas_det
product the inventory_other census consumes).

Pure: no I/O, no wall-clock, no RNG, no float literals (the engine lint's
discipline; the set points are the code-basis strings the book states).
"""
import collections
import re

# The species book: (match pattern over stream id + carries, detector,
# mounting, alarm, trip, extra stated sources). The set points: H2 10 % / 25 %
# LFL (LFL 4.0 vol %, NFPA2_2026, NFPA69_2024); O2 deficiency 19.5 % and
# enrichment 23.5 % (OSHA_1910_146); toxic at the ACGIH_TLV_2024 TWA (alarm)
# and 2 x TWA or the ceiling (trip).
SP = {
    'H2': (r'\bH2\b|hydrogen', 'catalytic bead + IR backup', 'ceiling', '0.4 vol % (10 % LFL)', '1.0 vol % (25 % LFL)', set()),
    'O2 deficiency': (r'\bN2\b|nitrogen|\bCO2\b|\bAr\b|argon', 'electrochemical O2', 'low (dense gases)', '19.5 vol %', '18.0 vol %',
                      {'CRYO_HE', 'CRYO_NE', 'CRYO_KR', 'CRYO_XE'}),
    'O2 enrichment': (None, 'electrochemical O2', 'breathing height', '23.5 vol %', '25 vol %',
                      {'CRYO_O2', 'H2O_ELYZ', 'HDR_O2', 'CRYO_ASU', 'FUEL_CELL'}),
    'CO': (r'\bCO\b|carbon monoxide|syngas', 'electrochemical CO', 'breathing height', '25 ppm', '50 ppm',
           {'OIL_PYRO', 'OIL_FRAC', 'OIL_DRYER', 'BACKUP_GEN', 'HTC', 'AFTERBURNER'}),
    'NOx': (r'NOx|NO2|nitric', 'electrochemical NO2', 'breathing height', '0.2 ppm NO2', '0.4 ppm NO2', set()),
    'Cl2 / HCl': (r'Cl2|chlorine|\bHCl\b', 'electrochemical Cl2 and HCl', 'low', '0.1 ppm Cl2 / 2 ppm HCl', '0.4 ppm Cl2 / 4 ppm HCl', set()),
    'HF': (r'\bHF\b|hydrogen fluoride', 'electrochemical HF', 'breathing height', '1 ppm', '2 ppm (ceiling)', set()),
}
SKIP = {'header', 'boundary', 'product', 'building', 'farm', 'dock'}    # node classes that are not detector sources
SIF3 = {'CRYO_H2', 'CRYO_O2', 'H2O_ELYZ'}                              # the SIF 2oo3 vote units (AQS-CTL-003)


def detector_rows(m):
    """The per-source detector rows of _gas_det.py, in its generation order:
    species book order, then sorted source units. qty is 3 where a SIF votes
    2oo3 on the unit (H2 and O2 enrichment only), else 2 (alarm 1oo2)."""
    n_map = m.nodes
    src = collections.defaultdict(set)
    for e in m.data['edges']:
        if e['presence'] != 'present' or not (e['rate']['value'] or 0) or e.get('phase') != 'G':
            continue
        t = e['stream_id'] + ' ' + str(e.get('carries', ''))
        for k, (pat, *_r) in SP.items():
            if pat and re.search(pat, t, re.I):
                src[k].update({e['from_unit_id'], e['to_unit_id']})
    for k, v in SP.items():
        src[k] |= v[5]
    rows = []
    for k, (pat, typ, mount, al, tr, extra) in SP.items():
        for u in sorted(src[k]):
            if (n_map.get(u) or {}).get('class') in SKIP and u not in extra:
                continue
            if u not in n_map:
                continue
            n = 3 if u in SIF3 and k in ('H2', 'O2 enrichment') else 2
            rows.append(dict(unit=u, sector=n_map[u].get('sector_id'), gas=k, type=typ, mounting=mount, alarm=al, trip=tr,
                             qty=n, voting='2oo3 to SIF (AQS-CTL-003)' if n == 3 else 'alarm 1oo2'))
    return rows


def detector_summary(rows):
    """The census totals: per-gas source-unit and detector counts (the
    summary table and the totals line of GAS_DETECTION.md)."""
    g = collections.Counter()
    q = collections.Counter()
    for r in rows:
        g[r['gas']] += 1
        q[r['gas']] += r['qty']
    return g, q
