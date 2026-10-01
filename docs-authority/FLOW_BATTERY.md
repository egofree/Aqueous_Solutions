# ZnBr2 flow battery

Sized to the Sol-Ark 60K-3P-480V battery window. Membranes are the same SEM Tech IEM family as the EW aisle (sulfonated / aminated PS–PVC on PP felt). This is a hybrid flow battery: energy lives in plated zinc plus stored bromine complex, not only in tank volume.

`znbr2_flow_pfd.png` is the PFD.

## Why this chemistry

- Cell ~1.8 V. ~330 series cells sit at ~600 V nominal, inside the inverter’s 160–700 V window.
- 60 kW at 600 V is 100 A — exactly the two 50 A battery ports in parallel.
- Zinc and bromide are already plant chemicals (EW-9, BMED brine, scrubber).
- Aqueous, non-flammable. The hazard is bromine vapor and hydrogen on abuse, not fire.

It is not a drop-in lithium rack. The 60K speaks CAN as if the pack were lithium. A BMS gateway translates stack voltage, current, two-tank levels, two-tank ORP, H2, and Br2 sensors into that CAN.

## Cell reactions

Charge (stack positive of inverter):

- Zinc half (negative): `Zn2+ + 2 e- → Zn(s)`
- Bromine half (positive): `2 Br- → Br2 + 2 e-`, then `Br2 + Br- → Br3-` and/or complexation on the quaternary amine

Discharge is the reverse. Water is not part of the intended reaction. If it becomes one, you are off-gassing.

Nominal 1.82 V. Charge cutoff 2.05 V/cell (677 V stack). Discharge cutoff 1.50 V/cell (495 V stack). Do not sit below ~1.4 V/cell — zinc corrosion and H2 rise.

## Separator

Two-compartment cell. One IEM.

- **CEM** (blue) is the working separator. It blocks `Br3-` and free `Br2` (anions / neutrals) from the zinc plate. Current is carried by `Zn2+`.
- A thin **AEM** (orange) faces the bromine compartment only as a sacrificial / wetting layer. It is not the main barrier. If it sees free Br2 for long it will oxidize — inspect on the same interval as EW membranes.
- Do not use a BPM here. Water split is the failure mode, not the feature.

Same double-layer felt construction as the EW CEM. Hot-swappable frames, 50 × 50 cm active, 0.25 m².

## Stack and tanks

| Item | Value |
|---|---|
| Series cells | 330 |
| Active area | 0.25 m² |
| Current at 60 kW | 100 A → 40 mA/cm² |
| Areal capacity cap | 80 mAh/cm² (dendrite limit) |
| Stack amp-hours | 200 Ah |
| Nameplate energy | 200 Ah × 600 V = 120 kWh |
| Usable | ~100–110 kWh after cutoff and strip reserve |
| Bipolar plates | carbon-filled PP |
| Frames / manifolds | PVDF |
| Zinc electrode | carbon-plastic; zinc plates onto it |
| Bromine electrode | carbon felt on carbon-plastic |
| Zinc tank | PP, 1.2 m³ |
| Bromine tank | PVDF, 1.2 m³, floating lid + vapour space to scrubber |
| Electrolyte | 2.0–2.2 M ZnBr2, 0.5 M KCl supporting, 0.8 M complexer (MEP or equivalent) |
| Pumps | PVDF mag-drive, ~20 L/min per side at 40 mA/cm² |

Tanks sit in a bunded yard skid, not inside either container. Secondary containment = 110 % of one tank.

Zinc plating is the capacity limit. Over-plate and you grow dendrites through the CEM. The BMS enforces 80 mAh/cm² and a weekly strip (full discharge to 1.50 V/cell so the zinc returns to solution).

## Charge

1. Pumps prove flow. No-flow interlock opens the DC contactors.
2. Sol-Ark CC at ≤100 A until 2.00 V/cell, then CV to 2.05 V/cell.
3. Zinc tank level falls slightly (Zn leaves solution); bromine-tank ORP rises (Br2/Br3- inventory).
4. Stop on any of: 2.05 V/cell, 80 mAh/cm² this cycle, Br2-in-headspace high, H2-in-headspace high, ΔP across CEM out of band.
5. Do not charge a dry zinc plate. If the last strip left the electrode bare, start at 20 A until voltage leaves the 1.4 V floor.

Round-trip on a clean stack: 70–80 % DC–DC. Pump work is ~0.4 kW/side, included.

## Discharge

1. Same flow-prove.
2. Sol-Ark draws ≤100 A to the 1.50 V/cell floor or the energy setpoint.
3. Zinc dissolves; bromine-tank ORP falls.
4. If voltage sags at constant current, current density is above the zinc kinetic limit — drop to 60 A. Do not “push through” with pulse. Pulse here makes dendrites, unlike EW-7.

Standby: pumps at trickle (2 L/min) or a 15 min pulse every hour so Br2 does not stratify. CEM still blocks most crossover; residual self-discharge is a few percent per day.

## Off-gas — what actually comes off

Intended operation is closed liquid. Gas is an abuse signal.

| Gas | Where | When | Action |
|---|---|---|---|
| Br2 vapour | Bromine-tank headspace | Warm tank, weak complexer, overcharge | Dedicated Br2 scrubber, never the plant Cl2 tower first |
| H2 | Zinc-tank headspace | Corrosion, over-discharge, water reduction | Plant H2 header if clean; else vent via flame arrester |
| O2 | Bromine side | Severe overcharge past Br- inventory | Stop charge. Not a product stream |
| HBr | Either tank if acidified | Leak of plant HCl into the battery | Stop. Neutralize. Do not run |

Keep this electrolyte off the Salria / chlorate header. Mixed Cl2 / Br2 / chlorate in one packed tower is how you make surprise oxidizers.

## Gas handling

Two small headers on the battery skid, not the container roof rail.

**Br2 header (PVDF):** bromine-tank vent, stack positive manifold vents, pump seals. Goes to a dedicated packed tower, 200 mm ID, 1.5 m packed height, 5–10 L/min BMED NaOH. Product liquor is NaBr / NaOBr. Return it to the bromine tank as bromide makeup after a hold tank / **ZNBR2_BR2_REGEN** and ORP check (**S69**, AQS-VENT-001). Do not send that liquor to CRU. Continuous outdoor Br₂ dump is not the design end state — regen return is.

**H2 header (316L or CPVC dry):** zinc-tank vent. Low point drain back to the zinc tank. Then a flame arrester and a tie into the plant H2 line that already leaves BMED cathode for the cryo / fuel-cell tote. If H2-in-zinc-headspace exceeds 1 % LEL-equivalent, open the DC contactors and raise zinc-tank purge with N2 or CO2 from the plant gas rack.

Both tanks run 20–50 mm water column positive so leaks go to the header, not into the pad. Makeup air is filtered into the zinc tank only.

The plant alkaline scrubber stays on Cl2 / HCl / Br from EW and leach. The battery tower is a second, smaller column next to it in the yard. Shared NaOH supply, separate liquor.

## Materials

Bromine solution attacks 316L, bare Ti, PP over years, and every foam-core PVC. Use PVDF for the bromine loop (tank, pipe, tower, pump). PP is acceptable on the zinc loop. Carbon-plastic for electrodes. Same rule as the EW aisle: titanium is an electrode substrate, not a wall.

Weld-On 724 does not join PVDF. Fusion-weld PVDF or use rated flanges.

## Controls and interlocks

- Pump-flow proved both sides before DC close.
- Stack voltage 495–677 V or contactors open.
- Cell-voltage tap every 10th cell; any tap >2.15 V opens charge.
- Br2 headspace sensor on the bromine tank.
- H2 headspace sensor on the zinc tank.
- Bund leak sensor.
- CEM ΔP.
- Weekly strip cycle forced by the BMS, not optional.
- CAN gateway to Sol-Ark: voltage, current, SOC from amp-hours and ORP, inhibit-charge, inhibit-discharge.

## Plant ties (optional makeup, not a shared loop)

- Zinc loss makeup from EW-9 product dissolved as ZnCl2 / ZnBr2, metered into the zinc tank.
- Bromide makeup from the Br2-tower hold tank, or from polish-bank bromide if that liquor is clean of chlorate.
- NaOH from BMED BASE to the Br2 tower.
- Q4 water for evaporation makeup.
- Heat: pumps and ohmic drop are Q4. Do not put this stack on Q2.

Do not circulate Salria through these tanks. Chlorate in a bromide complexer is a different plant.

## What this is not

Not a second EW aisle. Not a chlorate cell. Not a place to dump pregnant leach. The membranes look the same; the liquor does not.
