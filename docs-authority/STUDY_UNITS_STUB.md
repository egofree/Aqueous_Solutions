# Study / deferred units — VCD·remin, ORC, litho, solar, blow-mold, electrode coat

Document number: AQS-EQP-STUDY-001  
Revision: F  
Date: 2026-10-01  
Authority: AQS-WTR-001; AQS-EQP-GEO-001; AQS-EQP-FAB-001; AQS-EQP-FAB-PV-001;
AQS-EQP-MFG-001; AQS-MFG-ELC-001; AQS-GAP-001; AQS-MVS-GAP-001 §4.1.3;
AQS-AUD-001 §10.4 / §11; seed `candidate_mvs.json`; Project decision 2026-10-01;
`planning/UNIT_EQUIPMENT_SPEC_GAP.md` (**AQS-EQ-GAP-001**).  
Style: AQS-DOC-001.  
**Stage = first-principles study + stubs toward MVS (Rev F: gap-register pointer).** Not Present CAD yet.
Not vendor nameplates. Not PE stamps. Numbers below are **study** with cited
method. Each open blocker is a **queued study in the plan** — not an accepted
unreclaimed or sub-MVS endpoint. Sandbox stays modular as studies close.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Name study units + streams for gap-close tracking | 2026-10-01 |
| B | 1 | Present-path blockers table; remain study — no fake Present (WP-A5) | 2026-10-01 |
| C | 2 | VCD first-principles kW; REMIN mineral balance; GEO_ORC Carnot-limited kW_e; SOLAR architecture promote; litho/blow/electrode in-scope units (WP-A5 close) | 2026-10-01 |
| D | 3 | Framing: gaps = open studies queued toward MVS; sandbox tracks progress (not accepted unreclaimed/sub-MVS) | 2026-10-01 |
| E | 4 | Phase A supplements A3b–d / A5b–e: LITHO/BLOW/ELC first-principles; VCD/REMIN/ORC/SOLAR physics closed + external next actions | 2026-10-01 |
| F | 5 | Pointer to equipment spec gap register AQS-EQ-GAP-001 (commercial interim → OSS policy) | 2026-10-01 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/process/STUDY_UNITS_STUB.md`

---

## 1. Purpose

Keep `loops_closed` accurate by **naming** deferred capabilities as study
units/streams in the candidate MVS graph — not silent omissions — and by
recording **first-principles** duty methods (system fit → standards/physics
→ practicality → cost metrics) with citations. Decision trail:
`planning/DECISION_LOG_A3_A5.md`.

---

## 2. Study units (seed)

| unit_id | sector_id | Role | Status | Streams (study) | Next measurement |
|---|---|---|---|---|---|
| **VCD_TRAIN** | WTR | Vapor-compression distill train (HX/EVAP/COMP/COND) | Study — **duty kW issued** (§3) | S25 distillate; S28 brine; S29 grey feed | Compressor selection / equipment IDs for Present |
| **REMIN** | WTR | Ca/Mg/K potable remineralization | Study — **mineral balance issued** (§4) | S26 potable → HAB | Confirm salt source vs S07; UV integrity; equipment IDs |
| **GEO_ORC** | GEO | Binary ORC electric (heat→electric) | Study — **Carnot-limited band** (§5) | S48 → Sol-Ark AC couple | GHEX conductivity / T_source survey |
| **LITHO_STUB** | FAB | Coat / aligner / develop Present-path schedule | **Study duty+mass issued** (§8) | WS_SOLV S38; resist waste → oil/org | FreeCAD children + wafer starts lock + UV datasheet (external) |
| **SOLAR_PV_CELL** | FAB | Texture→emitter→ARC→contact→fire | **Study duty bands locked** (§6) | PV_* reagents; S03/S02; etch S10 | In-house tool designs (X-MFG-38) + PV_COUNT offtake (external) |
| **BLOW_MOLD** | MFG | Blow / shoe mold polymer forming | **Study duty issued** (§9) | Polymer melt; scrap S16 | Mold FreeCAD + machine datasheet (external) |
| **ELECTRODE_COAT** | MFG | Electrode coating booth (non-precious M1 class) | **Study duty+class issued** (§10) | MET substrate; exhaust S71–S72 | Booth CAD + lab formulation (external); RuO₂–IrO₂ deferred |

---

## 2.1 Present-path blockers (Rev C / WP-A5)

| unit_id | Promote to Present? | Blockers (do not invent) | Seed `params.present_path` |
|---|---|---|---|
| VCD_TRAIN | **No** — study duty only | Equipment IDs; compressor selection; AHJ | `study_duty_issued` |
| REMIN | **No** — study balance only | Mineral source lock vs S07; UV; equipment IDs | `study_balance_issued` |
| GEO_ORC | **No** — Carnot band only | GHEX survey; T_h / Q_surplus | `study_carnot_band` |
| LITHO_STUB | **No CAD** — duty+mass **issued** | Coat/align/develop FreeCAD children; UV datasheet | `study_duty_mass_issued` |
| SOLAR_PV_CELL | **Partial** — bands **locked** | Belt/PECVD **nameplates**; offtake vs PV_COUNT | `study_duty_bands_locked` |
| BLOW_MOLD | **No** — duty **issued** | Mold CAD; selected datasheet | `study_duty_issued` |
| ELECTRODE_COAT | **No** — duty+class **issued** | Booth CAD; lab formulation | `study_duty_formulation_class_issued` |

**Potable surplus claim:** only if VCD_TRAIN + REMIN are **Present**. Seed keeps
`self_copy.vcd_remin_on_site=false`. Inventory clean-water `pass_study` ≠
drinking export. Study duty/balance **does not** flip Present — remaining
blockers (equipment IDs, UV, source lock) stay on the **plan study queue**.

---

## 3. VCD first-principles duty (kW) — study

### 3.1 System fit

Habitation regenerates distillate into roof–catch inventory (AQS-WTR-001):
treated grey (~S12/S29) + clean condensates → VCD → S25 distillate /
S28 brine. Distillate is **not** potable until ED polish + REMIN.

### 3.2 Physics / engineering standard method

Single-effect **mechanical vapor compression (MVC / VCD)** compressor work
(DESWARE / classic MVC texts):

\[
w_\mathrm{ideal} \approx \frac{\lambda\,\Delta T}{T}
\quad[\mathrm{kJ/kg}]
\]

with latent heat \(\lambda\), evaporator absolute temperature \(T\), and
temperature lift \(\Delta T\) across evaporator/condenser (plus boiling-point
elevation for saline feeds). Actual specific energy consumption:

\[
\mathrm{SEC} \approx \frac{w_\mathrm{ideal}}{\eta_\mathrm{comp}\,\eta_\mathrm{motor}}
\quad[\mathrm{kWh/m^3}]
\]

(plus small pump share). Literature single-effect MVC SEC class ≈
**10–25 kWh/m³** product (lower end for low-salinity / small lift; upper for
high-salinity / small machines) — see cites §3.5.

### 3.3 M1 numbers (study)

| Quantity | Value | Source |
|---|---|---|
| Grey → VCD feed class | **~110 L/d** (0.110 m³/d) | AQS-AUD-001 §11; seed S12/S25 |
| Study \(\Delta T\) | 4–8 K | MVC design class (DESWARE sample) |
| Study \(T\) | ~343–373 K (70–100 °C class) | Hab VCD low-temp intent |
| \(\lambda\) | ~2250–2400 kJ/kg | Steam tables (IAPWS / textbook) |
| \(w_\mathrm{ideal}\) mid | ~\(\lambda\times5/353\) ≈ **33 kJ/kg** ≈ **9.2 kWh/m³** | §3.2 |
| Combined η (small machine) | **0.5–0.7** | DESWARE small-MVC range |
| **SEC study band** | **14–20 kWh/m³** (mid **~16**) | Ideal/η + ~5% pumps |
| Energy / day | 0.110 × 14…20 = **1.5–2.2 kWh/d** | |
| **Average continuous kW_e** | **0.06–0.09 kW** (mid **~0.08**) | energy/24 h |
| Batch 8 h/d run duty | **~0.2–0.3 kW_e** during run | Optional campaign framing |

**Seed study continuous_kw:** **0.08 kW_e** (status=`study`), note cites this
section. **Supersedes** SLINGSHOT narrative 5–10 kW fresh-water allocation
(AQS-WTR-001 / AQS-GAP-001) at M1 rates.

### 3.4 Practicality / cost metrics

| Metric | Study judgment |
|---|---|
| Fit under module parasitics (~9 kW AC class, ELECTRICAL.md) | **Yes** — ≪ 1% of continuous plant |
| Cost driver | Compressor + HX area vs ΔT trade (classic MVC) |
| Present blocker | Named equipment IDs + selected compressor — **not** the kW order of magnitude |

### 3.5 Citations (public / prior AQS — no PE)

1. DESWARE *Mechanical Vapor Compression Distillation* sample chapter
   (D08-053) — ideal work \(\lambda\Delta T/T\); small-system η 20–50%
   combined; example ~25 kWh/m³ at ΔT=4 °C.
2. Nafey et al. / Alasfour-class MVC analyses — SEC decreases with higher
   top brine T and smaller ΔT (trade vs heat-transfer area).
3. Recent MVC thermoeconomic studies — SEC often **~10–13 kWh/m³**
   (efficient single-effect) up to **~16–32 kWh/m³** cost-optimal bands
   (Desalination / DOE literature class).
4. AQS-WTR-001 §2.4; AQS-AUD-001 §11; AQS-GAP-001 (SLINGSHOT 5–10 kW
   superseded).

---

## 4. REMIN mineral balance — first-principles study

### 4.1 System fit

REMIN doses Ca²⁺ / Mg²⁺ / K⁺ into **drinking** water after ED polish
(AQS-WTR-001). **Not** S07 farm nutrient dose (FARM path separate).

### 4.2 Standards / targets

WHO expert guidance on demineralized / desalinated water (not a single
mandatory GDWQ number): population-benefit discussion often cites about
**Ca 20–30 mg/L** and **Mg ~10 mg/L** as desirable order-of-magnitude
targets for remineralized drinking water; K has no WHO GV and is mainly
dietary (WHO *Nutrients in Drinking-water*; *Safe Drinking Water from
Desalination* WHO/HSE/WSH/11.03).

### 4.3 Mass balance (study)

| Case | Volume | Ca target 25 mg/L | Mg 10 mg/L | K 5 mg/L (optional) |
|---|---|---|---|---|
| Drink only | 4 crew × 2.5 L/d = **10 L/d** | **0.25 g/d** | **0.10 g/d** | **0.05 g/d** |
| Full potable distribute | ~**130 L/d** (AQS-AUD-001 §11) | **3.25 g/d** | **1.3 g/d** | **0.65 g/d** |

**Decision (study default):** remineralize **drink stream (~10 L/d)** to
WHO-class Ca/Mg; optionally stabilize full distribute for corrosion —
document which when Present IDs issue. Salt mass is **grams/day** vs farm
nutrients **kg/d** — negligible system mass.

**Source trail:** prefer core-salt / BMED inventory salts (carbonates /
chlorides as issued chemistry allows) — **forbid** silent tee of S07 farm
dose into potable (AQS-WTR-001).

### 4.4 Practicality / cost

| Metric | Study |
|---|---|
| Electrical | Dosing pumps ≪ 0.05 kW — treat as **none** / negligible |
| UV integrity after remin | Required for potable claim — equipment TBD |
| Cost | Salt grams/day negligible vs CAPEX of VCD/ED |

### 4.5 Citations

1. WHO, *Nutrients in Drinking-water* (WHO/SDE/WSH/05.09) — Ca/Mg
   discussion ~20–30 / ~10 mg/L class.
2. WHO, *Safe Drinking Water from Desalination* (WHO/HSE/WSH/11.03) —
   remineralization annex; K residual notes.
3. AQS-WTR-001 §2.5; AQS-AUD-001 §11 (130 L/d potable study).

---

## 5. GEO_ORC — Carnot-limited kW_e study

**Definition:** GEO_ORC = geothermal **Organic Rankine Cycle**
(heat → electric). Same first-principles trail.

### 5.1 System fit

GHEX closed loop (S43) → GEO_HP → Q4 life priority (S44). ORC taps
**surplus** heat after life priority, AC-couples via S48 (AQS-EQP-GEO-001;
AQS-PWR-001). Forbidden: loop fluid into potable / Salria.

### 5.2 Physics

Carnot limit between source \(T_h\) and sink \(T_c\):

\[
\eta_\mathrm{C} = 1 - \frac{T_c}{T_h}
\]

Practical binary ORC thermal efficiency is a fraction of Carnot. Locked
study class (AQS-AUD-001 §10.4 / AQS-EQP-GEO-001):

\[
P_\mathrm{ORC} \approx \eta_\mathrm{ORC}\times(Q_\mathrm{GHEX,avail}-Q_{4,\mathrm{life}})
\]

with \(\eta_\mathrm{ORC}\) study **0.08–0.12** for medium-low binary ORC;
literature low-T geothermal (70–100 °C) often **~5–9%** thermal efficiency
(Hepbasli / Hettiarachchi-class reviews).

### 5.3 M1 practicality (shallow GHEX)

| Premise | Implication |
|---|---|
| M1 GHEX serves **heat pump** to Q4 (HVAC ~1.5 kW_e class context) | Primary product is **thermal**, not power |
| Shallow ground \(T_h\) near ambient | \(\eta_\mathrm{C}\) tiny if ORC tried on loop fluid alone |
| \(Q_\mathrm{surplus}\) after Q4 priority | **≈ 0** until survey shows extra capacity or process waste-heat HX |

**Study band:**

| Case | Q_surplus (kW_th) | η_ORC | P_ORC (kW_e) |
|---|---|---|---|
| M1 shallow, life-priority first | **~0** | 0.08–0.12 | **~0** |
| Illustrative if survey frees 10 kW_th | 10 | 0.10 | **1.0** |
| Illustrative upper study (not claim) | 20 | 0.12 | **2.4** |

**Seed:** `continuous_kw.value=null`, `status=study_carnot_band`, note
“0–2 kW_e illustrative if Q_surplus 0–20 kW_th; M1 default ~0 until GHEX
survey — **forbid hard-coded 100 kW**”.

### 5.4 Cost metrics

ORC CAPEX is not justified while Q_surplus≈0 at shallow GHEX — but the unit
**stays in the seed** so the sandbox tracks the MVS power path. Next work is
**ST-ORC-01** (GHEX survey / T_source / Q_surplus) on the plan queue. Do not
force `required_for_mvs_closure` true on GEO until ORC evidence (AQS-SEC-001 A7).

### 5.5 Citations

1. AQS-AUD-001 §10.4 method lock; AQS-EQP-GEO-001; AQS-PWR-001 §2.1.
2. Hettiarachchi et al., *Energy* — low-T geothermal ORC ~5–9% (70–100 °C).
3. Guo / Shengjun et al. — subcritical ORC thermal efficiency ~11% class
   at 80–100 °C optimized fluids (illustrative, not M1 nameplate).
4. Cengel/Boles *Thermodynamics* (textbook) — Carnot efficiency definition.

---

## 6. SOLAR_PV_CELL — architecture promote (physics)

Promote as far as physics + issued schedule allow (AQS-EQP-FAB-PV-001):

| Step | Physics readiness | Seed |
|---|---|---|
| PV_TEXTURE (KOH pyramids) | Standard alkaline texture — **ready** | Named |
| PV_EMITTER (POCl₃) | Standard diffusion — **ready** | Named |
| PV_PSG_ETCH | Standard — **ready**; return S10 | Named |
| PV_ARC (SiNₓ PECVD) | Physics OK; **nameplate kW TBD** | REQ-PECVD study 0.5–2 avg / 5–15 peak |
| PV_CONTACT / PV_FIRE | Physics OK; **belt kW TBD** | REQ-BELT study 0.5–2 avg / 10–25 peak |
| PV_IV | Electrical only | Named |

**present_path:** `architecture_promoted`. Continuous study share remains
**1.0 kW_e** mid (existing seed) — not belt nameplate. Does **not** claim
Present FreeCAD solids complete.

---

## 7. Framing (correction 2026-10-01)

We design the **MVS in theory** because not all answers are known yet.
The **sandbox is the live model** of progress toward that MVS — modular
and extensible as gaps fill — **not** locked to a sub-MVS intended product.

- Disabling or leaving Incomplete an in-scope unit **queues an open study**
  (must happen before proceeding on that path). Solver may flag incomplete
  physics; those flags are **work queue**, not accepted emissions / unreclaimed
  endpoints.
- Seed enables parent sectors; study units carry `electrical_role` /
  `continuous_kw` study or null with `open_study_queued` where applicable.
- `mvs_criteria.loops_closed` remains **false** until evidence closes loops.
- `reprap_bom_complete` remains **false** until the BOM matrix warrants it.

**Sector cross-use:** designs may host parts of a capability inside present
sectors (e.g. electrode coat in MFG using FAB wet practice) — AQS-SEC-001
§3.1 / AQS-UI-001. Boundaries are organisational, not physics firewalls.

### 7.1 Open studies queued (A3/A5) — plan before proceeding

| Study ID | WP | Topic | Phase A physics | Remaining (external — owner/date TBD) |
|---|---|---|---|---|
| ST-LITHO-01 | WP-A3b | LITHO duty + resist mass (§8) | **Closed** — 0.1 kW_e; 0.2–1 g/d dry | FreeCAD LITHO_* children; wafer starts lock; UV datasheet |
| ST-BLOW-01 | WP-A3c | Blow-mold clamp/air duty (§9) | **Closed** — 0.5 kW_e avg / 2–4 peak | Mold FreeCAD; selected machine datasheet |
| ST-ELC-01 | WP-A3d | Electrode coat duty + formulation class (§10) | **Closed** — 0.3 kW_e; non-precious M1 | Booth CAD; lab formulation trial |
| ST-VCD-01 | WP-A5b | VCD compressor + equipment IDs | **Closed** (duty §3) — 0.08 kW_e | Compressor selection; equipment IDs |
| ST-REMIN-01 | WP-A5c | Mineral source + UV + IDs | **Closed** (balance §4) | Source vs S07; UV; equipment IDs |
| ST-ORC-01 | WP-A5d | GHEX survey / T_source / Q_surplus | **Closed** (Carnot §5) — M1 ~0 | Site GHEX survey |
| ST-SOLAR-01 | WP-A5e | PECVD/belt nameplates; PV_COUNT | **Reopened** 2026-10-15 (X-GOV-20: it rested on bought-tool datasheets); 1.0 kW share kept as study | In-house tool designs (X-MFG-38); offtake decision |

---

## 8. ST-LITHO-01 — resist mass + duty (first principles)

### 8.1 System fit

Photolithography required for MVS electronics self-copy (AQS-BOM-SC-001 §3.1).
Steps: LITHO_COAT → LITHO_ALIGN → LITHO_DEV inside FAB envelope; residual to
WS_SOLV / organics (S38 class).

### 8.2 Method

Pilot wafer starts **1–5 /d** (AQS-AUD-001 labeled assumption — not freeze).
Spin photoresist on **150 mm** class wafer: film ~1–3 µm; dispense ~**2 mL/wafer**
(~2 g wet at ~1 g/cm³); solids fraction ~10% → **~0.2 g dry resist/wafer**.
At 1–5 starts: **2–10 g/d** wet dispense; **0.2–1.0 g/d** dry residual after develop.

Electrical (intermittent): spin + softbake heaters ~0.3–1 kW; UV contact/LED
aligner ~0.1–0.5 kW; develop pumps negligible. At low starts most time idle →
**average continuous ~0.05–0.15 kW_e** (mid **0.1**); peak while running **0.5–1.5 kW_e**.

### 8.3 Practicality / cost

Fit under FAB module parasitics. Cost driver = tool CAD + resist chemistry, not
kW order of magnitude. **Present** blocked on FreeCAD children + UV datasheet +
starts lock — **owner/date TBD**.

### 8.4 Citations

1. AQS-AUD-001 FAB pilot starts assumption (1–5/d labeled).
2. AQS-EQP-FAB-001 / AQS-BOM-SC-001 §3.1 schedule.
3. Semiconductor process class (Campbell / Sze-class spin-coat practice) —
   dispense volume order-of-magnitude; not a PE stamp.

---

## 9. ST-BLOW-01 — clamp / air duty (first principles)

### 9.1 System fit

Blow / shoe mold **in MFG / in MVS** beside EXTRUSION / INJECTION
(AQS-EQP-MFG-001; AQS-BOM-SC-001 §3.2). Prefer **lab/pilot or Precious Plastic
extrusion add-on** architecture for M1.

### 9.2 Method

SI-MFG-01 polymer motors **2.2–4 kW** class (Precious Plastic kit). Clamp + blow
air share study: **2–4 kW_e peak** while running; campaign **2–4 h/d** → average
continuous mid **~0.5 kW_e** (band 0.3–0.8). Throughput campaign **1–5 kg/h**
polymer articles.

**Forbid** claiming industrial EBM average **14–28 kW** (KSY/ABLB/MEPER-class
catalog) as M1 continuous — architecture reference only (same rule as full-line
PECVD forbid in AQS-REQ-KW-001).

### 9.3 Practicality / cost

Fits REQ-MFG-POLY-CONT **1–3 kW_e** avg intermittent budget. Present blocked on
mold FreeCAD + selected datasheet within 2–4 kW peak — **owner/date TBD**.

### 9.4 Citations

1. AQS-REQ-KW-001 SI-MFG-01 / REQ-MFG-POLY-CONT.
2. Precious Plastic / ONEARMY kit motor class (DEPENDENCIES.md).
3. Industrial EBM catalog powers (KSY ~14 kW avg; ABLB65 ~21 kW avg) — **cited as
   forbidden M1 continuous**, not selected nameplate.

---

## 10. ST-ELC-01 — coating duty + formulation class

### 10.1 System fit

Electrode coating **IN SCOPE** (AQS-MFG-ELC-001); MFG primary; exhaust
MET_AHU → MET_SCRUB (S71–S72). Sector cross-use OK (FAB wet practice).

### 10.2 Formulation class (decision — no precious nameplate)

**M1 default study class:** non-precious conductive **carbon** / **Ni** /
stainless passivation coats for EW / BMED replaceable electrodes.
**RuO₂–IrO₂ DSA** remains **deferred** — do not invent slurry recipes or
purchase claims.

### 10.3 Duty method

Booth exhaust fan **0.2–0.75 kW_e**; cure oven **0.5–2 kW_e** intermittent.
Campaign ~**2 h/d** at ~1.5 kW cure+exhaust → average continuous mid **~0.3 kW_e**;
peak **1–2 kW_e**.

### 10.4 Practicality / cost

Negligible vs MET melt / FAB strip. Present blocked on booth FreeCAD + lab
formulation trial — **owner/date TBD**.

### 10.5 Citations

1. AQS-MFG-ELC-001 Rev B; AQS-VENT-001 exhaust path.
2. AQS-BOM-SC-001 §3.3; industrial paint-booth / IR-cure class duty bands
   (order-of-magnitude — not a stamped rating).

---


---

## 11. Equipment specification gap register (pointer)

Manufacturer / model inventory, OSS target policy, and researched **commercial
interim** shortlists for ST-* / P0 underspecified units live in planning
(not cad):

**`planning/UNIT_EQUIPMENT_SPEC_GAP.md`** — document **AQS-EQ-GAP-001**.

Commercial interim never freezes as final MVS Present authority; open-source
replacement tracked as `OSS-REP-*` work items. Physics / duty in §§3–10 of
this stub remain controlling for study numbers.

## 12. Sync

Part of cad/process — include in `rebuild.py --sync` docs-authority copy.
Decision log planning-only: `planning/DECISION_LOG_A3_A5.md`.
