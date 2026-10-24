# Remaining after BLD CAD pass (2026-09-27)

Superseded by `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). This page is kept as history; open work is tracked there only.

Document number: AQS-REM-BLD-001  
Revision: Y
Date: 2026-10-01  
Authority: AQS-AUTH-001; style AQS-DOC-002.

Completed this pass: authority lock, building/fire CAD, campus re-origin,
plant rebuild, mass-flow doc + PFD, simplified building/campus/hazard PFD
generators, `iso_fab_drawings.pdf` from `iso/*.png`.

Completed 2026-09-27 layout pass: wet cassette XY inside SLAB_Lm1
(`PROCESS_DX=5000`, `PROCESS_DY=4000`); CRYO on L-1 east of CORE with
`FB_CRYO_PROCESS`; per-level fit-out massing (`fitout.py`); slab /
envelope transparency; `docs-authority/LIFE_FITOUT_PLAN.md` (AQS-LIFE-001).

Completed 2026-09-27 scale pass (Rev B stack order: discrete life floors above L0; discrete `BASEMENT_LEVELS` for wet/CRYO; CATCH deepest; MFG always L0):
Completed 2026-09-27 scale pass: `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001);
`params.py` drivers (`SCALE_M` / `MODULE_BAYS_*`); continuous tanks;
discrete MFG/CRYO/FAB cassette jumps; paired life plates; electrical
module counts; `OVERFLOW_TERRACE_*` stubs; plant rebuild at `SCALE_M=1`.

Completed 2026-09-27 SCALE_M=2 on-disk pass: `SCALE_M=2.0` left saved;
`LIFE_LEVELS=2` / `BASEMENT_LEVELS=2`; larger tanks; discrete electrical
jumps; `CRYO_B2` / `PROCESS_B2`; deepened `OVERFLOW_TERRACE_*_B{n}`
bands + roof spill/downcomer link; `plant.FCStd` rebuilt at scale 2
(documented in `SCALE_MODEL.md` §8). No commit.

Completed 2026-09-27 **high-fidelity building PFD** pass: upgraded
`flow_graph/exporters/matplotlib/building_stack_pfds.py` and `campus_life_hazard_pfds.py`
to read live `models/freecad/params.py` (SCALE_M, plate, Z datums, cores,
tanks, terraces). Sheets now show full vertical stack (not flat Phase F),
M1 keep-out envelopes on plans, FB_*/HA_* ratings, CORE_LIFE/PROCESS
shaft sizes from AQS-BLD-001 §2.1. Doc nos AQS-PFD-BLD-001…006,
AQS-PFD-CMP-001, AQS-PFD-HSE-001, AQS-PFD-PIP-002, AQS-PFD-GAS-001,
AQS-PFD-WTR-001. Regenerated PNGs in diagrams hub + share `pfd/images/`.
`SCALE_M` left unchanged (still 2.0 on disk).

Completed 2026-09-27 **sector PFD generators** pass (Rev G): wrote
missing regenerable scripts (orphaned Wave-2 PNGs replaced):

| Doc | Script | PNG |
|---|---|---|
| AQS-PFD-FRM-001 | `farm_pfd.py` | `farm_pfd.png` |
| AQS-PFD-HAB-001 | `habitation_pfd.py` | `habitation_pfd.png` |
| AQS-PFD-CRY-001 | `cryo_pfd.py` | `cryo_pfd.png` |
| AQS-PFD-FAB-001 | `wafer_fab_pfd.py` | `wafer_fab_pfd.png` |
| AQS-PFD-MFG-001 | `mfg_shop_pfd.py` | `mfg_shop_pfd.png` |
| AQS-PFD-NUT-001 | `nutrient_pfd.py` | `nutrient_pfd.png` |
| AQS-PFD-WET-001 | `wet_line_factory_pfd.py` (machine-list callout) | `wet_line_factory_pfd.png` |

Shared helper: `flow_graph/exporters/matplotlib/sector_style.py`. Process lists under
`docs-authority/` (AQS-EQP-FRM/HAB/CRY/FAB/MFG/NUT-001). Synced scripts +
PNGs + process docs into share tree. No SCALE_M change; no FreeCAD
rebuild; no git commit.

Completed 2026-09-27 **hab / fab water PFD** pass (Rev H): authority
`docs-authority/WATER_PURIFICATION.md` (AQS-WTR-001 Rev A) already locked; wrote
regenerable `hab_water_pfd.py` / `fab_upw_pfd.py`; softened HAB-001 /
FAB-001 stubs to cite detail sheets; upgraded AQS-PFD-WTR-001
(`water_cycle_pfd.png`) so roof–catch inventory and VCD/remin + FAB UPW
pointers both appear; roof plan footnote. PNGs + scripts synced to
share. No SCALE_M change; no FreeCAD rebuild; no git commit. Fab forge→cut + reagent forks closed this Rev I (item 10).


Completed 2026-09-27 **farm / terrace landscape** pass (Rev J): expanded
`docs-authority/FARM_EQUIPMENT.md` (AQS-EQP-FRM-001 Rev B) and
`NUTRIENT_DOSE.md` (Rev B); new `docs-authority/TERRACE_LANDSCAPE.md` (AQS-TRR-001)
with open-terrace vs enclosed-greenhouse climate decision rule and
justified water source (S40 clean overflow primary; S21 makeup;
FARM_SUMP / S26 forbidden); streams S40–S42 on AQS-STR-001 / AQS-MF-001
Rev D; new `terrace_irrigation_pfd.py` (AQS-PFD-TRR-001); upgraded
farm/nutrient PFDs; campus / roof footnotes for overflow→terrace→catch.
No SCALE_M change; no FreeCAD rebuild; no git commit. FreeCAD bed /
greenhouse solids listed as follow-up.

Completed 2026-09-27 **fab forge→cut + wet reagent forks** pass (Rev I):
expanded `docs-authority/WAFER_FAB_EQUIPMENT.md` (AQS-EQP-FAB-001 Rev B)
ordered CZ train (cool/anneal → crop/grind → wire/ID saw → edge →
lap/CMP → clean → PREP/BENCH/TOOL); **CZ recommended**, FBR alternate
stub; new `FAB_WET_REAGENTS.md` (AQS-EQP-FAB-RGN-001) with issued WS_*
module IDs; `FAB_WET_INTERFACE.md`; upgraded `wafer_fab_pfd.py`; new
`fab_reagent_forks_pfd.py` (AQS-PFD-FAB-RGN-001); wet factory callout
points at fab forks; STREAM_REGISTER / MASS_FLOW S31–S39 qualitative.
Solar-cell branch left **explicit open stub** (not dropped). No
SCALE_M change; no FreeCAD rebuild; no git commit.


Completed 2026-09-27 **SCALE_M=1.0 restore + FB refine** pass (Rev K):
`params.py` `SCALE_M=1.0` (4×3 / M1 / life=1 / basement=1); refined
`fire_barriers.py` so **FB_HAB_CORE** (3 h, T=300 mm CORE enclosure +
centreline through CORE Y-band) is geometrically distinct from
**FB_HAB_FARM** (2 h, T=200 mm party wall outside CORE Y-band); plant
rebuilt; key PFDs regenerated against live params; share synced.
No git commit.

Completed 2026-09-27 **geothermal + backup genset** pass (Rev L): new
`docs-authority/GEOTHERMAL_BACKUP.md` (AQS-PWR-001); equipment lists
`GEOTHERMAL_EQUIPMENT.md` / `BACKUP_GEN_EQUIPMENT.md`; PFDs
`geothermal_pfd.py` / `backup_gen_pfd.py`; Sol-Ark GEN port closed with
plant-H₂ BACKUP_GEN (diesel contingency only); geothermal = closed-loop
GHEX + heat pump → Q4, binary ORC electric stub rating TBD; streams
S43–S48; electrical_sld + campus/building POWER callouts; optional
`electrical_yard.py` envelope stubs. SCALE_M left **1.0**. No full
plant FreeCAD rebuild; no git commit.

Completed 2026-09-28 **PEM fuel cell** pass (Rev M): new
`docs-authority/FUEL_CELL.md` (AQS-FC-001); `FUEL_CELL_EQUIPMENT.md`
(AQS-EQP-FC-001); PFD `fuel_cell_pfd.py` (AQS-PFD-FC-001); chemistry =
PEM on plant H₂ + O₂ (MeOH DMFC deferred); FC on Sol-Ark **BATT DC** via
FC_DCDC (≠ BACKUP_GEN GEN port); heat → Q4 via FC_HX_Q4; streams
S49–S53; S24 closing narrative via GEN+FC; ELECTRICAL.md + electrical_sld
FC node; GEOTHERMAL_BACKUP / HAZARD_SEPARATION / CRYO_EQUIPMENT / LEGACY
item 3 updates; `electrical_yard.py` FC envelope stubs. SCALE_M left
**1.0**. No plant.FCStd rebuild; no git commit. kW nameplate TBD.

Completed 2026-09-28 **CRYO cold-box internals** pass (Rev N): new
`docs-authority/CRYO_COLD_BOX.md` (AQS-CRY-002); `CRYO_EQUIPMENT.md` Rev C
with Stirling / DIST_COL_* / REBOILER_COND / COMP_EXPAND / MOL_SIEVE /
HEPA / CRYO_HX_Q4 / CRYO_DED_COOL / CRYO_AHU tags; regenerated
`cryo_pfd.py` (AQS-PFD-CRY-001) showing internals + Q4/HVAC + GEN/FC/S24
draws from CRYO_H2; streams S54–S56; HVAC/geo split (Q4 vs dedicated vs
room vent); `freecad/cryo.py` child envelope stubs; LEGACY item 5
Present/Partial. SCALE_M left **1.0**. No plant.FCStd rebuild; no git
commit. Duties / holdup kg TBD.

Completed 2026-09-28 **MFG metal forming** pass (Rev O): new
`docs-authority/METAL_FORMING.md` (AQS-MFG-MET-001); `METAL_FORMING_EQUIPMENT.md`
(AQS-EQP-MFG-MET-001); PFD `metal_forming_pfd.py` (AQS-PFD-MFG-MET-001);
path = MET_MELT (electric induction) → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER;
MET_MELT ≠ INDUCTION_PYROLYZER; dedicated MET_AHU (no HAB return); Q4 via
MET_HX_Q4; streams S57–S63; `mfg_shop.py` MET_* stubs; LEGACY item 6
Present/Partial; MFG_SHOP_EQUIPMENT Rev B. SCALE_M left **1.0**. No
plant.FCStd rebuild; no git commit. kW / kg/h TBD.


Completed 2026-09-28 **sector capacity / footprint audit** pass (Rev Q): new
Local planning SECTOR_CAPACITY_AUDIT (AQS-AUD-001 Rev A, not published) — M1 envelopes vs PHF /
PFD density; sizing from AQS-EQP-* + ELECTRICAL + params (`SCALE_M=1.0`);
study throughputs with labeled assumptions; closed vs open loops from
AQS-STR-001 / AQS-MF-001 (S24, stacks, S56/S62). AUTHORITY pointer added.
Planning audit retained as local planning artefacts (not published). SCALE_M left **1.0**. No plant rebuild;
no git commit.

Completed 2026-09-28 **site / yard / dock / egress** pass (Rev P): new
`docs-authority/SITE_ACCESS.md` (AQS-SITE-001); AQS-BLD-001 **Rev D** — site north =
**+Y**; primary truck dock relocated to **north** (pole-facing) L0 with
`DOCK_APRON_N` / `DOCK_DOOR_N`; `SERVICE_ENTRY` + `STAIR_SERVICE` (L0–L-2)
as service access and basement secondary egress (hab sleeping stays on
STAIR_P / STAIR_S*; no H-area routing); yard stub enrichment in
`electrical_yard.py` (CLEAR_*/KO_*/UTIL_ROUGH_*/YARD_*); HSE Rev E egress
notes; building + campus PFDs updated; `plant.FCStd` rebuild this pass if
scripts clean. SCALE_M left **1.0**. Full NFPA 101 / IBC Ch. 10 calc =
next. No git commit.


Completed 2026-09-28 **vent / stack closure** pass (Rev R): new
`docs-authority/VENT_CLOSURE.md` (AQS-VENT-001 Rev A) + `VENT_SCRUB_EQUIPMENT.md`
(AQS-EQP-VENT-001); owner lock — none of S24 / acid-gas / afterburner /
Br₂ / S56 / S62 are “open by intent”; each → scrub+regen or CRYO.
STREAM_REGISTER / MASS_FLOW **Rev I** (S64–S72); SECTOR_CAPACITY_AUDIT
**Rev B**; HAZARD_SEPARATION **Rev F**; CRYO_COLD_BOX **Rev B** /
CRYO_EQUIPMENT **Rev D**; METAL_FORMING / MET_* scrub hooks; SCRUBBER_CHEMISTRY
/ FAN_STACK / FLOW_BATTERY notes; PFDs mass_flow / cryo / metal_forming /
znbr2 / oil updated. Claimed architecture advanced for H₂→GEN/FC, CO₂
capture, WS_* returns, ORC electric (kW unverified). SCALE_M left **1.0**.
Plant rebuild optional/note only; no git commit.


Completed 2026-09-28 **vent closure PFD end-to-end** pass (Rev S): new
`flow_graph/exporters/matplotlib/vent_closure_pfd.py` (AQS-PFD-VENT-001); updated cryo, mass_flow,
metal_forming, znbr2, oil (FLUE_CAP), wet (ACID_POLISH), backup_gen, fuel_cell,
geothermal (ORC Claimed), fab_reagent_forks, building_stack, container_layout,
campus hazard/gas. All six former opens + claimed-incomplete (H₂→GEN/FC, CO₂,
WS_*, ORC) appear **Partial** or **Claimed** with named scrub/regen/CRYO return
streams S64–S72. MASS_FLOW **Rev J**, VENT_CLOSURE **Rev B**, AUDIT **Rev C**.
Duties / Nm³/h / kW still TBD (item 19). SCALE_M left **1.0**. No git commit.

Completed 2026-10-01 **Wave 1 open-item close** pass (Rev T): study-estimate
duties for ACID_POLISH / ZNBR2_BR2_REGEN / CRYO_AHU_COND / MET_SCRUB
(AQS-EQP-VENT-001 Rev B; AQS-VENT-001 Rev C); GEN/FC/ORC/CRYO/MFG study
nameplate bounds; water L/d + farm food + WS_* OoM (AQS-AUD-001 Rev D);
FAB/CRY layout relief in `params.py` (FAB 12×10, MFG 12×8, CRYO 9×6) +
AQS-BLD-001 Rev E; FreeCAD scrub/terrace stubs; plant.FCStd rebuild;
PFDs regenerated; share sync. SCALE_M left **1.0**. No git commit.


Completed 2026-10-01 **Wave 2** (Rev U): **AQS-COMPL-001** compliance matrix
(NFPA/NEC/OSHA/ASME/ISO themes; permits not fabricated); **AQS-DOC-002**
house style + authority header fixes (ELECTRICAL as AQS-ELC-001; Purpose on
FC/CRYO/GEO; HSE Rev G; SITE Rev B); textiles/HEPA + ELECTRODE_FAB
Partial architecture stubs; OpenSCAD PATH install note (no forced
install); MeOH DMFC remains deferred. SCALE_M left **1.0**. Share sync.
No git commit.

Completed 2026-10-01 **Wave 3** (Rev V): **AQS-EGR-001** NFPA 101 / IBC Ch.10
study egress calc (travel, exit width, STAIR_SERVICE+STAIR_MAINT basement
pair, north dock discharge; AHJ verify); **AQS-ASM-001** vessel inventory +
B31.3 PC-01…10 templates (CMP-ASM-01 Gap→Partial; MAWP not assigned without basis);
**AQS-MEP-001** Life Phase D Partial (fixtures / header OD / one-line);
**AQS-EQP-FAB-PV-001** solar-cell schedule (architecture Partial);
OpenSCAD via build-host `openscad` on PATH (apt sudo
blocked) + **51/51** detail STL compile; VJ iso + GH envelope as **doc schedules**
(AQS-ASM-001 §6 / AQS-TRR-GH-001) not full CAD; GUI animation remains
operator overlay (schematic D0–D6 already present). SCALE_M left **1.0**.
Share sync. No git commit. Plant FreeCAD rebuild **not required** this
wave (docs + STL only).


Completed 2026-10-01 **layout locks** pass (Rev X): Project layout locks —
(1) `ARRAY_ROOF` / `PV_ARRAY*` tilt = **+SITE_LAT_DEG** about +X (equator /
south face NH; prior −lat faced north/dock); (2) life-floor balconies
`TERRACE_{S,E,W}_L*` + `TERRACE_DOOR_*` starting top floor, step down S/E/W
(grade `OVERFLOW_*` remains surplus receiver); (3) yard GEN/FC inset —
east faces west of `ENV_WALL_W` (`YARD_WALL_CLEAR`; no wall punch-through);
(4) `DOCK_COUNT = CASSETTE_COUNT` — one dock + `ELEV_DOCK` at M1; add
pairs E–W. AQS-EGR-001 Rev B controlling-code table; `CRYO_EGRESS_DOOR` /
`CRYO_EGRESS_LOBBY` stubs. AQS-BLD-001 Rev F; AQS-SITE-001; AQS-SCALE-001
Rev C; AQS-TRR-001 Rev B. `plant.FCStd` rebuild; share sync. SCALE_M
left **1.0**. No git commit. No unverified MAWP / vendor kW.

Completed 2026-10-01 **Wave 4** (Rev W): closable CAD/PFD residuals —
**AQS-PFD-FAB-PV-001** (`solar_cell_pfd.py` + PNG); FreeCAD `PV_*`
east-strip envelopes in `wafer_fab.py`; **AQS-TRR-GH-001** GH_ENV_* /
GH_AHU / GH_IRRIG_HDR / GH_DOOR_AIRLOCK solids in `building_stack.py`;
**AQS-ASM-001** §6 `VJ_001`…`VJ_005` CRYO line envelope stubs in
`cryo.py` (not fabricator isos); `plant.FCStd` rebuild via
`/usr/bin/freecadcmd`; REMAINING_BLD / AUTHORITY / share sync.
SCALE_M left **1.0**. No git commit. AHJ / vendor kW / MAWP / WPS /
truck counts remain explicitly open.


Completed 2026-10-01 **design-tool architecture** pass (Rev Y): new
`docs-authority/DESIGN_TOOL_ARCHITECTURE.md` (**AQS-UI-001** Rev A) — MVS = smallest
all-sector gold standard; sandbox scales up/down; never overwrite MVS
(export design pack); schematic-first then 3D; unit_id+stream_id;
ISA-95-ish hierarchy; mass-energy+electrical solver; sector toggles;
cycle views; most-restrictive NFPA/IBC/ISO flags; crew+SITE_LAT inputs;
stack FastAPI+typed JSON+React/SVG (Three.js later); phased roadmap;
six open questions (MVS freeze size, downsize semantics, pumped hydro
membership, export minimum, Odysseus link, UI licence). AUTHORITY
**Rev F** pointer. Share sync. SCALE_M left **1.0**. No git commit.

## Still open

1. ~~**Block / sector PFDs not yet scripted**~~ — **Done Rev G** (generators
   above). Basement wet/oil/glass detail remains on those line PFDs.
2. **Basement process detail beyond massing** — wet/oil/glass equipment
   lists belong on sector / line PFDs (wet callout added; oil/glass already
   have dedicated sheets).
3. ~~**STL compile**~~ — **Wave 3 Done**: OpenSCAD AppImage on PATH;
   **51/51** `detail/*.scad` → `detail/stl/*.stl` (0 fail).
4. **GUI animation overlay** — schematic D0–D6 + F0 present; GUI 12 fps
   capture on `plant.FCStd` still operator FreeCAD session (not auto-fixed).
5. ~~**FB_HAB_CORE vs FB_HAB_FARM**~~ — **Done Rev K**: distinct 3 h
   CORE enclosure (`FB_HAB_CORE`, T=300) vs 2 h party wall outside
   CORE Y-band (`FB_HAB_FARM`, T=200); per life floor.
6. ~~**Life MEP Phase D**~~ — **Partial Wave 3**: AQS-MEP-001; AQS-LIFE-001
   Rev B. Remaining: vendor AHU kW, berth lock, NEC 700 fixture schedule.
7. ~~**SCALE_M restore to 1**~~ — **Done Rev K**: `SCALE_M=1.0`,
   `plant.FCStd` rebuilt at M1 baseline; PFDs follow live params.
8. ~~**Terrace landscape detail**~~ — **Done Rev J** (docs + PFD);
   **life balconies + doors Done Rev X** (`TERRACE_*_L*` /
   `TERRACE_DOOR_*`). Grade OVERFLOW / GH remain.
9. ~~**Hab / fab water purification**~~ — **Done Rev H**: AQS-WTR-001 +
   AQS-EQP-HAB-001 / AQS-EQP-FAB-UPW-001; generators `hab_water_pfd.py`
   (AQS-PFD-HAB-WTR-001) and `fab_upw_pfd.py` (AQS-PFD-FAB-UPW-001);
   HAB-001 / FAB-001 stubs point at detail sheets; water_cycle shows
   roof–catch inventory ≠ VCD regeneration. Streams S25–S30 on
   AQS-STR-001 Rev B.
10. ~~**Wafer fab crystal forge → cut + wet-line reagent forks**~~ — **Done Rev I**:
    AQS-EQP-FAB-001 Rev B ordered train (CZ primary); AQS-EQP-FAB-RGN-001
    WS_* forks + S31–S39; AQS-PFD-FAB-001 / AQS-PFD-FAB-RGN-001 regenerated.
    Solar-cell branch remains explicit open stub (item 11 companion).
10b. ~~**Solar-cell branch equipment**~~ — **Partial Wave 4**:
    AQS-EQP-FAB-PV-001 Rev B + AQS-PFD-FAB-PV-001 + FreeCAD PV_*
    envelopes. Remaining: vendor PECVD/belt kW; PV_COUNT resize decision.
11. ~~**Farm terrace / greenhouse planting (docs)**~~ — **Done Rev J**.
    FreeCAD planting beds / irrig header stubs **Done Wave 1**;
    quantitative L/d + food study **Done** (AQS-AUD-001 §§11–12).
    Enclosed GH envelope solids **Done Wave 4** (AQS-TRR-GH-001 Rev B).

12. ~~**Geothermal + backup generator (docs/PFD)**~~ — **Done Rev L**:
    AQS-PWR-002 + AQS-EQP-GEO/GEN-001 + AQS-PFD-GEO/GEN-001;
    S43–S48; GEN port closed (H₂). Remaining: ORC rating after
    site survey; genset kW nameplate; yard stubs rebuilt Rev P
    (`plant.FCStd` — confirm in success report).
13. ~~**PEM fuel cell (docs/PFD/SLD)**~~ — **Done Rev M** (Present/Partial):
    AQS-FC-001 + AQS-EQP-FC-001 + AQS-PFD-FC-001; S49–S53; BATT DC;
    heat → Q4; LEGACY item 3 closed. Remaining: FC continuous kW TBD;
    MeOH DMFC deferred; yard stubs rebuilt Rev P.
14. ~~**CRYO cold-box internals (docs/PFD/stubs)**~~ — **Done Rev N**
    (Present/Partial): AQS-CRY-002 + AQS-EQP-CRY-001 Rev C +
    AQS-PFD-CRY-001; S54–S56; LEGACY item 5 closed. Remaining:
    quantitative Stirling/column duties TBD; CRYO_H2 holdup kg under
    MAQ TBD; VJ **envelope stubs** Done Wave 4 (AQS-ASM-001 §6);
    fabricator VJ isometrics still open.
15. ~~**MFG metal forming (wire / cold-mill / atomizer)**~~ — **Done Rev O**
    (Present/Partial): AQS-MFG-MET-001 + AQS-EQP-MFG-MET-001 +
    AQS-PFD-MFG-MET-001; S57–S63; LEGACY item 6 closed. Remaining:
    nameplate kW/kg/h TBD; MET_* stubs via Rev P plant rebuild;
    ELECTRODE_FAB coating deferred; architecture stub **AQS-MFG-ELC-001** (Partial).

16. ~~**NFPA 101 / IBC Ch. 10 egress calc**~~ — **Study Wave 3 + Rev X**:
    AQS-EGR-001 Rev B controlling-code table; CRYO_EGRESS_* stubs.
    CMP-NFPA-04 / CMP-OSH-01 still Partial pending AHJ clear widths.
17. **North dock traffic / apron geometry** — dock+ELEV_DOCK discrete
    jump Done Rev X; truck counts not fabricated; city street dock still
    AQS-BLD-001 §5 narrative only.
18. ~~**Sector capacity follow-ons (AQS-AUD-001)**~~ — **Done Rev T / AUD D**
    (2026-10-01): CRYO/FAB layout relief; GEN/FC study bounds; L/d water +
    farm food; WS_* OoM. Vendor nameplates still TBD.

19. ~~**Vent closure hardware duties**~~ — **Done Rev T** (2026-10-01):
    study Nm³/h / liquor / KO in AQS-EQP-VENT-001 Rev B; FreeCAD stubs
    on plant rebuild. Upset-stack AHJ residuals remain. Vendor curves TBD.

AQS-REM-001 closed ≠ this list. REM was shop-envelope; this is BLD stack.

20. ~~**Textiles / HEPA architecture**~~ — **Partial Rev U**: AQS-MFG-TEX-001 stub. CAD/PFD still open.
21. ~~**ASME vessel / B31.3 piping class sheets**~~ — **Partial Wave 4**:
    AQS-ASM-001 Rev B + VJ envelopes; CMP-ASM-01 Partial. MAWP / WPS still TBD/Gap.
22. ~~**OpenSCAD on PATH**~~ — **Done Wave 3**: build-host `openscad` (AppImage or package)
    (apt sudo blocked). STL_MANIFEST Rev B.


23. **Design-tool implementation (AQS-UI-001)** — Architecture Rev A
    locked. Implementation (schema file, FastAPI, React schematic) not
    started. Resolve §11 open questions before freezing MVS JSON.

## MeOH / continuous kW (2026-10-01)

Gap fill: **AQS-MeOH-001**, **AQS-REQ-KW-001**, **AQS-ASM-001 Rev C**. SCALE_M unchanged 1.0.
