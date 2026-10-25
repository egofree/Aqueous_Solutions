# Wafer fab equipment and process list

Document number: AQS-EQP-FAB-001  
Revision: C  
Date: 2026-10-24  
Process flow diagrams: AQS-PFD-FAB-001 (`wafer_fab_pfd.png`); reagents AQS-PFD-FAB-RGN-001 (`fab_reagent_forks_pfd.png`); ultrapure water AQS-PFD-FAB-UPW-001.  
Basis: `03-silicon-wafer-fabrication.md`; `MANUFACTURING/SILICON_FAB/Silicon_Fab_overview.md`; `freecad/wafer_fab.py`; AQS-STR-001; AQS-MF-001; AQS-WTR-001; AQS-EQP-FAB-RGN-001; AQS-GAP-001.  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Placeholder forge→cut chain; wet-line forks TBD | 2026-09-27 |
| B | 1 | Ordered forge→cut train; CZ recommendation; reagent interface | 2026-09-27 |
| C | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; sections renumbered (the solar-cell branch is now §6); working-log wording removed. Units, train and decisions unchanged. | 2026-10-24 |

## 1. Purpose and scope

The plant makes its own silicon wafers from silicon it recovers by electrowinning. This page sets the process that feeds and uses the fab units modelled in `freecad/wafer_fab.py`: the choice of crystal-growth method, the ordered equipment train from crystal to cleaned wafer, the solar-cell branch, the fab streams and the reagent interface. It does not add FreeCAD solids; the train tags in §5 are process names, not yet solids, apart from the units in §3.

## 2. Terms

- Czochralski (CZ) pulling: growing a single-crystal ingot (boule) by slowly drawing a seed crystal from molten silicon.
- Fluidised-bed reactor (FBR): a reactor that grows polysilicon granules in a bed of particles kept suspended by gas.
- Boule: the single-crystal ingot.
- Lapping: flattening wafers between plates with an abrasive slurry.
- RCA clean: the standard two-step wet clean for silicon wafers (developed at RCA).
- RTA: rapid thermal anneal.
- L0: building level 0. M1, M2: the first and second modules of the plant.

Stream numbers are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Fab units (level 0 cassette)

These massing names are fixed in `freecad/wafer_fab.py` (Table 3.1).

Table 3.1. Fab units

| Tag | Duty |
|---|---|
| FAB_PREP | Slice / dope handoff; receives polished-prep wafers from cut train |
| WET_BENCH | RCA / etch / rinse with fab UPW (S27) + acids/bases (S09, S31–S35) |
| FAB_TOOL | Dry tools (ox, litho, implant/diffusion, metal, RTA, probe); N₂ purge (S03) |
| ETCH_RETURN | HDR_ETCH collect → REGEN LEACH (S10) |

## 4. Crystal-growth method

Root document 03 §4.1 names Czochralski pullers or fluidised-bed reactors. The older `Silicon_Fab_overview.md` schedules a laboratory or pilot Czochralski puller, and the control narrative (§5.1) and energy domain (§4.4.2) of document 03 are for Czochralski pulling (Table 4.1).

Table 4.1. Crystal-growth options

| Option | Role | Evidence | M1 status |
|---|---|---|---|
| **Czochralski (CZ)** | Melt Si @ ~1414 °C; seed pull → monocrystalline ingot 150–300 mm class | Doc 03 §4.1, §5.1; SILICON_FAB Mermaid | **Recommended primary** |
| Fluidized-bed reactor (FBR) | Polysilicon / powder feed path from electrowon Si | Doc 03 §4.1, §4.2 (boule charge or FBR feedstock) | Alternate / later cassette — not primary M1 solid |

Decision: the M1 crystal forge is a Czochralski puller. Electrowon silicon powder (the S08 crib) is the boule charge. The fluidised-bed reactor remains a documented alternative for when the cassette count or the powder form warrants it; a second forge is not modelled.

## 5. Equipment train, crystal to cleaned wafer

The stages below set the order for AQS-PFD-FAB-001.

### 5.1 Crystal forge, cooling and anneal

Table 5.1. Crystal forge

| Stage | Tag | Duty | Utilities / notes |
|---|---|---|---|
| 1 | CZ_CHARGE | Si powder / scrap charge prep from S08 crib | Ar / N₂ blanketing TBD |
| 2 | CZ_PULLER | Czochralski puller — Si melt → monocrystalline ingot | Induction heat; S03 N₂; LN₂ cool path per doc 03 / 09 |
| 3 | INGOT_COOL | Controlled cool-down / stress relief after pull | N₂; no water quench into etch drain |
| 4 | INGOT_ANNEAL | Optional post-growth anneal (800–1200 °C class) | Doc 03 §4.4.3 energy domain |

### 5.2 Crop, grind, saw and edge

Table 5.2. Crop, grind, saw and edge

| Stage | Tag | Duty | Notes |
|---|---|---|---|
| 5 | CROP_GRIND | Crop seed/tail; OD grind to diameter | Kerf / grind dust → HDR_DUST / S08 recycle |
| 6 | ID_WIRE_SAW | Multi-wire diamond saw (primary) or ID saw (alternate) | Doc 03 / SILICON_FAB; kerf slurry → recovery |
| 7 | EDGE_PROFILE | Edge grind / profile | Broken edge scrap → S08 / leach |

### 5.3 Lapping, polish preparation and clean

Table 5.3. Lapping, polish preparation and clean

| Stage | Tag | Duty | Reagents |
|---|---|---|---|
| 8 | LAP_CMP | Lapping → CMP (colloidal silica slurry) | S37 slurry; spent → S39 / leach |
| 9 | PRE_CLEAN | Post-CMP rinse / dilute clean before handoff | S27 UPW |
| 10 | → FAB_PREP | Handoff into locked L0 cassette | Solid wafers only on this arrow |

### 5.4 Level 0 tool train

Table 5.4. Level 0 tool train

| Stage | Tag | Duty |
|---|---|---|
| 11 | FAB_PREP | Slice / dope handoff staging |
| 12 | WET_BENCH | RCA SC-1/SC-2, HF oxide strip, wet etch, cascade rinse |
| 13 | FAB_TOOL | Thermal ox, litho (coat/align/develop), diffusion/implant, plasma/wet etch finish, metal, RTA, probe |
| 14 | ETCH_RETURN | Spent baths → S10 HDR_ETCH → REGEN LEACH |

Photolithography, implantation and metallisation stay inside the `FAB_TOOL` massing (AQS-GAP-001, Partial). Separate CAD bays for them are not modelled.

## 6. Solar-cell branch (architecture Partial)

`Silicon_Fab_overview.md` and root document 03 require a photovoltaic branch from polished wafers: alkaline texture (KOH), POCl₃ emitter, SiNₓ anti-reflection coating, Ag/Al contacts, belt firing and IV test. Its equipment schedule is `docs-authority/SOLAR_CELL_EQUIPMENT.md` (AQS-EQP-FAB-PV-001), the `PV_TEXTURE` to `PV_IV` train (Table 6.1).

Table 6.1. Solar-cell branch status

| Item | Status |
|---|---|
| Texture / emitter / ARC / contact / fire | **Partial** — schedule issued; not in L0 FreeCAD |
| KOH feed | Mapped on AQS-EQP-FAB-RGN-001 (`WS_KOH`) |
| Power offtake (cells → campus PV) | Narrative only; electrical yard sizing unchanged |
| Dedicated PFD / FreeCAD solids | **Done** — AQS-PFD-FAB-PV-001 + PV_* envelopes |

The branch is not to be dropped. Nameplate power for the belt furnace or the PECVD tool is not invented until the in-house tool designs set it (X-MFG-38).

## 7. Fab streams

Table 7.1. Fab streams

| ID | Role | Authority |
|---|---|---|
| S08 | Si / metals / silicate in (crib) | AQS-STR-001 |
| S01 / S21 | Pre-remin plant water → FAB UPW | AQS-WTR-001 |
| S27 | Fab UPW > 18 MΩ·cm → WET_BENCH | AQS-STR-001 |
| S09 | HCl / NaOH PRODUCT → WET_BENCH | BMED |
| S03 | N₂ purge / cool | CRYO |
| S10 | Etch return → REGEN LEACH | closed |
| S31–S39 | Fab wet-reagent forks | AQS-EQP-FAB-RGN-001 / AQS-STR-001 Rev C |

Mass rates are to be determined; no balance is invented.

## 8. Wet-line reagent interface

The dedicated synthesis forks and the reagent map are in AQS-EQP-FAB-RGN-001 (`docs-authority/FAB_WET_REAGENTS.md`), with an optional interface note in `docs-authority/FAB_WET_INTERFACE.md`. The process flow diagram is AQS-PFD-FAB-RGN-001.

The SEM-Tech ion-exchange membrane work is referenced by link only (`DEPENDENCIES.md`); its membrane code is not copied into the fab.

## 9. Open items

1. FreeCAD solids for `CZ_PULLER` to `PRE_CLEAN` (with the `SCALE_M` and cassette work).
2. Solar-cell branch: the schedule (AQS-EQP-FAB-PV-001), its process flow diagram and FreeCAD envelopes are done; vendor power ratings are still open.
3. Separating photolithography, implantation and metallisation out of `FAB_TOOL` once the plant reaches module M2.
4. Restoring the terraces and `SCALE_M = 1` (AQS-REM-BLD-001), outside fab chemistry.

## 10. Rebuilding the drawings

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 wafer_fab_pfd.py
python3 fab_reagent_forks_pfd.py
python3 fab_upw_pfd.py
```
