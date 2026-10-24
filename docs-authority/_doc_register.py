# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Document number register (AQS-REG-001), generated from the pages' own front matter.

Each page states its number in its first lines:

    Document number: AQS-XXX-NNN
    Former number: AQS-OLD-NNN (optional, one or more; why it changed)

An older page may instead say "Renumbered <date> from AQS-OLD-NNN ..."; that reads the same.

A number followed by a qualifier ("sheet MF-01", "annex", "note ...") names a part of that
document and is not a separate claim. The register is a pure function of the pages, so it
never needs hand-editing and never disagrees with them.

    python3 docs-authority/_doc_register.py              # write docs-authority/DOC_REGISTER.md
    python3 docs-authority/_doc_register.py --check      # exit 1 on a duplicate or missing number
    python3 docs-authority/_doc_register.py --next AQS-DUTY   # next free number in a series

Rules (checked by --check and flow_graph/test_doc_numbers.py):
- a number is claimed by at most one page;
- every page directly under docs-authority/ (except README.md) has a number;
- a former number is never issued again (--next skips it); it may still be held by the page that shared it.
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = 'docs-authority/DOC_REGISTER.md'
NUM = r'AQS-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*'
CLAIM = re.compile(r'^\**Document(?: number)?\**:?\**\s*\**`?(' + NUM + r')`?\**\s*(.*)$', re.M)
FORMER = re.compile(r'^(?:\**Former numbers?\**:?\**\s*|Renumbered \S+ from )(.+)$', re.M)
PART_WORDS = ('sheet', 'annex', 'note', 'part', 'companion', '(folder')
HEAD_LINES = 30
REV, DATE = 'B', '2026-10-24'   # this register's own revision (it lists itself)


def tracked_md():
    try:
        out = subprocess.run(['git', 'ls-files', '-z', '*.md'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        files = [f for f in out.split('\0') if f]
    except (OSError, subprocess.CalledProcessError):
        files = [os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT) if '.git' not in d for f in fs if f.endswith('.md')]
    return sorted(f for f in files if os.path.isfile(os.path.join(ROOT, f)))


def required(path):
    d, f = os.path.split(path)
    return d == 'docs-authority' and f != 'README.md'


def scan():
    """Return (claims, parts, formers, problems). claims: number -> [page dicts]."""
    claims, parts, formers, problems = defaultdict(list), [], [], []
    for p in tracked_md():
        text = open(os.path.join(ROOT, p), errors='replace').read()
        head = '\n'.join(text.split('\n')[:HEAD_LINES])
        m = CLAIM.search(head)
        title = (re.search(r'^# (.+)$', text, flags=re.M) or [None, ''])[1].strip()
        rev = (re.search(r'^\**Revision\**:?\**\s*\**([A-Za-z0-9+]+)', head, flags=re.M) or [None, '—'])[1]
        date = (re.search(r'^\**Date\**:?\**\s*\**([0-9]{4}-[0-9]{2}-[0-9]{2})', head, flags=re.M) or [None, '—'])[1]
        if p == OUT:
            rev, date = REV, DATE
        sup = re.search(r'^\**Superseded by\**\b.*?(' + NUM + ')', head, flags=re.M)
        status = f'superseded by {sup.group(1)}' if sup else 'current'
        page = dict(path=p, title=title, rev=rev, date=date, status=status)
        if m:
            tail = m.group(2).strip(' *`.,;:').lower()
            if tail.startswith(PART_WORDS):
                parts.append(dict(page, number=m.group(1), qualifier=m.group(2).strip(' *`')[:60]))
            else:
                claims[m.group(1)].append(dict(page, number=m.group(1)))
                for fm in FORMER.finditer(head):  # the first number on the line is the former one
                    old = re.match(r'\W*(' + NUM + ')', fm.group(1))
                    if old:
                        formers.append(dict(old=old.group(1), new=m.group(1), path=p, note=fm.group(1).strip()))
        elif required(p):
            problems.append(f'{p}: no "Document number:" line in its first {HEAD_LINES} lines')
    for num, pages in claims.items():
        if len(pages) > 1:
            problems.append(f'{num} is claimed by {len(pages)} pages: ' + ', '.join(x["path"] for x in pages))
    return claims, parts, formers, problems


def series_of(num):
    m = re.match(r'^(AQS-[A-Za-z0-9_]+(?:-[A-Za-z_][A-Za-z0-9_]*)*)-(\d{3})$', num)
    return (m.group(1), int(m.group(2))) if m else (None, None)


def next_free(series):
    claims, parts, formers, _ = scan()
    used = set(claims) | {f['old'] for f in formers} | {p['number'] for p in parts}
    n = max([series_of(x)[1] for x in used if series_of(x)[0] == series] + [0]) + 1
    while f'{series}-{n:03d}' in used:
        n += 1
    return f'{series}-{n:03d}'


def cell(s):
    return str(s).replace('|', '/').strip()


def render(claims, parts, formers):
    """The register text for a scan; a pure function of the pages."""
    L = ['# Document number register', '', 'Document number: AQS-REG-001', f'Revision: {REV}', f'Date: {DATE}',
         'Authority: AQS-PLAN-007 task X-GOV-04. Generated by `docs-authority/_doc_register.py` from the "Document number:" '
         'and "Former number:" lines at the top of every Markdown page. Do not edit; change the page and run the pipeline.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         '| A | First issue (hand-built); duplicate numbers resolved by renumbering. | 2026-10-15 |',
         '| B | Generated from front matter; remaining duplicates renumbered with their old numbers kept as former numbers; '
         'numbers made mandatory for pages under docs-authority/. | 2026-10-24 |', '',
         '## 1. Rules', '',
         '- A number belongs to one page. The page states it in its first lines as `Document number: AQS-XXX-NNN`.',
         '- Every page directly under `docs-authority/` has a number. Folder indexes (`README.md`) do not.',
         '- A new page takes the next free number in its series: '
         '`python3 docs-authority/_doc_register.py --next AQS-XXX`.',
         '- A page that is renumbered keeps its old number on a `Former number:` line, so older citations can be '
         'resolved (section 3). A former number is never reissued. Where two pages once shared a number, a citation '
         'of it before 2026-10-24 may mean either; section 3 names both.',
         '- A number followed by a qualifier (for example `AQS-INV-005 sheet MF-01`) names a part of that document '
         '(section 4).',
         '- `flow_graph/test_doc_numbers.py` fails on a duplicate or missing number.', '',
         '## 2. Register', '', 'Status is "superseded by" when the page opens with a `Superseded by ...` line naming its successor.', '',
          '| Number | Page | Rev | Date | Title | Status |', '| --- | --- | --- | --- | --- | --- |']
    for num in sorted(claims, key=lambda n: (series_of(n)[0] or n, series_of(n)[1] or 0, n)):
        x = claims[num][0]
        L.append(f'| {num} | `{x["path"]}` | {x["rev"]} | {x["date"]} | {cell(x["title"])} | {x["status"]} |')
    L += ['', '## 3. Former numbers', '',
          'Older documents may cite these numbers. Read them as the current number shown.', '',
          '| Former | Current | Page | Former number still held by | Note |', '| --- | --- | --- | --- | --- |']
    for f in sorted(formers, key=lambda f: (f['old'], f['new'])):
        held = ', '.join(f'`{x["path"]}`' for x in claims.get(f['old'], []) if x['path'] != f['path']) or '—'
        L.append(f'| {f["old"]} | {f["new"]} | `{f["path"]}` | {held} | {cell(f["note"])} |')
    L += ['', '## 4. Parts of numbered documents', '', '| Number | Part | Page |', '| --- | --- | --- |']
    for p in sorted(parts, key=lambda p: (p['number'], p['path'])):
        L.append(f'| {p["number"]} | {cell(p["qualifier"])} | `{p["path"]}` |')
    return '\n'.join(L) + '\n'


def write():
    claims, parts, formers, problems = scan()
    if problems:
        raise SystemExit('DOC_REGISTER not written:\n  ' + '\n  '.join(problems))
    txt = render(claims, parts, formers)
    path = os.path.join(ROOT, OUT)
    if not os.path.exists(path) or open(path).read() != txt:
        open(path, 'w').write(txt)
    print(f'DOC_REGISTER.md: {len(claims)} numbers, {len(formers)} former, {len(parts)} parts')


if __name__ == '__main__':
    if '--next' in sys.argv:
        print(next_free(sys.argv[sys.argv.index('--next') + 1]))
    elif '--check' in sys.argv:
        probs = scan()[3]
        print('\n'.join(probs) or 'document numbers: unique and present')
        sys.exit(1 if probs else 0)
    else:
        write()
