# Derived STREAM / MASS sync pointer — WP-Ap3

Source graph: AQS-FLOW-GRAPH-001 Rev BH (`plant_flow_graph.json`)
Generated: 2026-10-15
Licence: CERN-OHL-S-2.0

## Generated (this directory)

| File | Role |
|---|---|
| `STREAM_REGISTER_DERIVED.md` | Full stream table from graph edges (incl. IA-* / TBD) |
| `MASS_FLOW_DERIVED.md` | Mass-layer S / SANDBOX / TBD claim excerpt |
| `CENSUS.md` | Node/edge counts + gap list |

## Human + derived hybrid (do not overwrite wholesale)

| CAD doc | Role after WP-Ap3 |
|---|---|
| `cad/STREAM_REGISTER.md` (AQS-STR-001) | **Sync target** — human narrative + inter-block S## table; compare to derived |
| `cad/MASS_FLOW.md` (AQS-MF-001) | **Sync target** — claim-status narrative; compare to derived |

Prefer editing the graph, then:

```bash
cd Diagrams/aqueous_diagrams/flow_graph
python3 export_authority_md.py
python3 render_layer_views.py   # layer stubs still graph-driven
```

Do **not** invent DOCK S## or fill null placeholder rates.
DOCK_EXPORT_TBD stays TBD. Layer views: `render_layer_views.py` → `views/`.
