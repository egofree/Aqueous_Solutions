"""The design lock contract: reentrant down the process tree, exclusive across trees.

Regression for the live wedge found 2026-11-03: a full regen wrapped in an
outer ``flock`` deadlocked the registered ``mfg_tracker`` stage for 56
minutes in ``locks_lock_inode_wait`` because the stage re-locked the file
the wrapper already held. ``acquire()`` in ``flow_graph/param/design_lock.py``
is the sanctioned path; these tests pin both sides of the contract.
"""
import os
import subprocess
import sys

from flow_graph.param import design_lock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHILD_ACQUIRE = (
    "import sys;"
    "sys.path.insert(0, {root!r});"
    "from flow_graph.param import design_lock;"
    "fh = design_lock.acquire();"
    "print('acquired')"
)
CHILD_PROBE_NB = (
    "import fcntl\n"
    "fh = open({p!r}, 'w')\n"
    "try:\n"
    "    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
    "    print('acquired')\n"
    "except BlockingIOError:\n"
    "    print('excluded')\n"
)


def _child_env(lock_path):
    """Stage-like environment: AQS_LOCK set, AQS_LOCK_FD inherited if present."""
    env = dict(os.environ)
    env['AQS_LOCK'] = str(lock_path)
    return env


def _spawn(code, lock_path, pass_lock_fd):
    env = _child_env(lock_path)
    return subprocess.run(
        [sys.executable, '-c', code],
        capture_output=True, text=True, timeout=30, env=env,
        pass_fds=design_lock.pass_fds() if pass_lock_fd else ())


def test_nested_acquisition_does_not_block(tmp_path, monkeypatch):
    """A stage acquiring under a held ancestor lock returns immediately (the wedge regression)."""
    lock_path = tmp_path / 'design.lock'
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(lock_path))
    parent = design_lock.acquire()
    try:
        r = _spawn(CHILD_ACQUIRE.format(root=ROOT), lock_path, pass_lock_fd=True)
        assert r.returncode == 0 and 'acquired' in r.stdout, r.stderr
    finally:
        design_lock.release(parent)


def test_unrelated_process_excludes(tmp_path, monkeypatch):
    """Without the inherited descriptor the lock still excludes (that is its purpose)."""
    lock_path = tmp_path / 'design.lock'
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(lock_path))
    parent = design_lock.acquire()
    try:
        r = _spawn(CHILD_PROBE_NB.format(p=str(lock_path)), lock_path, pass_lock_fd=False)
        assert 'excluded' in r.stdout, r.stdout + r.stderr
    finally:
        design_lock.release(parent)
    r = _spawn(CHILD_PROBE_NB.format(p=str(lock_path)), lock_path, pass_lock_fd=False)
    assert 'acquired' in r.stdout                                     # released


def test_child_close_does_not_release_ancestor(tmp_path, monkeypatch):
    """A descendant closing its duplicate must not drop the ancestor's lock."""
    lock_path = tmp_path / 'design.lock'
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(lock_path))
    parent = design_lock.acquire()
    try:
        child = (
            "import sys;"
            "sys.path.insert(0, {root!r});"
            "from flow_graph.param import design_lock;"
            "design_lock.acquire().close()"                            # closes only its duplicate
        ).format(root=ROOT)
        _spawn(child, lock_path, pass_lock_fd=True)
        r = _spawn(CHILD_PROBE_NB.format(p=str(lock_path)), lock_path, pass_lock_fd=False)
        assert 'excluded' in r.stdout, 'ancestor lock dropped by a descendant close'
    finally:
        design_lock.release(parent)


def test_stale_fd_env_falls_back(tmp_path, monkeypatch):
    """A lingering AQS_LOCK_FD pointing at a closed descriptor falls back to a fresh acquisition."""
    lock_path = tmp_path / 'design.lock'
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(lock_path))
    monkeypatch.setenv(design_lock.FD_ENV, '999999')                  # closed or never existed in this process
    fh = design_lock.acquire()                                        # must not EBADF
    try:
        assert fh.fileno() != 999999
    finally:
        design_lock.release(fh)


def test_release_clears_env_for_this_tree(tmp_path, monkeypatch):
    lock_path = tmp_path / 'design.lock'
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(lock_path))
    fh = design_lock.acquire()
    assert design_lock.FD_ENV in os.environ
    design_lock.release(fh)
    assert design_lock.FD_ENV not in os.environ


def test_stage_env_propagates(tmp_path, monkeypatch):
    """regen's child_env() copies os.environ, so AQS_LOCK_FD reaches stage subprocesses."""
    monkeypatch.delenv(design_lock.FD_ENV, raising=False)
    monkeypatch.setenv('AQS_LOCK', str(tmp_path / 'design.lock'))
    fh = design_lock.acquire()
    try:
        assert design_lock.FD_ENV in os.environ
        from flow_graph.param.regen import child_env
        assert design_lock.FD_ENV in child_env()
        from flow_graph.param.design_lock import pass_fds
        assert pass_fds() == (int(os.environ[design_lock.FD_ENV]),)
    finally:
        design_lock.release(fh)
