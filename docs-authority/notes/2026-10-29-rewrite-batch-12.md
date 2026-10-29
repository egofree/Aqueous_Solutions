# Rewrite batch 12: evaporator and polymers line sizing pages

Date: 2026-10-29

The evaporator design page AQS-DUTY-060 is rewritten through `flow_graph/param/evap_design.py` as revision C. Its header had no document number, revision or date lines. The basis now states the driver values in sentences, the result table names each quantity with its unit, and the sentence that compared the specific energy with an upper bound used before is removed. The values are unchanged.

The polymers line page AQS-DUTY-073 is rewritten through `docs-authority/_polymers_sizing.py` as revision B. Its section on the fluoropolymer train said the train was blocked for want of a fluorine source, but the graph has run the train on imported fluorspar since assumption A-M-289. The section now reports the train from the graph: the imports, the recovery through F_RECOVER, and the flows and electrical feed of each unit. The open item on a missing feed to FILM_CAST is printed only when the graph lacks that feed, and it now has one. The figures typed into the text for the feed heating are read from the drivers.
