# Campus plan - recycle core, farm, fab, habitation and cryo blocks

Document number: AQS-CMP-001
Revision: C
Date: 2026-10-25

| Rev | Description | Date |
|---|---|---|
| A | First issue: campus blocks, header split and phase plan | 2026-09-27 |
| B | Block envelopes re-stated from `models/freecad/params.py`; wave checkboxes updated | 2026-09-27 |
| C | Rewritten to the documentation style guide (AQS-DOC-002). Planning jargon removed; the invented label "Salria" replaced by plain wording (the same ruling as the retired invented label in Q-017); each locked name marked present or retired against graph Rev AC. No rule or envelope changed. | 2026-10-25 |

Licence: CERN-OHL-S-2.0. Plant artwork is the scripted diagrams and the parametric CAD; no rendered imagery is used.

## 1. Purpose and scope

This page records the campus plan that grew the plant from the recycle aisle to the full block layout: the standing rules for what may share a header, the locked block names and envelopes, and the phase order in which the diagrams and the CAD were built. The plant flow graph is now the authority for what exists; `docs-authority/BUILDING_STACK.md` and `docs-authority/PHASE_F_ENVELOPES.md` are the authorities for floors and envelope sizes. This page keeps the rules and the plan history.

## 2. Standing rules

1. The four process headers stay on the recycle aisle: HDR_DUST, HDR_ACID_GAS, HDR_H2 and HDR_OIL_VAPOR. HDR_CAUSTIC stays with the digest and BMED base duty. None of them enters FARM, WAFER_FAB or HABITATION.
2. Life-support gases are separate headers: HDR_O2, HDR_N2 and HDR_CO2. Process cathode hydrogen may feed the cold box or the fuel cell after H2_DRYER; it never tees into HDR_O2.
3. The ZnBr2 bromine tower shares no header and no cold box with the CRYO trains.
4. Wafer-fab etchant and metals return in a closed line to the leach: stream S10 carries WET_BENCH to LEACH_CSTR_1. There is no floor drain.
5. Aluminium, magnesium, calcium, lithium and the rare earths are not electrowon from the chloride liquor. Farm nutrients come from the P-Al, P-Mg and P-Ca cakes, struvite and the BMED salts, not from a new electrowinning aisle.
6. FR-4 never enters INDUCTION PYROLYZER.
7. One parameter file per model set. Campus dimensions live in `models/freecad/params.py` (the envelopes are placed by `models/freecad/campus.py`). No second copy of a dimension constant is forked.

## 3. Locked block names and envelopes

Table 3.1 states the blocks as locked at revision A, with their envelope and their state in graph Rev AC.

Table 3.1. Campus blocks

| Block | CAD name | Envelope (mm) | Floor | In graph Rev AC |
|---|---|---|---|---|
| Recycle core aisle | (existing plant) | per `PHASE_F_ENVELOPES.md` | L-1/L0 | yes (sector CORE units) |
| Farm | `FARM` | 12 000 x 18 000 x 4 500 | L1 | block retired as a unit; the grow bed (GROW_BED, 29.12 m2) and NUTRIENT_DOSE are the graph units |
| Wafer fab | `WAFER_FAB` | 12 000 x 8 000 x 4 000 | L0 | yes |
| Habitation | `HABITATION` | 12 000 x 18 000 x 3 200 | L1 | yes |
| Cryo | `CRYO` | 6 000 x 6 000 x 4 000 | L-1, east of CORE | yes (CRYO_ASU, CRYO_H2, CRYO_O2, CRYO_N2, CRYO_CO2) |
| Manufacturing shop | `MFG_SHOP` | 12 000 x 10 000 x 5 000 | L0 | yes |

## 4. Life and utility headers

Table 4.1 records the header split at issue. The names are the locked strings; the graph carries the live edge list.

Table 4.1. Life and utility headers locked at revision A

| Header | Carries | Must never carry |
|---|---|---|
| HDR_UPW | Electrodeionised and polished water below 1 microS/cm | leach liquor, etchant, grey water |
| HDR_O2 | Cold-box and farm oxygen to HABITATION | process hydrogen, acid gas |
| HDR_N2 | Cold-box nitrogen to WAFER_FAB and FARM | air in-leak into the acid header |
| HDR_CO2 | Cold-box CO2 and the hab return to FARM | afterburner flue as a raw duct |
| HDR_GREY | Hab and farm condensate and wash water | blackwater (the blackwater barrier train owns that duty) |
| HDR_ORG | Plant waste and hab organics to the hopper or the oil line | FR-4, glass |
| HDR_ETCH | Fab spent etchant to the leach | sewer discharge |

## 5. Unit names locked at revision A, and what became of them

Revision A locked the first unit names per block so the diagrams could start. Table 5.1 records each name and its state in graph Rev AC; the graph node list is the current authority.

Table 5.1. Locked names and their present state

| Name locked at Rev A | State in graph Rev AC |
|---|---|
| FISH_TANK, BIOFILTER, FARM_SUMP, LED_CANOPY | retired; the aquaponic loop left the design and the grow bed is GROW_BED |
| GROW_BED | present as GROW_BED |
| NUTRIENT_DOSE | present as NUTRIENT_DOSE |
| FAB_PREP, FAB_TOOL, ETCH_RETURN | retired; the fab duty is carried by WET_BENCH and the tools of the FAB sector (see AQS-IF-FAB-WET-001 review) |
| WET_BENCH | present as WET_BENCH |
| HAB_AIR, HAB_WATER, HAB_WASTE, GALLEY, SLEEP | retired as separate units; the duties are HABITATION internals and the blackwater barrier train (AQS-DUTY-063) |
| COLD_BOX | present as CRYO_ASU ("air liquefaction cold box", the plain wording per Q-017) |
| CRYO_H2, CRYO_O2, CRYO_N2, CRYO_CO2 | present as CRYO_H2, CRYO_O2, CRYO_N2, CRYO_CO2 |
| ED, UPW POLISH, CONDENSATE | retired as named units; the water utility is the RO/EDI train of the WTR sector |

No second leach tank, no pre-leach filter and no shared campus stack were added.

## 6. Phase record

The build proceeded in phases. All phases are complete; the outputs listed here are the current artifacts.

- Phase 0, register: block names and envelopes (Table 3.1), the inter-block stream table (`docs-authority/STREAM_REGISTER.md`) and the process-versus-life header split (Table 4.1).
- Phase 1, overview diagrams: the plant process flow diagram generated from the graph (`flow_graph/views/pfd.svg`, from `flow_graph/render_layer_views.py`) and the nutrient diagram (`nutrient_pfd.png`, from `flow_graph/exporters/matplotlib/nutrient_pfd.py`). The hand-drawn campus overview, water-cycle and life-gas sheets of revision A were superseded by these generated views.
- Phase 2, block diagrams: the farm, wafer-fab, habitation, cryo and manufacturing-shop process flow diagrams.
- Phase 3, CAD massing: `models/freecad/campus.py` (four keep-out boxes from `params.py`), `farm.py`, `wafer_fab.py`, `habitation.py`, `cryo.py`, `mfg_shop.py`, attached by `models/freecad/build_plant.py`. Object names are the Table 5.1 strings with underscores.
- Phase 4, shop detail: the life-support nozzle schedule (`docs-authority/LIFE_NOZZLE_SCHEDULE.md`, AQS-NZ-002) and the first-article models of the farm, fab, habitation water and cryo units. The OpenSCAD unit models follow only after a unit's phase-3 origin is frozen. The foam-board electrowinning coupon model (`models/openscad/foam_ew/`) is a coupon model; it does not stand in for the plant cells.
- Phase 5, routed utilities: the life-header tier table (`docs-authority/LIFE_HEADERS.md`, AQS-PIP-002), the life racks (`_life_racks` in `models/freecad/pipe_services.py`: RACK_LIFE_N/S/W/E) and `mfg_life_rack.scad`. HDR_ORG stays a tote and conveyor path with no tee onto the four process headers.

## 7. Work order inside a phase

1. Update `docs-authority/STREAM_REGISTER.md` if a new stream appears.
2. Draw or edit the diagram; the reader checks names and forbidden mixes against Section 2 and Table 4.1.
3. Place or move the CAD envelope.
4. Add nozzles on that envelope.
5. Only then internals.

A change that would mix HDR_ACID_GAS with HDR_O2, send fab etchant to a sewer, or feed FR-4 to INDUCTION PYROLYZER stops.

## 8. File ownership

| File | Owns |
|---|---|
| `docs-authority/CAMPUS_PLAN.md` | phases and campus names (this page) |
| `docs-authority/STREAM_REGISTER.md` | inter-block streams |
| `docs-authority/PHASE_F_ENVELOPES.md` | envelope sizes and origins |
| `flow_graph/render_layer_views.py` | overview sheet |
| `GLOSSARY.md` | definitions once a name is drawn |

Rebuild the overview with `python3 -m flow_graph.param.regen` (the `regen_derived` stage runs `flow_graph/render_layer_views.py`).
