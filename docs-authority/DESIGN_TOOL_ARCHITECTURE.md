# Design-tool architecture

Document number: AQS-UI-001  
Revision: H  
Date: 2026-10-24  
Basis: AQS-AUTH-001; style AQS-DOC-002; scale AQS-SCALE-001 (`SCALE_M = 1.0`); streams AQS-STR-001; mass flow AQS-MF-001; compliance themes AQS-COMPL-001; flow graph AQS-FLOW-GRAPH-001; plan AQS-PLAN-UI-001 Rev N (`unify_then_reshape`).  
Status: architecture decisions. This is not shipped software and not a professional engineer's stamp.  
Licence: CERN-OHL-S-2.0 for the CAD, the model, the authority documents, the design-tool interface and any public or cloud service. There is no separate interface or cloud licence.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: MVS/sandbox rules, schema, solver, UI stack, roadmap | 2026-10-01 |
| B | Sector taxonomy + surplus MVS | Sector Definition classes; MVS = closed loops + surplus export; modular export; CERN-OHL-S for UI+model | 2026-10-01 |
| B+ | Catalogue pointer | AQS-SEC-001 Rev A issued (`SECTOR_DEFINITIONS.md`); §11.1 item 3 closed by catalogue | 2026-10-01 |
| C | Colony MVS + all ESS | MVS = self-sustaining colony (manufacture, habit, self-copy, scale); all three ESS peers required; disabled ESS → unreclaimed-resource / incomplete-closure gaps | 2026-10-01 |
| D | unify_then_reshape | Typed plant graph = sole topology authority; fold/project `candidate_mvs`; matplotlib demoted to optional exporters; roadmap A′→B′→C→D→E; 3D FreeCAD bias (Three.js only with written decision); stack re-eval the unpublished planning note STACK_REEVAL_2026-10-01 | 2026-10-01 |
| E | Unified-engine wiring | Working UI on the unified parametric system: read-only `/system-tree`, `/params`, `/regen-status` endpoints; ParamsPanel / TreeTogglePanel / RegenStatusBadge; four-level sandbox toggles (sector/system/subsystem/unit) resolving most-specific-wins server-side; regen receipt as the provenance the badge reads (commits 5f77bee, f64ad84, fc083f8) | 2026-10-19 |
| F | Sector names | Header revision brought in line with this table (it still said D). Examples use graph Rev AC sector ids (AQS-SEC-001 Rev H): DIGESTER for WET; PV_ARRAY, ZNBR2 and BACKUP_GEN are units in ELEC. No architecture change. | 2026-10-24 |
| G | Plain language | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope merged into §1, terms in §2, captions; counts removed from §13; an internal working rule removed from §10. Decisions unchanged. | 2026-10-24 |
| H | External source removed | The section on an outdated external planning source and every reference to it removed (open question Q-016 closed by the owner); the licence section is now §3.11. Other decisions unchanged. | 2026-10-24 |

## 1. Purpose and scope

This document sets the architecture of an interactive design tool for the plant. The tool:

1. Classifies every plant sector by its Sector Definition, that is, its role in the mass and energy graph.
2. Treats the minimum viable system (MVS) as the smallest self-sustaining human colony, at Moon or Mars class intent. The MVS has full manufacturing and habitation, can make its own parts, can copy itself (RepRap class), can scale up (GVCS class) or down, closes all loops including all three energy storage peers, and still produces a surplus of food, clean water, raw materials or manufactured goods, and energy. The aim is overproduction and export, not only self-sustainment.
3. Provides a sandbox in which any set of sectors or modules can be switched on or off, derated continuously where the scale rules allow it, and checked for gaps (missing roles, streams that do not close). The sandbox never invents closure.
4. Never overwrites the locked MVS. Every sandbox result is exported as a new, modular design pack in which unused modules are switched off.

Table 1.1 sets what is in and out of scope.

Table 1.1. Scope

| In | Out |
|---|---|
| Sector Definition taxonomy; unit_id / stream_id rules | Rewriting root narrative folders `01-…`–`09-…` |
| Typed JSON/YAML MVS schema sketch | Vendor nameplates as issued ratings |
| Mass-energy + electrical match solver API | Live PE / AHJ permit issuance |
| Schematic-first UI (React/SVG graph-layer); 3D later (FreeCAD bias) | Overwriting MVS files in place |
| Sector toggles; gap / unclosed-stream flags; cycle views; code-flag hooks | Any runtime dependency on an external data source |
| Modular export pack; phased roadmap | Data under a licence incompatible with CERN-OHL-S in the MVS or UI tree |
| Host path local → GitHub → cloud | Invented permits or clause quotations |

The canonical copy of this document is `docs-authority/DESIGN_TOOL_ARCHITECTURE.md`.

## 2. Terms

- Sector Definition: the role a sector or unit plays in the mass and energy graph: source, load, storage, sink or export, or process (§3.1). The catalogue is AQS-SEC-001.
- Minimum viable system (MVS): the smallest plant configuration that meets the closure and surplus tests of §3.2. Until a formal freeze of `AQS-MVS-001`, the on-disk baseline is the candidate MVS.
- Energy storage system (ESS) peers: the three storage systems the MVS requires together, `ZNBR2` (zinc-bromide flow battery), `MEOH` (methanol store) and `PUMPED_HYDRO`.
- Sandbox: an editable copy of the MVS with sectors switched on or off and parameters changed.
- Gap: a missing Sector Definition, or a stream that no longer closes because of one.
- Design pack: the exported result of a sandbox (§8).
- Plant graph: the typed graph in `flow_graph/` (AQS-FLOW-GRAPH-001), the only source of units and streams.
- `unify_then_reshape`: the plan (AQS-PLAN-UI-001) that first makes the plant graph the only topology source and then rebuilds the interface on it.

Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Decisions

### 3.1 Sector Definition (taxonomy)

Every sector, and every unit class that matters for energy, shall carry a Sector Definition. The definition tells the solver whether the block is a source, a load, storage that charges and discharges, a sink or export, or a process that transforms streams. Definitions are independent of the physical bay layout. Table 3.1 lists the classes.

Table 3.1. Sector Definition classes

| Sector Definition | Mode behaviour | Examples (illustrative) |
|---|---|---|
| **Energy Storage System (Gravity)** | Alternating **load** (charge / pump-up) and **source** (discharge / generate) | Pumped hydro |
| **Energy Storage System (Electrochemical)** | Alternating charge / discharge; chemical + electrical legs | ZnBr₂ flow battery; MeOH store + IEM / DMFC path |
| **Energy Production (Electrical)** | Source (generation); may be intermittent | Solar PV |
| **Energy Production (Combustion Engine)** | Source when fuelled; load on fuel / oxidizer streams | Backup H₂ genset |
| **Energy Production (Electrochemical)** | Source when reactants available | PEM FC; IEM MeOH FC |
| **Process (Mass transform)** | Transforms streams; usually a load electrically | DIGESTER, OIL, GLASS, FOUNDRY, POLYMERS, FAB, MFG |
| **Life support / habitat** | Load + export opportunity (food, water, waste return) | HAB, FARM |
| **Utility / header** | Distributes; rarely a net source | CRYO cold-box, HVAC/geo Q4, headers |
| **Export / dock** | Boundary sink or source for surplus goods / freight | North dock, freight elevator |

Rules:

1. Any or all components may be missing in a sandbox. The solver shall report gaps (Sector Definitions the graph still references but which are absent) and the mass or energy streams left unclosed by them. It shall not invent closure.
2. Energy storage classes shall model both charge and discharge on the same unit, or on paired units, so that the electrical match and the mass balance agree.
3. The physical rules of AQS-SCALE-001 (`SCALE_M`, bays, cassettes) drive the layout; the Sector Definition drives the role. A smaller envelope is a valid MVS only if its loops close, including all required storage peers, and it meets the surplus criteria of §3.2. Bay count alone does not define the MVS. Capabilities left out of a scaled-down plant are modelled as unreclaimed resources or incomplete closure (§3.2 item 2).

### 3.2 MVS and sandbox

1. The MVS shall be the smallest plant configuration that:
   - is a self-sustaining human colony at Moon or Mars class intent: full manufacturing and habitation, able to make its own parts, able to copy itself (RepRap-class self-replication), and able to scale up (GVCS class) or down;
   - includes the Sector Definitions needed to close all loops (AQS-MF-001, AQS-STR-001), with all three storage peers (`ZNBR2`, `MEOH`, `PUMPED_HYDRO`) switched on. Redundancy is a core principle. Methanol also feeds other process streams; it is not storage only;
   - still produces a surplus for export of food, clean water, raw materials or manufactured goods, and energy.
   Self-sustainment alone is not enough; the goal is overproduction and export.
2. Scaled-down configurations, with capabilities left out for practical reasons, may be useful in operation. The model shall treat each missing capability as an incompletely closed loop or an unreclaimed resource stream: a problem to solve, not accepted pollution, emissions or silent loss.
3. The sandbox shall allow:
   - switching any sector or module on or off;
   - continuous derating where the continuous classes of AQS-SCALE-001 apply (for example, tank footprint proportional to plan area);
   - discrete steps where those rules apply (cassettes, docks, PV and zinc-bromide modules).
   When a required storage peer, or another required sector, is off, the solver shall report an unreclaimed-resource or incomplete-closure gap (`reason: unreclaimed_resource` for storage peers) and shall not invent storage or mass closure.
4. Export shall not be blocked only because a sandbox has sectors switched off. The pack carries the gap and unclosed-stream flags instead. Export is blocked only for hard schema or integrity failures (orphan identifiers, a corrupt model), not for "incomplete compared with the MVS".
5. The tool shall not overwrite the locked MVS. Every sandbox edit is exported as a new design pack (§8).
6. The on-disk plant baseline remains `SCALE_M = 1.0` in `models/freecad/params.py`, the current manufacturing baseline. Whether that envelope becomes the frozen MVS is decided by the surplus and closure tests of this section, not by bay count. Until a commit explicitly freezes `AQS-MVS-001`, the baseline is the candidate MVS.

### 3.3 Schematic first, 3D later

1. The first interactive surface shall be a 2D schematic (process flow diagram, single-line diagram and layered graph views), not a free-orbit 3D editor. Under `unify_then_reshape` the schematic is a viewer and editor over the layers of the plant graph (Phase B′), not a second store of topology.
2. 3D follows once export from the graph is settled (Phase D). The default is a FreeCAD rebuild from the graph and the `params` model (`freecadcmd`, AQS-REB-001). A live parametric mesh, a campus mesh with levels of detail, or Three.js are used only if a written decision (a Phase D plan item, or a follow-on to this document) selects them over the FreeCAD rebuild. The decision record is AQS-3D-STACK-001 (`STACK_3D_DECISION.md`).

### 3.4 Identifiers

1. The stable identifiers shall be `unit_id` and `stream_id` only. A generic `element` identifier is not used as the primary key.
2. Plant tags (ISA or operator tags) may be added later as aliases; they do not replace `unit_id` or `stream_id`.
3. Streams between blocks keep the `S##` register (AQS-STR-001). Recycle streams within an aisle stay on the line process flow diagrams.

### 3.5 Hierarchy

The hierarchy follows the levels of ISA-95 (Figure 3.1, Table 3.2).

Figure 3.1. Model hierarchy

```
site
 └── area / sector
      └── unit
           └── equipment module
```

Table 3.2. Hierarchy levels

| Level | Examples (locked names stay names) |
|---|---|
| Site | One campus; `SITE_LAT` input |
| Area / sector | The graph's `mvs.sectors` (AQS-SEC-001), for example DIGESTER, OIL, CRYO, FARM, ELEC, MEOH |
| Unit | `LEACH_CSTR_1`, `EW_1`, `SOL_ARK_60K`, `ZNBR2`, `PUMPED_HYDRO` |
| Equipment module | Cassette, PV string, ZnBr2 skid cell, dock bay |

Each sector row shall declare its `sector_definition` under §3.1.

### 3.6 Solver

1. A solver shall close the mass and energy balances and the electrical match (generation, storage and load) against the typed model.
2. The solver shall work with the rest of the Aqueous system: the stream register, the `SCALE_M` rules, and the electrical and continuous-power themes (AQS-REQ-KW-001).
3. The solver shall flag bottlenecks, redundant parallel paths, missing Sector Definitions and unclosed streams.
4. Surplus shall be reported for food, clean water, materials or goods, and energy, with sign and magnitude. These are study tolerances until the power requirements and farm balances are frozen.

### 3.7 Interface behaviour

Table 3.3 sets the required behaviour of the interface.

Table 3.3. Interface behaviour

| Behaviour | Rule |
|---|---|
| Sector toggles | Enable / disable whole sectors; gaps flagged |
| Continuous derate | Allowed on continuous scale classes; discrete classes jump |
| Energy storage trade | MeOH / ZnBr₂ / pumped hydro = **all three required in MVS** (redundancy); sandbox may disable → unreclaimed-resource gaps |
| Cycle views | C, O, H₂O, … with greying of off-cycle geometry and line-weight emphasis on the active cycle |
| Code flags | Flag the **most-restrictive** applicable NFPA / IBC / ISO theme on footprint and height (AQS-COMPL-001 / AQS-EGR-001 themes; not clause text) |
| Crew | UI input (occupancy / life-load driver) |
| `SITE_LAT` | UI input (climate / insolation / geothermal context) |
| Gap panel | List missing Sector Definitions and unclosed `stream_id`s |

### 3.8 Hosting

Deployment proceeds from a local install to GitHub to a cloud service. The local install remains the authoring authority until a published remote exists.

### 3.9 One machine-readable model

1. One typed plant graph (JSON preferred; YAML allowed as an equivalent view), currently `flow_graph/` (AQS-FLOW-GRAPH-001), shall be the only source of topology for units and streams (`typed_graph_sole`). The design tool's `candidate_mvs` is either folded into that graph or produced only as a projection of it, never a competing master (AQS-PLAN-UI-001 Phase A′, WP-Ap1).
2. Sector, surplus and sandbox criteria may be stored with the design-tool schema, but topology (units, streams, layer membership) shall come from the plant graph or its projection.
3. Markdown pages, the optional matplotlib exporters (`pfd_scripts`) and the FreeCAD scripts are consumers or generators of the graph, never competing authorities. `STREAM_REGISTER` and `MASS_FLOW` are derived from it or kept in step with it.

### 3.10 Scale rules

The scale classes follow AQS-SCALE-001 (Table 3.4).

Table 3.4. Scale classes

| Class | Rule |
|---|---|
| Continuous tanks | `ROOF_TANK` / `CATCH_TANK` footprint ∝ plan area |
| Discrete MFG / CRYO | Cassette / basement-plate jumps |
| Module PV / ZnBr2 | Discrete module counts |
| Dock | Discrete by cassette (`DOCK_COUNT = CASSETTE_COUNT`) |

### 3.11 Licence

CERN-OHL-S-2.0 applies to the CAD, the model, the authority documents, the design-tool source and any public or cloud distribution. There is no alternative interface or cloud licence.

## 4. Recommended stack

Table 4.1 gives the recommended software for each layer.

Table 4.1. Recommended stack

| Layer | Recommendation | Notes |
|---|---|---|
| API / solver host | **Python FastAPI** | Fits `params.py`, graph adapters, freecadcmd bridge |
| Topology authority | **Typed plant graph** (`flow_graph/`) | Sole units/streams master; `candidate_mvs` fold or projection |
| Model | **Typed JSON** (± YAML isomorphic) + **Pydantic** | Schema evolves with graph unify (aqs-mvs-*); no dual master |
| Schematic UI | **React + SVG** | **Graph-layer** viewer/editor (Phase B′); cycle greying, toggles, gaps |
| PFD PNG / matplotlib | **Optional exporters** | `pfd_scripts` demoted; bridge from graph only; rewrite optional |
| 3D (later) | **FreeCAD rebuild (bias)** | Three.js / live mesh / LOD only with **written decision** (§3.3) |
| Host | Local process → GitHub package → cloud API | §3.8; Phase C blocked until graph unify |

The reasoning is recorded in the unpublished planning note STACK_REEVAL_2026-10-01.

### 4.1 Alternatives considered

Table 4.2. Alternatives considered

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Node-only full stack | One language in UI | Solver/chem libraries weaker; duplicates Python authority | Reject as primary |
| Django | Batteries | Heavier than needed for JSON+solver API | Should not be default |
| Qt / desktop | Offline CAD feel | Poor GitHub→cloud path; harder SVG schematic share | Defer |
| Streamlit / Gradio | Fast prototype | Not a durable schematic editor | Prototype only |
| Blender as primary 3D | Mesh power | Breaks freecadcmd rebuild path | Reject as authority |
| FreeCAD as sole UI | Already in tree | Weak web/cloud story; schematic second | **Generator / Phase D bias** — not sole interactive UI |
| Three.js as default 3D | Browser-native | Forks from FreeCAD params path unless decided | **Not default**; written decision required |
| matplotlib as topology authority | Existing PFD scripts | Diverges from typed graph | **Reject** — exporters only |
| Dual `candidate_mvs` + `flow_graph` masters | Fast interim | Silent divergence | **Reject** — unify (fold or projection) |

## 5. Rules for `unit_id` and `stream_id`

### 5.1 `unit_id`

1. A `unit_id` shall be a stable string that matches the locked plant name, with spaces and hyphens replaced by `_` (for example `LEACH_CSTR_1`, `HDR_H2`, `SOL_ARK_60K`).
2. A `unit_id` shall be unique within a design pack.
3. Each unit sits under exactly one `sector_id`, with an optional `area_id`.
4. Renaming a locked process flow diagram name is a model change with a new revision, not a silent alias swap.

### 5.2 `stream_id`

1. Streams between blocks shall use the `S##` identifiers of AQS-STR-001 (`S01` and onwards). A new route takes the next free identifier; an identifier is never reused for a different route.
2. Streams within a sector should use `S_<sector>_##`, or keep their local identifiers from the line process flow diagram until they are added to the register.
3. Each stream shall declare `from_unit_id` and `to_unit_id` (or header or boundary nodes), its phase (`S`, `L`, `G` or `E`) and, optionally, a species vector for the solver.
4. Electrical streams on the single-line diagram shall still carry `stream_id` values (for example `S17`, `S20`), so that the mass and energy balance and the electrical match share one graph.

### 5.3 Not allowed

- A primary key named `element` or `element_id`.
- Reusing an `S##` identifier for a new route.
- Orphan streams with neither end found in the unit table, unless explicitly marked as a gap or open boundary because the sandbox is incomplete.

## 6. Model schema (sketch)

Figure 6.1 is an informative sketch, not a frozen JSON Schema file. The field names show the intended form; topology comes from the plant graph, and the schema version may advance.

Figure 6.1. Model schema sketch

```json
{
  "schema_version": "aqs-mvs-0.2",
  "doc_id": "AQS-MVS-001",
  "revision": "A",
  "licence": "CERN-OHL-S-2.0",
  "scale_m": 1.0,
  "mvs_criteria": {
    "loops_closed": true,
    "surplus_export": ["food", "clean_water", "materials_or_goods", "energy"]
  },
  "site": {
    "site_id": "AQS_SITE_M1",
    "site_lat_deg": null,
    "crew": null,
    "jurisdiction_theme": "USA_Dallas_class"
  },
  "sectors": [
    {
      "sector_id": "DIGESTER",
      "sector_definition": "Process (Mass transform)",
      "enabled": true,
      "required_for_mvs_closure": true
    },
    {
      "sector_id": "ELEC",
      "sector_definition": "Utility / header",
      "enabled": true,
      "required_for_mvs_closure": true
    },
    {
      "sector_id": "MEOH",
      "sector_definition": "Energy Storage System (Electrochemical)",
      "enabled": true,
      "required_for_mvs_closure": true
    },
    {
      "sector_id": "PUMPED_HYDRO",
      "sector_definition": "Energy Storage System (Gravity)",
      "enabled": true,
      "required_for_mvs_closure": true
    }
  ],
  "units": [
    {
      "unit_id": "LEACH_CSTR_1",
      "sector_id": "DIGESTER",
      "class": "vessel",
      "tags": [],
      "params": { "V_m3": null },
      "modules": []
    }
  ],
  "streams": [
    {
      "stream_id": "S01",
      "from_unit_id": "BMED_UPW_POLISH",
      "to_unit_id": "HDR_UPW",
      "phase": "L",
      "carries": "UPW",
      "rate": { "value": null, "unit": "kg/d", "status": "study" }
    }
  ],
  "electrical": {
    "bus_nodes": ["SOL_ARK_60K", "ZNBR2", "RECTIFIER"],
    "storage_options": ["ZNBR2", "MEOH", "PUMPED_HYDRO"]
  },
  "scale_rules": {
    "tanks": "continuous",
    "mfg_cryo": "discrete",
    "pv_znbr2": "module",
    "dock": "by_cassette"
  },
  "ui": {
    "cycle_views": ["C", "O", "H2O", "H2", "N", "heat"],
    "sector_toggles": true,
    "gap_panel": true,
    "export_modules": [
      "params", "streams", "sld", "pfd", "bom",
      "compliance_flags", "3d"
    ]
  }
}
```

YAML shall round-trip to the same typed objects. The consumers are the Markdown exporters, the process flow diagram generators, the FreeCAD `params` writers and the bill-of-materials CSV.

`required_for_mvs_closure` marks the sectors the MVS needs for loop closure and surplus, including all three storage peers. A sandbox may switch them off; the solver then reports unreclaimed-resource or incomplete-closure gaps rather than treating the pack as an MVS.

## 7. Solver interface (sketch)

The solver is served by FastAPI (informative). All paths are under `/api/v1` (Table 7.1).

Table 7.1. Solver endpoints

| Method | Path | Role |
|---|---|---|
| `GET` | `/mvs` | Return locked MVS model (read-only) |
| `POST` | `/sandbox` | Create sandbox from MVS + overrides (sectors, scale, crew, `SITE_LAT`) |
| `GET` | `/sandbox/{id}` | Fetch sandbox model |
| `PATCH` | `/sandbox/{id}` | Mutate toggles / params (does not touch MVS) |
| `POST` | `/sandbox/{id}/solve` | Run mass-energy + electrical match + surplus + gaps |
| `GET` | `/sandbox/{id}/flags` | Bottlenecks, redundant paths, gaps, unclosed streams, code flags |
| `POST` | `/sandbox/{id}/export` | Build design pack (§8); optional module list |
| `GET` | `/system-tree` | **Rev E** — AQS-SYS-TREE-001 nodes with resolved unit sets + kW aggregates (read-only) |
| `GET` | `/params` | **Rev E** — `drivers.json` listing with citations and sha (read-only) |
| `GET` | `/regen-status` | **Rev E** — derived-artefact staleness (`_rev_stamp.py --check-only`) + last regen receipt (read-only) |

### 7.1 Solve request and response (sketch)

Figure 7.1. Solve request and response

```json
{
  "request": {
    "sandbox_id": "sbx_…",
    "objectives": [
      "close_mass",
      "close_energy",
      "match_electrical",
      "report_surplus",
      "report_gaps"
    ],
    "tolerances": { "mass_rel": 1e-3, "power_kW": 0.5 }
  },
  "response": {
    "status": "ok | partial | infeasible",
    "mvs_equivalent": false,
    "residuals": { "mass": [], "energy": [], "electrical": [] },
    "surplus": {
      "food": { "value": null, "unit": "kg/d", "status": "study" },
      "clean_water": { "value": null, "unit": "kg/d", "status": "study" },
      "materials_or_goods": { "value": null, "unit": "kg/d", "status": "study" },
      "energy": { "value": null, "unit": "kWh/d", "status": "study" }
    },
    "gaps": [
      {
        "sector_definition": "Energy Storage System (Gravity)",
        "reason": "unreclaimed_resource",
        "sector_id": "PUMPED_HYDRO",
        "detail": "Required ESS peer disabled — incomplete closure / unreclaimed stream"
      }
    ],
    "unclosed_streams": [
      { "stream_id": "S64", "reason": "downstream_sector_off" }
    ],
    "bottlenecks": [
      { "stream_id": "S05", "reason": "H2_pool_contended" }
    ],
    "redundant_paths": [
      { "ids": ["S49", "S45"], "reason": "parallel_H2_consumers" }
    ],
    "code_flags": [
      {
        "theme": "IBC_height_or_NFPA_footprint",
        "controlling": "most_restrictive",
        "refs": ["AQS-COMPL-001", "AQS-EGR-001"]
      }
    ]
  }
}
```

The solver should call the shared Python modules that already encode the rules of AQS-SCALE-001, AQS-REQ-KW-001 and AQS-STR-001, rather than reimplementing them in the interface.

## 8. Design pack contents

Each export shall produce a new directory or archive and shall not replace the MVS tree. The content is modular: the person exporting, or the `export_modules` list of the interface, may leave out artefacts that are not needed (Table 8.1).

Table 8.1. Design pack contents

| Artefact | Module key | Role |
|---|---|---|
| `mvs_snapshot.json` | always | Frozen copy of source MVS revision used |
| `design.json` / `.yaml` | always | Sandbox model as exported (includes gap flags) |
| `README.md` | always | Pack identity, parent MVS rev, date (US Central time), enabled modules |
| `params_overlay.py` or `params.json` | `params` | SCALE_M / bay / module overlays |
| `streams.csv` | `streams` | Stream register slice for this pack |
| `sld.svg` / `sld.json` | `sld` | Electrical single-line (**graph** `views/efd-elec`; WP-C1) |
| `pfd/` | `pfd` | Graph layer SVG/JSON (`views/pfd`+`mfd`; WP-C1); matplotlib optional separate |
| `bom.csv` | `bom` | Equipment roll-up from **graph nodes** + self-copy flags (WP-C1; no invented rates) |
| `compliance_flags.md` | `compliance_flags` | Most-restrictive NFPA/IBC/ISO theme flags |
| `3d/` | `3d` | Mesh / FreeCAD export or rebuild recipe (when available) |
| `gaps.md` | always | Missing Sector Definitions + unclosed streams |

## 9. Phased roadmap (`unify_then_reshape`)

The roadmap follows AQS-PLAN-UI-001 Rev N. The early evidence phase (Phase A, P0) and the interface scaffold (Phase B, P1) are complete. Table 9.1 lists the forward phases and Table 9.2 the completed ones.

Table 9.1. Forward phases

| Phase | Code | Deliverable | Exit criteria |
|---|---|---|---|
| **A′ — Unify** | A′ | Typed plant graph = sole topology authority; fold `candidate_mvs` or make it a projection | Single write path; API/solver consume graph/projection; STREAM/MASS derived/sync; contract tests |
| **B′ — Layer UI on graph** | B′ | **done** 2026-10-01 | React+SVG graph-layer; layer filters PFD/MFD/EFD-*; export graph snapshot; B′ exit Yes; C planned/unblocked |
| **C — Export-from-graph → GitHub** | C | Modular export packs from graph + public CERN-OHL-S package | **WP-C1 done** (local pfd/sld/bom from graph; matplotlib optional); **C2/C3 blocked** pending GitHub publish authorize |
| **D — P2 3D** | D | Campus 3D from same model | **FreeCAD rebuild bias**; Three.js only with written decision |
| **E — P3 Cloud** | E | Hosted API/UI under CERN-OHL-S | Auth, pack storage; MVS still immutable |

Table 9.2. Completed phases

| Phase | Status | Path |
|---|---|---|
| **P0 — Schema + solver / evidence** | **done** | `design_tool/` schema aqs-mvs-0.3; FastAPI; Phase A WPs; ESS peers required |
| **P1 — Schematic UI scaffold** | **done**; **B′ done** | `design_tool/web/` Vite+React+TS; Phase B exit + B′ exit 2026-10-01 (US Central time) |

The plant graph is in `flow_graph/` (AQS-FLOW-GRAPH-001). Its adapter, layer SVG and process flow diagram bridges are issued (WP-A10, closed). Folding `candidate_mvs` into the graph is done (WP-Ap1): it is now a generated projection of `plant_flow_graph.json` (`export_candidate_mvs.py`).

Planning is in the unpublished planning notes DESIGN_UI_COMPLETION_PLAN (AQS-PLAN-UI-001 Rev N) and STACK_REEVAL_2026-10-01.

The local install shall stay usable at every phase.

## 10. Authority and synchronisation

- `docs-authority/AUTHORITY.md` (AQS-AUTH-001) points to this document (AQS-UI-001).
- The scale authority remains `docs-authority/SCALE_MODEL.md` and `models/freecad/params.py`.
- Planning audits are local planning records. They are separate from the CAD authority and are not published.

## 11. Decided questions

Table 11.1 records questions decided in Rev C.

Table 11.1. Decided questions

| # | Question | Decision |
|---|---|---|
| 1–3 | MVS footprint / downsizing / ESS | Reframed (Rev C): MVS = **self-sustaining colony** (manufacture, habit, self-copy, scale) + **closed loops + surplus export**. **All three** ESS peers (ZNBR2, MEOH, PUMPED_HYDRO) **required in MVS**; sandbox may disable → **unreclaimed-resource / incomplete-closure** gaps (not accepted emissions). Bay count alone does not freeze MVS. |
| 4 | Export pack minimum | Confirmed modular set in §8; always include model snapshot, design JSON, gaps, README; other modules optional. |
| 5 | Licence | **CERN-OHL-S-2.0** for UI, model, CAD, and cloud. |

### 11.1 Open questions

These are not to be answered by assumption.

1. Formal freeze of `AQS-MVS-001`: which on-disk revision first passes the surplus and closure tests of §3.2, with evidence tables?
2. Surplus thresholds: study tolerances compared with hard pass criteria for food, water, goods and energy, tied to the farm and to AQS-REQ-KW-001. Study thresholds are issued in AQS-SUR-001 (`SURPLUS_PASS_THRESHOLDS.md`).
3. Sector Definition catalogue: closed. The catalogue is `docs-authority/SECTOR_DEFINITIONS.md` (AQS-SEC-001). The class list remains in §3.1 of this document; questions on how sectors map to classes are in AQS-SEC-001 §5.
4. Choice of 3D path: FreeCAD rebuild by default (§3.3, Phase D). Three.js, a live mesh or levels of detail only with a written decision that revises the 3D stack.
5. Folding `candidate_mvs` into the graph: done (WP-Ap1, graph write and projection). Phase C remains blocked until Phase A′ is complete (WP-Ap2 contract tests).

## 12. Related documents

Table 12.1. Related documents

| Doc | ID | Role |
|---|---|---|
| AUTHORITY.md | AQS-AUTH-001 | Hub pointer |
| DOCUMENTATION_STYLE.md | AQS-DOC-002 | House style |
| SCALE_MODEL.md | AQS-SCALE-001 | Growth rules |
| STREAM_REGISTER.md | AQS-STR-001 | `S##` IDs |
| MASS_FLOW.md | AQS-MF-001 | Closed-loop claims |
| COMPLIANCE_MATRIX.md | AQS-COMPL-001 | Code themes |
| CONTINUOUS_KW_REQUIREMENTS.md | AQS-REQ-KW-001 | Electrical match inputs |
| REBUILD.md | AQS-REB-001 | Regeneration pipeline |
| SECTOR_DEFINITIONS.md | AQS-SEC-001 | sector_id → Sector Definition catalogue |
| MeOH_TRAIN.md | AQS-MeOH-001 | MeOH ESS / process peer |
| Local planning artefacts (not published): MVS_GAP / SECTOR_CAPACITY / LEGACY_PROFILE audits | AQS-MVS-GAP-001 / AQS-AUD-001 / AQS-GAP-001 | Planning audits; not CAD authority |

## 13. Implementation status of the unified engine

The three endpoints added in Rev E (§7, Table 7.1) are implemented in `design_tool/aqs_design_tool/api/app.py`, and the web panels (ParamsPanel, TreeTogglePanel, RegenStatusBadge) in `design_tool/web/src/components/`.

Sandbox switches exist at four levels: `sector_enabled`, `system_enabled`, `subsystem_enabled` and `unit_enabled`. The server resolves them with the most specific level winning (`store.apply_overrides`), against the sector, train and unit tree in `flow_graph/system_tree.yaml` (AQS-SYS-TREE-001).

`/regen-status` reads `flow_graph/derived/_regen_receipt.json`, which `python3 -m flow_graph.param.regen` writes. It checks staleness with the same evaluator (`--check-only`), so a GET request has no side effects.

Details of the panels and of the precedence rule are in `design_tool/README.md` and `design_tool/web/README.md`. The implementing commits are 5f77bee (tree), f64ad84 (regeneration) and fc083f8 (interface).
