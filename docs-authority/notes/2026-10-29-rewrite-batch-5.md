# Rewrite batch 5: protection, isometric sheets and jellybean parts

Date: 2026-10-29

AQS-ELEC-006 (`PROTECTION.md`) was a hand-kept page whose values came from `docs-authority/_protection.py`, which printed the study but did not write the page. The page had fallen behind: it gave a superseded inverter count, five collection sections where the graph has four, and the retired unit name RECT_EW. The script now writes the page from its own results, the graph and the grounding study, and carries over the code basis section that `flow_graph/param/code_basis.py` appends, because that stage runs before it. The grounding grid values were reported, not changed.

AQS-ISO-002 (`ISO_SHEETS.md`) and AQS-MFG-011 (`JELLYBEAN.md`) were rewritten through their generators.
