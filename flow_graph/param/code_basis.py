"""X-STD-01 code basis (owner decision 2026-10-15: NFPA and ISO applied throughout; IBC/IFC/NEC/IEEE where they govern).
One table per check document; generators call append(path, key) after writing, and test_code_basis.py fails if a block or a
governing clause is missing. Editions come from the EDITIONS table below, the single source (AQS-STD-007). Study; not a PE stamp."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Edition table (X-STD-01, owner decision Q-018 of 2026-10-24: the latest published edition of every code and standard
# applies; where two revisions conflict, the most recent governs). This table is the single source of editions: every
# citation in the repository must name the edition given here, and test_code_editions.py fails on any other.
# Columns: standard, edition, edition before Q-018, how the edition was confirmed (2026-10-24).
PUB = 'publisher page'; CUR = 'publisher page; no newer edition'; SRCH = 'search listing; to confirm at the publisher'
EDITIONS = [
    ('NFPA 1', '2027', '2021', PUB), ('NFPA 2', '2026', '2023', PUB), ('NFPA 13', '2025', '2022', PUB), ('NFPA 15', '2027', '2022', PUB),
    ('NFPA 20', '2025', '2022', PUB), ('NFPA 22', '2023', '2023', CUR), ('NFPA 25', '2026', '2023', PUB), ('NFPA 30', '2027', '2024', PUB),
    ('NFPA 55', '2027', '2026', PUB), ('NFPA 69', '2024', '2019', PUB), ('NFPA 70', '2026', '2023', PUB), ('NFPA 70B', '2026', '2023', SRCH),
    ('NFPA 70E', '2027', '2024', PUB), ('NFPA 72', '2025', '2022', PUB), ('NFPA 91', '2026', '2020', PUB), ('NFPA 99', '2027', '2021', PUB),
    ('NFPA 101', '2027', '2024', PUB), ('NFPA 110', '2025', '2022', PUB), ('NFPA 111', '2025', '2022', PUB), ('NFPA 400', '2025', '2022', PUB),
    ('NFPA 497', '2027', '2024', PUB), ('NFPA 704', '2027', '2022', PUB), ('NFPA 855', '2026', '2023', PUB),
    ('IBC', '2027', '2021', PUB), ('IFC', '2027', '2021', PUB), ('ASME BPVC', '2025', '2023', PUB),
    ('ASME B31.3', '2024', '2022', PUB), ('ASME B36.10M', '2018', '2018', CUR), ('ASME RTP-1', '2025', '2019', PUB),
    ('ASME B30.2', '2022', '2022', CUR), ('ASME B30.16', '2022', '2022', CUR), ('ASME Y14.1', '2020', '2020', SRCH),
    ('ASME Y14.5', '2018', '2018', SRCH), ('ASME Y14.35', '2025', '2014', SRCH), ('ASME Y14.100', '2017', '2017', SRCH),
    ('IEEE 80', '2013', '2013', CUR), ('IEEE 1547', '2018', '2018', CUR), ('IEEE 1547.1', '2020', '2020', SRCH),
    ('IEEE 2030.7', '2017', '2017', CUR), ('IEEE C57.12.34', '2022', '2015', PUB),
    ('ASHRAE 90.1', '2025', '2019', SRCH), ('ASHRAE 62.1', '2025', '2019', SRCH), ('ANSI C12.1', '2026', '2015', SRCH),
    ('ISO 668', '2020', '2020', CUR), ('ISO 898-1', '2013', '2013', CUR), ('ISO 1452-2', '2009', '2009', CUR), ('ISO 3506-1', '2020', '2020', CUR),
    ('ISO 3585', '1998', '1998', CUR), ('ISO 4126-1', '2013', '2013', CUR), ('ISO 7010', '2019', '2019', CUR), ('ISO 7200', '2004', '2004', CUR),
    ('ISO 7500-1', '2018', '2018', CUR), ('ISO 10628-2', '2012', '2012', CUR), ('ISO 13256-1', '2021', '2021', CUR), ('ISO 14120', '2015', '2015', CUR),
    ('ISO 14122-2', '2016', '2016', CUR), ('ISO 14687', '2025', '2019', PUB), ('ISO 16069', '2017', '2017', CUR), ('ISO 16528-1', '2007', '2007', CUR),
    ('ISO 21940-11', '2016', '2016', CUR), ('ISO 22734-1', '2025', '2019', PUB), ('ISO 23251', '2019', '2006', CUR), ('ISO 30500', '2025', '2018', PUB),
    ('ISO 45001', '2018', '2018', CUR), ('EN 16798-3', '2017', '2017', SRCH),
    ('IEC 60034-1', '2026', '2022', PUB), ('IEC 60034-2-1', '2024', '2014', PUB), ('IEC 60034-9', '2021', '2021', SRCH), ('IEC 60034-30-1', '2025', '2014', PUB),
    ('IEC 60072-1', '2022', '1991', PUB), ('IEC 60079-10-1', '2020', '2020', SRCH), ('IEC 60909-0', '2026', '2016', PUB), ('IEC 61131-2', '2017', '2017', PUB),
    ('IEC 61131-3', '2025', '2013', PUB), ('IEC 61511-1', '2016', '2016', PUB), ('IEC 61724-1', '2021', '2021', PUB), ('IEC 61882', '2016', '2016', SRCH),
    ('IEC 62282-3-100', '2019', '2019', SRCH), ('IEC 62439-2', '2021', '2016', PUB),
    ('ASTM B3', '13', '13', SRCH), ('ASTM B8', '23', '23', PUB), ('ASTM B49', '20', '20', SRCH), ('ASTM B193', '25', '20', PUB),
    ('ASTM C547', '25', '22', SRCH), ('ASTM C680', '24', '23', SRCH), ('ASTM C1055', '20', '20', PUB), ('ASTM D618', '21', '21', SRCH),
    ('ASTM D638', '22', '22', PUB), ('ASTM D790', '25', '17', SRCH), ('ASTM D792', '20', '20', SRCH), ('ASTM D1785', '21a', '15', PUB),
    ('ASTM D1998', '21', '21', SRCH), ('ASTM D2855', '20', '15', PUB),
]
ED = {s: e for s, e, _, _ in EDITIONS}
# Documents replaced under a new designation (old citation -> current citation).
RENAMED = {'ISO 22734:2019': 'ISO 22734-1:2025', 'ISO 16798-3:2017': 'EN 16798-3:2017', 'ANSI C12.20-2015': 'ANSI C12.1-2026'}
Y = r'(20\d\d)(?!\d)'
Y19 = r'((?:19|20)\d\d)(?!\d)'
def _patterns():
    P = []
    for s, e, _, _ in EDITIONS:
        fam, num = s.split(' ', 1) if ' ' in s else (s, '')
        n = re.escape(num)
        if fam == 'NFPA':
            P += [(s, re.compile(rf'(\bNFPA {n}(?![0-9A-Z.])(?:\s*[-\u2013]\s*|\s+|\s*\(\s*)){Y}')),
                  (s, re.compile(rf'(\bNFPA {n}, [A-Z][^,()\n\d]{{3,90}}?(?:,\s*|\s*\(\s*)){Y}')),
                  (s, re.compile(rf'(\bNFPA{n}_){Y}'))]
            if num == '70':
                P += [(s, re.compile(rf'(\bNEC[ _]?){Y}'))]
        elif fam in ('IBC', 'IFC'):
            long = 'International Building Code' if fam == 'IBC' else 'International Fire Code'
            P += [(s, re.compile(rf'(\b{fam}(?:\s*[-\u2013]\s*|\s*\(\s*|\s*)){Y}')), (s, re.compile(rf'({long}\s*\(?\s*){Y}'))]
        elif s == 'ASME BPVC':
            P += [(s, re.compile(rf'(BPVC[^()\n]{{0,40}}\(){Y}'))]
        elif fam == 'ASTM':
            P += [(s, re.compile(rf'(\bASTM {n}-)(\d\d[a-z]?)(?![0-9a-z])'))]
        elif fam in ('ISO', 'IEC', 'EN'):
            P += [(s, re.compile(rf'(\b(?:ISO/)?{fam}(?:/IEC)? {n}:){Y19}'))]
        elif s.startswith('ASHRAE'):
            P += [(s, re.compile(rf'(\b(?:ANSI/)?ASHRAE(?:/IES)? {re.escape(s.split()[1])}-){Y}'))]
        elif fam == 'IEEE':
            P += [(s, re.compile(rf'(\bIEEE (?:Std )?{n}-){Y}'))]
        else:
            P += [(s, re.compile(rf'(\b{re.escape(s)}-){Y}'))]
    return P
PATTERNS = _patterns()
def _needles(s):
    fam, num = s.split(' ', 1) if ' ' in s else (s, '')
    if fam == 'NFPA':
        return [f'NFPA {num}', f'NFPA{num}_'] + (['NEC'] if num == '70' else [])
    if s == 'IBC': return ['IBC', 'International Building Code']
    if s == 'IFC': return ['IFC', 'International Fire Code']
    if s == 'ASME BPVC': return ['BPVC']
    if fam == 'ASHRAE': return [num]
    if fam == 'IEEE': return [num]
    return [num or s]
NEEDLES = {s: _needles(s) for s, _, _, _ in EDITIONS}
def edition(std):
    return ED[std]
def cite(std):
    fam = std.split(' ')[0]
    return f'{std}:{ED[std]}' if fam in ('ISO', 'IEC', 'EN') else f'{std} {ED[std]}' if fam in ('IBC', 'IFC', 'ASME') and std in ('IBC', 'IFC', 'ASME BPVC') else f'{std}-{ED[std]}'
def update(text):
    for a, b in RENAMED.items():
        text = text.replace(a, b)
    for s, p in PATTERNS:
        if not any(k in text for k in NEEDLES[s]):
            continue
        text = p.sub(lambda m: m.group(1) + ED[s], text)
    return text
REV_ROW = re.compile(r'^\|\s*[A-Z][A-Z0-9+.\u2032]{0,3}\s*\|.*\|\s*20\d\d-\d\d-\d\d\s*\|\s*$')
def stale(text):
    """(line number, citation, edition in force) for every citation that names another edition; revision rows skipped."""
    out = []
    def where(pos):
        a = text.rfind('\n', 0, pos) + 1; b = text.find('\n', pos); line = text[a:b if b >= 0 else len(text)]
        return text.count('\n', 0, pos) + 1, bool(REV_ROW.match(line))
    for a, b in RENAMED.items():
        k = text.find(a)
        while k >= 0:
            n, rev = where(k)
            if not rev: out.append((n, a, b))
            k = text.find(a, k + 1)
    for s, p in PATTERNS:
        if not any(k in text for k in NEEDLES[s]):
            continue
        for m in p.finditer(text):
            if m.group(2) != ED[s]:
                n, rev = where(m.start())
                if not rev: out.append((n, m.group(0), ED[s]))
    return out
B = {
 'HAZMAT_SEPARATION': [('Incompatible storage separation', 'NFPA 400-2022 6.1.12.1; IFC 2021 5003.9.8'), ('Safety signs at bunds and cabinets', 'ISO 7010:2019; NFPA 704-2022 hazard diamond'), ('Corrosive and oxidizer quantities', 'NFPA 400-2022 ch. 13 and 15')],
 'ACCESS_CHECK': [('Electrical working space', 'NFPA 70-2023 (NEC) 110.26(A)'), ('Aisle and egress width', 'NFPA 101-2024 7.3.4.1.1; IBC 2021 1018.5'), ('Permanent walkways and platforms', 'ISO 14122-2:2016 (600 mm minimum; 914 mm used)')],
 'HALL_EGRESS': [('Means of egress', 'NFPA 101-2024 ch. 7 and 40; IBC 2021 ch. 10 (most restrictive governs)'), ('Sprinklers', 'NFPA 13-2022'), ('Emergency lighting', 'NFPA 101-2024 7.9; NFPA 70-2023 Art. 700'), ('Escape signs', 'ISO 7010:2019 E001/E002; ISO 16069:2017 safety way guidance')],
 'EVAP_DESIGN': [('Pressure relief, fire case', 'ISO 23251:2019 (API 521); ISO 4126-1:2013 (API 520)'), ('Corrosive liquid handling', 'NFPA 400-2022 ch. 13'), ('Fasteners', 'ISO 898-1:2013; ISO 3506-1:2020'), ('Pressure equipment practice', 'ISO 16528-1:2007 (ASME VIII-1 study basis)')],
 'VENT_SCRUBBER': [('Vapour exhaust duct', 'NFPA 91-2020'), ('Corrosive liquid handling', 'NFPA 400-2022 ch. 13'), ('PVC-U pipe', 'ISO 1452-2:2009 (ASTM D1785 sizes)'), ('Exposure limit basis', 'ACGIH TLV-C 2 ppm HCl; ISO 16000 / NIOSH 7903 sampling')],
 'ONE_LINE': [('Interconnected sources', 'NFPA 70-2023 Art. 705'), ('Overcurrent protection', 'NFPA 70-2023 240.6(A), Art. 240'), ('Energy storage', 'NFPA 70-2023 Art. 706; NFPA 855-2023'), ('Interconnection', 'IEEE 1547-2018; UL 1741 SB'), ('Electrical safety in operation', 'NFPA 70E-2024; ISO 45001:2018 management system')],
 'COLLECTION_BUS': [('Arc energy reduction threshold', 'NFPA 70-2023 240.87'), ('Switchboards', 'UL 891; NFPA 70-2023 Art. 408'), ('Transformers', 'IEEE C57.12.34-2015; NFPA 70-2023 450.3'), ('Energy storage installation', 'NFPA 855-2023 (outdoor ZNBR2 yard)'), ('Microgrid control', 'IEEE 2030.7-2017')],
 'PROTECTION': [('Overcurrent and coordination', 'NFPA 70-2023 Art. 240; 240.87'), ('Short-circuit method', 'IEC 60909-0:2016 (inverter-limited study)'), ('Grounding, touch and step', 'IEEE 80-2013; NFPA 70-2023 Art. 250'), ('Arc flash', 'NFPA 70E-2024 130.5')],
 'POWER_SIZING': [('Roof PV access', 'NFPA 1-2021 11.12; IFC 2021 1205.3'), ('Energy storage', 'NFPA 855-2023'), ('Ventilation fans', 'ISO 16798-3:2017'), ('PV modelling', 'NREL PVWatts v8; IEC 61724-1:2021 performance monitoring')],
 'GA_CHECK': [('Clearance for access and maintenance', 'ISO 14122-2:2016; NFPA 70-2023 110.26 (AQS-BLD-012)'), ('Separation', 'NFPA 400-2022 (AQS-BLD-011)')],
}
STD_ROWS = [(c, e, st) for c, e, _, st in EDITIONS]
MARK = '## Code basis (X-STD-01)'
B = {k: [(a, update(b)) for a, b in v] for k, v in B.items()}
def block(key):
    return MARK + '\n\n| Check | Governing clause |\n| --- | --- |\n' + '\n'.join(f'| {a} | {b} |' for a, b in B[key]) + '\n'
def append(path, key):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    s = open(p).read(); s = re.sub(r'\n' + re.escape(MARK) + r'.*?(?=\n## |\Z)', '', s, flags=re.S).rstrip('\n') + '\n\n' + block(key)
    open(p, 'w').write(s)
PATHS = {'HAZMAT_SEPARATION': 'docs-authority/HAZMAT_SEPARATION.md', 'ACCESS_CHECK': 'docs-authority/ACCESS_CHECK.md', 'HALL_EGRESS': 'docs-authority/HALL_EGRESS.md',
         'EVAP_DESIGN': 'docs-authority/sizing/EVAP_DESIGN.md', 'VENT_SCRUBBER': 'docs-authority/sizing/VENT_SCRUBBER.md', 'ONE_LINE': 'docs-authority/ONE_LINE.md',
         'COLLECTION_BUS': 'docs-authority/COLLECTION_BUS.md', 'PROTECTION': 'docs-authority/PROTECTION.md', 'POWER_SIZING': 'docs-authority/POWER_SIZING.md', 'GA_CHECK': 'docs-authority/GA_CHECK.md'}
def write_std():
    L = ['# Code basis', '', 'Document number: AQS-STD-007', 'Former number: AQS-STD-002 (shared with MATERIALS_STD.md until 2026-10-24; that page keeps it)', 'Revision: D', 'Date: 2026-10-24',
         'Basis: AQS-PLAN-007 task X-STD-01; project owner decision of 2026-10-15 (NFPA and ISO throughout; IBC, IFC, NEC and IEEE where they govern; the most restrictive requirement governs).',
         'Source: generated by `flow_graph/param/code_basis.py` and checked by `flow_graph/param/test_code_basis.py`. Do not edit by hand. This is a study, not a professional engineer\'s stamp.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. Editions, and the governing clause for each check document. | 2026-10-15 |', '| B | Renumbered AQS-STD-007 (AQS-STD-002 belongs to MATERIALS_STD.md); file renamed from AQS-STD-002_CODE_BASIS.md. | 2026-10-24 |',
         '| C | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope, terms, captions; sections renumbered. Editions and clauses unchanged. | 2026-10-24 |', '| D | Owner decision Q-018: the latest published edition of every standard applies, and the most recent revision governs a conflict. Table 3.1 is now the single source of editions for the whole repository; Table 4.1 clauses carried from earlier editions are listed as assumptions to verify. | 2026-10-24 |', '',
         '## 1. Purpose and scope', '',
         'The plant is checked against published codes and standards. This page fixes which edition of each standard applies (Table 3.1) and, for each check document, which clause governs each check (Table 4.1). Where two standards cover the same point, the most restrictive requirement governs.', '',
         'Each check document carries its own copy of its rows in a "Code basis (X-STD-01)" section, written by the same generator. A check document that lacks that section, or a check without a governing clause, fails `test_code_basis.py`.', '',
         'Table 3.1 is the single source of editions. Every citation in the repository, in any document, generator or data file, must name the edition given there; `flow_graph/param/test_code_editions.py` fails on any other. A clause number or value taken from an earlier edition is recorded as an assumption until it is checked against the edition in force.', '',
         'This page does not quote clause text, and it is not a permit or a code review by the authority having jurisdiction.', '',
         '## 2. Terms', '',
         '- Check document: a page that tests the design against a code requirement, for example a separation, access or egress check.',
         '- Governing clause: the clause, with its standard and edition, that a check is tested against.',
         f'- Edition: the year of the standard that applies. A citation such as {cite("NFPA 101")} or {cite("ISO 7010")} names the edition. Amendments to an edition apply with it.',
         '- NFPA: National Fire Protection Association. ISO: International Organization for Standardization. IEC: International Electrotechnical Commission. IEEE: Institute of Electrical and Electronics Engineers. UL: UL Standards & Engagement.',
         '- IBC, IFC: the International Building Code and the International Fire Code (International Code Council). NEC: the National Electrical Code, NFPA 70.',
         '', 'Other abbreviations are in `docs-authority/GLOSSARY.md`.', '',
         '## 3. Editions', '', 'Table 3.1. Editions in force, with how each was confirmed on 2026-10-24', '', '| Standard | Edition | Confirmed by |', '| --- | --- | --- |']
    L += [f'| {a} | {b} | {c} |' for a, b, c in STD_ROWS]
    L += ['', 'ASTM editions are the two-digit year suffix of the designation. Where the third column says to confirm, the edition comes from a search listing rather than the publisher\'s own page; assumption A-M-333 records it.', '',
          '## 4. Checks', '', 'Table 4.1. Governing clause for each check', '', '| Document | Check | Governing clause |', '| --- | --- | --- |']
    L += [f'| `{PATHS[k]}` | {a} | {b} |' for k in B for a, b in B[k]]
    open(os.path.join(ROOT, 'docs-authority/CODE_BASIS.md'), 'w').write('\n'.join(L) + '\n')
if __name__ == '__main__':
    for k, p in PATHS.items(): append(p, k)
    write_std()
