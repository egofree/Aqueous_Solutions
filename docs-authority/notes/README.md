# Change records

This folder holds dated change records, one per change set, named
`YYYY-MM-DD-<topic>.md`. AGENTS.md requires one for every change to the graph,
the drivers or a transfer function, and the task plan's evidence pass reads
them. The file names sort by date, so the folder listing is the index.

Topic notes that are not tied to one change (design notes, sizing derivations,
audits) are in the top-level [`notes/`](../../notes/) folder. Keep one copy of
each note: `flow_graph/test_doc_consistency.py` fails on duplicate content.
