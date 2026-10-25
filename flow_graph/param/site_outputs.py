# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Locale regeneration into sites/<site_id>/ (AQS-PLAN-011 section 4.4, task X-LOC-04).

A locale is regenerated in a temporary git worktree of HEAD with AQS_SITE set, so the baseline files
in this working tree are never written. The outputs that differ from the baseline are copied to
sites/<site_id>/ under their repository paths; sites/<site_id>/SITE_OUTPUTS.json lists them with the
hash of the profile. An output not listed is the same as the baseline output. A copied document keeps
its base number with the site code as a suffix (section 4.5). Nothing is written outside
sites/<site_id>/."""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from . import site as S

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_WT = 'AQS_LOCALE_WORKTREE'        # set only by this module, to the worktree it created
MANIFEST = 'SITE_OUTPUTS.json'
# Commit-stamped registers: their content names commits, so a locale copy would go stale at every commit.
SKIP = {'docs-authority/DERIVED_REVISIONS.md'}
NUM_LINE = re.compile(r'^(\**Document(?: number)?\**:?\**\s*\**`?)(AQS-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*)(?![A-Za-z0-9_/-])', re.M)


def git(*args, cwd=ROOT):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def site_dir(sid, root=ROOT):
    if sid == S.BASELINE: raise SystemExit('the baseline outputs stay in place; they have no sites/ folder')
    if not re.match(r'^[a-z][a-z0-9_]*$', sid): raise SystemExit(f'bad site id {sid!r}')
    return os.path.join(root, 'sites', sid)


def target(sid, rel, root=ROOT):
    """Path of a locale copy of repository path rel. Refuses any path that would leave sites/<site_id>/."""
    base = os.path.realpath(site_dir(sid, root))
    p = os.path.realpath(os.path.join(base, rel))
    if os.path.isabs(rel) or not p.startswith(base + os.sep):
        raise SystemExit(f'{rel}: a locale output must stay under sites/{sid}/')
    return p


def suffix_numbers(text, code):
    """Add the site code to the document number line in the first lines of a page."""
    lines = text.split('\n')
    top = '\n'.join(lines[:30]); tail = '\n'.join(lines[30:])
    top = NUM_LINE.sub(lambda m: m.group(1) + m.group(2) + '/' + code, top, count=1)
    return top + ('\n' + tail if len(lines) > 30 else '')


def profile_hash(sid, root=ROOT):
    return hashlib.sha256(open(os.path.join(root, 'flow_graph', 'param', 'sites', f'{sid}.json'), 'rb').read()).hexdigest()


def changed(wt):
    out = []
    for l in git('status', '--porcelain', '--untracked-files=all', cwd=wt).splitlines():
        f = l[3:].strip('"')
        if f.startswith('sites/') or f in SKIP: continue
        out.append(f)
    return sorted(out)


def collect(sid, wt, root=ROOT):
    """Return {repo path: bytes} for the locale outputs in worktree wt, with document numbers suffixed."""
    code = S.load_profile(sid).get('site_code')
    if not code: raise SystemExit(f'{sid}: a locale profile needs a site_code')
    out = {}
    for f in changed(wt):
        p = os.path.join(wt, f)
        if not os.path.isfile(p): continue          # an output the locale removes is recorded as removed
        b = open(p, 'rb').read()
        if f.endswith('.md'): b = suffix_numbers(b.decode('utf-8'), code).encode('utf-8')
        out[f] = b
    return out


def write(sid, files, removed, root=ROOT):
    d = site_dir(sid, root)
    if os.path.isdir(d): shutil.rmtree(d)
    for f, b in files.items():
        p = target(sid, f, root); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(b)
    man = {'site_id': sid, 'profile_sha256': profile_hash(sid, root), 'outputs': sorted(files), 'removed': sorted(removed),
           'note': 'Outputs not listed are the same as the baseline outputs at the same commit.'}
    p = target(sid, MANIFEST, root); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(json.dumps(man, indent=1) + '\n')
    return man


def read(sid, root=ROOT):
    d = site_dir(sid, root); out = {}
    for dp, _, fs in os.walk(d):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), d)
            if rel != MANIFEST: out[rel] = open(os.path.join(dp, f), 'rb').read()
    return out


def run(sid, check=False, extra=()):
    """Regenerate locale sid in a temporary worktree of HEAD; write sites/<sid>/, or with check=True compare
    the fresh outputs with sites/<sid>/ and write nothing. Returns 0 or 1."""
    S.load_profile(sid)                                   # fails on an unknown or invalid profile
    rel = f'flow_graph/param/sites/{sid}.json'
    if git('status', '--porcelain', '--', rel).strip():
        raise SystemExit(f'{rel} has uncommitted changes; a locale runs from HEAD, so commit the profile first')
    tmp = tempfile.mkdtemp(prefix=f'aqs-site-{sid}-'); wt = os.path.join(tmp, 'wt')
    try:
        git('worktree', 'add', '--detach', wt, 'HEAD')
        env = dict(os.environ, AQS_SITE=sid, **{ENV_WT: os.path.realpath(wt)})
        r = subprocess.run([sys.executable, '-m', 'flow_graph.param.regen', *extra], cwd=wt, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print((r.stdout + r.stderr)[-3000:]); raise SystemExit(f'{sid}: locale regeneration failed')
        files = collect(sid, wt)
        removed = [f for f in changed(wt) if not os.path.isfile(os.path.join(wt, f))]
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', wt], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
    if check:
        have = read(sid) if os.path.isdir(site_dir(sid)) else {}
        stale = sorted(f for f in set(files) | set(have) if files.get(f) != have.get(f))
        print(f'{sid}: ' + ('current' if not stale else f'{len(stale)} stale output(s), e.g. {stale[:5]}'))
        return 0 if not stale else 1
    man = write(sid, files, removed)
    print(f"{sid}: {len(man['outputs'])} output(s) differ from the baseline -> sites/{sid}/")
    return 0


def locales(root=ROOT):
    return [s for s in S.available() if s != S.BASELINE]


def in_locale_worktree(root):
    """True when this process runs inside a worktree that run() created for a locale."""
    return os.environ.get(ENV_WT) == os.path.realpath(root)
