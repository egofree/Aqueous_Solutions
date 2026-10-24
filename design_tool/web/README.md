# Aqueous design tool: web interface

A browser interface to the design tool API (`design_tool/README.md`, architecture AQS-UI-001), written in React, Vite and TypeScript. Licence: CERN-OHL-S-2.0.

## 1. Run

Start the API first (see `design_tool/README.md`), then:

```bash
cd design_tool/web
npm install
npm run dev      # serves http://127.0.0.1:5173 and forwards /api to port 8000
npm run build    # type check and production build
```

## 2. Components

Table 2.1. Components in `src/`

| Component | Role |
|---|---|
| `App.tsx` | Loads the graph, system tree, drivers and MVS model; creates a sandbox and solves it once |
| `SchematicCanvas` | Draws the schematic from the graph's diagram layer views |
| `LayerFilters` | Switches between the process, mass and energy flow layers |
| `SectorToggles` | Switches sectors on and off in the sandbox |
| `TreeTogglePanel` | The system tree (AQS-SYS-TREE-001) with a check box per sector, train, subsystem and unit |
| `SiteInputs` | Crew size and site latitude for the sandbox |
| `GapPanel` | Solve status, the electrical balance (generation, storage, load, need and target), gaps and unclosed streams |
| `ParamsPanel` | The design drivers, searchable and read-only |
| `RegenStatusBadge` | Shows whether generated files are current; checks again after every solve |
| `ExportButton` | Writes an export pack |

## 3. What the interface does not do

Nothing in the interface writes the graph, the drivers, the system tree or the design documents. Changes to the design are made in those files and followed by `python3 -m flow_graph.param.regen`. The interface changes sandboxes only, through `PATCH /api/v1/sandbox/{id}`.
