# Self-copy critical-path BOM — parts × feedstock (RepRap-class)

Document number: AQS-BOM-SC-001  
Revision: G  
Date: 2026-10-02  
Authority: AQS-AUTH-001; MVS AQS-UI-001 Rev C §3.2 / §11; AQS-GAP-001;
AQS-MFG-MET-001; AQS-EQP-MFG-001; AQS-EQP-FAB-001; AQS-EQP-FAB-PV-001;
AQS-MFG-ELC-001; AQS-MeOH-001; AQS-MF-001; AQS-STR-001; AQS-EQP-STUDY-001;
Mike lock 2026-10-01 (litho / blow-mold / electrode coating in MVS);
Mike authorize C4 2026-10-02 (reprap_bom_complete when matrix warrants);
shopping lists under hub `manufacturing_bom.xlsx` / `materials_shopping_list.xlsx`
(procurement ≠ this); graph equipment_ids on ST-* units.  
Style: AQS-DOC-002.  
**Stage = critical-path matrix complete at study-doc level (Rev F).** Every
MVS-required self-copy capability has feedstock × making-unit × equipment-ID
× study-rate evidence from WP-L2 / STUDIES_COMPLETE. **Not** vendor purchase
orders. **Not** FreeCAD Present solids — those gate `*_on_site` (C3), not this
matrix (C4). **MVS is the ideal we pursue** (AQS-UI-001); the sandbox tracks
progress; Present CAD / AHJ / field survey remain open studies, not accepted
omissions.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Critical-path parts × on-site feedstock; Partial vs Closed flags | 2026-10-01 |
| B | 1 | Litho deferred-with-unreclaimed; blow-mold out-of-MVS-at-M1; deepen Partial next-measurement (WP-A3) | 2026-10-01 |
| C | 2 | Mike lock: litho **IN SCOPE** Present-path study schedule; blow-mold **in MFG / in MVS**; electrode coating **IN SCOPE**; `reprap_bom_complete` stays false (Partial) | 2026-10-01 |
| D | 3 | Framing: MVS is the pursued ideal; sandbox tracks progress; gaps = **open studies queued in plan** (not accepted unreclaimed/sub-MVS endpoints) | 2026-10-01 |
| E | 4 | Side quests: ST-LITHO/BLOW/ELC first-principles duty issued (0.1 / 0.5 / 0.3 kW_e); Present CAD still external | 2026-10-01 |
| G | 6 | Section 6: reconciliation with the unit BOMs (X-PRO-04); `reprap_bom_complete` false: Cr, Mo, Ti, F not recovered | 2026-10-16 |
| F | 5 | Equipment-ID map for LITHO/BLOW/ELC/VCD/REMIN/ORC/SOLAR; matrix completeness warrants `reprap_bom_complete=true`; `*_on_site` stay false (C3≠C4) | 2026-10-02 |

Licence: **CERN-OHL-S-2.0**.

Canonical: `Diagrams/aqueous_diagrams/bom/SELF_COPY_BOM.md`  
(Hub BOM authority — not `cad/` planning fluff; not mirrored as planning.)  
Share: copy into `docs-authority/` on sync pass when listed; prefer hub path until freeze.

---

## 1. Purpose

Evidence table for MVS “make own parts + copy itself (RepRap-class)”:
map **critical-path** assemblies to on-site streams / units / equipment IDs.

**C4 vs C3 (locked 2026-10-02):**

| Gate | Flag | Meaning |
|---|---|---|
| **C4** | `reprap_bom_complete` | Critical-path matrix rows + feedstock + study rates + equipment IDs issued |
| **C3** | `*_on_site` / Present CAD | FreeCAD Feature mapped + AHJ design-basis → Present promotion |

C4 may be true while C3 remains false. Do **not** invent vendor certificates,
PE stamps, or FreeCAD solids to force either gate.

---

## 2. Status key

| Flag | Meaning |
|---|---|
| **Closed (doc)** | Path named; feedstock stream exists; study rates + equipment IDs issued |
| **Partial** | Path named; some rate / CAD / tool next-measurement still open (does **not** alone veto C4 when study class filled) |
| **Missing** | No on-site path yet — **open study required** (plan queue); not an accepted design outcome |
| **Study** | First-principles / schedule issued; Present CAD still open (C3) |
| **In-scope study** | Required for MVS; Present CAD / nameplate not yet issued — study queued |

---

## 3. Critical-path matrix (SCALE_M = 1.0)

| Part / capability | On-site feedstock / stream | Making unit / sector | Equipment IDs (graph) | Flag | Study rate / next |
|---|---|---|---|---|---|
| Structural metal stock / fasteners | S08 metals crib; S57–S63 MET forming; IA-MET-FEED/FAB-CRIB/MFG-DOCK | MFG / MET_MELT / draw / mill | MET forming set (AQS-EQP-MFG-001) | Closed (doc) | Residuals crib split≈0; campaign kg/h study class |
| RepRap / CNC frames + printed parts | Polymer line (oil cuts); scrap S16; IA-BLOW-* | MFG polymer + CNC/MILL; **BLOW_MOLD** | BLOW-CLAMP-01 / BLOW-AIR-01 / BLOW-MOLD-TOOL-01 | Closed (doc) | ST-BLOW-01: 0.5 kW_e avg; 3 kg/h × 3 h/d study |
| Metal powder (S60) | Plated / melt atomize; IA-MELT-ATOM | MFG MET | Atomizer massing (AQS-MFG-MET-001) | Closed (doc) | Residuals melt split; FreeCAD stubs = C3 |
| Wire / mill / melt | S08 → MET; IA-MELT-MILL | MFG | Wire-draw / mill (MFG) | Closed (doc) | Continuous share 0.2–2 kg/h study (AQS-AUD-001 §10.6) |
| IEM / membrane film | Prefer SI-IEM-01 open membrane fab; oil-line recycle narrative | MEOH / WET polish | SI-IEM stand-in (AQS-MeOH-001) | Closed (doc) | Oil-recycle vs full EDC→PVC remains study option — not missing path |
| Electrodes / coating | Substrate MET mesh/plate; coat booth → MET_AHU/SCRUB | MFG **ELECTRODE_COAT** | ELC-BOOTH-01 / ELC-SPRAY-01 / ELC-CURE-01 / ELC-EXH-01 | Closed (doc) | ST-ELC-01: 0.3 kW_e; non-precious M1; booth CAD = C3 |
| Seals / elastomers | Oil cuts / polymer | MFG | Class TBD (no invented vendor cert) | Partial | Spec sheet class TBD — does not block matrix row coverage |
| Sensors / power electronics | FAB wafers + assemble; litho schedule | FAB + MFG + **LITHO_STUB** | LITHO-COAT-01 / ALIGN-01 / DEV-01 | Closed (doc) | ST-LITHO-01: 0.1 kW_e; 3 starts/d; solids = C3 |
| CZ puller / wafer tools | Si from S08; FAB train | FAB | FAB train (AQS-EQP-FAB-001) | Partial | Tool copy of itself not proven — open study; not Missing |
| Cold-box / CRYO internals | Metals + vacuum fab | MFG + CRYO | CRYO envelope | Partial | ASME MAWP TBD — no fake cert; not self-copy Present claim |
| ZnBr₂ stack / Br₂ scrub | Electrolyte make-up study; S69 regen | ZNBR2 + GAS | ZNBR2 / scrub set | Closed (doc) | ESS peer enabled; listing/BMS finish = ops |
| MeOH synth / DMFC | S73/S74/S76; SI-DMFC / SI-IEM | MEOH | MEOH_SYNTH / MEOH_FC | Closed (doc) | Stand-in ≠ purchase; bank sizing AQS-ESS-001 |
| Hydro turbine-pump | Metals + seals | MFG + PUMPED_HYDRO | HYDRO_SET | Closed (doc) | M1 energy symbolic (AQS-ESS-001) |
| PV cells (campus renew) | Solar-cell branch AQS-EQP-FAB-PV-001 | FAB **SOLAR_PV_CELL** | PV-TEX/EMIT/PSG/ARC/CON/FIRE/IV-01 | Reopened (X-GOV-20) | ST-SOLAR-01: 1.0 kW share; 3 cells/d; tool nameplates from in-house designs (X-MFG-38) |
| Photolithography (coat/align/develop) | WS_SOLV S38/S85; resist | FAB / **LITHO_STUB** | LITHO-COAT-01 / LITHO-ALIGN-01 / LITHO-DEV-01 | Closed (doc) | ST-LITHO-01; `lithography_on_site=false` until FCStd (C3) |
| Blow mold / shoe mold | Polymer melt from EXTRUSION / oil cuts | MFG **BLOW_MOLD** | BLOW-CLAMP-01 / BLOW-AIR-01 / BLOW-MOLD-TOOL-01 | Closed (doc) | ST-BLOW-01; mold FreeCAD = C3 |
| Textiles / HEPA | AQS-MFG-TEX-001 stub | MFG optional | — | Partial | Optional for MVS electrical |
| VCD / remin potable train | Grey S12/S29; condensate; Ca/Mg/K | WTR **VCD_TRAIN** + **REMIN** | OSS-VCD-* + OSS-REMIN-* + HAB_UV-01 | Closed (doc) | ST-VCD/REMIN; `vcd_remin_on_site=false` until solids/AHJ (C3) |
| GEO_ORC / GHEX | GEO loop heat; GHEX design-survey-locked | GEO **GEO_GHEX** / **GEO_ORC** | OSS-ORC-EVAP/TURB/COND-01; KO_GEO_GHEX | Closed (doc) | ST-ORC-01; Q_surplus=0 M1; field bore still external |

---

## 3.1 Photolithography Present-path study schedule (Rev C — still in force)

**Lock (Mike 2026-10-01):** Photolithography is **IN SCOPE** for realistic
self-sustaining tech — not an accepted omission.

| Step | Study tag | Duty | Streams / utilities | Status |
|---|---|---|---|---|
| 1 | LITHO_COAT | Spin / spray photoresist coat + softbake | Resist; WS_SOLV S38; N₂ S03 | Closed (doc) schedule — ID LITHO-COAT-01 |
| 2 | LITHO_ALIGN | Align / expose (contact or projection class) | Optical / UV interim MIDAS MDA-150 | Closed (doc) schedule — ID LITHO-ALIGN-01 |
| 3 | LITHO_DEV | Develop + hardbake; rinse | Developer → organics / oil path; UPW | Closed (doc) schedule — ID LITHO-DEV-01 |
| 4 | → FAB_TOOL etch / implant / metal | Existing L0 train (AQS-EQP-FAB-001) | S10 etch return | Closed (doc) massing |

Seed unit `LITHO_STUB` retains `lithography_in_mvs=true` /
`lithography_on_site=false` until FreeCAD children exist (C3).

## 3.2 Blow mold — in MFG / in MVS (Rev C — still in force)

| Item | Decision |
|---|---|
| Sector | **MFG** (polymer aisle beside INJECTION / EXTRUSION) |
| Seed unit | `BLOW_MOLD` |
| Equipment IDs | BLOW-CLAMP-01 / BLOW-AIR-01 / BLOW-MOLD-TOOL-01 |
| Present CAD | C3 open — FreeCAD mold solid absent |
| If disabled in sandbox | Solver flags **open study queued** — not accepted unreclaimed endpoint |

## 3.3 Electrode coating — IN SCOPE (Rev C — still in force)

| Item | Decision |
|---|---|
| Seed unit | `ELECTRODE_COAT` (sector_id MFG) |
| Equipment IDs | ELC-BOOTH-01 / ELC-SPRAY-01 / ELC-CURE-01 / ELC-EXH-01→MET_AHU |
| Exhaust | MET_AHU → MET_SCRUB (S71–S72) |
| `electrode_coating_on_site` | **false** until Present booth CAD / formulation (C3) |
| Precious-metal RuO₂–IrO₂ claim | Deferred — no fake nameplate |

## 3.4 Equipment ID ↔ unit map (Rev F)

| Unit | Study | Equipment IDs | Freecad / on_site |
|---|---|---|---|
| LITHO_STUB | ST-LITHO-01 | LITHO-COAT-01, LITHO-ALIGN-01, LITHO-DEV-01 | placeholder_skip / false |
| BLOW_MOLD | ST-BLOW-01 | BLOW-CLAMP-01, BLOW-AIR-01, BLOW-MOLD-TOOL-01 | placeholder_skip / false |
| ELECTRODE_COAT | ST-ELC-01 | ELC-BOOTH-01, ELC-SPRAY-01, ELC-CURE-01, ELC-EXH-01 | placeholder_skip / false |
| VCD_TRAIN | ST-VCD-01 | OSS-VCD-FEED/HX/EVAP/COMP/COND-01 | placeholder_skip / false |
| REMIN | ST-REMIN-01 | OSS-REMIN-CA/MG/K/MIX-01, HAB_UV-01, OSS-POTABLE-TK-01 | placeholder_skip / false |
| SOLAR_PV_CELL | ST-SOLAR-01 | PV-TEX/EMIT/PSG/ARC/CON/FIRE/IV-01 | placeholder_skip / false |
| GEO_ORC | ST-ORC-01 | OSS-ORC-EVAP/TURB/COND-01 | massing_only |
| GEO_GHEX | ST-ORC-01 | KO_GEO_GHEX (mapped Feature) | mapped; survey design-locked |

No vendor certificates or PE stamps are asserted for any row.

## 3.5 WP-A3 deepen notes (Rev F)

| Topic | Decision | C3 blocker (not C4) |
|---|---|---|
| Litho | **IN SCOPE**; IDs + rates issued | FreeCAD LITHO_* solids; UV purchase lock |
| Blow mold | **In MFG / in MVS**; IDs + rates issued | Mold FreeCAD solid |
| Electrode coating | **IN SCOPE** (MFG primary); IDs + rates issued | Booth FreeCAD; lab recipe |
| VCD / REMIN | Physics + IDs issued | FreeCAD skids; AHJ potable |
| MET powder / membranes | Feedstock paths named | Optional deeper kg/h campaigns |
| `reprap_bom_complete` | **true** (Rev F matrix) | Independent of `*_on_site` |

---

## 4. Completeness checklist (solver / schema flags)

| Flag id | Meaning | Seed default (Rev F) |
|---|---|---|
| `self_copy.critical_path_documented` | This matrix exists | **true** |
| `self_copy.reprap_bom_complete` | Critical-path matrix + IDs + study rates warrant complete | **true** (Rev F) |
| `self_copy.lithography_on_site` | LITHO path **Present** CAD | **false** (C3) |
| `self_copy.lithography_in_mvs` | Litho required for MVS (pursue to Present) | **true** |
| `self_copy.blow_mold_in_mvs` | Blow mold required for MVS (pursue to Present) | **true** |
| `self_copy.vcd_remin_on_site` | Potable train Present | **false** (C3) |
| `self_copy.electrode_coating_on_site` | Coating Present | **false** (C3) |
| `self_copy.shopping_list_only` | xlsx procurement without feedstock map | **false** |

---

## 5. Gap summary → plan study queue

Rev F: critical-path **matrix complete** (C4). Present CAD / AHJ / field GHEX
bore / ASME MAWP / in-house design data remain **C3 / external** — queued, not
accepted omissions. `loops_closed` still requires C1–C5 including Present
CAD (C3). Sandbox tracks progress toward MVS as Present studies finish.

---

## 6. Related / licence

AQS-MVS-GAP-001 §4.3; AQS-GAP-001; AQS-EQP-STUDY-001; AQS-STUDY-L2-001;
AQS-STUDY-PRESENT-001; the unpublished planning note DECISION_LOG_A3_A5; CERN-OHL-S-2.0.

<!-- X-PRO-04 BEGIN -->
## 7. Reconciliation with the unit BOMs (rev G, X-PRO-04, A-M-206)

Generated by `docs-authority/_sc_reconcile.py` from AQS-PRO-001 (1219 lines) against the species on present graph edges. Per line: `docs-authority/inventory/SELF_COPY_RECON.csv`.

| Flag | BOM lines |
|---|---|
| Closed | 151 |
| Partial | 340 |
| Missing | 339 |
| Unstated | 389 |

| Flag | Gap | Lines |
|---|---|---|
| Unstated | material not stated on the unit BOM line | 355 |
| Unstated | not classed: PE (rotomoulded / fabricated) (graph nod | 13 |
| Unstated | not classed: n/a (massing only) | 10 |
| Unstated | not classed: cabinet, IP54 | 4 |
| Unstated | not classed: carbon (ram class) | 2 |
| Unstated | not classed: ceramic-fibre board 128 kg/m3 | 1 |
| Unstated | not classed: alumina (90 % class) | 1 |
| Unstated | not classed: purchase item | 1 |
| Unstated | not classed: IEC frame | 1 |
| Unstated | not classed: resistance, PID | 1 |
| Missing | needs Cr (and Mo for 316L); Cr/Mo not recovered by the leach/EW train | 245 |
| Missing | no fluorine source on site; end of life Q-011 | 65 |
| Missing | Ti not recovered (ilmenite route not in the graph) | 21 |
| Missing |  | 4 |
| Missing | no mica source; substitute glass-mica from GLASS is a study | 3 |
| Missing | line says bought: no on-site path stated | 1 |
| Partial | olefin cracking and polymerisation are not yet units in the graph | 221 |
| Partial | Cl on site; ethylene and VCM steps not yet units | 72 |
| Partial | monomer route not yet in the graph | 14 |
| Partial | graphitisation above 2,500 C not in the heat ladder | 10 |
| Partial | glass fibre from GLASS; vinyl ester resin route is a study | 9 |
| Partial | boron not recovered; soda-lime or high-silica glass from GLASS is the substitute study | 8 |
| Partial | electrical steel and magnet wire enamel are studies | 4 |
| Partial | Al stays in the leach liquor as solute; alumina recovery is a study | 2 |

Result: the section 3 matrix rows "Structural metal stock" and "Wire / mill / melt" hold for carbon steel, Cu and Ni, but not for the stainless and titanium lines, which need Cr, Mo and Ti that the graph does not recover. Those rows, and every fluoropolymer line, are Missing until an on-site route or a substitute material is designed. `reprap_bom_complete` is therefore false at rev G.
<!-- X-PRO-04 END -->
