# docs-authority/process/ (retired)

This folder held copies of equipment lists whose current versions are in
`docs-authority/` under the same file names (for example
[`../CRYO_EQUIPMENT.md`](../CRYO_EQUIPMENT.md)). Some copies were identical;
the rest were earlier revisions already marked superseded. They were removed on
2026-10-24 so that each document has one copy. The old text is in git history:
`git log --follow -- docs-authority/process/<FILE>.md`.

`flow_graph/test_doc_consistency.py` fails if two Markdown files in the
repository have the same content again.
