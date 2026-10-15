# Remaining work checklist

Queue: `docs-authority/MASTER_PLAN.md` (AQS-PLAN-004). This page is history.

Document number: AQS-REM-002  
Renumbered 2026-10-15 from AQS-REM-001 to clear a duplicate (AQS-REG-001).
Revision: E  
Date: 2026-10-01

| Rev | Change | Date |
|---|---|---|
| — | Opened | 2026-09-27 |
| A | Aisle instancing + shop upgrades in CAD | 2026-09-27 |
| B | Walked 1.3–8.2. SKUs, fans, racks, tray, weld register, campus envelopes | 2026-09-27 |
| C | Closed 7.3 schematic frames + 8.1 manifest. List complete at this fidelity. | 2026-09-27 |
| D | Wave 2 pointers (CMP/DOC/OpenSCAD); shop fidelity unchanged | 2026-10-01 |
| E | Continuous kW reqs + MeOH gap fill + ASME study MAWP | 2026-10-01 |

Checked = file exists at the stated fidelity. This sandbox has no
`openscad` / `freecadcmd`. Operator compiles STLs and captures GUI
overlays locally.

## 1. Wet aisle instancing

- [x] 1.1 EW fit-out on EW-1…9 (`import_mfg.py` loop)
- [x] 1.2 Fit-out on PK cells except PK-4/5 CEM boxes
- [x] 1.3 GF exact article numbers on N1–N12 — `cad/CSTR_NOZZLE_SCHEDULE.md` Rev B

## 2. BMED / CRU

- [x] 2.1 BMED stack of 8 units — `mfg_bmed_stack.scad`
- [x] 2.2 CRU — `mfg_cru.scad`

## 3. Harvest

- [x] 3.1 VDF cloth wrap + vacuum pump envelope — `mfg_harvest_vdf.scad`
- [x] 3.2 Auto vs pail remains a mode note

## 4. Oil line

- [x] 4.1 DRYER UCP208 + jacket nozzles
- [x] 4.2 QUENCH sprays + knockout pot
- [x] 4.3 FRACTIONATOR + HX-3 reboiler stub
- [x] 4.4 AFTERBURNER burner register

## 5. Glass line

- [x] 5.1 ROTARY UCP213 trunnions
- [x] 5.2 MILL jar
- [x] 5.3 DIGEST stuffing box + caustic vent

## 6. Gas / electrical

- [x] 6.1 ZnBr2 tanks + Br2 tower — `mfg_znbr2_skid.scad`
- [x] 6.2 Q4 skid — `mfg_q4_hvac.scad`
- [x] 6.3 Fan curves / stack height — `cad/FAN_STACK.md` (AQS-GAS-003)
- [x] 6.4 Cable tray / grounding — `mfg_cable_tray.scad`, `freecad/pipe_services.py`

## 7. Plant-wide

- [x] 7.1 Routed pipe racks — `mfg_pipe_rack.scad`, `freecad/pipe_services.py`
- [x] 7.2 Weld / joint register — `cad/WELD_MAP.md` (AQS-WLD-001)
- [x] 7.3 Animation frames — schematic D0–D6 + F0 in `cad/animation/`. Generator `freecad/render_frames.py`. GUI 12 fps overlay remains operator-box.
- [x] 7.4 Farm, wafer fab, habitation, cryo — envelopes. `PHASE_F_ENVELOPES.md`, `campus.py`, `cad/animation/F0_campus.png`. Internals out of this model set.

## 8. Data

- [x] 8.1 Rebuild contract issued — `cad/STL_MANIFEST.md`, `cad/REBUILD.sh`. Compile + stamp is operator-box (`openscad` + `/usr/bin/freecadcmd`).
- [x] 8.2 Refresh `materials_shopping_list.xlsx` from `cad/materials.csv`

## Operator box (not this sandbox)

```
bash cad/REBUILD.sh
python3 cad/freecad/render_frames.py
```

GUI capture of D1–D6 on `plant.FCStd` is optional overlay of the same
waypoints. Do not use the 1.1.1 AppImage. Do not use diffusion frames.

## Vent closure (AQS-VENT-001) — PFD architecture

- [x] AQS-PFD-VENT-001 + affected line PFDs show Partial/Claimed returns (S64–S72)
- [x] Quantitative scrub/regen / GEN/FC/ORC **study** duties (labeled estimates; no vendor invent) — 2026-10-01; AQS-EQP-VENT-001 Rev B / AQS-AUD-001 Rev D

## Closed

AQS-REM-001 is complete at shop-envelope + schedule fidelity. Next work
is fabricator drawings (welds/balloons/tolerances), site AERMOD, or a
separate Phase F internals brief.

## Layout locks (2026-10-01 Rev X)

See `cad/REMAINING_BLD.md` Rev X: equator PV tilt, life terraces+doors,
yard wall inset, dock+ELEV_DOCK discrete E–W jump, AQS-EGR-001 Rev B.

## Wave 2 doc pointers (2026-10-01)

- Compliance themes: cad/COMPLIANCE_MATRIX.md (AQS-CMP-001)
- House style: cad/DOCUMENTATION_STYLE.md (AQS-DOC-001)
- OpenSCAD PATH: see cad/STL_MANIFEST.md (do not force install)
- MeOH train: **issued** AQS-MeOH-001 / AQS-EQP-MEOH-001 / AQS-PFD-MEOH-001 (gap filled)
- Continuous kW requirements: AQS-REQ-KW-001 (GEN/FC/CRYO/PECVD/belt/MFG/MeOH)
- ASME study MAWP / relief / WPS class notes: AQS-ASM-001 Rev C

