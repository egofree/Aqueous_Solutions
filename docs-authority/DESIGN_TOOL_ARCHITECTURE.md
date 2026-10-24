# Design-tool architecture — Aqueous MVS sandbox

Document number: AQS-UI-001  
Revision: D  
Date: 2026-10-01  
Authority: AQS-AUTH-001; style AQS-DOC-001; scale AQS-SCALE-001
(`SCALE_M = 1.0`); streams AQS-STR-001; mass-flow AQS-MF-001;
compliance themes AQS-CMP-001; flow graph AQS-FLOW-GRAPH-001;
plan AQS-PLAN-UI-001 Rev N (`unify_then_reshape`).  
**Stage = architecture lock.** Not shipped software. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: MVS/sandbox rules, schema, solver, UI stack, roadmap | 2026-10-01 |
| B | Sector taxonomy + surplus MVS | Sector Definition classes; MVS = closed loops + surplus export; modular export; Odysseus internal-only; CERN-OHL-S for UI+model | 2026-10-01 |
| B+ | Catalogue pointer | AQS-SEC-001 Rev A issued (`SECTOR_DEFINITIONS.md`); §11.1 item 3 closed by catalogue | 2026-10-01 |
| C | Colony MVS + all ESS | MVS = self-sustaining colony (manufacture, habit, self-copy, scale); all three ESS peers required; disabled ESS → unreclaimed-resource / incomplete-closure gaps | 2026-10-01 |
| D | unify_then_reshape | Typed plant graph = sole topology authority; fold/project `candidate_mvs`; matplotlib demoted to optional exporters; roadmap A′→B′→C→D→E; 3D FreeCAD bias (Three.js only with written decision); Odysseus out of runtime; stack re-eval `planning/STACK_REEVAL_2026-10-01.md` | 2026-10-01 |
| E | Unified-engine wiring | Working UI on the unified parametric system: read-only `/system-tree`, `/params`, `/regen-status` endpoints; ParamsPanel / TreeTogglePanel / RegenStatusBadge; four-level sandbox toggles (sector/system/subsystem/unit) resolving most-specific-wins server-side; regen receipt as the provenance the badge reads (commits eedb79f, d44e7de, 5024743) | 2026-10-19 |

Licence: **CERN-OHL-S-2.0** for CAD, MVS model, authority docs, design-tool UI, and public/cloud surfaces. Full freedom of information — no separate UI/cloud licence.

---

## 1. Purpose

Define the architecture of an interactive design tool that:

1. Classifies every plant sector by a **Sector Definition** (role in the
   mass–energy graph).
2. Treats the **Minimum Viable System (MVS)** as the smallest **self-
   sustaining human colony** (Moon/Mars class intent): full manufacturing
   + habitation; can make its own parts; can **copy itself** (RepRap-
   class); can **scale up** (GVCS-class) or **down**; **closes all loops**
   including **all three ESS peers**; and still **produces a surplus** of
   food, clean water, raw materials (or manufactured goods), and energy —
   i.e. overproduction and export, not mere self-sustainment.
3. Lets a **sandbox** enable or disable any subset of sectors/modules,
   continuously derate where rules allow, and **flag gaps** (missing
   roles, unclosed streams) without inventing closure.
4. **Never overwrites** the locked MVS — every sandbox outcome exports a
   new design pack (modular artefacts; unused modules off).

---

## 2. Scope

| In | Out |
|---|---|
| Sector Definition taxonomy; unit_id / stream_id rules | Rewriting root narrative folders `01-…`–`09-…` |
| Typed JSON/YAML MVS schema sketch | Vendor nameplates as issued ratings |
| Mass-energy + electrical match solver API | Live PE / AHJ permit issuance |
| Schematic-first UI (React/SVG graph-layer); 3D later (FreeCAD bias) | Overwriting MVS files in place |
| Sector toggles; gap / unclosed-stream flags; cycle views; code-flag hooks | Any runtime dependency on Odysseus |
| Modular export pack; phased roadmap | Mixing Odysseus AGPL data into the MVS or UI tree |
| Host path local → GitHub → cloud | Invented permits or clause quotations |

Canonical in this tree: `docs-authority/DESIGN_TOOL_ARCHITECTURE.md`  
---

## 3. Locked decisions

### 3.1 Sector Definition (taxonomy)

Every sector (and energy-relevant unit class) **shall** carry a
**Sector Definition**: a role type that tells the solver whether the
block is a source, a load, storage (charge/discharge), a sink/export, or
a process transformer. Definitions are orthogonal to physical bay
layout.

| Sector Definition | Mode behaviour | Examples (illustrative) |
|---|---|---|
| **Energy Storage System (Gravity)** | Alternating **load** (charge / pump-up) and **source** (discharge / generate) | Pumped hydro |
| **Energy Storage System (Electrochemical)** | Alternating charge / discharge; chemical + electrical legs | ZnBr₂ flow battery; MeOH store + IEM / DMFC path |
| **Energy Production (Electrical)** | Source (generation); may be intermittent | Solar PV |
| **Energy Production (Combustion Engine)** | Source when fuelled; load on fuel / oxidizer streams | Backup H₂ genset |
| **Energy Production (Electrochemical)** | Source when reactants available | PEM FC; IEM MeOH FC |
| **Process (Mass transform)** | Transforms streams; usually a load electrically | WET, OIL, GLASS, FAB wet, MFG |
| **Life support / habitat** | Load + export opportunity (food, water, waste return) | HAB, FARM |
| **Utility / header** | Distributes; rarely a net source | CRYO cold-box, HVAC/geo Q4, headers |
| **Export / dock** | Boundary sink or source for surplus goods / freight | North dock, freight elevator |

Rules:

1. **Any or all** components may be missing in a sandbox. The solver
   **shall** note **gaps** (absent Sector Definitions that the graph
   still references) and **unclosed mass / energy streams** where those
   gaps reappear — it **shall not** silently invent closure.
2. Energy storage classes **shall** model both charge and discharge
   modes on the same unit (or paired units) so electrical match and
   mass balance stay consistent.
3. Physical `SCALE_M` / bay / cassette rules (AQS-SCALE-001) remain the
   **layout** driver; Sector Definition is the **role** driver. A
   smaller envelope is valid MVS **only if** loops close (including all
   required ESS peers) **and** surplus criteria in §3.2 are met — bay
   count alone does not define MVS. Scaled-down omissions are modelled
   as unreclaimed / incomplete closure (§3.2 item 2).

### 3.2 MVS and sandbox

1. **MVS** **shall** be the smallest plant configuration that:
   - constitutes a **self-sustaining human colony** at Moon/Mars class
     intent: **full manufacturing + habitation**; ability to **make its
     own parts**; ability to **copy itself** (RepRap-class self-
     replication); and ability to **scale up** (GVCS-class) or **scale
     down**;
   - includes the Sector Definitions required to **close all loops**
     (AQS-MF-001 / AQS-STR-001), including **all three** ESS peers
     (**ZNBR2**, **MEOH**, **PUMPED_HYDRO**) enabled — **redundancy is a
     core tenet**; MeOH also feeds other process streams (not ESS-only);
   - still produces a **surplus** suitable for **export** of:
     - food,
     - clean water,
     - raw materials **or** manufactured goods, and
     - energy.
   Self-sustainment alone is **not** sufficient; the goal remains
   **overproduction and export**.
2. **Scaled-down** configurations (capabilities omitted for practical
   reasons) **may** be useful operationally, but the model **shall**
   treat missing capabilities as **incompletely closed** loops /
   **unreclaimed resource streams** — problems to solve — **not** as
   accepted pollution, emissions, or silent losses.
3. The **sandbox** **shall** allow:
   - enable / disable any sector or module (checkbox),
   - continuous derate where AQS-SCALE-001 continuous classes apply
     (e.g. tank footprint ∝ plan),
   - discrete jumps where those rules apply (cassette, dock, PV/ZnBr₂
     modules).
   When any **required** ESS peer (or other required sector) is off, the
   solver **shall** emit an **unreclaimed-resource / incomplete-closure**
   gap (`reason: unreclaimed_resource` for ESS peers) and **shall not**
   invent storage or mass closure.
4. Export **shall not** be blocked solely because a non-MVS sandbox has
   sectors off. Instead the pack **shall** carry **gap and unclosed-
   stream flags**. Blocking export is reserved for hard schema /
   integrity failures (orphan IDs, corrupt model), not “incomplete vs
   MVS.”
5. The tool **shall not** overwrite the locked MVS in place. Any sandbox
   edit **shall** export a **new design pack** (§8).
6. On-disk plant baseline remains `SCALE_M = 1.0` in
   `models/freecad/params.py` as the **current manufacturing baseline**.
   Whether that exact envelope is the frozen MVS gold file is decided
   by applying §3.2 surplus + closure tests, not by bay count alone.
   Until an explicit freeze commit of `AQS-MVS-001`, the baseline is
   **candidate MVS**.

### 3.3 Schematic first; 3D later

1. The first interactive surface **shall** be a **2D schematic** (PFD /
   SLD / layered graph views), not a free-orbit 3D editor. Under
   **unify_then_reshape**, the schematic **shall** be a **graph-layer
   viewer/editor** over the typed plant graph (Phase B′), not a second
   topology store.
2. 3D **shall** follow export-from-graph lock (Phase D). **Default bias:
   FreeCAD rebuild** from the graph / `params` model (`freecadcmd` /
   AQS-REB-001). Live parametric mesh, LOD campus mesh, and **Three.js**
   remain candidates **only** if a **written decision** (Phase D plan item or
   this file follow-on) selects them over FreeCAD rebuild.

### 3.4 Identifiers

1. Stable IDs **shall** be `unit_id` and `stream_id` only. Do **not** use
   a generic `element` ID as the primary key.
2. Optional plant tags (ISA / operator tags) **should** be added later as
   aliases; they **shall not** replace `unit_id` / `stream_id`.
3. Inter-block streams **shall** keep the existing `S##` register
   (AQS-STR-001). Intra-aisle recycles remain on line PFDs.

### 3.5 Hierarchy (ISA-95-ish)

```
site
 └── area / sector
      └── unit
           └── equipment module
```

| Level | Examples (locked names stay names) |
|---|---|
| Site | One campus; `SITE_LAT` input |
| Area / sector | WET, OIL, GLASS, CRYO, FAB, MFG, FARM, HAB, ELEC, TRR, MEOH, … |
| Unit | `LEACH_CSTR_1`, `EW_1`, `SOL_ARK_60K`, `ZNBR2`, `PUMPED_HYDRO` |
| Equipment module | Cassette, PV string, ZnBr2 skid cell, dock bay |

Each sector row **shall** declare `sector_definition` per §3.1.

### 3.6 Solver

1. A solver **shall** close **mass-energy** balances and **electrical
   match** (generation / storage / load) against the typed MVS model.
2. The solver **shall** integrate with the larger Aqueous system
   (stream register, SCALE_M rules, ELECTRICAL / AQS-REQ-KW-001 themes).
3. The solver **shall** flag **bottlenecks**, **redundant parallel
   paths**, **missing Sector Definitions**, and **unclosed streams**.
4. Surplus metrics **shall** be reported for food, clean water, materials /
   goods, and energy (sign and magnitude; study tolerances until
   AQS-REQ / farm balances freeze).

### 3.7 UI behaviours (locked)

| Behaviour | Rule |
|---|---|
| Sector toggles | Enable / disable whole sectors; gaps flagged |
| Continuous derate | Allowed on continuous scale classes; discrete classes jump |
| Energy storage trade | MeOH / ZnBr₂ / pumped hydro = **all three required in MVS** (redundancy); sandbox may disable → unreclaimed-resource gaps |
| Cycle views | C, O, H₂O, … with greying of off-cycle geometry and line-weight emphasis on the active cycle |
| Code flags | Flag the **most-restrictive** applicable NFPA / IBC / ISO theme on footprint and height (AQS-CMP-001 / AQS-EGR-001 themes; not clause text) |
| Crew | UI input (occupancy / life-load driver) |
| `SITE_LAT` | UI input (climate / insolation / geothermal context) |
| Gap panel | List missing Sector Definitions and unclosed `stream_id`s |

### 3.8 Host path

Deployment **shall** progress: **local → GitHub → cloud**. Local remains
the authoring authority until a published remote exists.

### 3.9 Single machine-readable model (typed plant graph sole)

1. One typed **plant graph** (JSON preferred; YAML allowed as isomorphic
   view), presently `flow_graph/`
   (**AQS-FLOW-GRAPH-001**), **shall** be the **sole topology authority**
   for units and streams (`typed_graph_sole`). Design-tool
   `candidate_mvs` **shall** be **folded into** that graph **or** exposed
   only as a **projection** of it — never a competing master
   (AQS-PLAN-UI-001 Phase A′ / WP-Ap1).
2. Sector / surplus / sandbox **MVS criteria** fields may travel with the
   design-tool schema, but **topology** (units, streams, layer membership)
   **shall** resolve from the plant graph (or its projection).
3. Markdown notes, matplotlib `pfd_scripts` (optional exporters), and
   FreeCAD scripts **shall** be **consumers or generators** secondary to
   that graph — not competing authorities once the graph is issued.
   `STREAM_REGISTER` / `MASS_FLOW` **shall** be derived or kept in sync.

### 3.10 Scale rules (align AQS-SCALE-001)

| Class | Rule |
|---|---|
| Continuous tanks | `ROOF_TANK` / `CATCH_TANK` footprint ∝ plan area |
| Discrete MFG / CRYO | Cassette / basement-plate jumps |
| Module PV / ZnBr2 | Discrete module counts |
| Dock | Discrete by cassette (`DOCK_COUNT = CASSETTE_COUNT`) |

### 3.11 Odysseus (internal meta only)

1. Odysseus (**AQS-ORG-001**) **shall** remain a **separate**, local-only
   planning/research layer for the **meta project** (designing the design
   system).
2. The **end-user design UI** **shall not** depend on Odysseus at runtime
   (no required deep-links, no shared database, no AGPL data in the MVS
   or UI tree).
3. Optional human navigation between spaces is fine for the Aqueous team;
   it is **out of scope** for the shipped design tool.

### 3.12 Licence

**CERN-OHL-S-2.0** applies to CAD, MVS model, authority docs, design-tool
UI source, and public/cloud distributions. No alternate UI/cloud licence.

---

## 4. Recommended stack

| Layer | Recommendation | Notes |
|---|---|---|
| API / solver host | **Python FastAPI** | Fits `params.py`, graph adapters, freecadcmd bridge |
| Topology authority | **Typed plant graph** (`flow_graph/`) | Sole units/streams master; `candidate_mvs` fold or projection |
| Model | **Typed JSON** (± YAML isomorphic) + **Pydantic** | Schema evolves with graph unify (aqs-mvs-*); no dual master |
| Schematic UI | **React + SVG** | **Graph-layer** viewer/editor (Phase B′); cycle greying, toggles, gaps |
| PFD PNG / matplotlib | **Optional exporters** | `pfd_scripts` demoted; bridge from graph only; rewrite optional |
| 3D (later) | **FreeCAD rebuild (bias)** | Three.js / live mesh / LOD only with **written decision** (§3.3) |
| Host | Local process → GitHub package → cloud API | §3.8; Phase C blocked until graph unify |
| Meta tracker | Odysseus **out** of runtime | AQS-ORG-001 local meta only; CERN-OHL-S for product |

Re-eval record (planning-only): `planning/STACK_REEVAL_2026-10-01.md`.

### 4.1 Alternatives weighed (brief)

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

---

## 5. `unit_id` / `stream_id` rules

### 5.1 `unit_id`

1. `unit_id` **shall** be a stable string matching locked plant names
   with spaces/hyphens → `_` (same convention as
   `SYSTEM_MODEL_PLAN.md`: `LEACH_CSTR_1`, `HDR_H2`, `SOL_ARK_60K`).
2. `unit_id` **shall** be unique within a design pack.
3. Hierarchy fields **shall** place each unit under exactly one
   `sector_id` (and optional `area_id`).
4. Renaming a locked PFD name **shall** be a revisioned model change,
   not a silent alias swap.

### 5.2 `stream_id`

1. Inter-block streams **shall** use `S##` from AQS-STR-001 (`S01`…);
   new routes get the next free ID — **never** reuse an ID for a
   different route.
2. Intra-sector streams **should** use `S_<sector>_##` or keep line-PFD
   local IDs until promoted to the register.
3. Each stream **shall** declare `from_unit_id`, `to_unit_id` (or
   header/boundary nodes), phase (`S`/`L`/`G`/`E`), and optional species
   vector for the solver.
4. Electrical “streams” on the SLD **shall** still carry `stream_id`
   values (existing `S17`, `S20`, …) so mass-energy and electrical match
   share one graph.

### 5.3 Forbidden

- Primary key named `element` or `element_id`.
- Reusing `S##` for a new route.
- Orphan streams with neither endpoint resolvable in the unit table
  (unless explicitly marked as a **gap / open boundary** for sandbox
  incompleteness).

---

## 6. MVS JSON / YAML schema sketch

Informative sketch — not yet a frozen JSON Schema file. Field names are
normative intent through Rev D (topology authority = plant graph; schema version may advance).

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
      "sector_id": "WET",
      "sector_definition": "Process (Mass transform)",
      "enabled": true,
      "required_for_mvs_closure": true
    },
    {
      "sector_id": "ELEC_PV",
      "sector_definition": "Energy Production (Electrical)",
      "enabled": true,
      "required_for_mvs_closure": true
    },
    {
      "sector_id": "ZNBR2",
      "sector_definition": "Energy Storage System (Electrochemical)",
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
    },
    {
      "sector_id": "BACKUP_GEN",
      "sector_definition": "Energy Production (Combustion Engine)",
      "enabled": true,
      "required_for_mvs_closure": false
    }
  ],
  "units": [
    {
      "unit_id": "LEACH_CSTR_1",
      "sector_id": "WET",
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

YAML **shall** round-trip to the same typed objects. Consumers:
markdown exporters, PFD generators, FreeCAD `params` writers, BOM CSV.

`required_for_mvs_closure` marks sectors the **gold MVS** needs for loop
closure + surplus (including **all three** ESS peers). Sandbox may turn
them off; the solver then flags **unreclaimed-resource / incomplete-
closure** gaps rather than pretending the pack is still MVS.

---

## 7. Solver API sketch

FastAPI surface (informative). All paths under `/api/v1`.

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

### 7.1 Solve request / response (sketch)

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
        "refs": ["AQS-CMP-001", "AQS-EGR-001"]
      }
    ]
  }
}
```

The solver **should** call into shared Python modules that already encode
AQS-SCALE-001 / AQS-REQ-KW-001 / AQS-STR-001 rules rather than
re-implementing them in the UI.

---

## 8. Export pack contents

Each export **shall** produce a new directory (or archive) that does
**not** replace the MVS tree. Content is **modular**: the user (or API
`export_modules` list) **may** omit artefacts they do not need.

| Artefact | Module key | Role |
|---|---|---|
| `mvs_snapshot.json` | always | Frozen copy of source MVS revision used |
| `design.json` / `.yaml` | always | Sandbox model as exported (includes gap flags) |
| `README.md` | always | Pack identity, parent MVS rev, date CT, enabled modules |
| `params_overlay.py` or `params.json` | `params` | SCALE_M / bay / module overlays |
| `streams.csv` | `streams` | Stream register slice for this pack |
| `sld.svg` / `sld.json` | `sld` | Electrical single-line (**graph** `views/efd-elec`; WP-C1) |
| `pfd/` | `pfd` | Graph layer SVG/JSON (`views/pfd`+`mfd`; WP-C1); matplotlib optional separate |
| `bom.csv` | `bom` | Equipment roll-up from **graph nodes** + self-copy flags (WP-C1; no invented rates) |
| `compliance_flags.md` | `compliance_flags` | Most-restrictive NFPA/IBC/ISO theme flags |
| `3d/` | `3d` | Mesh / FreeCAD export or rebuild recipe (when available) |
| `gaps.md` | always | Missing Sector Definitions + unclosed streams |

---

## 9. Phased roadmap (**unify_then_reshape**)

Aligned to AQS-PLAN-UI-001 Rev N. Historical P0 evidence (Phase A) and P1
scaffold (Phase B) are **complete**. Forward phases:

| Phase | Code | Deliverable | Exit criteria |
|---|---|---|---|
| **A′ — Unify** | A′ | Typed plant graph = sole topology authority; fold `candidate_mvs` or make it a projection | Single write path; API/solver consume graph/projection; STREAM/MASS derived/sync; contract tests |
| **B′ — Layer UI on graph** | B′ | **done** 2026-10-01 | React+SVG graph-layer; layer filters PFD/MFD/EFD-*; export graph snapshot; B′ exit Yes; C planned/unblocked |
| **C — Export-from-graph → GitHub** | C | Modular export packs from graph + public CERN-OHL-S package | **WP-C1 done** (local pfd/sld/bom from graph; matplotlib optional); **C2/C3 blocked** pending GitHub publish authorize |
| **D — P2 3D** | D | Campus 3D from same model | **FreeCAD rebuild bias**; Three.js only with written decision |
| **E — P3 Cloud** | E | Hosted API/UI under CERN-OHL-S | Auth, pack storage; MVS still immutable |

**Historical (closed):**

| Phase | Status | Path |
|---|---|---|
| **P0 — Schema + solver / evidence** | **done** | `design_tool/` schema aqs-mvs-0.3; FastAPI; Phase A WPs; ESS peers required |
| **P1 — Schematic UI scaffold** | **done**; **B′ done** | `design_tool/web/` Vite+React+TS; Phase B exit + B′ exit 2026-10-01 CT |

**Graph seed:** `flow_graph/` (AQS-FLOW-GRAPH-001);
adapter + layer SVG + process PFD bridges issued (WP-A10 Closed). Unify of
`candidate_mvs` **WP-Ap1 done** — generated projection of `plant_flow_graph.json` (`export_candidate_mvs.py`).

Planning: `planning/DESIGN_UI_COMPLETION_PLAN.md` (AQS-PLAN-UI-001 Rev N);
stack re-eval `planning/STACK_REEVAL_2026-10-01.md`.

Local host **shall** remain usable at every phase. Odysseus is **not**
a phase dependency.

---

## 10. Sync and authority

- Pointer: `docs-authority/AUTHORITY.md` (AQS-AUTH-001) → this file (**AQS-UI-001**).
- Scale truth remains `docs-authority/SCALE_MODEL.md` / `freecad/params.py`.
- Share mirror via `rebuild.py --sync` into
  `share/aqueous-solutions/docs-authority/`.
- Planning audits (local planning artefacts, not published) are separate from
  CAD authority and are not mirrored into the public share tree.
- No git commit from agent passes unless the operator explicitly requests one.
- Odysseus board (**AQS-ORG-001**) may track meta tasks for building this
  tool; it is not an authority for the MVS model or UI runtime.

---

## 11. Closed questions (Rev C)

| # | Question | Decision |
|---|---|---|
| 1–3 | MVS footprint / downsizing / ESS | Reframed (Rev C): MVS = **self-sustaining colony** (manufacture, habit, self-copy, scale) + **closed loops + surplus export**. **All three** ESS peers (ZNBR2, MEOH, PUMPED_HYDRO) **required in MVS**; sandbox may disable → **unreclaimed-resource / incomplete-closure** gaps (not accepted emissions). Bay count alone does not freeze MVS. |
| 4 | Export pack minimum | Confirmed modular set in §8; always include model snapshot, design JSON, gaps, README; other modules optional. |
| 5 | Odysseus | **Separate.** Meta planning only. Design UI **shall not** rely on it. |
| 6 | Licence | **CERN-OHL-S-2.0** for UI, model, CAD, and cloud. |

### 11.1 Remaining open (do not invent)

1. **Formal freeze of `AQS-MVS-001`** — Which on-disk revision first
   passes the §3.2 surplus + closure tests with evidence tables?
2. **Surplus numeric thresholds** — Study tolerances vs hard MVS pass
   criteria for food / water / goods / energy (tie to farm and
   AQS-REQ-KW-001).
3. ~~**Complete Sector Definition catalogue**~~ — **Issued:** `docs-authority/SECTOR_DEFINITIONS.md`
   (**AQS-SEC-001** Rev D). Class list remains AQS-UI-001 §3.1; ambiguities
   for the operator in AQS-SEC-001 §5 (schema worker reconcile).
4. **3D path pick** — **Bias FreeCAD rebuild** (§3.3 / Phase D). Three.js /
   live mesh / LOD only with a **written decision** revising the 3D stack.
5. **`candidate_mvs` unify** — **WP-Ap1 done** (graph write + projection).
   Phase C remains blocked until A′ exit (WP-Ap2 contract tests).

---

## 12. Related documents

| Doc | ID | Role |
|---|---|---|
| AUTHORITY.md | AQS-AUTH-001 | Hub pointer |
| DOCUMENTATION_STYLE.md | AQS-DOC-001 | House style |
| SCALE_MODEL.md | AQS-SCALE-001 | Growth rules |
| STREAM_REGISTER.md | AQS-STR-001 | `S##` IDs |
| MASS_FLOW.md | AQS-MF-001 | Closed-loop claims |
| COMPLIANCE_MATRIX.md | AQS-CMP-001 | Code themes |
| CONTINUOUS_KW_REQUIREMENTS.md | AQS-REQ-KW-001 | Electrical match inputs |
| ODYSSEUS_PLANNING.md | AQS-ORG-001 | Separate meta planning (not UI runtime) |
| REBUILD.md | AQS-REB-001 | PFD / plant / share sync |
| SECTOR_DEFINITIONS.md | AQS-SEC-001 | sector_id → Sector Definition catalogue |
| MeOH_TRAIN.md | AQS-MeOH-001 | MeOH ESS / process peer |
| Local planning artefacts (not published): MVS_GAP / SECTOR_CAPACITY / LEGACY_PROFILE audits | AQS-MVS-GAP-001 / AQS-AUD-001 / AQS-GAP-001 | Planning audits; not CAD authority |

---

## 13. Unified-engine implementation status (Rev E, 2026-10-19)

Issued, not sketch. The three §7 Rev E endpoints are implemented in
`design_tool/aqs_design_tool/api/app.py`; the web panels (ParamsPanel, TreeTogglePanel,
RegenStatusBadge) in `design_tool/web/src/components/`. Sandbox toggles now exist at four
levels — `sector_enabled`, `system_enabled`, `subsystem_enabled`, `unit_enabled` — resolved
most-specific-wins server-side (`store.apply_overrides`) against
`flow_graph/system_tree.yaml` (AQS-SYS-TREE-001: 19 sectors / 30 trains / 178 leaves).
`/regen-status` reads `flow_graph/derived/_regen_receipt.json`, written by
`python3 -m flow_graph.param.regen`, and checks staleness through the same evaluator
(`--check-only`) so a GET stays side-effect free. Panel and precedence details:
`design_tool/README.md` and `design_tool/web/README.md`. Implementation commits:
eedb79f (tree), d44e7de (regen), 5024743 (UI).
