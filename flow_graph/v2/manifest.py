"""engine v2: the one staleness rule — input hashes plus per-function code
fingerprints, evaluated on demand. No commit-order rule, no vouch lists: content
decides, and the fingerprints close the code-edit hole (a transfer-function edit
changes its stage's fingerprint, so dependent artifacts show stale).

Fingerprints read source files directly (deterministic); they never record opens.
The default input set is the engine's declared data: the drivers, references,
assumptions, site profiles, and the grid declaration itself.
"""
import hashlib, inspect, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PKG = os.path.dirname(os.path.abspath(__file__))

INPUT_FILES = [
    'flow_graph/param/drivers.json',
    'flow_graph/param/refs.py',
    'docs-authority/assumptions_manual.json',
    'flow_graph/v2/grid.json',
]


def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def input_hashes(extra_paths=()):
    files = sorted(set(INPUT_FILES) | set(extra_paths))
    return {p: _sha(os.path.join(ROOT, p)) for p in files}


def code_fingerprint(fn_obj):
    """sha256 of a solve function's own source. Within one file the source block
    is deterministic; combined with the package fingerprint (which catches helper
    edits), a function's fingerprint identifies its code."""
    return hashlib.sha256(inspect.getsource(fn_obj).encode('utf-8')).hexdigest()


def package_fingerprint():
    """sha256 over every engine module's source, in sorted path order: any code
    edit in the engine changes this. The test modules are not engine code —
    editing one must not fail-close the whole gate — so test_*.py files are
    not hashed."""
    h = hashlib.sha256()
    for name in sorted(os.listdir(PKG)):
        if name.endswith('.py') and not name.startswith('test_'):
            with open(os.path.join(PKG, name), 'rb') as f:
                h.update(name.encode())
                h.update(f.read())
    return h.hexdigest()


def build(functions, extra_input_paths=(), artifact_sha=None):
    """The manifest: declared-input hashes, the package code fingerprint, each
    function's own fingerprint, and the sha256 of the artifact render this manifest
    describes (the content rule: a hand-edited artifact no longer matches). Byte-stable
    (sorted, no timestamps)."""
    return {
        'manifest_version': 1,
        'inputs': input_hashes(extra_input_paths),
        'code': package_fingerprint(),
        'functions': sorted({f.stage_name: code_fingerprint(f) for f in functions}.items()),
        'artifact_sha256': artifact_sha,
    }


def dumps(manifest):
    return json.dumps(manifest, indent=1, sort_keys=True) + '\n'
