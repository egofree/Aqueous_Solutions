# Vent, scrubber and regenerator equipment

Document number: AQS-EQP-VENT-001  
Revision: C  
Date: 2026-10-24  
Basis: AQS-VENT-001, AQS-GAS-002, AQS-GAS-003, AQS-CRY-002, AQS-MFG-MET-001, `FLOW_BATTERY.md`, AQS-STR-001 streams S64 to S72, AQS-AUD-001, `ELECTRICAL.md` (AQS-ELC-001), AQS-MF-001.  
Licence: CERN-OHL-S-2.0. `SCALE_M = 1.0`. Wet feed design basis: 150 kg/d.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: scrub/regen + CRYO KO stubs for vent closure | 2026-09-28 |
| B | 1 | Study-estimate duties (formula + assumptions); FreeCAD stubs | 2026-10-01 |
| C | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; sections renumbered (study estimates now §4) and references in other pages updated. Duties and rules unchanged. | 2026-10-24 |

## 1. Purpose and scope

The plant does not release process gas continuously to open air (AQS-VENT-001). The streams that were once vented are instead scrubbed and the scrubbing liquor regenerated, or returned to the cryogenic plant. This page lists the equipment that does this: the acid polish scrubber, the bromine regenerator of the zinc-bromide battery, the condensate knockout of the cryogenic room air handler, the metal-aisle scrubber and the afterburner flue capture.

Each duty is a study estimate: a formula with its assumptions, applied to issued plant throughputs. Study estimates are not vendor nameplates; pack heights and fan curves still need stamped vendor curves against the actual duct take-off (AQS-GAS-003 §3).

## 2. Terms

- Study estimate: a figure derived by formula from issued plant data, labelled as such and not a nameplate.
- Polish scrubber: a short packed column after the main alkali scrubber (`ALK_SCRUBBER`) that removes what the main scrubber lets through.
- Static pressure (SP): the pressure drop across the scrubber train that the fan must overcome.
- ACH: air changes per hour, the air flow divided by the room volume.
- Knockout (KO): a vessel that separates condensed liquid from a gas stream.
- ORP: oxidation–reduction potential, used to judge when liquor is ready to transfer.
- NCG: non-condensable gas.
- CRU: the chlorine recovery unit that receives spent acid-polish liquor.

Stream numbers (S65 and so on) are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Equipment tags

Table 3.1. Vent, scrubber and regenerator units

| Tag | Duty | Stream hooks | Status |
|---|---|---|---|
| ACID_POLISH_SCRUB | Post-ALK_SCRUBBER polish pack; lean BMED NaOH | S65 in; gas residual upset only | **Study estimate** §4.1 |
| ACID_POLISH_REGEN | Blowdown / media regen → CRU | S66 / SCRUBBER_TO_CRU | **Study estimate** §4.1 |
| ZNBR2_BR2_SCRUBBER | Existing Br₂ tower (FLOW_BATTERY) | Br₂ header | Issued massing |
| ZNBR2_BR2_REGEN | Hold + ORP + Br⁻ return to pos. tank | S69 | **Study estimate** §4.2 |
| CRYO_AHU | CRYO room NFPA 2/55 AHU | S56 residual | Issued (AQS-EQP-CRY-001) |
| CRYO_AHU_COND | Condensate knockout / condensable return | S70 → COLD_BOX | **Study estimate** §4.3 |
| MET_AHU | Dedicated MFG metal-aisle capture | S71 | Issued (AQS-EQP-MFG-MET-001) |
| MET_SCRUB | Fume / oil-mist scrub on MET_AHU train | S71 | **Study estimate** §4.4 |
| MET_SCRUB_REGEN | Liquor / media regen toward returns | S72 | **Study estimate** §4.4 |
| FLUE_CAP | AFTERBURNER → CRYO CO₂ / condensate KO | S67 / S18; S68 | Claimed + §4.5 study |

## 4. Study estimates

### 4.1 Acid polish scrubber and regenerator (`ACID_POLISH_SCRUB`, `ACID_POLISH_REGEN`)

Source flow (issued): the acid gas header `HDR_ACID_GAS` has a design flow of 0.42 m³/s (1 500 m³/h) at 40–60 °C into the alkali pack (AQS-GAS-003). The polish scrubber sees the same volume after `ALK_SCRUBBER`: residual chlorine, hydrogen chloride and wet air (Table 4.1).

Table 4.1. Acid polish scrubber

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Gas Q to polish (S65) | **0.42 m³/s (1 500 m³/h)** | = HDR_ACID_GAS design (AQS-GAS-003 §1); not a new generation rate |
| Pack ID / height | **0.5–0.7 m ID; 0.6–1.0 m pack** | ~⅓–½ of the ALK_SCRUBBER 1.8 m pack (AQS-GAS-003); film-area polish, not primary absorb |
| Added SP | **0.4–0.6 kPa** | Scale from the ALK_SCRUBBER pack 1.2 kPa × (H_polish/H_alk) |
| Liquor recirculation | **50–80 L/min** | L/G ≈ 2–3 L/m³ × 1 500 m³/h → 50–75 L/min; lean 5–15 wt% NaOH (AQS-GAS-002 §1) |
| Blowdown → CRU (S66) | **50–200 L / transfer** | On ORP/level (AQS-GAS-002 §1.5); not continuous dump |
| NaOH stoichiometric order | **~2 mol NaOH / mol Cl₂; 1 mol / mol HCl** | AQS-GAS-002 §1.5; size BMED BASE bleed from EW/CRU Faraday + CSTR + 20 % CO₂/slip |

### 4.2 Bromine regenerator (`ZNBR2_BR2_REGEN`)

The issued tower (`FLOW_BATTERY.md`) is 200 mm in diameter with a 1.5 m pack and 5–10 L/min of sodium hydroxide recirculation from the bipolar membrane electrodialysis unit (Table 4.2).

Table 4.2. Bromine regenerator

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Hold / regen volume | **50–150 L** | Tower sump + hold tank class; ORP settle before S69 |
| Liquor return (S69) | **Intermittent at 5–10 L/min** | Match tower recirculation when transferring Br⁻ to pos. tank |
| Headspace purge gas | **10–50 m³/h** class | Abuse/offgas (FLOW_BATTERY §Off-gas); **not** continuous Faraday Br₂ product |
| Chemistry | Br₂ + 2 NaOH → NaBr + NaOBr; return as Br⁻ | AQS-GAS-002 §3; never hot-hold to bromate; never CRU |

### 4.3 Cryogenic room condensate knockout (`CRYO_AHU_COND`)

After the layout relief, the cryogenic room is 9 × 6 × 4 m, a volume of 216 m³ (`params.py`; it was 144 m³ at 6 × 6 m) (Table 4.3).

Table 4.3. Cryogenic room condensate knockout

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Room ACH | **6–12 ACH** | NFPA 2/55 mechanical ventilation practice class for H₂ fire area |
| AHU volumetric | **1 300–2 600 m³/h** | Q = ACH × V; V = 216 m³ |
| Condenser / KO duty | **~2–5 kW** | m·Cp·ΔT: Q_vol × 1.2 kg/m³ × 1.0 kJ/(kg·K) × 5–10 K / 3600; dehumidifier class, not Stirling |
| S70 condensable mass | **Method TBD** until CRYO holdup kg issued | Rate ≈ boil-off + purge condensable fraction × AHU flow; do not invent kg/h |

The S56 residual after the knockout is a contingency only (AQS-VENT-001).

### 4.4 Metal-aisle scrubber and regenerator (`MET_SCRUB`, `MET_SCRUB_REGEN`)

Table 4.4. Metal-aisle scrubber

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Capture Q (S71) | **0.15–0.25 m³/s (540–900 m³/h)** | Local LEV for atomizer + mist hoods; ~⅓–½ of HDR_DUST 0.55 m³/s (AQS-GAS-003) |
| Train SP | **0.8–1.2 kPa** | Mist eliminator + light pack; fan after treatment |
| Liquor | Aqueous demist + oil coalescer | Fines → CSTR (S19/S72); organics → OIL / HDR_ORG; not HDR_ACID_GAS primary |
| Regen transfer (S72) | Intermittent on level/turbidity | No continuous sewer |

### 4.5 Afterburner flue capture (`FLUE_CAP`)

Table 4.5. Afterburner flue capture

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| NCG into AFTERBURNER | **0.05 m³/s (180 m³/h)** | AQS-GAS-003 HDR_OIL_VAPOR NCG |
| Flue products after oxidation | Air + CO₂ + H₂O (destruction remains) | Capture efficiency **TBD** — Claimed architecture S67/S18 |
| Condensate S68 | Order of NCG moisture + oxidation water | Treat as S13 class; not potable |

## 5. Separation rules

1. Acid polish liquor goes to the CRU only: no bromide, no organics, no ammonia.
2. Bromine regenerator liquor goes to the positive tank of the zinc-bromide battery only, never to the CRU.
3. `CRYO_AHU_COND` returns condensables to `COLD_BOX`, never to habitation return air.
4. `MET_SCRUB` fines go to the CSTR (S19 class) and organic mist to `OIL` or `HDR_ORG`. Metal fume is not teed into `HDR_ACID_GAS` as its main path.
5. Hydrogen is not scrubbed wet (AQS-GAS-002 §5); its path is the dryer, then `CRYO_H2`.

## 6. FreeCAD models

Stubs are attached in `gas_handling.py` (`ACID_POLISH_*`), `cryo.py` (`CRYO_AHU_COND`, `FLUE_CAP`), `mfg_shop.py` (`MET_SCRUB*`) and `electrical_yard.py` (`ZNBR2_BR2_REGEN`). Rebuild with `/usr/bin/freecadcmd models/freecad/build_plant.py`.

## 7. Rebuilding the process flow diagrams

The process flow diagrams are regenerated from the plant graph with the rest of the derived files:

```bash
python3 -m flow_graph.param.regen
```
