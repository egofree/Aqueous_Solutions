"""U3 single-flight cache for docs-authority/_power_sizing.py (AQS-PAR-001 regen pipeline).

_power_sizing.py is content-addressed by its real inputs: flow_graph/param/drivers.json +
flow_graph/plant_flow_graph.json + the generator sources (its own file, the flow_graph/param
solver modules and its two JSON feeders _ew_sizing.py/_rect_ew_sizing.py). Within one
orchestrator pass it is spawned 3-4 times (solver.solve() inside write_graph.process,
write_graph.power, and any consumer that re-derives it); on a converged tree those spawns
share the same (drivers, graph) key and only the first executes.

Mechanism: regen.py puts a two-line sitecustomize.py on PYTHONPATH for its whole subprocess
tree and sets AQS_PS_CACHE_DIR; the shim imports install() from this module, which wraps
subprocess.run/check_output/check_call. A spawn whose argv targets docs-authority/
_power_sizing.py is served from the cache on a key hit (byte-identical stdout; the cached
bytes ARE the fresh-run bytes, so the U2a byte-identical guarantee is respected) and cached
on the first real execution. Everything else — git calls, other scripts, non-capture runs —
passes through untouched. With AQS_PS_CACHE_DIR unset (any process outside a regen pass)
install() is a no-op, so interactive runs are never cached.

The cache lives outside the repo (default <system temp dir>/aqs-ps-cache) so `git status` stays
clean; it is disposable at any time.
"""
import functools, glob, hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = '_power_sizing.py'
ENV_CACHE = 'AQS_PS_CACHE_DIR'
DEFAULT_CACHE_DIR = os.path.join(__import__('tempfile').gettempdir(), 'aqs-ps-cache')

def _key_paths(root):
    """Every file whose bytes can change _power_sizing stdout for a given (drivers, graph)."""
    ps = [os.path.join(root, 'docs-authority/_power_sizing.py'),
          os.path.join(root, 'docs-authority/_ew_sizing.py'),
          os.path.join(root, 'docs-authority/_rect_ew_sizing.py'),
          os.path.join(root, 'flow_graph/param/drivers.json'),
          os.path.join(root, 'flow_graph/plant_flow_graph.json')]
    ps += sorted(glob.glob(os.path.join(root, 'flow_graph/param/*.py')))
    ps += sorted(glob.glob(os.path.join(root, 'flow_graph/param/sizing/*.py')))
    return ps

def cache_key(root=None):
    root = root or ROOT
    h = hashlib.sha256()
    for p in _key_paths(root):
        h.update(p.encode()); h.update(b'\0')
        try: h.update(open(p, 'rb').read())
        except OSError: h.update(b'?missing?')
    return h.hexdigest()

def _is_target(args):
    return any(isinstance(a, str) and a.endswith(TARGET) and ('docs-authority' + os.sep in a or a == TARGET or a.endswith('/' + TARGET)) for a in args)

def _cache_path(cdir, key):
    return os.path.join(cdir, key + '.json')

def lookup(cdir, key):
    try:
        d = json.load(open(_cache_path(cdir, key)))
        if isinstance(d, dict) and 'stdout' in d: return d
    except (OSError, ValueError): pass
    return None

def store(cdir, key, stdout_text):
    try:
        os.makedirs(cdir, exist_ok=True)
        tmp = _cache_path(cdir, key) + f'.{os.getpid()}.tmp'
        with open(tmp, 'w') as f: json.dump({'stdout': stdout_text}, f)
        os.replace(tmp, _cache_path(cdir, key))
    except OSError: pass   # cache is best-effort; the real spawn already produced the bytes

_ORIG_RUN, _ORIG_CKO, _ORIG_CKC = subprocess.run, subprocess.check_output, subprocess.check_call

def _wrap(runner):
    """Wrap subprocess.run / check_output / check_call for capture-semantics _power_sizing spawns."""
    @functools.wraps(runner)
    def wrapped(*args, **kw):
        argv = args[0] if args else kw.get('args')
        cdir = os.environ.get(ENV_CACHE)
        if not cdir or not isinstance(argv, (list, tuple)) or not _is_target(argv):
            return runner(*args, **kw)
        root = os.environ.get('AQS_REGEN_ROOT') or ROOT
        key = cache_key(root)
        hit = lookup(cdir, key)
        text = kw.get('text') or kw.get('universal_newlines')
        if hit is not None:
            out = hit['stdout'] if text else hit['stdout'].encode()
            if runner is _ORIG_RUN:
                return subprocess.CompletedProcess(argv, 0, stdout=out, stderr='' if text else b'')
            return out if runner is _ORIG_CKO else 0
        r = runner(*args, **kw)          # real execution (captures stdout exactly as the caller asked)
        out = r if isinstance(r, (str, bytes)) else getattr(r, 'stdout', None)
        rc = 0 if isinstance(r, (str, bytes)) else getattr(r, 'returncode', 1)
        if rc == 0 and out:
            store(cdir, key, out.decode(errors='replace') if isinstance(out, bytes) else out)
        return r
    return wrapped

_installed = False
def install():
    """Activate the interception for this process tree (no-op unless AQS_PS_CACHE_DIR is set)."""
    global _installed
    if _installed or not os.environ.get(ENV_CACHE): return
    subprocess.run = _wrap(_ORIG_RUN)
    subprocess.check_output = _wrap(_ORIG_CKO)
    subprocess.check_call = _wrap(_ORIG_CKC)
    _installed = True

HOOK_TEMPLATE = '''# generated at runtime by flow_graph/param/regen.py (U3); disposable
import os, sys
try:
    if os.environ.get({env!r}):
        sys.path.insert(0, os.environ.get({root_env!r}, {root!r}))
        from flow_graph.param._ps_cache import install
        install()
except Exception:
    pass
'''

def write_hook(hook_dir, root):
    """Write the sitecustomize.py shim regen.py puts on PYTHONPATH for its children."""
    os.makedirs(hook_dir, exist_ok=True)
    with open(os.path.join(hook_dir, 'sitecustomize.py'), 'w') as f:
        f.write(HOOK_TEMPLATE.format(env=ENV_CACHE, root_env='AQS_REGEN_ROOT', root=root))
    return os.path.join(hook_dir, 'sitecustomize.py')

if __name__ == '__main__':   # manual probe: python3 -m flow_graph.param._ps_cache
    print('cache key', cache_key()[:16], 'root', ROOT)
