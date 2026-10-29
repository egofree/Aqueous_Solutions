# Rewrite batch 17: the parametric model page

Date: 2026-10-29

`docs-authority/PARAMETRIC_MODEL.md` (AQS-PAR-001) is written by `flow_graph/param/report.py`, and the rewrite was done there. The pending list had named `_graph.py` as its generator, which was wrong.

Revision C makes these changes:

- A purpose and scope section and a terms section were added, and the record of revisions moved above the first section.
- The framework, the table of converted scripts and the acid-loop decision are written as full sentences. The decision items now run in order; before, item 7 came before item 6.
- The decision no longer points to POWER_SIZING Rev C or placement seed Rev I, which are long out of date.
- The relief row described a blocked-discharge case for EXPANDER, a unit no longer on the graph, and a count of atmospheric nodes typed into the text. It now lists, from the graph, the units with a relief case and the atmospheric units vented to API 2000.
- The scrubber row said the scrubber library was not yet applied to a unit. It is used by `house_scrubbers.py` and `vent_scrubber.py`, and the row now says so.
- The library list now names the vent, evaporator, HCl equilibrium and trim heater functions.
- The values in the verification list are cut at a word instead of at a fixed character, and table cells no longer break on a vertical bar inside a value.

No value computed by the solver changed.
