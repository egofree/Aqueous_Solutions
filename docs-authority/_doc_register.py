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
REV, DATE = 'C', '2026-10-25'   # this register's own revision (it lists itself)
# Numbers of pages that were deleted. They are never issued again (next_free skips them) and no page may claim them.
WITHDRAWN = {
    'AQS-DUTY-081': ('docs-authority/DUTY_CALC.md', '2026-10-25',   # retired path
                     'Orphaned snapshot of a retired duty calculation at an earlier graph revision; no generator writes it '
                     'and no document cites it. The unit duty sheets in docs-authority/duties/ replace it.'),
    'AQS-ISO-003': ('docs-authority/ISOMETRIC.md', '2026-10-25',   # retired path
                    'Orphaned list of close-pipe isometrics for IA-CLOSE edges, most of which are no longer in the graph; '
                    'no generator writes it. The per-line isometric set AQS-ISO-002 replaces it.'),
}


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
                parts.append(dict(page, number=m.group(1), qualifier=re.split(r'\.\s', m.group(2).strip(' *`'))[0].rstrip('.')[:60]))
            else:
                claims[m.group(1)].append(dict(page, number=m.group(1)))
                for fm in FORMER.finditer(head):  # the first number on the line is the former one
                    old = re.match(r'\W*(' + NUM + ')', fm.group(1))
                    if old:
                        formers.append(dict(old=old.group(1), new=m.group(1), path=p, note=fm.group(1).strip()))
        if m and m.group(1) in WITHDRAWN:
            problems.append(f'{p}: claims withdrawn number {m.group(1)}')
        if not m and required(p):
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
    used = set(claims) | {f['old'] for f in formers} | {p['number'] for p in parts} | set(WITHDRAWN)
    n = max([series_of(x)[1] for x in used if series_of(x)[0] == series] + [0]) + 1
    while f'{series}-{n:03d}' in used:
        n += 1
    return f'{series}-{n:03d}'


def cell(s):
    return str(s).replace('|', '/').strip()


def render(claims, parts, formers):
    """The register text for a scan; a pure function of the pages."""
    L = ['# Document number register', '', 'Document number: AQS-REG-001', f'Revision: {REV}', f'Date: {DATE}',
         'Generated by `docs-authority/_doc_register.py` from the "Document number:" and "Former number:" lines at '
         'the top of every Markdown page. Do not edit this page by hand; change the page concerned and run the '
         'pipeline.', '',
         '| Rev | Description | Date |', '| --- | --- | --- |',
         '| A | First issue, compiled by hand; duplicate numbers resolved by renumbering. | 2026-10-15 |',
         '| B | Generated from the identity lines of each page; remaining duplicates renumbered with their old numbers '
         'kept as former numbers; a number made mandatory for every page directly under docs-authority/. | 2026-10-24 |',
         '| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). | 2026-10-25 |', '',
         '## 1. Purpose and scope', '',
         'Every controlled page in this repository carries a document number, such as AQS-SEC-001, so that other '
         'pages, drawings and tests can cite it without depending on its file name. This register lists every number '
         'in use, the page that holds it, the revision and date that page states, and whether a later page has '
         'superseded it. It also lists the numbers that pages held before they were renumbered, so that a reader can '
         'resolve a citation found in an older document.', '',
         'The register covers every tracked Markdown page that states a document number in its first lines. It does '
         'not judge whether a page is complete or correct; the task plan (AQS-PLAN-007) tracks that.', '',
         '## 2. Numbering rules', '',
         '- Each number belongs to one page. The page states it in its first lines as `Document number: AQS-XXX-NNN`, '
         'where `XXX` is the series and `NNN` is the sequence number within the series.',
         '- Every page directly under `docs-authority/` has a number. Folder indexes (`README.md`) do not.',
         '- A new page takes the next free number in its series. Run '
         '`python3 docs-authority/_doc_register.py --next AQS-XXX` to find it.',
         '- A page that is renumbered keeps its old number on a `Former number:` line, so that older citations can '
         'still be resolved (section 4). A former number is never issued again. Where two pages once shared a number, '
         'a citation of that number dated before 2026-10-24 may refer to either page; section 4 names both.',
         '- When a page is deleted, its number is withdrawn and listed in section 6. A withdrawn number is never '
         'issued again.',
         '- A number followed by a qualifier, for example `AQS-INV-005 sheet MF-01`, names a part of that document '
         'and is listed in section 5.',
         '- The test `flow_graph/test_doc_numbers.py` fails if a number is claimed twice or if a page that needs a '
         'number has none.', '',
         '## 3. Register', '',
         'Table 3.1 lists the numbers in use. The status column reads "superseded by" followed by a number when the '
         'page opens with a `Superseded by` line that names its successor; otherwise it reads "current".', '',
         'Table 3.1. Document numbers in use', '',
          '| Number | Page | Rev | Date | Title | Status |', '| --- | --- | --- | --- | --- | --- |']
    for num in sorted(claims, key=lambda n: (series_of(n)[0] or n, series_of(n)[1] or 0, n)):
        x = claims[num][0]
        L.append(f'| {num} | `{x["path"]}` | {x["rev"]} | {x["date"]} | {cell(x["title"])} | {x["status"]} |')
    L += ['', '## 4. Former numbers', '',
          'Table 4.1 lists numbers that pages held before they were renumbered. Older documents may cite these '
          'numbers. Read each one as the current number shown in the same row.', '',
          'Table 4.1. Former numbers and their current equivalents', '',
          '| Former | Current | Page | Former number still held by | Note |', '| --- | --- | --- | --- | --- |']
    for f in sorted(formers, key=lambda f: (f['old'], f['new'])):
        held = ', '.join(f'`{x["path"]}`' for x in claims.get(f['old'], []) if x['path'] != f['path']) or '—'
        L.append(f'| {f["old"]} | {f["new"]} | `{f["path"]}` | {held} | {cell(f["note"])} |')
    L += ['', '## 5. Parts of numbered documents', '',
          'Table 5.1 lists pages that form part of a numbered document, such as the individual sheets of a '
          'generated inventory. They share the parent number and add a qualifier.', '',
          'Table 5.1. Parts of numbered documents', '', '| Number | Part | Page |', '| --- | --- | --- |']
    for p in sorted(parts, key=lambda p: (p['number'], p['path'])):
        L.append(f'| {p["number"]} | {cell(p["qualifier"])} | `{p["path"]}` |')
    L += ['', '## 6. Withdrawn numbers', '',
          'Table 6.1 lists the numbers of pages that have been deleted from the repository. A withdrawn number is never '
          'issued again. The deleted page remains in the git history.', '',
          'Table 6.1. Withdrawn numbers', '', '| Number | Former page | Withdrawn | Reason |', '| --- | --- | --- | --- |']
    for num, (path, when, why) in sorted(WITHDRAWN.items()):
        L.append(f'| {num} | `{path}` | {when} | {cell(why)} |')
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
