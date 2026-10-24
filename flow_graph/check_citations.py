# SPDX-License-Identifier: MIT
# Copyright 2026 Mike Matthews.
"""Live text must not cite a retired document number, sector, path or commit.

Data, not lists in code:
  * former document numbers: the "Former number:" lines on renumbered pages (docs-authority/_doc_register.py scan);
  * retired sector ids: RETIRED_SECTOR_IDS in design_tool/aqs_design_tool/sector_definitions.py, with the
    sector_use rules in docs-authority/retired_names.json for ids that are also ordinary words;
  * retired paths and script names: docs-authority/retired_names.json; beyond that, any repository path a page cites must exist;
  * commits: docs-authority/rewritten_commits.json maps pre-rewrite commit ids to their rewritten ids; any id cited
    after the word "commit" or "HEAD" must exist in the history.
A line that states the history itself ("Former number: ...", "renamed from ...", "formerly ...") is an alias and is allowed,
as are the files that hold the alias data and the generated register that lists the former numbers.

    python3 -m flow_graph.check_citations           # report
    python3 -m flow_graph.check_citations --fix     # rewrite retired paths and former numbers in place"""
import fnmatch, glob, importlib.util, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = ('.md', '.py', '.sh', '.txt', '.yml', '.yaml', '.toml', '.cfg', '.ini', '.scad', '.st')
ALIAS_LINE = re.compile(r'Former numbers?|Renumbered \S+ from|renamed from|formerly|previously|moved from|retired|superseded|was renamed'
                        r'|numbered \S+ until \d{4}-\d{2}-\d{2}|until \d{4}-\d{2}-\d{2}|registered twice|duplicate', re.I)
DONE_WHEN = re.compile(r'Done when:(.*?)(?:Evidence:|$)')   # a task's acceptance criterion names a file it will create
PLANNED = '(to be created)'                                  # prose marker for a planned file
HISTORY_COLUMN = re.compile(r'^(Removed|Former|Old|Retired|Was)\b', re.I)   # table column that records what is gone
HEX = re.compile(r'\b[0-9a-f]{7,40}\b')
COMMIT_REF = re.compile(r'(?:\bcommit|\bHEAD)[ :=`]+([0-9a-f]{7,40})\b')
NUM = re.compile(r'\bAQS-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*\b')


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True).stdout


def tracked():
    return [f for f in git('ls-files').splitlines() if os.path.isfile(os.path.join(ROOT, f))]


def load():
    sys.path.insert(0, os.path.join(ROOT, 'docs-authority'))
    import _doc_register as reg
    claims, _parts, formers, _ = reg.scan()
    rn = json.load(open(os.path.join(ROOT, 'docs-authority/retired_names.json')))
    former = {f['old']: f['new'] for f in formers if f['old'] not in claims}      # retired outright: every citation is stale
    reissued = {r['number']: r for r in rn.get('reissued_numbers', [])}
    missing = sorted({f['old'] for f in formers if f['old'] in claims} - set(reissued))
    assert not missing, f'renumbered pages whose old number is still held elsewhere need a reissued_numbers entry in retired_names.json: {missing}'
    spec = importlib.util.spec_from_file_location('sd', os.path.join(ROOT, 'design_tool/aqs_design_tool/sector_definitions.py'))
    sd = importlib.util.module_from_spec(spec); spec.loader.exec_module(sd)
    g = json.load(open(os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')))
    live_ids = {n['unit_id'] for n in g['nodes']} | {e['stream_id'] for e in g['edges']} | {s['sector_id'] for s in g['mvs']['sectors']}
    sectors = {k: v for k, v in sd.RETIRED_SECTOR_IDS.items() if k not in live_ids}   # a retired sector id reused as a unit id stays live
    exempt = {'design_tool/aqs_design_tool/sector_definitions.py', 'docs-authority/retired_names.json', reg.OUT,
              'flow_graph/check_citations.py'}
    man = json.load(open(os.path.join(ROOT, 'flow_graph/param/regen_manifest.json')))
    migrations = [g for n in man['not_stages'] if n['role'] == 'migration' for g in n['scripts']]   # one-time scripts kept as a record
    exempt.add('docs-authority/rewritten_commits.json')
    return former, reissued, sectors, rn['paths'], exempt, migrations, rn['sector_use'], rn.get('names', [])


def path_tokens(line):
    tops = TOPS
    return re.findall(r'(?<![\w/.<>-])((?:' + '|'.join(map(re.escape, tops)) + r')/[\w./<>*{}@+-]*[\w>*}/])', line)


TOPS = sorted({f.split('/')[0] for f in git('ls-files').splitlines() if '/' in f}
              | {r['old'].split('/')[0] for r in json.load(open(os.path.join(ROOT, 'docs-authority/retired_names.json')))['paths']})
FILES = None


def exists(p, base='', ignored_ok=True):
    """A cited path exists at the repository root or relative to the citing file's folder; placeholders act as wildcards."""
    p = re.sub(r'(\.\w+)/\.\w+$', r'\1', p)    # "LOAD_LIST.md/.json" shorthand
    p = p.replace('/.../', '/*/')
    return _exists(p, ignored_ok) or bool(base) and _exists(os.path.normpath(os.path.join(base, p)), ignored_ok)


def _exists(p, ignored_ok=True):
    global FILES
    if FILES is None:
        FILES = set(tracked()); FILES |= {d for f in list(FILES) for d in [f.rsplit('/', i)[0] for i in range(1, f.count('/') + 1)]}
    p = p.rstrip('/').rstrip('.')
    if p in FILES:
        return True
    p = re.sub(r'\{[^}]*$', '*', p)        # a brace list cut at its first comma: {A,B,...}
    if ignored_ok and subprocess.run(['git', 'check-ignore', '-q', p.replace('*', 'x')], cwd=ROOT).returncode == 0:
        return True                          # an ignored run output (log, scratch folder) that the text describes
    pat = re.sub(r'<[^>]*>|\{[^}]*\}|(?<=-)(?:nn|NN|xx|XX)\b', '*', p)
    return '*' in pat and any(fnmatch.fnmatch(f, pat) for f in FILES)


def retired_rule(p, rules):
    for r in rules:
        if p.startswith(r['old']) and not any(p.startswith(k) for k in r.get('keep', [])):
            return r
    return None


def replacement(p, rule):
    rest = p[len(rule['old']):]
    for now in rule['now']:
        cand = now + rest
        if exists(cand):
            return cand
    return None


def scan(fix=False):
    former, reissued, sectors, rules, exempt, migrations, use, names = load()
    name_res = [(n, re.compile(n['pattern'])) for n in names]
    sec_re = re.compile(r'(?<![\w-])(' + '|'.join(map(re.escape, sorted(sectors, key=len, reverse=True))) + r')(?![\w-])') if sectors else None
    history = re.compile(use['history_words'])
    as_sector = {w: re.compile('|'.join(p.replace('{id}', re.escape(w)) for p in use['patterns'])) for w in use['word_ids']}
    found = []
    old_ids = json.load(open(os.path.join(ROOT, 'docs-authority/rewritten_commits.json')))['map']
    known = {}
    def is_commit(t):
        if t not in known:
            known[t] = subprocess.run(['git', 'merge-base', '--is-ancestor', t, 'HEAD'], cwd=ROOT, capture_output=True).returncode == 0
        return known[t]
    for f in tracked():
        if not f.endswith(TEXT + ('.json',)) or f in exempt or any(fnmatch.fnmatch(f, g) for g in migrations):
            continue
        try:
            lines = open(os.path.join(ROOT, f), encoding='utf-8').read().split('\n')
        except UnicodeDecodeError:
            continue
        changed = False
        history_cols = set()
        for i, line in enumerate(lines):
            cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.lstrip().startswith('|') else None
            if cells and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i + 1]):
                history_cols = {k for k, c in enumerate(cells) if HISTORY_COLUMN.match(c)}
            elif not cells:
                history_cols = set()
            new = line
            for t in set(HEX.findall(line)):
                old = next((o for o in old_ids if o.startswith(t)), None)
                if old:
                    found.append((f, i + 1, 'pre-rewrite commit', t, old_ids[old][:len(t)]))
                    new = re.sub(r'\b' + t + r'\b', old_ids[old][:len(t)], new)
            for t in set(COMMIT_REF.findall(line)):
                if t not in old_ids and not any(o.startswith(t) for o in old_ids) and not is_commit(t):
                    found.append((f, i + 1, 'unknown commit', t, ''))
            if new != line:
                lines[i] = new; changed = True; line = new
            if ALIAS_LINE.search(line):
                continue
            for num in set(NUM.findall(line)):
                r = reissued.get(num)
                if r and re.search(r['context'], line) and not (r.get('unless') and re.search(r['unless'], line)):
                    found.append((f, i + 1, 'reissued number', num, f"{r['moved_to']} ({r['page']})"))
                    new = re.sub(r'\b' + re.escape(num) + r'\b', r['moved_to'], new)
                elif num in former:
                    found.append((f, i + 1, 'former number', num, former[num]))
                    new = re.sub(r'\b' + re.escape(num) + r'\b', former[num], new)
            for n, rx in name_res:
                if rx.search(line):
                    found.append((f, i + 1, 'retired name', n['old'], n['now']))
            if sec_re and not history.search(line):
                for sid in set(sec_re.findall(line)):
                    if sid in as_sector and not as_sector[sid].search(line):
                        continue
                    if any(re.search(r'\| ' + re.escape(sid) + r' \| ' + re.escape(now) + r'\b', line) for now in sectors[sid]['now']):
                        continue   # the alias table: retired id, then the sector that holds its units now
                    found.append((f, i + 1, 'retired sector', sid, ', '.join(sectors[sid]['now']) or 'retired'))
            dw = DONE_WHEN.search(line)
            for p in set(path_tokens(line)):
                if f.endswith('.py') and '{' in p:
                    continue   # an f-string template, not a citation
                if dw and p in dw.group(1):
                    continue
                if PLANNED in line[line.index(p):line.index(p) + len(p) + len(PLANNED) + 3]:
                    continue
                if history_cols and cells and any(p in cells[k] for k in history_cols if k < len(cells)):
                    continue
                rule = retired_rule(p, rules)
                if exists(p, os.path.dirname(f), ignored_ok=not rule):   # a retired folder may still be ignored locally
                    continue
                rep = replacement(p, rule) if rule else None
                found.append((f, i + 1, 'missing path', p, rep or (f"retired: {rule['old']} -> {', '.join(rule['now'])}" if rule else '')))
                if rep:
                    new = new.replace(p, rep)
            if new != line:
                lines[i] = new; changed = True
        if fix and changed:
            open(os.path.join(ROOT, f), 'w', encoding='utf-8').write('\n'.join(lines))
    return found


if __name__ == '__main__':
    res = scan(fix='--fix' in sys.argv)
    for r in res:
        print(' | '.join(map(str, r)))
    print(len(res), 'findings', file=sys.stderr)
