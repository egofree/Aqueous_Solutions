"""Input-hash manifest: which files each regen stage was made from, and staleness from that
(pipeline-simplification step 4, docs-authority/notes/2026-11-04-pipeline-simplification-plan.md).

flow_graph/param/regen.py writes flow_graph/derived/_input_manifest.json on every full run:
per stage, the hash of every project file the stage (or anything it spawned) actually opened
for reading, hashed once after the run settled, plus the stage's final-pass status. A derived
file is stale under this rule when its producing stage's recorded inputs no longer hash the
same, or when that stage did not finish ok. Content, not commit order, decides.

docs-authority/_rev_stamp.py evaluates this rule in parallel with its committed rule until the
two agree on every file; the gate still follows the committed rule until step 5 of the plan.
"""
import glob, hashlib, json, os

MANIFEST_NAME = 'flow_graph/derived/_input_manifest.json'
GENERATED_BY = 'flow_graph/param/regen.py'


def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def _hash_of(path, cache):
    if cache is None:
        return hash_file(path) if os.path.isfile(path) else None
    if path not in cache:
        cache[path] = hash_file(path) if os.path.isfile(path) else None
    return cache[path]


def build(captures, root, graph_sha256):
    """The manifest dict from {stage: {'paths': set, 'status': str, 'complete': bool}}.

    Inputs are hashed now, after the run settled, so a circular input (a document that
    feeds another document) hashes to its final content -- what the settling pass read.
    A captured file already gone at hashing time is recorded under missing_inputs and
    decides stale; its stage keeps capture_incomplete only for true capture holes
    (the wrapper fallback, a lost sidecar).
    """
    stages = {}
    for name in sorted(captures):
        c = captures[name]
        inputs, missing = {}, []
        for p in sorted(c.get('paths') or ()):
            rel = os.path.relpath(p, root)
            if os.path.isfile(p):
                inputs[rel] = hash_file(p)
            else:
                missing.append(rel)          # read during the run, gone before hashing: recorded, decides stale
        stages[name] = {'status': c.get('status', 'unknown'), 'inputs': inputs}
        if missing:
            stages[name]['missing_inputs'] = missing
        if not c.get('complete', True):
            stages[name]['capture_incomplete'] = True
    return {'manifest_version': 1, 'generated_by': GENERATED_BY,
            'graph_sha256': graph_sha256, 'stages': stages}


def write(manifest, root):
    path = os.path.join(root, MANIFEST_NAME)
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write('\n')
    return path


def load(root):
    path = os.path.join(root, MANIFEST_NAME)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def output_stage_map(regen_manifest, root):
    """Derived file (repo-relative) -> the stages that write or amend it."""
    out = {}
    for s in regen_manifest['stages']:
        owned = set()
        for pat in s.get('outputs', []) + s.get('amends', []):
            owned.update(os.path.relpath(f, root) for f in glob.glob(os.path.join(root, pat), recursive=True))
        for f in owned:
            out.setdefault(f, []).append(s['name'])
    return out


def verdict(manifest, stage_map, relfile, root, cache=None):
    """Staleness of one derived file under the input-hash rule.

    cache: an optional {path: sha} dict reused across calls (a long census over many
    files hashes each input once); a caller that mutates inputs between verdicts passes
    no cache. Returns (verdict, detail) with verdict one of:
      fresh, stale           - the rule decided (detail names the reason)
      producer-failed        - its stage's final pass was not ok (counts as stale downstream)
      no-stage               - no manifest stage claims this file
      no-entry               - the stage ran but is not in this manifest (partial/older run)
      capture-incomplete     - the stage's reads were not fully recorded (wrapper fallback,
                               non-Python grandchildren); the rule abstains
      no-manifest            - the manifest file is absent (pre-gate)
    """
    if manifest is None:
        return 'no-manifest', 'flow_graph/derived/_input_manifest.json absent'
    names = stage_map.get(relfile, [])
    if not names:
        return 'no-stage', 'no manifest stage writes or amends this file'
    reasons = []
    for name in names:
        entry = manifest['stages'].get(name)
        if entry is None:
            return 'no-entry', f'stage {name} not in the manifest'
        if entry.get('capture_incomplete'):
            return 'capture-incomplete', f'stage {name} reads not fully recorded'
        if entry['status'] != 'ok':
            reasons.append(f'stage {name} final pass {entry["status"]}')
            continue
        for rel in entry.get('missing_inputs') or ():
            reasons.append(f'{rel} vanished at manifest build')
        for rel, sha in sorted(entry['inputs'].items()):
            p = os.path.join(root, rel)
            cur = _hash_of(p, cache)
            if cur is None:
                reasons.append(f'{rel} vanished')
            elif cur != sha:
                reasons.append(f'{rel} changed')
    if reasons:
        return 'stale', '; '.join(reasons[:4]) + ('' if len(reasons) <= 4 else f' (+{len(reasons) - 4} more)')
    return 'fresh', 'all recorded inputs match'


def census(manifest, stage_map, root, old_status):
    """Compare the input-hash rule with the committed rule across registered derived files.

    old_status: {relfile: 'current' | 'stale' | other} from the committed evaluation.
    Returns {'agree': n, 'input_stale': [files], 'input_fresh': [files], 'unmeasured': n}
    where input_stale lists files the committed rule calls current but the input-hash rule
    calls stale (the under-declared risk the plan names) and input_fresh the reverse.
    """
    agree = unmeasured = 0
    input_stale, input_fresh = [], []
    for f, old in sorted(old_status.items()):
        if old not in ('current', 'stale'):
            unmeasured += 1
            continue
        v, _ = verdict(manifest, stage_map, f, root)
        if v == 'fresh':
            if old == 'current':
                agree += 1
            else:
                input_fresh.append(f)
        elif v in ('stale', 'producer-failed'):
            if old == 'stale':
                agree += 1
            else:
                input_stale.append(f)
        else:
            unmeasured += 1
    return {'agree': agree, 'input_stale': input_stale, 'input_fresh': input_fresh,
            'unmeasured': unmeasured}
