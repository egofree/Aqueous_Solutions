# The design lock is reentrant: the mfg_tracker wedge inside a wrapped regen

Date: 2026-11-04. Branch: `qc/batch-1-farm-design-tool-placement`.

## Finding

A full regen wrapped in an outer `flock .aqs-design.lock` deadlocked its own
`mfg_tracker` stage for 56-72 minutes in `locks_lock_inode_wait`:
`models/mfg/tracker.py` takes the design lock internally for its write phase
(its docstring said "do not wrap it in a second flock" - a sentence, not a
check), and the outer wrapper held the same path. The stage waited on a lock
its own ancestor held. Live evidence: `/proc/<pid>/wchan` =
`locks_lock_inode_wait` on the wedged stage child.

## Fix

- New `flow_graph/param/design_lock.py`: the first acquirer opens the lock
  file, flocks it exclusively, marks the descriptor inheritable and records it
  as `AQS_LOCK_FD`. Descendants re-lock the same open file description -
  flock treats that as the same owner, so nested acquisition returns
  immediately. `release()` clears the variable when this process was the
  tree's first acquirer; `acquire()` falls back to a fresh acquisition when
  the recorded descriptor is stale.
- `flow_graph/param/regen.py` takes the lock itself for every write run
  (`--check` and `--dry-run` stay lock-free) and passes the descriptor to
  every stage (`subprocess.run(..., pass_fds=design_lock.pass_fds())` -
  POSIX subprocess closes inherited descriptors unless they are in
  `pass_fds`; the inheritable flag alone does not survive it).
- `models/mfg/tracker.py` takes the lock through the helper.
- `AGENTS.md` Concurrency: the shell-wrapper `flock` example is replaced by
  the self-locking contract.

## Checks

`flow_graph/param/test_design_lock.py`: nested acquisition does not block
(the wedge regression); an unrelated process still excludes and releases on
close; a descendant closing its duplicate does not drop the ancestor's lock;
a stale `AQS_LOCK_FD` falls back to a fresh acquisition; `regen.child_env()`
propagates the descriptor. End to end: a full self-locked regen ran through
the `mfg_tracker` stage in 30.3 s (previously the 56-minute wedge) and
converged (476 vouched patterns).

## Operational note

The same session also found two orphaned background regens from an
interrupted lane holding the lock for 21-72 minutes; fresh acquisitions
blocked on them. Standing rule: one write lane at a time; a lane that
backgrounds a regen must either wait for it or kill it before ending.
