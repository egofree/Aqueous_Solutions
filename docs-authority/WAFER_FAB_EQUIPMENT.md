# Wafer fab equipment / process list

Document number: AQS-EQP-FAB-001  
Revision: B  
Date: 2026-09-27  
PFD: AQS-PFD-FAB-001 (`wafer_fab_pfd.png`); reagents AQS-PFD-FAB-RGN-001
(`fab_reagent_forks_pfd.png`); UPW AQS-PFD-FAB-UPW-001

Authority: `03-silicon-wafer-fabrication.md`,
`MANUFACTURING/SILICON_FAB/Silicon_Fab_overview.md`, `freecad/wafer_fab.py`,
AQS-STR-001, AQS-MF-001, AQS-WTR-001, AQS-EQP-FAB-RGN-001, AQS-GAP-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Placeholder forge→cut chain; wet-line forks TBD | 2026-09-27 |
| B | 1 | Ordered forge→cut train; CZ recommendation; reagent interface | 2026-09-27 |

Licence: CERN-OHL-S-2.0.

---

## 1. Locked CAD units (L0 cassette)

These massing names are locked in `freecad/wafer_fab.py`. This sheet
schedules the process that feeds and uses them. It does **not** add
FreeCAD solids this pass.

| Tag | Duty |
|---|---|
| FAB_PREP | Slice / dope handoff; receives polished-prep wafers from cut train |
| WET_BENCH | RCA / etch / rinse with fab UPW (S27) + acids/bases (S09, S31–S35) |
| FAB_TOOL | Dry tools (ox, litho, implant/diffusion, metal, RTA, probe); N₂ purge (S03) |
| ETCH_RETURN | HDR_ETCH collect → REGEN LEACH (S10) |

---

## 2. Crystal growth method — options and recommendation

Doc 03 §4.1 names **Czochralski pullers or fluidized-bed reactors**.
Legacy `Silicon_Fab_overview.md` schedules a lab/pilot **Czochralski**
puller. Doc 03 §5.1 control narrative and §4.4.2 energy domain are CZ.

| Option | Role | Evidence | M1 status |
|---|---|---|---|
| **Czochralski (CZ)** | Melt Si @ ~1414 °C; seed pull → monocrystalline ingot 150–300 mm class | Doc 03 §4.1, §5.1; SILICON_FAB Mermaid | **Recommended primary** |
| Fluidized-bed reactor (FBR) | Polysilicon / powder feed path from electrowon Si | Doc 03 §4.1, §4.2 (boule charge or FBR feedstock) | Alternate / later cassette — not primary M1 solid |

**Decision (this pass):** M1 crystal forge = **Czochralski**. Electrowon
Si powder (S08 crib) is the boule charge. FBR remains a documented
alternate when cassette count or powder morphology warrants it; do not
CAD a second forge this pass.

---

## 3. Ordered equipment train (forge → cut → clean → L0 tools)

Stages below are the authority order for AQS-PFD-FAB-001. Tags are
process names (not yet FreeCAD solids except §1).

### 3.1 Crystal forge and cool / anneal

| Stage | Tag | Duty | Utilities / notes |
|---|---|---|---|
| 1 | CZ_CHARGE | Si powder / scrap charge prep from S08 crib | Ar / N₂ blanketing TBD |
| 2 | CZ_PULLER | Czochralski puller — Si melt → monocrystalline ingot | Induction heat; S03 N₂; LN₂ cool path per doc 03 / 09 |
| 3 | INGOT_COOL | Controlled cool-down / stress relief after pull | N₂; no water quench into etch drain |
| 4 | INGOT_ANNEAL | Optional post-growth anneal (800–1200 °C class) | Doc 03 §4.4.3 energy domain |

### 3.2 Crop, grind, saw, edge

| Stage | Tag | Duty | Notes |
|---|---|---|---|
| 5 | CROP_GRIND | Crop seed/tail; OD grind to diameter | Kerf / grind dust → HDR_DUST / S08 recycle |
| 6 | ID_WIRE_SAW | Multi-wire diamond saw (primary) or ID saw (alternate) | Doc 03 / SILICON_FAB; kerf slurry → recovery |
| 7 | EDGE_PROFILE | Edge grind / profile | Broken edge scrap → S08 / leach |

### 3.3 Lapping, polish prep, clean

| Stage | Tag | Duty | Reagents |
|---|---|---|---|
| 8 | LAP_CMP | Lapping → CMP (colloidal silica slurry) | S37 slurry; spent → S39 / leach |
| 9 | PRE_CLEAN | Post-CMP rinse / dilute clean before handoff | S27 UPW |
| 10 | → FAB_PREP | Handoff into locked L0 cassette | Solid wafers only on this arrow |

### 3.4 L0 tool train (existing)

| Stage | Tag | Duty |
|---|---|---|
| 11 | FAB_PREP | Slice / dope handoff staging |
| 12 | WET_BENCH | RCA SC-1/SC-2, HF oxide strip, wet etch, cascade rinse |
| 13 | FAB_TOOL | Thermal ox, litho (coat/align/develop), diffusion/implant, plasma/wet etch finish, metal, RTA, probe |
| 14 | ETCH_RETURN | Spent baths → S10 HDR_ETCH → REGEN LEACH |

**NOTE**

Photolithography, implant, and metallization remain **inside**
`FAB_TOOL` massing (AQS-GAP-001 Partial). Break-out CAD bays are
out of this pass.

---

## 4. Solar-cell branch (architecture Partial)

`Silicon_Fab_overview.md` and root doc 03 require a PV branch from
polished wafers: alkaline texture (KOH) → POCl₃ emitter → SiNₓ ARC →
Ag/Al contact → belt fire → IV test.

**Equipment schedule:** `docs-authority/SOLAR_CELL_EQUIPMENT.md`
(**AQS-EQP-FAB-PV-001** Rev A) — named PV_TEXTURE … PV_IV train.

| Item | Status |
|---|---|
| Texture / emitter / ARC / contact / fire | **Partial** — schedule issued; not in L0 FreeCAD |
| KOH feed | Mapped on AQS-EQP-FAB-RGN-001 (`WS_KOH`) |
| Power offtake (cells → campus PV) | Narrative only; electrical yard sizing unchanged |
| Dedicated PFD / FreeCAD solids | **Done** Wave 4 — AQS-PFD-FAB-PV-001 + PV_* envelopes |

Do not silently drop this branch. Do not invent belt-furnace or
PECVD nameplate kW until the in-house tool designs set them (X-MFG-38).

---

## 5. Streams (fab-facing)

| ID | Role | Authority |
|---|---|---|
| S08 | Si / metals / silicate in (crib) | AQS-STR-001 |
| S01 / S21 | Pre-remin plant water → FAB UPW | AQS-WTR-001 |
| S27 | Fab UPW > 18 MΩ·cm → WET_BENCH | AQS-STR-001 |
| S09 | HCl / NaOH PRODUCT → WET_BENCH | BMED |
| S03 | N₂ purge / cool | CRYO |
| S10 | Etch return → REGEN LEACH | closed |
| S31–S39 | Fab wet-reagent forks | AQS-EQP-FAB-RGN-001 / AQS-STR-001 Rev C |

Mass rates: TBD (no invented balance this pass).

---

## 6. Wet-line reagent interface

Dedicated synth forks and reagent map: **AQS-EQP-FAB-RGN-001**
(`docs-authority/FAB_WET_REAGENTS.md`) and optional interface note
`docs-authority/FAB_WET_INTERFACE.md`. PFD: AQS-PFD-FAB-RGN-001.

SEM-Tech / IEM membrane work remains **link-only**
(`share/.../DEPENDENCIES.md`); do not vendor membrane code into fab.

---

## 7. Open (next)

1. FreeCAD solids for CZ_PULLER … PRE_CLEAN (SCALE_M / cassette pass).
2. ~~Solar-cell equipment schedule~~ **Done** AQS-EQP-FAB-PV-001; ~~PFD + FreeCAD envelopes~~ **Done** Wave 4. Vendor kW still open.
3. Litho / implant / metal break-out of FAB_TOOL when cassette ≥ M2.
4. Terrace / SCALE_M=1 restore (AQS-REM-BLD-001) — out of fab chemistry.

---

## 8. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 wafer_fab_pfd.py
python3 fab_reagent_forks_pfd.py
python3 fab_upw_pfd.py
```
