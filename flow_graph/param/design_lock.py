"""The design lock: exclusive writer ownership for the model tree.

Contract
--------
The first acquirer in a process tree opens the lock file, takes an
exclusive flock, marks the descriptor inheritable, and records its
number in ``AQS_LOCK_FD``. Descendants that acquire through this module
re-lock the *same open file description*, which flock treats as the
same owner, so nested acquisition returns immediately instead of
deadlocking: a full regen holds the lock for its write run, and stages
that take the lock internally (``models/mfg/tracker.py``) re-enter it.

Unrelated processes that open the lock path directly still mutually
exclude - that remains the point of the lock. Only the recorded
descriptor is the reentrant path.

Two mechanics matter and are pinned by
``flow_graph/param/test_design_lock.py``:

- subprocess on POSIX closes inherited descriptors unless they are in
  ``pass_fds``; ``flow_graph/param/regen.py`` passes the recorded
  descriptor to every stage. The shell-level equivalent is
  ``subprocess.run(..., pass_fds=(int(os.environ['AQS_LOCK_FD']),))``.
- a released acquirer removes ``AQS_LOCK_FD`` again; ``acquire`` also
  falls back to a fresh acquisition when the recorded descriptor is
  stale (closed or reused), so a lingering variable can never dup an
  unrelated descriptor.

This closes the wrap-vs-internal deadlock class. It was found live:
``flock .aqs-design.lock python3 -m flow_graph.param.regen`` with the
registered ``mfg_tracker`` stage wedged for 56 minutes in
``locks_lock_inode_wait`` because the stage re-locked the file the
outer wrapper already held. The house guidance is: run
``python3 -m flow_graph.param.regen`` directly - it takes the lock
itself; do not shell-wrap it in ``flock``.
"""
import fcntl
import os

FD_ENV = 'AQS_LOCK_FD'

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_first = False          # this process is the tree's first acquirer (owns releasing the env var)


def lock_path():
    """The lock file path (AQS_LOCK overrides; default <repo>/.aqs-design.lock)."""
    return os.environ.get('AQS_LOCK', os.path.join(_ROOT, '.aqs-design.lock'))


def acquire():
    """Take the design lock reentrantly; return the open handle.

    Hold the handle for the write phase and hand it to ``release``. A
    descendant's handle is a duplicate of the inherited descriptor:
    closing it does not drop the ancestor's lock, because flock
    releases only when the last descriptor of the open file
    description closes.
    """
    global _first
    inherited = os.environ.get(FD_ENV)
    if inherited is not None:
        try:
            fh = os.fdopen(os.dup(int(inherited)), 'w')
        except OSError:                       # stale variable: descriptor closed or reused
            fh = None
        else:
            fcntl.flock(fh, fcntl.LOCK_EX)    # same open file description: returns immediately
            return fh
    fh = open(lock_path(), 'w')
    fcntl.flock(fh, fcntl.LOCK_EX)
    os.set_inheritable(fh.fileno(), True)
    os.environ[FD_ENV] = str(fh.fileno())
    _first = True
    return fh


def release(fh):
    """Release the lock. The tree's first acquirer also clears AQS_LOCK_FD."""
    global _first
    if _first:
        os.environ.pop(FD_ENV, None)
        _first = False
    fh.close()


def pass_fds():
    """Descriptor tuple for subprocess ``pass_fds`` so stages inherit the lock (empty when unlocked)."""
    inherited = os.environ.get(FD_ENV)
    return (int(inherited),) if inherited is not None else ()
