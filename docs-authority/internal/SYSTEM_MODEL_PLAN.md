# System 3D model plan

Full-plant FreeCAD / OpenSCAD model. Check a box when the solid exists,
is named with a locked string, and rebuilds from `/usr/bin/freecadcmd`.
Do not invent synonyms. Protocol: `FREECAD_PROTOCOL.md`.

This file’s Phase A/B/C are the **model-fidelity** phases the operator
set on 2026-09-26. They overlay the earlier wet-line construction order
(still valid for *where* things sit).

---

## Naming

| Kind | Pattern | Example |
|---|---|---|
| Equipment | locked name, `_` for space/hyphen | `LEACH_CSTR_1`, `EW_1`, `INDUCTION_PYROLYZER` |
| Subassembly group | `SA_<LINE>` | `SA_WET`, `SA_OIL`, `SA_GLASS`, `SA_ELEC`, `SA_GAS` |
| Product crib | `PROD_<STREAM>` | `PROD_METALS`, `PROD_C5_C10`, `PROD_SILICATE` |
| Hovering label plate | `LBL_<UNIT>` | `LBL_EW_1` |
| Safety sign | `SIGN_<HAZARD>_<WHERE>` | `SIGN_H2_EW_AISLE` |
| Header | `HDR_DUST`, `HDR_ACID_GAS`, `HDR_H2`, `HDR_OIL_VAPOR` | already used |

Label plates: 400 × 120 × 8 mm, Z = 1600 (standing eye-line), parented
in space above the walkway in front of the machine — not glued to the
lid. Feature name **is** the label; do not depend on Draft ShapeString
(headless 1.0 has no reliable font).

Safety signs: 500 × 400 × 12 mm, Z = 1500, 600 mm off the equipment
face toward the operator path. Color later; topology first.

---

## Phase A — FreeCAD 3D PFD of the whole plant

Massing. Every unit that appears on the PFDs has a body, a label plate,
and any sign that belongs at a standing position. Electrical gear is
in the model, not a 2D overlay.

### A0. Tooling

- [x] `FREECAD_PROTOCOL.md` (1.0 binaries, argv gate, Part::Feature, no helix pipe)
- [x] Shared `params.scad` / `freecad/params.py`
- [x] `freecad/labels.py` — `label_plate(name, x, y, z)` and `sign(name, x, y, z)`
- [x] `freecad/build_plant.py` — load `wet_line.FCStd` if present, else
      `leach_cstr.FCStd`, then attach A2–A5. One document: `PLANT`.

### A1. Wet line — already built (construction steps 1–10)

- [x] LEACH CSTR 1 + CSTR 2 weir + CSTR 3 floor auger
- [x] Lid drop slot + coaming, LEACHATE PUMP + strainer
- [x] HOPPER / SHREDDER + dust hood + vibratory conveyor
- [x] FLOAT DEWATER + SINK DEWATER + VIBRATORY SPLIT
- [x] OIL LINE stub + GLASS / CERAMIC BRANCH stub
- [x] EW-1…9 on bund, liquor pipe, harvest VDF, pails
- [x] Four header pipes (schematic)

### A2. Wet line — to finished products  ← next solids

Liquor path after EW-9, solids path after the funnels.

- [x] P-Al, P-Mg, P-Ca tanks after EW-9 (+X). (`wet_products.py`)
- [x] POLISH BANK PK-1…PK-9. PK-4 / PK-5 = CEM boxes. (`wet_products.py`)
- [x] BMED REGEN +Y of CSTR 1: stack, NaOH PRODUCT, HCl PRODUCT, CRU,
      SALT FEED, REGEN LEACH. (`wet_products.py`)
- [x] PROD_METALS crib + per-metal bins Au…Zn. (`wet_products.py`)
- [x] MELT stub. (`wet_products.py`)
- [x] LBL_* on wet units and EW-1…9 metals. (`labels.py`)
- [x] Wet signs listed above. (`labels.py` / `wet_products.py`)
- [x] PK-6 / PK-9 sealed lids + dedicated acid-gas hose.

### A3. Oil line  (off the existing OIL LINE stub)

- [x] DRYER, INDUCTION PYROLYZER, QUENCH, FRACTIONATOR, four cut tanks,
      AFTERBURNER massing + oil signs. (`oil_line.py`)
      Coils, packed column internals, flue jacket solid: Phase B/C.

### A4. Glass / ceramic line  (off the existing GLASS stub)

- [x] RINSE + DEWATER, BURNOUT ROTARY, MILL, NaOH DIGEST, three product
      bins + glass signs. (`glass_line.py`)
      Flue-jacket solid and rinse-liquor pipe: Phase C.

### A5. Electrical systems  (spatial, not a schematic)

Sit outside both process atmospheres. See `electrical_sld.png`,
`ELECTRICAL.md`, `FLOW_BATTERY.md`.

- [x] RECTIFIER, ATS, SOL_ARK_60K, ZNBR2 + Br₂ scrubber, PV_ARRAY,
      arc-flash and Br₂ signs. (`electrical_yard.py`)
      Separate pos/neg electrolyte tanks: refine later.

### A6. Phase A exit criteria

- [x] Operator confirmed 2026-09-26: FreeCAD view looks good (CSTR, aisle,
      products, oil, glass, electrical).
- [x] Naming convention in force. Four headers remain four objects.
- [x] No second leach tank. No pre-leach filter. No FR-4 in the pyro pipe.

---

## Phase B — OpenSCAD detail parts, then import

Small parts that Part scripting is bad at. Export STL/STEP, `Part.insert`
or mesh-proxy in FreeCAD. Do not rebuild the plant in OpenSCAD.

- [x] `models/openscad/detail/` one part per file, includes `../params.scad`
- [x] `cstr3_flight.scad` — true helix (not yet swapped into the FC tank)
- [x] `cem_cassette.scad`
- [x] `funnel_valve.scad`
- [x] `induction_coil.scad`
- [x] `bmed_cell.scad`
- [x] `znbr2_iem.scad`
- [x] `import_details.py` places STLs as `DETAIL_*` meshes on the plant
      after `models/openscad/detail/build_stls.sh`. Missing STL is a skip, not a crash.

---

## Phase C — Gas handling to a full utility model

Headers exist as pipes. This phase gives them equipment.

- [x] DEMISTER + ALK_SCRUBBER + FAN_STACK + SCRUBBER_TO_CRU (`gas_handling.py`)
- [x] BAGHOUSE + FINES_TO_CSTR
- [x] H2_DRYER + H2_STACK (separate from oil vapor)
- [x] QUENCH remains the oil-vapor condenser; flue is `HX7_FLUE_JACKET` only
- [x] Br₂ packed tower remains `ZNBR2_BR2_SCRUBBER` on the battery
- [x] HVAC_Q4 massing next to SALT FEED
- [x] ZNBR2_POS_TANK / ZNBR2_NEG_TANK (`electrical_yard.py`)

---

## Phase F / G — campus (farm, fab, hab, cryo)

Plan: `docs-authority/CAMPUS_PLAN.md`. Do not start Wave-4 shop models until
Wave-3 origins are frozen.

- [x] F0 envelopes + F0_campus.png
- [x] Wave 0 names + stream register
- [x] Wave 1 overview PFD (`campus_pfd.png`)
- [x] Wave 1b water / life-gas / nutrient sheets
- [x] Wave 2 block PFDs
- [x] Wave 3 CAD internals (scripts; operator rebuilds plant.FCStd)
- [x] Wave 4 campus shop SCAD + AQS-NZ-002
- [x] Wave 5 life-header racks (AQS-PIP-002)

---

## Phase D — animation

- [x] Brief: `docs-authority/internal/ANIMATION_BRIEF.md` (D1–D6, cameras, bans)
- [x] Waypoints: `freecad/animate_shots.py` (D1–D6 + C29 + NCG)
- [x] Schematic frames: `freecad/render_frames.py` → `models/freecad/animation/`
- [ ] Optional GUI 12 fps overlay on `plant.FCStd` — operator box only

---

## File ownership

| File | Owns |
|---|---|
| `freecad/leach_cstr.py` | vessel, feed train, fork stubs |
| `freecad/ew_cell.py` | one funnel cell |
| `freecad/build_wet.py` | aisle, bund, pipe, harvest, headers |
| `freecad/labels.py` | plates + signs |
| `freecad/wet_products.py` | precip, polish, BMED, metals crib |
| `freecad/oil_line.py` | dryer → cuts + afterburner |
| `freecad/glass_line.py` | rinse → grit |
| `freecad/electrical_yard.py` | rectifier through PV |
| `freecad/build_plant.py` | assembly document `PLANT` |
| `freecad/gas_handling.py` | demister, scrubber, baghouse, H2, HX-7 jacket |
| `models/openscad/detail/*.scad` | Phase B printable / importable parts |
| `models/openscad/detail/build_stls.sh` | OpenSCAD → `detail/stl/` |
| `freecad/import_details.py` | mesh insert onto PLANT |
| `docs-authority/internal/ANIMATION_BRIEF.md` | Phase D shot list |
| `freecad/pipe_services.py` | racks, trays, ground ring |
| `freecad/campus.py` | FARM / WAFER_FAB / HABITATION / CRYO boxes |
| `docs-authority/FAN_STACK.md` | ID fans + stack heights |
| `docs-authority/WELD_MAP.md` | JW-001…029 joint register |
| `docs-authority/CSTR_NOZZLE_SCHEDULE.md` | N1–N12 + GF articles |
| `freecad/animate_shots.py` | D1–D5 waypoints |
| `assembly_wet.scad` | OpenSCAD twin of wet + later includes |

Rebuild: `leach_cstr.py` → `ew_cell.py` → `build_wet.py` →
`bash models/openscad/detail/build_stls.sh` → `build_plant.py`.

---

## Status log

- 2026-09-26: A1 complete.
- 2026-09-26: Plan opened. A0–A5 generators written.
- 2026-09-26: Operator signed A6. PK-6/9 lids+hose. ZnBr tanks.
  Phase C gas massing (`gas_handling.py`). Phase B detail `.scad`
  written; STL import into FreeCAD still open.
- 2026-09-26: Plan closed in-repo. `import_details.py`, C29 recycle,
  rinse→salt pipe, Phase D brief + waypoints. GUI capture of D1–D6
  is the only remaining operator-box step.

---

## Authority lock (2026-09-27)

**CAD truth = AQS-BLD-001 Rev B.** See `docs-authority/AUTHORITY.md`.
Phase F flat Z=0 envelopes are subordinate keep-outs only.

| File | Owns |
|---|---|
| `docs-authority/AUTHORITY.md` | Single active CAD authority |
| `docs-authority/BUILDING_STACK.md` | Levels, cores, shafts, masses |
| `freecad/building_stack.py` | SLAB_*, CORE_*, SHAFT_*, STAIR_*, ELEV_SVC, ROOF_TANK, CATCH_TANK, ARRAY_ROOF |
| `freecad/fire_barriers.py` | FB_* + HA_L1_L0, HA_L0_Lm1, HA_Lm1_Lm2 |
| `docs-authority/MASS_FLOW.md` | AQS-MF-001 closed vs open streams |

Process cassette: wet_line local Z=0 = L-1 FFL; `build_plant.py` shifts by `Z_Lm1`.

### Building stack CAD

- [x] Authority lock documented
- [x] Floor plates L-2…L2 + CORE_LIFE / CORE_PROCESS
- [x] SHAFT_H2 / ACID / OIL / UTIL / PENSTOCK + STAIR_P / S* / ELEV_SVC
- [x] ROOF_TANK + CATCH_TANK + ARRAY_ROOF (tilt = site latitude)
- [x] FB_* + HA_* horizontal assemblies
- [x] Campus re-origin to BLD levels
- [ ] Building / campus / life / hazard PFD generators restored under `pfd_scripts/`
- [ ] `iso_fab_drawings.pdf` recreated from `iso/*.png`

