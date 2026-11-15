"""Input-read capture for the regen input-hash manifest (pipeline-simplification step 4).

The regen orchestrator runs every stage under this wrapper. The wrapper installs a
Python audit hook that records which project files the stage (and anything it spawns)
actually opens for reading, then runs the stage unchanged. After the run the recorded
path sets are hashed once and written to flow_graph/derived/_input_manifest.json.

Reading the real opens instead of trusting declared inputs is what closes the
under-declaration risk the migration plan names for step 4: a generator whose inputs
are under-declared still records everything it truly reads.

Mechanism:
- regen.py runs each stage as
    python3 -m flow_graph.param.input_audit --capture <base> -- python3 -m <module> <args...>
  with AQS_INPUT_AUDIT=<base> and a sitecustomize shim on PYTHONPATH.
- The shim installs the same hook in grandchild processes the stage spawns, so reads
  behind a solver subprocess are captured too. Each process dumps its own set to
  <base>.<pid> at exit; regen.py merges and deletes the sidecars.
- Known gap: reads by non-Python grandchildren (the FreeCAD/OpenSCAD binaries) are not
  recorded; their outputs are covered by the CAD byte gate instead.

The hook never records outside the repository, never records write or create opens,
and never records the pipeline's own bookkeeping (receipt, run log, input manifest,
audit sidecars, design lock).
"""
import atexit, json, os, runpy, sys

_records = None      # set of absolute paths this process saw opened for reading
_root = None         # repository root; reads outside it are not inputs
_base = None         # sidecar path prefix, from AQS_INPUT_AUDIT
_paused = 0          # >0 while an evaluation-only reader (e.g. the staleness census) runs:
                     # its opens verify the tree, they are not generation inputs
_EXCLUDE_SUFFIX = ('.pyc',)
_AUDIT_BASE = '_input_audit'
_EXCLUDE_PARTS = ('.git', '__pycache__', '.aqs-shim')
_EXCLUDE_NAMES = ('.aqs-design.lock', '_regen_receipt.json', '_regen_run.json',
                  '_input_manifest.json')
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC


def pause():
    """Suspend recording: evaluation-only reads are not generation inputs."""
    global _paused
    _paused += 1


def resume():
    global _paused
    _paused = max(0, _paused - 1)


def default_root():
    """The repository root, from this file's own location (flow_graph/param/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def install(root=None, base=None):
    """Install the audit hook (idempotent). Returns the recording set."""
    global _records, _root, _base
    if _records is not None:
        return _records
    _records = set()
    _root = os.path.abspath(root or default_root())
    _base = base or os.environ.get('AQS_INPUT_AUDIT')
    atexit.register(dump)                 # dump() is a no-op when _base is None
    sys.addaudithook(_hook)
    return _records


def _hook(event, args):
    if event != 'open' or _paused:
        return
    path, mode, flags = args
    if not isinstance(path, str) or _records is None:
        return
    if mode and any(c in mode for c in 'wx+a'):
        return
    if flags & _WRITE_FLAGS:
        return
    ap = os.path.abspath(path)
    if not ap.startswith(_root + os.sep) or not os.path.isfile(ap):
        return
    rel = os.path.relpath(ap, _root)
    if any(p in _EXCLUDE_PARTS for p in rel.split(os.sep)):
        return
    if rel.endswith(_EXCLUDE_SUFFIX) or os.path.basename(rel) in _EXCLUDE_NAMES:
        return
    if rel.startswith('flow_graph/derived/' + _AUDIT_BASE + '.'):
        return
    _records.add(ap)


def dump():
    """Write this process's recorded set to its sidecar; best effort."""
    if _records is None or not _base:
        return
    try:
        sidecar = f'{_base}.{os.getpid()}'
        with open(sidecar, 'w') as f:
            json.dump(sorted(_records), f)
    except OSError:
        pass


def merge_sidecars(base):
    """Union every sidecar <base>.* into one set; delete the sidecars. Returns (paths, complete)."""
    import glob as _glob
    paths, seen = set(), False
    for sc in sorted(_glob.glob(base + '.*')):
        seen = True
        try:
            paths.update(json.load(open(sc)))
        finally:
            try:
                os.remove(sc)
            except OSError:
                pass
    return paths, seen


def main():
    """Wrapper entry point: capture, then run the real stage in this process."""
    argv = sys.argv[1:]
    if len(argv) < 4 or argv[0] != '--capture' or '--' not in argv:
        raise SystemExit('usage: input_audit --capture <base> -- python3 -m <module> <args...>')
    base = argv[1]
    rest = argv[argv.index('--') + 1:]
    if len(rest) < 3 or rest[1] != '-m':
        # Unexpected launch shape: run it unchanged, capture nothing (regen marks the
        # stage capture-incomplete when the wrapper did not merge its sidecar).
        os.execvp(rest[0], rest)
    # The sitecustomize shim (grandchild capture) imports this file as the plain module
    # `input_audit`; import the same instance here so hook state and the exit dump are
    # shared, never doubled.
    import input_audit as ia
    if ia._records is None:
        ia.install(base=base)
    module, mod_args = rest[2], rest[3:]
    sys.argv = [module] + mod_args
    runpy.run_module(module, run_name='__main__', alter_sys=True)


if __name__ == '__main__':
    main()
