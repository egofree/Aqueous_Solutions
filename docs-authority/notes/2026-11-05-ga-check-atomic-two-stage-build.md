# GA_CHECK.md is renamed into place complete, in one step

Date: 2026-11-05. Branch: `qc/batch-1-farm-design-tool-placement`.

## Finding

`docs-authority/GA_CHECK.md` was built by two writer stages that each rewrote
the published file in place: `docs-authority/_ga_check.py` wrote the envelope
sections over the whole page, and `docs-authority/_cad_clash.py` later rewrote
the page again with the CAD clash sections appended. Between the two stages
the published page was a partial document, and a run killed in that window
left a truncated page that read as an edit (see the note on in-place
regeneration in agent rounds, same date).

## Change

The page is now composed away from its published path and moved into place
once complete:

- `docs-authority/_ga_check.py` stages the envelope body, with its code-basis
  section, to `docs-authority/GA_CHECK.md.tmp`. It no longer writes
  `GA_CHECK.md`.
- `docs-authority/_cad_clash.py` appends the CAD solid and equipment clash
  sections to the staged body and calls `os.replace` to move the complete
  document over `GA_CHECK.md`. The published path is therefore always either
  the previous complete page or the new complete page, never a partial one.

The stage graph (`flow_graph/param/regen_manifest.json`) is unchanged:
`doc_cad_clash` still amends `GA_CHECK.md` after `doc_ga_check`, and a full
run executes both stages in that order, as before. `GA_CHECK.md.tmp` is
ignored by git, so an interrupted run cannot leave the tree dirty;
`flow_graph/clear_pairs.py`, which runs `_ga_check.py` for its pair report,
is unaffected because it reads the printed report, not the staged file.

## Checks

- Both stages were run in sequence against a scratch checkout of the commit
  that precedes this change: the composed `GA_CHECK.md` is byte-for-byte
  identical to the page committed at that state, no staging file is left
  behind, and the envelope, clearance and CAD results (271 envelopes, 25
  overlaps, 47 pairs inside the 600 mm clearance, 0 CAD contacts) are
  unchanged.
- `scripts/check_all.sh --full` passed after the commit: both scratch
  regenerations left the committed tree unchanged.
