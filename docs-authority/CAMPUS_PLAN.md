# Campus plan — recycle core + farm + fab + habitation + cryo

Document number: AQS-CMP-001  
Revision: B  
Date: 2026-09-27

Waves. Broad strokes first. Do not invent synonyms for names already
in `GLOSSARY.md`. New names in §2 are locked by this file unless the
operator strikes them.

Licence: CERN-OHL-S-2.0. No diffusion plant pictures.

---

## 0. What already exists

Recycle core PFDs and CAD are the authority for the wet / oil / glass /
BMED / gas / electrical aisle. Do not redraw that chemistry.

| Layer | Where |
|---|---|
| Names | `GLOSSARY.md` (locked strings) |
| Plant PFD | `continuous_recycling_pfd.png` |
| Line PFDs | wet, EW, oil, glass, BMED, polish, ZnBr2, SLD, container |
| 3D | `models/freecad/build_plant.py` → `plant.FCStd` |
| Campus boxes | `PHASE_F_ENVELOPES.md`, `freecad/campus.py` |
| Inter-block streams | `docs-authority/STREAM_REGISTER.md` |

Gaps this plan fills: farm, wafer fab, habitation, cryo internals;
water / life-gas / nutrient cycles; PFDs and CAD that sit *outside*
the four process gas headers.

Vertical building (basement dirty → roof tank): `docs-authority/BUILDING_STACK.md`
and `building_section_pfd.png`. Plan-view envelopes still apply *on*
those floors.

---

## 1. Rules that do not move

1. Four process headers stay on the recycle aisle: HDR_DUST,
   HDR_ACID_GAS, HDR_H2, HDR_OIL_VAPOR. HDR_CAUSTIC stays with digest /
   BMED BASE. None of these enter FARM, WAFER_FAB, or HABITATION.
2. Life-support gases are separate objects: HDR_O2, HDR_N2, HDR_CO2.
   Process cathode H₂ may feed CRYO or fuel *after* H2_DRYER. It does
   not tee into HDR_O2.
3. ZnBr2 Br₂ tower does not share a header or a cold box with CRYO.
4. WAFER_FAB etchant and metals return in a closed line to REGEN LEACH
   / LEACH CSTR 1. No floor drain.
5. Al, Mg, Ca, Li, REE are not electrowon from this chloride liquor.
   Farm nutrients come from P-Al / P-Mg / P-Ca cakes, struvite, and
   BMED salts — not from a new EW aisle.
6. FR-4 still never enters INDUCTION PYROLYZER.
7. One parameter file per model set. Campus mm live in
   `models/freecad/params.py` (envelopes already there via `campus.py`).
   Do not fork a second `CSTR_L`.

---

## 2. Locked campus names

Pattern matches `internal/SYSTEM_MODEL_PLAN.md`: equipment in SMALL CAPS,
CAD `Name` uses `_`.

### 2.1 Blocks (already on the plant tree)

| Drawing | CAD `Name` | Envelope (mm) |
|---|---|---|
| FARM | `FARM` | 12 000 × 18 000 × 4 500 on **L1** (AQS-BLD-001) |
| WAFER FAB | `WAFER_FAB` | 12 000 × 8 000 × 4 000 on **L0** |
| HABITATION | `HABITATION` | 12 000 × 18 000 × 3 200 on **L1** |
| CRYO | `CRYO` | 6 000 × 6 000 × 4 000 on **L-1** east of CORE (18, 6) |
| MFG SHOP | `MFG_SHOP` | 12 000 × 10 000 × 5 000 on **L0** |

### 2.2 New headers (life / utility — not process gas)

| Header | Carries | Must not carry |
|---|---|---|
| HDR_UPW | ED / polish water < 1 µS/cm | leach, etch, grey |
| HDR_O2 | CRYO / farm O₂ to HABITATION | process H₂, acid gas |
| HDR_N2 | CRYO N₂ to FAB / FARM | air in-leak into acid header |
| HDR_CO2 | CRYO + hab return → FARM | afterburner flue as a raw duct |
| HDR_GREY | hab / farm condensate and wash | Salria |
| HDR_ORG | plant waste + hab organics → HOPPER or OIL LINE | FR-4, glass |
| HDR_ETCH | fab spent etch → REGEN LEACH | sewer |

### 2.3 Wave-2 units (locked here so PFDs can start)

**FARM**

| Name | Role |
|---|---|
| FISH TANK | aquaponics livestock |
| BIOFILTER | NH₄⁺ → NO₃⁻ |
| GROW BED | hydroponic / aeroponic |
| FARM SUMP | water loop with HDR_GREY / HDR_UPW makeup |
| LED CANOPY | DC from yard |
| NUTRIENT DOSE | struvite, NH₄ salts, chelates from core |

**WAFER FAB**

| Name | Role |
|---|---|
| FAB PREP | Si from core + recovered Al / Cu / Fe |
| WET BENCH | clean / etch, UPW + HCl / NaOH from BMED |
| FAB TOOL | dry tools, N₂ purge |
| ETCH RETURN | HDR_ETCH to REGEN LEACH |

**HABITATION**

| Name | Role |
|---|---|
| HAB AIR | O₂ in, CO₂ out, Q4 HVAC |
| HAB WATER | UPW / grey split |
| HAB WASTE | solids / liquor to core (HDR_ORG + SALT FEED path) |
| GALLEY | food from FARM |
| SLEEP | berth envelope |

**CRYO**

| Name | Role |
|---|---|
| COLD BOX | Stirling 77–90 K + distillation / PSA |
| CRYO H2 | product, not HDR_H2 |
| CRYO O2 | to HDR_O2 |
| CRYO N2 | to HDR_N2 |
| CRYO CO2 | to HDR_CO2 |

**WATER** (shared utility, sits with BMED / Q4)

| Name | Role |
|---|---|
| ED | already implied by BMED middle / polish water |
| UPW POLISH | conductivity spec for FAB / HAB |
| CONDENSATE | HVAC + dryer + farm |

Do not add a second leach tank, a pre-leach filter, or a shared stack
to “simplify” campus air.

---

## 3. Waves

### Wave 0 — register  ← this file

- [x] Block names and envelopes
- [x] Inter-block stream table (`STREAM_REGISTER.md`)
- [x] Header split (process vs life)

### Wave 1 — board-stroke PFDs

- [x] Campus overview
- [x] Water / life-gas / nutrient sheets

One sheet per cycle. Boxes and labelled arrows only. No internals.

| Sheet | Script | Output |
|---|---|---|
| Campus overview | `pfd_scripts/campus_pfd.py` | `campus_pfd.png` |
| Water cycle | `pfd_scripts/water_cycle_pfd.py` | `water_cycle_pfd.png` |
| Life gas | `pfd_scripts/life_gas_pfd.py` | `life_gas_pfd.png` |
| Nutrient / N-P | `pfd_scripts/nutrient_pfd.py` | `nutrient_pfd.png` |

Recycle-core PFDs already exist. Wave 1 does not replace them.

### Wave 2 — block PFDs

- [x] `farm_pfd.png`
- [x] `wafer_fab_pfd.png`
- [x] `habitation_pfd.png`
- [x] `cryo_pfd.png`
- [x] `mfg_shop_pfd.png`

### Wave 3 — CAD massing

- [x] Scripts written. Rebuild on the operator box (`build_plant.py`).

Same order as the recycle line: envelope, then nozzles, then feed.

| Script | Adds |
|---|---|
| `freecad/campus.py` | four keep-out boxes from `params.py` |
| `freecad/farm.py` | farm units inside `FARM` |
| `freecad/wafer_fab.py` | fab units inside `WAFER_FAB` |
| `freecad/habitation.py` | hab units inside `HABITATION` |
| `freecad/cryo.py` | cold box + CRYO_H2/O2/N2/CO2 |
| `freecad/mfg_shop.py` | `MFG_SHOP` at (2000, 9000) |
| `freecad/build_plant.py` | attach after `campus.attach` |

Object names = §2 strings with `_`. Labels via `labels.py`.

### Wave 4 — shop detail

- [x] Nozzle schedule `LIFE_NOZZLE_SCHEDULE.md` (AQS-NZ-002)
- [x] `mfg_fish_tank` / `biofilter` / `grow_bed` / `farm_sump` / `nutrient_dose`
- [x] `mfg_wet_bench` / `etch_return` / `hab_water` / `hab_waste` / `cold_box`
- [x] FreeCAD stubs `campus_shop.py` (operator rebuilds STLs)

OpenSCAD `mfg_*` only after the Wave-3 origin of that unit is frozen.
Foam-board 1:3 EW (`cad/foam_ew/`) stays a coupon model. It does not
replace plant EW cells.

### Wave 5 — routed utilities between blocks

- [x] `LIFE_HEADERS.md` (AQS-PIP-002) tier table
- [x] `pipe_services.py` `_life_racks` — RACK_LIFE_N/S/W/E
- [x] `mfg_life_rack.scad`
- [x] `life_headers_pfd.png`

HDR_ORG stays a tote / conveyor path. No tee onto the four process
headers.

---

## 4. Work order inside a wave

1. Update `STREAM_REGISTER.md` if a new stream appears.
2. Draw or edit the PFD. Operator reads names and forbidden mixes.
3. Place or move the CAD envelope.
4. Add nozzles on that envelope.
5. Only then internals.

Stop if a stream would mix HDR_ACID_GAS with HDR_O2, or send fab etch
to sewer, or put farm waste in INDUCTION PYROLYZER as FR-4.

---

## 5. File ownership

| File | Owns |
|---|---|
| `docs-authority/CAMPUS_PLAN.md` | waves + campus names |
| `docs-authority/STREAM_REGISTER.md` | inter-block streams |
| `docs-authority/PHASE_F_ENVELOPES.md` | box sizes / origins |
| `pfd_scripts/campus_pfd.py` | overview sheet |
| `freecad/campus.py` | four keep-out solids |
| `GLOSSARY.md` | definitions once a name is drawn |

Rebuild overview: `python3 pfd_scripts/campus_pfd.py`.
