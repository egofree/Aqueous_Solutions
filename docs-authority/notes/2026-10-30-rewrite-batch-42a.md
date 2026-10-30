# Rewrite batch 42a: MG_POT_CL2 retired

Date: 2026-10-30

## Change

The owner rule is that a route without flow is either given flow or retired. MG_POT_CL2 carried chlorine from MG_POT to CRU at zero flow, so task X-RTE-MG_POT_CL2 was open.

- MG_POT electrolyses the magnesium chloride that the Kroll retort returns, together with the dock make-up. The chlorine it makes goes to the Kroll chlorinator on IA-CL2-MG-TI. The make-up is sized so that the pot delivers exactly the magnesium and chlorine that the retort and the chlorinator draw. Both draws follow the titanium rate, so the pot has no chlorine surplus at any rate.
- `flow_graph/param/foundry_poly.py` therefore sets MG_POT_CL2 to presence retired. The task list records the route as done.
- No value changes. The chlorine supply of CRU is treated with AL_POT_CL2 in the next batch.
