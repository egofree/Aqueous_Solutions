# HL-Q4-REJ heat-sink study — resolving D-GEO_ORC

Document number: AQS-HEAT-STUDY-002
Revision: A
Date: 2026-10-18
Authority: graph Rev AC (`flow_graph/plant_flow_graph.json`, commit `67bd63d`). Briefed at `eacaf47`; commit `67bd63d` (Wave-1 corrections) retired only the dead HL-HX8-Q3-A/B edges and non-Q4 streams — every Q4_BUS edge, rate and the 10.1627 kW rejection cited below are identical at both commits (re-verified). Study note; no graph edit, no commit. Not a PE stamp.
Owner brief (D-GEO_ORC, ruled 2026-10-18, commit `eacaf47`): *"Do an engineering study and determine the best option (most robust and modular and in keeping with the closed-system design. We want to re-use the energy as much as possible before rejecting waste heat to the outside."*

Scored criteria: **robustness** (failure modes, maintenance), **modularity** (add/remove in N+1 blocks), **closed-system reuse** (kW reused vs rejected), **ladder-rule consistency** (down-only; GEO_HP is the only lift; Q4 water only, <80 °C; HEAT_LADDER.md / AQS-HEAT-LADDER-001).

---

## 1. What is actually on the Q4 bus (graph Rev AC, cited)

Sources into `Q4_BUS` (rated case, edge `rate.value`):

| Stream | From | kW | Basis (edge note) |
|---|---|---:|---|
| HL-Q4-A-BUS | Q4_A | 4.7481 | DUTY-008 Rev B rated ×1.25; normal 2.122; X-THM-01 5.51 less 0.7619 line loss |
| HL-Q4-B-BUS | Q4_B | 4.6729 | same; 0.8371 line loss |
| S53 | FUEL_CELL | 1.1419 | FC heat above Q4 return |
| S54 | CRYO_HX_Q4 | 0.5448 | ASU shaft + TSA heat above Q4 return |
| S63 | MET_HX_Q4 | 0.0171 | Cu melt 4.392 kg/d × 0.55 recovered |
| S80 | MEOH_FC | 0.3689 | DMFC heat above Q4 return |
| IA-ZNBR-HEAT | ZNBR2 | 1.67 | round-trip loss |
| **Total in** | | **13.16** | |

Sinks: `IA-Q4-LIFE` → HABITATION 3.0 kW; `HL-Q4-REJ` → GEO_ORC **10.1627 kW** ("AQS-DUTY-011 Rev M… 13.09 in − 3.0 life load. **Dry cooler, not an ORC.**"). Bus closes at 13.16 in = 13.16 out (INSULATION_SCHEDULE X-THM-01: line losses carried down the ladder close it at 10.1627).

Two bases matter:

- **Normal design day** (both ladders, draws running, FC on): batteries 2.122 × 2 + 3.74 other sources = 7.99 kW in → surplus after 3.0 kW life = **≈ 5.0 kW**.
- **Rated / bounding case** (single-ladder feeds ×1.25): 13.16 in → **10.16 kW** must leave. This is the number the sink must be sized to *pass*, not to *absorb*.

Rev AC dropped the three Rev M Q4 sinks — S100/HX-9 leach make-up preheat 0.53 kW, S101/HX-10 digest caustic preheat 0.28 kW, S102 borefield recharge 0.67 kW (AQS-DUTY-011 §4.15; docs-authority/HEAT_LADDER.md line 69) — in the scope pivot; at Rev M the bus closed with the ORC pad at 0 kW. That is the direct cause of the 10.16 kW rejection.

Delivery medium: water, batteries 70 °C nominal, header <80 °C, bus supply 65 / return 45 °C (DUTY-008 §7; HX-9/HX-10 branches 60/45).

Site design temps (AQS-SITE-002 via AQS-THM-002): winter 99.6 % **−7.2 °C**, summer 0.4 % **37.8 °C**. Make-up air ≈ 23,900 m³/h ≈ 6.6 kg·s⁻¹ ≈ **6.65 kW/K** of tempering duty, already specified as "tempered from the Q4 ladder in winter… by the building chiller in summer" (AQS-THM-002 line 43). Building HVAC/makeup electrical class 1.5 kW (ELECTRICAL.md), i.e. ≈ 4.5 kW_c at compression COP 3.

---

## 2. Option (a) — small ORC on the Q4 rejection

**Physics at the available ΔT.** Source 65 °C (338 K) cooling to 45 °C return; condensing 35 °C summer / 10 °C winter:
- Carnot 65→35 °C: 8.9 %. Small ORCs realise 30–45 % of Carnot (Quoilin et al. 2013, *Renew. Sustain. Energy Rev.* 22:168–186 — micro-scale low-ΔT ORC class; in-repo ref Hettiarachchi et al., *Energy*, low-T ORC 5–9 % at 70–100 °C sources — our source is *below* that band).
- Gross: 10.16 kW_th × 2.5–4 % ≈ **0.25–0.45 kW_e**. Less feed pump and condenser fan (≈0.1–0.2 kW at 7 K approach over 37.8 °C air) → **net ≈ 0.1–0.35 kW_e summer, ≈ 0.5–0.7 kW_e winter**, ≈ 0.3 kW_e annual average.
- The existing illustrative band "0–2 kW_e" (GEO_ORC params, AQS-EQP-STUDY-001 Rev F §5) assumed η_ORC 0.08–0.12 **absolute** — at a 285 K GHEX source (η_Carnot 0.059) that is above Carnot and impossible; even on the 338 K Q4 source, 8–12 % absolute exceeds practical Carnot fraction. The honest endpoint is **≈ 0.2–0.4 kW_e net**. This closes the ST-ORC-01 "not accepted zero-power endpoint without study" question: the endpoint is near-zero *and* dominated by better uses of the same heat (below).

**Vendor class.** Commercial small ORCs (ElectraTherm ≥77 °C source, ≥35 kW_th; E-Rational ≥70 °C, 50 kW class) sit above both our temperature and our duty; a 10 kW_th / 0.3 kW_e machine is laboratory/hobby class, not vendor class.

**Robustness on cold/cloudy days.** The Q4 surplus is process-driven (EW reject 4.57 kW, ZNBR 1.67, FC 1.14, cryo 0.54), not solar: cloudy days *increase* it (ZNBR/FC work harder). Cold days improve the condenser and the ORC efficiency — but that is exactly when the same kW is worth 20× more in the make-up-air coil (§3): each kW_th sent to the ORC in winter returns ~0.05 kW_e while displacing 1.0 kW_e of resistance tempering it could have replaced. An ORC that trips must be bypassed to a dry cooler anyway — **the terminal sink can never be deleted, so the ORC adds a machine without removing one**.

**Scores.** Robustness 1 (hot-day collapse, working-fluid maintenance, duplicates the mandatory terminal), modularity 2 (skid exists, N+1 for 0.3 kW_e is meaningless), closed-system reuse 1 (converts ~4 %, rejects ~96 % *outside*, still ~9.7 kW after it), ladder-rule consistency 3 (legal downhill sink; AQS-EQP-GEO-001 forbidden-mix rule 2 respected via a named HX). **Total 7/20.**

---

## 3. Option (b) — lift Q4 surplus to Q3 with GEO_HP (a second lift)

**COP at source/sink temps**, plant convention 0.45 × Carnot (used on S43: COP 3.43 = 0.45 × 285→328 K):
- 65 °C → Q3 at 85 °C: COP = 0.45 × 358/20 = **8.1**
- 65 °C → Q3 at 100 °C (store t_nom): COP = 0.45 × 373/35 = **4.8**

**What it would displace:** the leach/digest/dryer trim currently met by electricity. Normal trim basis: 0.121 (HX-4) + 3.176 (HX-5) + 0.542 (HX-6) kW per ladder = 7.4 kW_e on the DUTY-008 Rev B note; **1.2 kW_e on the Rev M basis with HX-9/HX-10 preheats in service** (MVS_CHECKLIST: HX-5 0.43 + HX-6 0.80). Electrical draw to lift 6.4 kW_th at COP 8 ≈ 0.8 kW_e. Gross prize ≈ 5.5 kW_e on the no-preheat basis, ≈ 0.4 kW_e on the Rev M basis.

**Rule conflict, stated plainly.** HEAT_LADDER.md: "GEO_HP is the only lift. It feeds Q4 and the farm. It does not push heat back up the ladder." Lifting Q4→Q3 is (i) a second lift or an out-of-scope GEO_HP duty, (ii) heat moving up the ladder, (iii) a thermal loop with the Q3→Q4 thermosyphon — the diode rule ("a valve is not a heat pump"; no uphill valve) was written to stop exactly this circulation, which would recirculate the same joules with each pass leaking store and line losses (0.164 kW/store + 0.49–0.58 kW step losses, X-THM-01).

**The kicker: option (c) makes (b) redundant.** The leach/digest preheats (HX-9/HX-10) deliver the same joules *downhill* — Q4 water preheating make-up to 55 °C — and were the closed, tested Rev M configuration. After (c), the residual normal trim is ~1.2 kW_e, too small to justify a rule change; and in the rated (upset) case the electric trim *is* the N+1 backup for the ladder by design — a second lift would duplicate the backup at worse availability (compressor vs resistance wire).

**Scores.** Robustness 3, modularity 3, closed-system reuse 5 (largest single kW_e lever if preheats absent), ladder-rule consistency **1** (breaks down-only + only-lift + GEO_HP scope; needs an owner rule change and a Q3→Q4 interlock). **Total 12/20 — rejected as baseline, documented as the upgrade path if foundry/polymers growth re-inflates the trim bill.**

---

## 4. Option (c) — expand Q4 demand to absorb the rejection (the winner)

Enumerated from the live graph; kW absorbed and seasonal availability:

| Candidate user | kW_th absorbed | Season | Basis / status |
|---|---:|---|---|
| HX-9 leach make-up preheat (**restore S100**) | 0.53 | all year | Rev M verbatim value (AQS-DUTY-011 §4.15); AQS-DUTY-012 Rev N family |
| HX-10 digest caustic preheat (**restore S101**) | 0.28 | all year | Rev M verbatim |
| Grease kettles, wax-melt/hold stage | 0.5–1.0 | all year | wax C19–C28 melts 45–60 °C (notes/GREASE_LINES.md); *saponification stays resistive* (Li kettle >150 °C) — temperature-class check required |
| BLACK_DIGEST mesophilic trim | 0.1–0.3 | winter-weighted | 35 °C digester; VS split still unmeasured (notes/DIGESTER_LI.md) |
| OIL_DRYER feed preheat | ≤0.05 | all year | 15 kg/d polyolefin × 2 kJ/kgK × 30 K — negligible; HX-4 jacket stays Q3 |
| Foundry charge preheat | ≤0.05 | all year | ~26 kg/d metal (notes/FOUNDRY_SIZING.md) × ~30 K — negligible |
| ZNBR2 battery thermal management | 0 | — | ZNBR2 is a Q4 **source** (1.67 kW); it wants cooling, not heat |
| Adsorption chiller, HAB/FAB summer cooling | 3.5–5.0 (≈2.25 kW_c at COP_c 0.45) | summer | silica-gel class runs 55–90 °C drive; building AC ≈ 4.5 kW_c / 1.5 kW_e displaced; compression chiller stays as N+1 |
| Make-up-air winter preheat coil | 10–12 | winter | 6.65 kW/K × ΔT; Q4 is already the named tempering source (AQS-THM-002) |
| GROW_BED root-zone water | 0.5–1.5 | winter | S06/GEO_HP class; beds 18–24 °C from 45 °C return |
| Dock / ROOF_TANK / CATCH_TANK freeze protection | 0.3–0.8 | winter design nights | circulating Q4 glycol loop instead of electric trace; 99.6 % = −7.2 °C |

**Absorption summary against the two bases:**
- All-season continuous block: 0.81 (HX-9+HX-10) + 0.5–1.0 (grease) ≈ **1.3–1.8 kW**, every day of the year.
- Summer: + chiller 3.5–5 kW → **≈ 5–6.5 kW** ≥ the 5.0 kW normal surplus.
- Winter: + MAU coil 10–12, beds, digester, freeze protection → **12–15 kW**, far above surplus; the winter sink is effectively unbounded (1.5 K on the make-up stream alone absorbs 10 kW).
- Shoulder: chiller and MAU both partial → **1–3 kW residual**, which is what GHEX + terminal handle.

**Genuinely consumed before rejection: ≈ 3.5–5 kW of the ≈ 5.0 kW normal surplus (70–100 %, season-dependent). Only the rated 10.16 kW upset flow ever reaches the terminal sink.** This is the only option that reduces the *rejected* number rather than decorating it.

**Scores.** Robustness 4 (each user is a passive branch or HX; a failed branch re-routes to buffer/terminal; adsorption chiller has no compressor and no phase-out refrigerant — its N+1 is the existing chiller), modularity 5 (independent Q4_BUS branches, add/remove per block; two are literal restores), closed-system reuse 5 (above), ladder-rule consistency 5 (exactly the documented Rev M pattern: "These are Q4_BUS branches; the HL-* edges still own the ladder path"). **Total 19/20.**

---

## 5. Option (d) — modular buffer store

The Q4 batteries (0.6 m³, 70 °C, 20 kWh at 30 K swing, loss 0.164 kW each at 30 mm PIR — DUTY-008 §5/§6) already buffer tier transit. A dedicated rejection-side buffer:

- **Size: one 1.5 m³ water module per ladder (2 total, N+1 by ladder)**, 70/45 K swing → 1500 kg × 4.186 kJ/kgK × 25 K = 157 MJ = **43.5 kWh each, 87 kWh total** ≈ 17 h at the 5 kW normal surplus; absorbs an 11 kW foundry batch for >8 h.
- **Standing loss:** ≈ 0.25–0.3 kW each at 50 mm PIR (area-scaled from the DUTY-008 store table; 5–6 % of throughput — insulate to 50 mm, not 30, since Q4 is envelope-limited at 30 mm).
- **What it smooths:** batch foundry coil-water reject (§7, ≤11 kW spikes), ZNBR/FC dispatch swings, single-ladder rerate transients, and the seasonal handover between chiller (summer) and MAU coil (winter). What it does *not* do: consume heat — it defers rejection so the terminal is sized at the ~5 kW average, not the 10.16 kW peak.

**Scores.** Robustness 5 (passive, no failure mode beyond leak; same class as existing batteries), modularity 5, closed-system reuse 3 (enabler, not consumer), ladder-rule consistency 5 (same tier, water, no lift). **18/20 — adopt as the companion, not the answer.**

---

## 6. Option (e) — reject to ground via GEO_GHEX (last resort)

- **Capacity check:** `GEO_GHEX` params: Q_GHEX_avail **3.0 kW_th**, k_ground 1.5 W/mK, T_source 285 K — a shallow closed loop, survey-locked (`design_survey_locked`, ST-ORC-01 blockers: conductivity, T_source, Q_surplus). Sustained 10.16 kW injection is 3.4× the study capacity: the ground around the bores warms, capacity collapses, and the GEO_HP winter source degrades. Rev M precedent S102 recharge was **0.67 kW** — within class.
- **Smart use:** modest summer recharge (≈0.7 kW, capped 3.0 kW) pre-charges the field for winter GEO_HP extraction (COP 3.43 at 285 K source; every K of field warming helps). It is the balancing channel, never the primary sink.

**Scores.** Robustness 3 (no moving parts, but capacity is survey-gated and thermally saturable), modularity 2 (least modular: bores, field, locked survey), closed-system reuse 2 (still rejection *outside* the building, partly recovered as winter HP benefit), ladder-rule consistency 4 (Rev M precedent as a Q4_BUS branch). **Total 11/20.**

---

## 7. The two audit findings (first_principles_audit_2026-10-17.md §Heat)

### 7.1 RECTIFIER 2 × 10.048 kW at Q3 (`IA-Q3A-TRIM`, `IA-Q3B-TRIM`)

The rate decomposes as the rated trim, not electronics cooling: (HX-5 6.353 + HX-6 1.663) × 1.25 ≈ **10.05 kW** per ladder, and the note says "sized to the neighbor" (AQS-DUTY-012 Rev N). Two defects, one fix each:

1. **If these are the trim heaters** (the arithmetic says they are): electric resistance heat belongs *at the process*, booked as RECTIFIER → LEACH_CSTR_1 / GLASS_DIGEST electric edges (the pattern `_rev_n_corrections_study.py` lines 864–869 already uses: "electric trim" on the unit). Booking it into the 100 °C Q3 store and drawing it back through HX-5/HX-6 double-counts against the ladder closure and inflates Q3 transit.
2. **If read as rectifier electronics reject** (the audit's reading): physics bans it at Q3. A 12 kW rectifier (POWER_DUTIES.md) at 92–96 % efficiency rejects **0.5–1.0 kW** at ≤60 °C cooling water — it cannot heat an 85–100 °C store (second law; identical to the ruled HX-8→Q3 finding, DUTY-008 §13.1: "HX-8 cannot charge Q3… belongs on Q4"). Electronics cooling belongs on **Q4** via a named HX, the established S53/S54/S63 pattern.

**Recommendation:** split the edges — a small RECTIFIER→Q4_BUS reject edge (~0.5–1.0 kW, 45–60 °C class) + trim re-homed to the process units.

### 7.2 Unintegrated foundry furnace heat (IND_MELT / VAC_IND)

The brief asks whether IND_MELT/VAC_IND heat "at Q1/Q2-class temps" should join the upper ladder. Physics says **it cannot, and mostly shouldn't**:

- Induction furnaces have **no flue** — there is no Q1-class offgas stream to capture. VAC_IND is vacuum induction (ISM/CCIM, 2 kg, 15 kW): its only reject path is the water-cooled **shell and coil circuit**, which must stay ≤60 °C to protect coil insulation — Q4-class by necessity.
- Recoverable duties at ~26 kg/d metal (FOUNDRY_SIZING.md): coil/PS losses 20–30 % of 45 kW input during a melt → **≈1.7 kW average, 8–11 kW batch peak** at 40–60 °C → Q4 via MET_HX_Q4 (this is what the unrated `IND_HEAT_TO_HX`/`VAC_HEAT_TO_HX` edges should carry); product metal sensible+latent ≈ 0.2–0.3 kW average total across Al/Fe/Cu — of which the graph already rates the Cu share (S63 = 0.0171 kW, 55 % recovery via mold/coil water).
- **How it joins the ladder:** at Q4, through MET_HX_Q4, exactly as LOAD_ROLLUP.md already ruled ("Treat as Q4-class unless a higher-tier HX is later justified"). A Q1 hot-face capture (holding-furnace hood, drain launders) would return <0.1 kW at this throughput — not worth a thermal-oil circuit. Re-study only if foundry throughput grows ×20 (toward 500 kg/d) or COMB_HEAT (combustion alternate) becomes baseline.

---

## 8. Score table

| Option | Robustness | Modularity | Closed-system reuse | Ladder rules | Total /20 |
|---|---:|---:|---:|---:|---:|
| (a) Small ORC on Q4 rejection | 1 | 2 | 1 | 3 | **7** |
| (b) Second lift Q4→Q3 (GEO_HP) | 3 | 3 | 5 | 1 | **12** |
| (c) Expand Q4 demand | 4 | 5 | 5 | 5 | **19** |
| (d) Modular buffer store | 5 | 5 | 3 | 5 | **18** |
| (e) GEO_GHEX ground rejection | 3 | 2 | 2 | 4 | **11** |

## 9. Recommendation

**Primary: (c) demand expansion, carried by (d) buffer. Backup/balancing: (e) GHEX at ≤0.7 kW sustained (3.0 kW survey-gated ceiling), terminal dry cooler rated 12 kW for the upset case. Reject (a) ORC — keep GEO_ORC at 0 kW_e with this study as the D-GEO_ORC record. Defer (b) behind an owner rule change; it is superseded by (c) at current loads.**

Rationale in one line each: (a) converts 4 % to electricity, rejects 96 % anyway, collapses on 37.8 °C days, and cannot remove the mandatory terminal sink; (b) breaks the two rules the ladder is built on to buy what (c) gets free downhill; (c) absorbs 70–100 % of the normal surplus with passive, modular, winter/summer-complementary branches; (d) lets every downstream piece be sized at average, not peak; (e) is a balancing channel with a real but small ceiling.

## 10. Sized implementation sketch (for the implementation commit)

1. **Restore** S100 (HX-9, 0.53 kW) and S101 (HX-10, 0.28 kW) Q4_BUS branches, Rev M values verbatim.
2. **Add** Q4_BUS→ADS_CHILL branch: one 5 kW_c silica-gel adsorption chiller (derates to ≈3–3.5 kW_c at 65 °C drive; COP_c 0.45 at 30 °C recooling via the shared terminal dry cooler); serves summer building cooling ≤4.5 kW_c, displaces ≤1.5 kW_e; existing compression chiller stays as N+1.
3. **Add** Q4_BUS→MAU_HX winter make-up preheat coil, 12 kW (= 1.8 K on 6.65 kW/K) — displaces 12 kW of winter tempering; already the documented intent of AQS-THM-002.
4. **Add** winter branches: GROW_BED root zone 1.0 kW; freeze-protection loop (ROOF_TANK/CATCH_TANK/NORTH_DOCK) 0.5 kW design-night.
5. **Add** grease-kettle wax-hold branch 0.5–1.0 kW after the temperature-class check.
6. **Buffer:** one 1.5 m³ module per ladder at the Q4 tier, 70/45 swing, 43.5 kWh each, 50 mm PIR, standing loss ≤0.3 kW each.
7. **GHEX recharge branch:** 0.7 kW normal, hard-limited 3.0 kW pending the bore survey (ST-ORC-01).
8. **Terminal:** re-home `HL-Q4-REJ` from the GEO_ORC placeholder to a named DRY_COOLER unit, 12 kW at 0.4 % 37.8 °C (LMTD ≈ 15 K at 65/45 water; fan ≈ 0.6 kW at full load) — the edge note already says "Dry cooler, not an ORC." GEO_ORC stays as placeholder, 0 kW_e, blockers closed by this study.
9. **Rectifier fix (§7.1):** RECTIFIER→Q4_BUS reject ≈0.5–1.0 kW via named HX; trim re-homed to LEACH_CSTR_1/GLASS_DIGEST.
10. **Foundry (§7.2):** rate `IND_HEAT_TO_HX`/`VAC_HEAT_TO_HX` at ≈1.7 kW average / 8–11 kW batch, 40–60 °C, into MET_HX_Q4; extend S63-class recovery to the Al/Fe/SS casting streams.
11. Resulting seasonal rejection at the terminal: winter ≈ 0, summer ≈ 0–2, shoulder ≈ 1–3 kW normal; the 10.16 kW rated case remains covered by buffer + 12 kW dry cooler.

## 11. Assumptions to register (for the implementation commit, per AGENTS.md)

| # | Value | Units | Where used | Basis | Sensitivity |
|---|---|---|---|---|---|
| 1 | 0.45 | COP_c per kW_th drive (silica-gel adsorption, 65 °C drive / 30 °C recool / 12 °C chilled) | ADS_CHILL branch, §4/§10.2 | vendor class 0.4–0.6 at 55–90 °C (InvenSor/Mayekawa class datasheets; Wang & Oliveira 2006, *Renew. Sustain. Energy Rev.*) | ±0.1 COP_c moves summer absorption ±1 kW |
| 2 | 4.5 (kW_c); 1.5 kW_e at COP 3.0 | building summer cooling load / displaced chiller draw | §4/§10.2 | ELECTRICAL.md "HVAC / makeup 1.5 kW"; AQS-THM-002 | if cooling doubles, add a second chiller module (modular) |
| 3 | 6.65 | kW/K make-up-air tempering (≈23,900 m³/h) | MAU_HX coil, §4/§10.3 | AQS-THM-002 extract/make-up table, 1.006 kJ/kgK | coil kW scales linearly with chosen ΔT |
| 4 | 1.5 m³ per ladder; 43.5 kWh at 70/45 K; ≤0.3 kW standing loss at 50 mm PIR | buffer module | §5/§10.6 | DUTY-008 §5 store table extended | ±0.5 m³ moves ride-through ±6 h |
| 5 | 3.0 kW_th sustained injection ceiling | GHEX recharge limit | §6/§10.7 | GEO_GHEX params (k 1.5 W/mK, 285 K), survey-locked | survey may raise ceiling; keep 0.7 kW normal regardless |
| 6 | 12 kW at 37.8 °C; fan 0.6 kW | terminal dry cooler rating | §10.8 | 0.4 % design temp AQS-SITE-002; 0.05 kW_fan/kW_th class | none — sized to the rated 10.16 kW case + margin |
| 7 | 1.7 kW avg / 8–11 kW batch at 40–60 °C | foundry coil+shell reject to MET_HX_Q4 | §7.2/§10.10 | 20–30 % of 45 kW input × 15–20 % duty (FOUNDRY_SIZING.md batch basis) | duty cycle dominates; rate from logged batches at first article |
| 8 | 0.5–1.0 kW at ≤60 °C | rectifier electronics reject to Q4 | §7.1/§10.9 | 12 kW rectifier at 92–96 % efficiency (POWER_DUTIES.md) | ±0.25 kW; confirm on the rectifier datasheet |
| 9 | 0.5–1.0 kW at 45–60 °C | grease-kettle wax-hold stage (Q4 branch) | §4/§10.5 | notes/GREASE_LINES.md wax C19–C28 melt band | saponification stays resistive; verify kettle jacket class |
| 10 | 8.1 (to 85 °C) / 4.8 (to 100 °C) | second-lift COP, 0.45 × Carnot from 65 °C | §3 only (deferred option) | plant S43 convention | not used in the recommended baseline |
| 11 | 0.2–0.4 kW_e net | micro-ORC endpoint on 10.16 kW_th at 65 °C | §2, GEO_ORC closure | 30–45 % of Carnot 8.9 % (Quoilin et al. 2013; Hettiarachchi et al., *Energy*) | replaces the impossible 0.08–0.12 absolute band on a 285 K source |

## 12. References

- Graph Rev AC @ `eacaf47`: edges HL-Q4-REJ, IA-Q4-LIFE, HL-Q4-A/B-BUS, S53/S54/S63/S80, IA-ZNBR-HEAT, IA-Q3A/B-TRIM, S43/S44, HL-HX8-Q4-A/B, HL-Q3-*-HX4/5/6, IND/VAC_HEAT_TO_HX; nodes Q4_BUS, Q1..Q4_A/B, GEO_ORC, GEO_GHEX, GEO_HP, ZNBR2, RECTIFIER, MET_HX_Q4.
- HEAT_LADDER.md and docs-authority/HEAT_LADDER.md (AQS-HEAT-LADDER-001); docs-authority/HEAT_LADDER_DUTIES.md (AQS-DUTY-008 Rev D §§5–7, 13); docs-authority/BALANCE_CLOSE.md §4.15 (AQS-DUTY-011); docs-authority/MVS_CHECKLIST.md lines 73–77; docs-authority/GEOTHERMAL_EQUIPMENT.md (AQS-EQP-GEO-001 Rev C, forbidden mixes §3); docs-authority/STUDY_UNITS_STUB.md §5 (AQS-EQP-STUDY-001 Rev F, ORC Carnot band); docs-authority/HVAC.md (AQS-THM-002, A-SITE-002 design temps); docs-authority/ELECTRICAL.md (HVAC/makeup 1.5 kW; RECT-EW 99 kW nameplate); docs-authority/INSULATION_SCHEDULE.md (X-THM-01 store closure; X-THM-04 line losses); docs-authority/POWER_SIZING.md.
- notes/LOAD_ROLLUP.md (AQS-PWR-ROLLUP); notes/POWER_DUTIES.md (AQS-DUTY-PWR); notes/FOUNDRY_SIZING.md; notes/GREASE_LINES.md; notes/DIGESTER_LI.md (AQS-DUTY-LI-DIG); notes/first_principles_audit_2026-10-17.md (D-GEO_ORC ruling; §Heat findings); notes/rev_ac_recovery_2026-10-17.md.
- Standard references: Quoilin, S. et al. (2013) "Techno-economic survey of Organic Rankine Cycle (ORC) systems", *Renewable and Sustainable Energy Reviews* 22:168–186; Hettiarachchi, H.D.M. et al. (2007), *Energy* — low-temperature geothermal ORC 5–9 % at 70–100 °C (both already in the repo's study basis); Wang, R.Z. & Oliveira, R.G. (2006) "Adsorption refrigeration — an efficient way to make good use of waste heat and solar energy", *Renewable and Sustainable Energy Reviews* 10:241–259; ASHRAE 62.1 (already the HVAC basis via AQS-THM-002).
