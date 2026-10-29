# Rewrite batch 10: storage, electrowinning cell and reactor sizing pages

Date: 2026-10-29

Three sizing pages were rewritten through their generators: the storage hold-up page AQS-DUTY-064 written by `docs-authority/_storage_sizing.py`, the electrowinning cell page AQS-DUTY-051 written by `docs-authority/_ew_sizing.py`, and the reaction chamber page AQS-DUTY-062 written by `flow_graph/param/reactor_design.py`. Each now has a purpose and scope section, a basis written as complete sentences, and numbered tables. The values are unchanged.

The reactor page typed several inputs into its text although the generator reads them from the drivers: the glass dissolution rate, the pyrolysis temperature, residence time and heat of reaction, and the heater efficiency. The text now prints the driver values. The empty table for catalytic tube reactors, which have no unit on the graph, is no longer printed.

The electrowinning cell page now computes the range of tank lengths that its first finding states. Its finding on the hydrogen-cell list is unchanged while that owner question is open.

The sanitation page was not rewritten. Its generator, `flow_graph/param/sanitation.py`, is a one-time edit that the regeneration no longer runs, and the page no longer matches the graph. The question is recorded in section 6 of AQS-DOC-003.
