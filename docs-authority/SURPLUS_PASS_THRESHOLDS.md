# Surplus pass thresholds — study freeze criteria (MVS)

Document number: AQS-SUR-001  
Revision: C  
Date: 2026-10-24  
Authority: AQS-AUTH-001; MVS criteria AQS-UI-001 Rev C §3.2 / §11.1 item 2;
capacity study AQS-AUD-001 §11–12; scale AQS-SCALE-001; electrical
AQS-REQ-KW-001 / AQS-ELC-001; sector map AQS-SEC-001; streams AQS-STR-001;
planning gap audit AQS-MVS-GAP-001.  
Style: AQS-DOC-001.  
**Stage = study pass thresholds.** Not a PE stamp. Not vendor nameplates.
Does **not** freeze `AQS-MVS-001`. Numbers are labeled **study** until
Project locks berth count, SITE_LAT, and wafer starts.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First numeric study pass thresholds for food / water / goods / energy | 2026-10-01 |
| B | 1 | Seed upper-band FARM path (S14=4.2) so food pass_study can clear ≥0.5 bar | 2026-10-01 |
| C | 2 | Sector names to graph Rev AC (AQS-SEC-001 Rev H): WET → DIGESTER, ELEC_PV → PV_ARRAY in ELEC. No threshold changed. | 2026-10-24 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/SURPLUS_PASS_THRESHOLDS.md`  
Solver: `design_tool/.../solver/stub.py` `_surplus_stub` + `MvsCriteriaModel.surplus_thresholds`

---

## 1. Purpose

Close AQS-UI-001 §11.1 item 2 with **numeric study pass thresholds** so the
P0 solver can report surplus values and pass/fail vs colony self-sustainment
**plus** export — without inventing freeze gold or PE claims.

Self-sustainment alone is insufficient (AQS-UI-001 §3.2).

---

## 2. Scope

| In | Out |
|---|---|
| Study min export / headroom for food, clean water, goods, energy at SCALE_M=1, crew=4 | Issued berth count; SITE_LAT insolation map; vendor nameplates |
| Solver wiring from FARM / WTR / DIGESTER+MFG+FAB / PV_ARRAY (ELEC) | Claiming `loops_closed=true` or frozen MVS |

---

## 3. Drivers (study assumptions)

| Driver | Study value | Source |
|---|---|---|
| Crew | **4** | Seed / AQS-AUD-001 §11 (berth count TBD) |
| SCALE_M | **1.0** | AQS-SCALE-001 manufacturing baseline |
| Food production band | 1.4–4.2 kg/d fresh | AQS-AUD-001 §12; seed S14 mid **2.8 kg/d** |
| Crew food ration (fresh-equiv) | **0.6 kg/person·d** | Study placeholder — not nutritionist lock |
| Potable + hygiene | **~130 L/d** | AQS-AUD-001 §11 |
| FARM makeup | **~50–140 L/d** | AQS-AUD-001 §11 |
| FAB UPW makeup | **20–100 L/d** | AQS-AUD-001 §11 |
| Wet feed / plated metals | 150 kg/d / ~4.5–42 kg/d | AQS-SCALE-001 / AQS-AUD-001 |
| ELEC_NEED / TARGET | 50 / 70 kW | AQS-SCALE-001 §6 |
| Study peak-sun-hours (SITE_LAT null) | **4.0 h/d** | Placeholder until SITE_LAT issued — **not** a climate claim |

---

## 4. Study pass thresholds (SCALE_M = 1.0)

| Surplus key | Unit | Study pass threshold (min) | How computed (solver) | Rationale |
|---|---|---|---|---|
| **food** | kg/d | **≥ 0.5** export-capable after crew ration | `max(0, S14_rate − crew×0.6)` vs threshold; S14X study = same residual | Mid production 2.8 − 2.4 crew = 0.4; floor **0.5** requires upper-band or yield improvement — **study bar**, not freeze |
| **clean_water** | L/d (kg/d ≈) | **≥ 50** export-capable above internal demand | Internal demand study = potable 130 + farm mid 95 + fab mid 60 ≈ **285 L/d**; roof inventory ≫ demand; pass if makeup/inventory headroom ≥ 50 L/d **and** WTR enabled | AQS-AUD-001 §11; S40 remains event-driven (no continuous L/d invent) |
| **materials_or_goods** | kg/d | **≥ 5.0** export-capable | Mid plated metals share exportable (~0.25× mid metals) + polymer continuous-equiv mid + glass stub; seed uses study **8 kg/d** envelope when DIGESTER+MFG+FAB+GLASS on | Goods surplus requires FAB+MFG (A2); magnitudes study |
| **energy** | kWh/d | **≥ 20** study export headroom | `(target_kw − need_kw) × study_sun_h` with sun_h=4 → (70−50)×4 = **80** kWh/d gross; pass ≥ **20** | STC ≠ continuous; SITE_LAT null → insolation **unknown** — threshold is study only |

**Pass language:** solver reports `surplus.<key>.value` (study) and
`surplus.<key>.note` including `pass_study=true|false|unknown` vs these
thresholds. **Never** sets `mvs_equivalent=true` from surplus alone while
loops/`rate_incomplete` remain.

---


## 4.1 Seed FARM path (Rev B / WP-A2)

Candidate seed uses **upper-band** S14 = **4.2 kg/d** (AQS-AUD-001 §12 band
1.4–4.2) so study food export = 4.2 − crew×0.6 = **1.8 kg/d** at crew=4 →
`pass_study=true` vs ≥0.5. Mid-band 2.8 remains a valid alternate sandbox
path but fails the study bar. **Yield/berth assumption = study** — not a
nutritionist lock; retune when berth/ration is issued.

## 5. Explicit unknowns (do not invent)

| Unknown | Blocks |
|---|---|
| Issued berth / nutrition ration | Food threshold retune |
| SITE_LAT / TMY insolation | Energy kWh/d as climate fact |
| Wafer starts/d; glass kg/d | Goods magnitude |
| VCD duty kW; potable remin online | Clean-water **potable** export claim (inventory surplus ≠ drinking export) |
| Continuous terrace S40 L/d | Not required — event path remains |

---

## 6. Next measurement / decision

1. Lock berth count and ration table (operator decision).
2. Issue SITE_LAT for energy surplus climate band.
3. Confirm VCD/remin equipment IDs online before claiming potable export.
4. Retune thresholds in Rev B when measurements land — keep study label until freeze evidence table exists.

---

## 7. Related documents

| Doc | ID | Role |
|---|---|---|
| DESIGN_TOOL_ARCHITECTURE.md | AQS-UI-001 | §11.1.2 open item |
| Local planning (not published): SECTOR_CAPACITY_AUDIT | AQS-AUD-001 | Bands |
| Local planning (not published): MVS_GAP_AUDIT | AQS-MVS-GAP-001 | Gap §4.2 |
| SCALE_MODEL.md | AQS-SCALE-001 | Overprod policy |
| AUTHORITY.md | AQS-AUTH-001 | Hub |

---

## 8. Regenerate

```bash
python3 -m flow_graph.param.regen
```
