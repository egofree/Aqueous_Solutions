# Scrubber chemistry

Document number: AQS-GAS-002  
Revision: Basic issue  
Date: 2026-09-27  
Measurement: metric

Liquor destinations are locked. Mixing towers mixes oxidizers. Shared
NaOH supply from BMED BASE is allowed. Shared liquor is not.

| Tower | Gas in | Liquid in | Liquid out | Gas out |
|---|---|---|---|---|
| Alkali (HDR_ACID_GAS) | HCl, Cl2, acid mist | BMED NaOH | CRU | → polish / upset residual |
| Caustic (HDR_CAUSTIC) | NaOH mist | Q4 water + BMED HCl trim | SALT FEED as NaCl | after pack (closed liquid primary) |
| Br2 (battery) | Br2, HBr | BMED NaOH | hold / regen → ZnBr2 pos. tank (S69) | no continuous dump |
| Demister (ahead of alkali) | same as alkali | none (knockout) | CSTR 1 or CRU | alkali tower |
| Dust / H2 | solids / H2 | — | fines to CSTR 1 | not a wet tower |


## 0. Closure end state (AQS-VENT-001)

Gas **out** columns below that historically read “stack” are **not**
design free outdoor dumps. Normal end states:

| Tower | Normal gas end state | Liquor return |
|---|---|---|
| Alkali (+ **ACID_POLISH**) | Upset residual only after polish | → CRU (S66) |
| Caustic | After pack; liquor → SALT FEED | already closed liquid |
| Br₂ (+ **ZNBR2_BR2_REGEN**) | No continuous dump | → ZnBr2 pos. tank (S69) |
| Demister | → alkali tower | knockout → CSTR / CRU |

H₂ is not scrubbed (see §5) — path is dryer → CRYO_H2 (S64).
AFTERBURNER flue → FLUE_CAP / CRYO (S67), not these towers.

## 1. Alkali tower — HDR_ACID_GAS

Duty: CSTR lid + EW / polish **anode** hoods. Induced draft. Fan is
**after** the pack so the impeller sees scrubbed gas.

Wetted wall: PP or FRP. Pack: 50 mm PP or ceramic saddles. Lean liquor:
BMED BASE, 5–15 wt% NaOH. Do not feed Salria into this tower.

### 1.1 Hydrogen chloride

```
HCl(g) + NaOH(aq) → NaCl(aq) + H2O
```

Fast. Controlling resistance is film area, not kinetics. Packed height
is set by Cl2, not by HCl.

### 1.2 Chlorine — cold absorption

At the top of the tower (lean, cooler):

```
Cl2 + 2 NaOH → NaCl + NaClO + H2O
```

Ionically:

```
Cl2 + 2 OH- → Cl- + ClO- + H2O
```

This is the same first step as industrial hypochlorite. Keep the
**inlet** liquor below ~40 °C so you do not flash Cl2 back off a hot
sump.

### 1.3 Chlorate — the CRU step

Hypochlorite disproportionates when the liquor is held hot and
slightly alkaline:

```
3 NaClO → 2 NaCl + NaClO3
```

```
3 ClO- → 2 Cl- + ClO3-
```

That hold is **CRU**, not the packed bed. The tower makes
NaCl + NaClO. CRU finishes NaClO3 for REGEN LEACH (with BMED HCl).
Chlorate is not made in BMED.

Target after CRU: NaClO3 inventory for leach ORP, residual NaCl
returned toward SALT FEED / BMED. Do not dump CRU liquor to sewer.

### 1.4 Side reactions to starve

Air in-leak:

```
2 NaOH + CO2 → Na2CO3 + H2O
```

Carbonate consumes BASE, adds dead salt, and does not make oxidant.
Keep the CSTR lid closed and the header tight. Makeup air only through
the designed breather.

If free Cl2 meets ammonia or organics in this tower you make
chloramines / AOX. Anode hoods only. Cathode H2 stays on HDR_H2.

If this liquor sees bromide (battery or polish Br), you start
mixed Cl/Br oxyanions. That liquor does not go to CRU. See §3.

### 1.5 Controls

- Lean NaOH: pH ≥ 12 at the top distributor.
- Sump pH 10–12. Below 9, Cl2 slips. Above ~13 and hot, you etch pack
  and accelerate carbonate pickup.
- Sump ORP: rising ORP at fixed pH means ClO- inventory is building —
  transfer to CRU, do not keep recirculating forever.
- Transfer on level or on ORP band, not on a timer alone.
- Gas out: Cl2 and HCl below the site permit after polish. Prefer
  liquor → CRU pull over continuous stack flow (AQS-VENT-001). If the
  residual sensor rises, increase liquor rate first, not fan speed.

Stoichiometry check (order of magnitude): 1 mol Cl2 needs 2 mol NaOH
at the cold step. 1 mol HCl needs 1 mol NaOH. Size BMED BASE bleed
from Faraday on the EW / CRU anodes plus the CSTR headspace load,
then add 20 % for CO2 and slip.

## 2. Caustic branch — HDR_CAUSTIC

Duty: NaOH DIGEST headspace and BMED BASE tank vents. Local suction.
Do **not** tee this header into HDR_ACID_GAS. You would spend BASE
neutralizing BASE and send the wrong salt to CRU.

### 2.1 Capture

NaOH mist dissolves in Q4 water:

```
NaOH(mist) → NaOH(aq)
```

### 2.2 Neutralize to salt

Trim with BMED ACID to a pH the SALT chamber will accept:

```
NaOH + HCl → NaCl + H2O
```

Target liquor: pH 6–8, conductivity as NaCl, no free caustic slug
into BMED SALT. Then SALT FEED.

If you skip the HCl trim and send dilute NaOH to SALT, the BPM still
runs but you have moved BASE into the wrong compartment and you will
fight pH on the stack.

Wall: PP. Pack: PP saddles. Pump: PP mag-drive. Not CPVC-required;
not PVDF-required.

## 3. Battery bromine tower

Duty: ZnBr2 positive-tank headspace and pump seals. PVDF tower,
separate liquor. Shared BMED BASE supply only.

Cold absorption:

```
Br2 + 2 NaOH → NaBr + NaOBr + H2O
```

```
HBr + NaOH → NaBr + H2O
```

Hypobromite will disproportionate to bromate if you cook it:

```
3 NaOBr → 2 NaBr + NaBrO3
```

Bromate is not a battery chemical. Do not hot-hold this sump the way
CRU hot-holds hypochlorite.

Liquor path: sump → hold tank → ORP check → return **bromide** to the
positive tank. If ORP says hypobromite/bromate is high, reduce
(plant options: contact with zinc granules from EW-9 scrap, or a
metered sulfite — sulfite is an extra salt, zinc is already in the
flowsheet). Do not send this liquor to CRU.

FLOW_BATTERY.md owns the skid dimensions (200 mm ID, 1.5 m pack,
5–10 L/min). This file owns why the liquor is segregated.

## 4. What each liquor is after the tower

| Liquor | Main solutes | Goes to | Must not contain |
|---|---|---|---|
| Alkali sump | NaCl, NaClO, leftover NaOH | CRU → NaClO3 + NaCl | Br, organics, NH3 |
| CRU product | NaClO3, NaCl | REGEN LEACH with BMED HCl | BrO3-, sewer |
| Caustic sump | NaCl after HCl trim | SALT FEED | free Cl2, chlorate slug |
| Br2 sump | NaBr, NaOBr | hold → pos. tank as Br- | chlorate, Salria |

## 5. Pressure and routing (chemistry constraints)

- Alkali and dust headers are negative at the source so leaks go
  inward. Fan after treatment.
- Battery tanks are 20–50 mmWC **positive** so Br2 leaks to the Br2
  header, not the pad (FLOW_BATTERY.md). Different sign from the
  plant acid-gas header. Do not manifold them.
- H2 is not scrubbed. Flame arrestor, dryer, CRYO_H2 / fuel (S64);
  roof (S24) contingency only. Water wash on H2 only adds a wet
  explosion problem.

## 6. Materials vs chemistry

| Stream | Wall |
|---|---|
| Cl2 / HCl gas + NaOH liquor | PP or FRP tower; PVDF pump |
| Hot CRU (chlorate finish) | CPVC or PVDF — this liquor is becoming an oxidizer |
| NaOH mist + dilute HCl trim | PP |
| Br2 gas + NaOH liquor | PVDF only |

Ti is not a scrubber wall. 316L pits in wet Cl2. PP is wrong for the
hot CRU oxidizer hold.
