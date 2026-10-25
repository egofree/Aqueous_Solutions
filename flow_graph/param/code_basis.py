"""X-STD-01 code basis (owner decision 2026-10-15: NFPA and ISO applied throughout; IBC/IFC/NEC/IEEE where they govern).
One table per check document; generators call append(path, key) after writing, and test_code_basis.py fails if a block or a
governing clause is missing. Edition years per AQS-STD-007 (docs-authority/CODE_BASIS.md). Study; not a PE stamp."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
STD_ROWS = [('NFPA 1', '2021'), ('NFPA 13', '2022'), ('NFPA 70 (NEC)', '2023'), ('NFPA 70E', '2024'), ('NFPA 91', '2020'), ('NFPA 101', '2024'), ('NFPA 400', '2022'), ('NFPA 704', '2022'), ('NFPA 855', '2023'),
            ('ISO 1452-2', '2009'), ('ISO 3506-1', '2020'), ('ISO 4126-1', '2013'), ('ISO 7010', '2019'), ('ISO 898-1', '2013'), ('ISO 13256-1', '2021'), ('ISO 14122-2', '2016'), ('ISO 16069', '2017'), ('ISO 16528-1', '2007'), ('ISO 16798-3', '2017'), ('ISO 23251', '2019'), ('ISO 45001', '2018')]
MARK = '## Code basis (X-STD-01)'
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
    L = ['# Code basis', '', 'Document number: AQS-STD-007', 'Former number: AQS-STD-002 (shared with MATERIALS_STD.md until 2026-10-24; that page keeps it)', 'Revision: C', 'Date: 2026-10-24',
         'Basis: AQS-PLAN-007 task X-STD-01; project owner decision of 2026-10-15 (NFPA and ISO throughout; IBC, IFC, NEC and IEEE where they govern; the most restrictive requirement governs).',
         'Source: generated by `flow_graph/param/code_basis.py` and checked by `flow_graph/param/test_code_basis.py`. Do not edit by hand. This is a study, not a professional engineer\'s stamp.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |', '| A | First issue. Editions, and the governing clause for each check document. | 2026-10-15 |', '| B | Renumbered AQS-STD-007 (AQS-STD-002 belongs to MATERIALS_STD.md); file renamed from AQS-STD-002_CODE_BASIS.md. | 2026-10-24 |',
         '| C | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope, terms, captions; sections renumbered. Editions and clauses unchanged. | 2026-10-24 |', '',
         '## 1. Purpose and scope', '',
         'The plant is checked against published codes and standards. This page fixes which edition of each standard applies (Table 3.1) and, for each check document, which clause governs each check (Table 4.1). Where two standards cover the same point, the most restrictive requirement governs.', '',
         'Each check document carries its own copy of its rows in a "Code basis (X-STD-01)" section, written by the same generator. A check document that lacks that section, or a check without a governing clause, fails `test_code_basis.py`.', '',
         'This page does not quote clause text, and it is not a permit or a code review by the authority having jurisdiction.', '',
         '## 2. Terms', '',
         '- Check document: a page that tests the design against a code requirement, for example a separation, access or egress check.',
         '- Governing clause: the clause, with its standard and edition, that a check is tested against.',
         '- Edition: the year of the standard that applies. A citation such as NFPA 101-2024 or ISO 7010:2019 names the edition.',
         '- NFPA: National Fire Protection Association. ISO: International Organization for Standardization. IEC: International Electrotechnical Commission. IEEE: Institute of Electrical and Electronics Engineers. UL: UL Standards & Engagement.',
         '- IBC, IFC: the International Building Code and the International Fire Code (International Code Council). NEC: the National Electrical Code, NFPA 70.',
         '', 'Other abbreviations are in `docs-authority/GLOSSARY.md`.', '',
         '## 3. Editions', '', 'Table 3.1. Editions in force', '', '| Standard | Edition |', '| --- | --- |']
    L += [f'| {a} | {b} |' for a, b in STD_ROWS]
    L += ['', 'Editions of other standards cited in Table 4.1 are given in the citation itself.', '',
          '## 4. Checks', '', 'Table 4.1. Governing clause for each check', '', '| Document | Check | Governing clause |', '| --- | --- | --- |']
    L += [f'| `{PATHS[k]}` | {a} | {b} |' for k in B for a, b in B[k]]
    open(os.path.join(ROOT, 'docs-authority/CODE_BASIS.md'), 'w').write('\n'.join(L) + '\n')
if __name__ == '__main__':
    for k, p in PATHS.items(): append(p, k)
    write_std()
