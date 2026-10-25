"""X-COD-01: close the AQS-COMPL-001 compliance matrix per item (rev D). Each row gets its present evidence and one closure state:
Closed (study): the design evidence exists in a generated document; AHJ/PE confirmation still applies to everything.
Open (design): a design deliverable is still missing; the TASK_PLAN item that closes it is named.
Open (external): needs the site, the AHJ, the utility, the fire engineer of record or a physical test.
Open (owner): an operating-programme or management-system decision.
N/A: not applicable. Rewrites section 11 of COMPLIANCE_MATRIX.md. Run: python3 docs-authority/_compliance.py"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param.refs import cite
cite('OSHA_1910_119')
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
h2 = N['CRYO_H2']['params'].get('store_kg', 0)
C = [
 ('CMP-NFPA-01', 'AQS-SAF-004 relief; AQS-SAF-005 flame and H2 detection, water spray, auto depressuring; AQS-HSE-001', 'Closed (study)', 'AHJ edition'),
 ('CMP-NFPA-02', 'AQS-DUTY-069 cold box (no cryogenic column); AQS-SAF-004/005 receivers', 'Closed (study)', '-'),
 ('CMP-NFPA-03', 'AQS-HSE-001 envelopes', 'Open (design)', 'X-ELS-09 area classification drawings'),
 ('CMP-NFPA-04', 'AQS-EGR-001, AQS-EGR-002; AQS-BLD-014 reservoir storeys (maintenance access, stairs to roof)', 'Closed (study)', 'AHJ clear widths'),
 ('CMP-NFPA-05', 'AQS-BLD-011 incompatible storage separation and quantities', 'Closed (study)', '-'),
 ('CMP-NFPA-06', 'ess_tf purge at 25 % LFL; AQS-SAF-005 detector setpoints 10 % alarm, 25 % trip', 'Open (design)', 'X-SAF-01 HAZOP then X-CTL-03 SIF/SIL'),
 ('CMP-NFPA-07', 'FLOW_BATTERY.md, AQS-SAF-005 (NFPA 855 detection row)', 'Closed (study)', 'listing with the AHJ'),
 ('CMP-NFPA-08', 'OIL fire area; AQS-SAF-005 L0 EH1', 'Open (design)', 'indoor NFPA 30 quantity ledger for the fractionator hold-up (X-SAF-09)'),
 ('CMP-NFPA-09', 'AQS-SAF-005 density/area demand, 451 m3 gravity reserve, NFPA 20 pump', 'Open (external)', 'hydraulic calculation from the riser by the fire engineer of record'),
 ('CMP-NFPA-10', 'AQS-ELEC-006 protection and coordination', 'Closed (study)', 'labels after the final one-line'),
 ('CMP-NEC-01', 'AQS-ELEC-002 one-line; AQS-ELEC-006 coordination', 'Closed (study)', '-'),
 ('CMP-NEC-02', 'AQS-ELEC-002; IEEE 1547 / UL 1741 SB basis', 'Open (external)', 'utility interconnection agreement'),
 ('CMP-NEC-03', 'AQS-ELEC-002; AQS-BLD-012 working space', 'Closed (study)', '-'),
 ('CMP-NEC-04', 'AQS-HSE-001 envelopes', 'Open (design)', 'X-ELS-09 (seal-offs and tray schedule follow)'),
 ('CMP-NEC-05', 'AQS-ELEC-003 load list (continuous kW from need); AQS-ELEC-002; AQS-OPS-002 NFPA 110 tests', 'Closed (study)', '-'),
 ('CMP-NEC-06', 'AQS-ELEC-002 FC on the DC bus', 'Closed (study)', '-'),
 ('CMP-NEC-07', 'AQS-HSE-001 section 8', 'Open (design)', 'emergency lighting fixture schedule (X-THM-02 / X-DWG)'),
 ('CMP-NEC-08', 'AQS-ELEC-005 grounding and bonding', 'Closed (study)', '-'),
 ('CMP-NEC-09', 'AQS-BLD-012 NEC 110.26 working-space check', 'Closed (study)', '-'),
 ('CMP-OSH-01', 'as CMP-NFPA-04', 'Closed (study)', 'AHJ'),
 ('CMP-OSH-02', 'AQS-BLD-012 ISO 14122-2 walkways', 'Open (design)', 'guardrail schedule on the level drawings'),
 ('CMP-OSH-03', 'AQS-OPS-002 lists confined spaces (reservoir cells, vessels)', 'Open (owner)', 'written permit-space programme (X-OPS-01)'),
 ('CMP-OSH-04', 'AQS-OPS-002 maintenance tasks', 'Open (owner)', 'energy-isolation procedures (X-OPS-01)'),
 ('CMP-OSH-05', '-', 'Open (owner)', 'industrial hygiene survey and written programme'),
 ('CMP-OSH-06', 'AQS-HSE-001 section 2', 'Closed (study)', '-'),
 ('CMP-OSH-07', 'AQS-DUTY-061 vent scrubber; house scrubbers on the graph', 'Closed (study)', 'capture velocity test at commissioning'),
 ('CMP-OSH-08', f'H2 inventory {h2:.0f} kg against the 10,000 lb (4,536 kg) flammable threshold of 29 CFR 1910.119 App. A', 'Closed (study)', 're-check if hold-ups grow'),
 ('CMP-OSH-09', 'as CMP-NFPA-10', 'Closed (study)', '-'),
 ('CMP-OSH-10', '-', 'Open (design)', 'guarding drawings and noise survey'),
 ('CMP-ASM-01', 'AQS-ASME-002 code intent per unit from the graph design pressures; receivers to B31.3 (ID under 152 mm)', 'Closed (study)', 'PE review'),
 ('CMP-ASM-02', 'AQS-ASM-001 class sheets; design pressures from cases (A-M-174); AQS-QA-001 tests', 'Closed (study)', '-'),
 ('CMP-ASM-03', 'AQS-WLD-002 WPS-03..07; AQS-QA-001 route R4', 'Closed (study)', '-'),
 ('CMP-ASM-04', 'AQS-WLD-002 WPS-01..08 and PQR tests', 'Open (external)', 'PQR coupons welded and tested (physical)'),
 ('CMP-ASM-05', 'AQS-SAF-004 relief register with set pressures; AQS-SAF-005 fire case', 'Closed (study)', '-'),
 ('CMP-ISO-01', 'DOC_REGISTER; AQS-QA-001', 'Closed (study)', 'not a certified QMS'),
 ('CMP-ISO-02', '-', 'Open (owner)', 'ISO 45001 adoption decision'),
 ('CMP-ISO-03', 'inventory caps, relief and fire cases', 'Open (design)', 'X-SAF-01 HAZOP, LOPA'),
 ('CMP-ISO-04', 'closed vents and scrubbers', 'Open (owner)', 'ISO 14001 adoption decision'),
 ('CMP-ISO-05', 'NFPA 2 primary', 'Closed (study)', '-'),
 ('CMP-ISO-06', 'wafer fab, UPW', 'Open (design)', 'cleanliness class with the fab tool set'),
 ('CMP-ISO-07', 'US basis is ASME', 'N/A', '-')]
p = 'docs-authority/COMPLIANCE_MATRIX.md'; s = open(p).read()
ids = re.findall(r'^\| (CMP-[A-Z]+-\d+) ', s, re.M); miss = set(ids) - {c[0] for c in C}; assert not miss, miss
s = s.split('\n## 11. Closure per item')[0].rstrip() + '\n'
s = re.sub(r'^Revision: C$', 'Revision: D', s, flags=re.M); s = re.sub(r'^Date: 2026-10-01  $', 'Date: 2026-10-16  ', s, flags=re.M)
if '| D | ' not in s: s = s.replace('| C | 1 | Egress controlling-code rule; CRYO_EGRESS stubs; layout locks (PV/terrace/dock) | 2026-10-01 |', '| C | 1 | Egress controlling-code rule; CRYO_EGRESS stubs; layout locks (PV/terrace/dock) | 2026-10-01 |\n| D | 11 | X-COD-01: every row closed to a state with evidence (section 11) | 2026-10-16 |')
from collections import Counter
K = Counter(c[2] for c in C)
s += '\n## 11. Closure per item (X-COD-01)\n\nThis section is generated by `docs-authority/_compliance.py` and records the current state of every row. The states are: Closed (study), the design evidence exists in a generated document and confirmation by the authority having jurisdiction or a professional engineer still applies; Open (design), a deliverable is missing and the task that closes it is named; Open (external), the item needs the site, the authority having jurisdiction, the utility, a fire engineer or a physical test; Open (owner), the item needs a programme or management-system decision; N/A, not applicable.\n\nTable 11.1. Closure state of each row\n\n| ID | Evidence | State | Remaining |\n|---|---|---|---|\n'
s += '\n'.join(f'| {a} | {b} | {c} | {d} |' for a, b, c, d in C) + '\n'
open(p, 'w').write(s); print(dict(K))
