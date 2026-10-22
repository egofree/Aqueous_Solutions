"""AQS-STD-002 section 14 census (X-MAT-03, Rev N). Elastomer and gasket compatibility per service.

Done-when evidence for "per service":
  1. parses the AQS-PIP-003 Rev A class rows out of docs-authority/PIPING_CLASSES.md,
  2. parses the docs-authority/MATERIALS_STD.md section 14.1 per-class decision rows and the
     section 14.2 family-exception rows,
  3. asserts every PIP-003 class has a section 14.1 decision row, every section 12.1 family
     class letter is covered by a 14.1 or 14.2 row, and every 14.1/14.2 row cites at least one
     registered source ([Snn] token, PERRY9_MAT, ULLMANN_FLUOROPOLY, AQS-REV-H2-001) or a
     named deferral (unit task 09, PIP-003 Rev B, a section cross-reference),
  4. exits 1 on any uncovered class, uncovered family class, or unsourced row.

Read-only. Rerun whenever either document changes.
"""
import re, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
pip = open('docs-authority/PIPING_CLASSES.md').read()
mat = open('docs-authority/MATERIALS_STD.md').read()

CLS = r'(P[1-5]|M[12]|G1|F1)'
def cited(l):
    return bool(re.search(r'\[(S\d+)[^\]]*\]|PERRY9_MAT|ULLMANN_FLUOROPOLY|AQS-REV-H2-001', l)
                or re.search(r'unit task 09|PIP-003 Rev B|section 12|section 13\.1|14\.1 P5', l))

pip_classes = set()
for line in pip.splitlines():
    m = re.match(r'^\| ' + CLS + r' \|', line)
    if m: pip_classes.add(m.group(1))

i = mat.index('### 14.1'); j = min(x for x in (mat.find('\n### ', i+1), mat.find('\n## ', i+1)) if x != -1)
s141 = mat[i:j]
i = mat.index('### 14.2'); j = mat.find('\n## ', i+1); j = j if j != -1 else len(mat)
s142 = mat[i:j]

rows141 = {}
for line in s141.splitlines():
    m = re.match(r'^\| (P[1-5]|M[12]|G1|F1)[ ]', line)
    if m: rows141.setdefault(m.group(1), []).append(line)
rows142 = [l for l in s142.splitlines() if l.startswith('|') and not l.startswith('| Service') and not l.startswith('| ---')]

rc = 0
missing_cls = sorted(pip_classes - set(rows141))
if missing_cls:
    print('no section 14.1 decision row for class(es):', ', '.join(missing_cls)); rc = 1
else:
    print(f'PIP-003 classes ({len(pip_classes)}): all covered in section 14.1')
unsourced = [x[1] for x in ((k, l) for k, v in rows141.items() for l in v) if not cited(x[1])]
unsourced += [l.split('|')[1].strip() for l in rows142 if not cited(l)]
if unsourced:
    print('rows with no registered source or named deferral:', unsourced[:8]); rc = 1
else:
    print(f'section 14 rows: {sum(len(v) for v in rows141.values())} per-class + {len(rows142)} family rows, all sourced')

fam_classes = set()
for line in mat.splitlines():
    m = re.match(r'^\| [^|]+\| ' + CLS + r' \| \d+', line)
    if m: fam_classes.add(m.group(1))
covered = set(rows141) | set(re.findall(r'\b' + CLS + r'\b', '\n'.join(rows142)))
uncovered = sorted(fam_classes - covered)
if uncovered:
    print('section 12.1 families with class(es) not covered by section 14:', uncovered); rc = 1
else:
    print(f'section 12.1 family classes ({len(fam_classes)}): all covered by section 14')
print('X-MAT-03 gasket census:', 'OK' if rc == 0 else 'NOT OK')
sys.exit(rc)
