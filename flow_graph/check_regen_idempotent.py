"""Full-regen idempotency check (AQS-PAR-001 U3).

A full `python3 -m flow_graph.param.regen` on a clean, committed tree must leave the tree
unchanged, and a second run must leave it unchanged again. Any difference means a generator
is non-deterministic, a stage is missing from flow_graph/param/regen_manifest.json, or a
committed derived file is stale.

    python3 flow_graph/check_regen_idempotent.py                # HEAD, in a temporary worktree
    python3 flow_graph/check_regen_idempotent.py --in-place     # this working tree (must be clean)
    python3 flow_graph/check_regen_idempotent.py --repeat-only  # only: the second run changes nothing

The default (strict) mode requires both: the first run reproduces the committed tree, and the
second run reproduces the first. --repeat-only checks determinism alone. Use it where the
toolchain differs from the one that produced the committed renders (e.g. CI with another
matplotlib or ffmpeg build), so raster and video bytes may legitimately differ from HEAD.

Exit 0 when the checked runs leave no difference; exit 1 and list the changed files otherwise.
"""
import argparse, hashlib, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args, cwd):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def changed(cwd):
    return [l[3:] for l in git('status', '--porcelain', '--untracked-files=all', cwd=cwd).splitlines()]


def snapshot(cwd):
    files = git('ls-files', '-co', '--exclude-standard', '-z', cwd=cwd).split('\0')
    out = {}
    for f in files:
        p = os.path.join(cwd, f)
        if f and os.path.isfile(p):
            out[f] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    return out


def regen(cwd):
    r = subprocess.run([sys.executable, '-m', 'flow_graph.param.regen'], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:] + r.stderr[-3000:])
        raise SystemExit('regen failed; idempotency not checked')


def check(cwd, repeat_only=False):
    if changed(cwd):
        raise SystemExit('working tree is not clean; commit or stash first (or run without --in-place)')
    regen(cwd)
    first = changed(cwd)
    if first and not repeat_only:
        print(f'first full regen changed {len(first)} file(s) against HEAD:')
        for f in first[:50]:
            print('  ' + f)
        if len(first) > 50:
            print('  ...')
        return False
    print('first full regen: ' + ('no change against HEAD' if not first else f'{len(first)} file(s) differ from HEAD (not checked: --repeat-only)'))
    before = snapshot(cwd)
    regen(cwd)
    after = snapshot(cwd)
    diff = sorted(f for f in set(before) | set(after) if before.get(f) != after.get(f))
    if diff:
        print(f'second full regen changed {len(diff)} file(s) against the first:')
        for f in diff[:50]:
            print('  ' + f)
        return False
    print('second full regen: no change against the first')
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--in-place', action='store_true', help='check this working tree instead of a temporary worktree of HEAD')
    ap.add_argument('--repeat-only', action='store_true', help='check only that a second run changes nothing (toolchain-independent)')
    args = ap.parse_args(argv)
    if args.in_place:
        return 0 if check(ROOT, args.repeat_only) else 1
    tmp = tempfile.mkdtemp(prefix='aqs-regen-idem-')
    wt = os.path.join(tmp, 'wt')
    try:
        git('worktree', 'add', '--detach', wt, 'HEAD', cwd=ROOT)
        return 0 if check(wt, args.repeat_only) else 1
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', wt], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
