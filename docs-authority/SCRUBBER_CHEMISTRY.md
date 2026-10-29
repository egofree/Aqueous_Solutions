# Scrubber chemistry

Document number: AQS-GAS-002  
Revision: B  
Date: 2026-10-29  
Authority: the plant flow graph `flow_graph/plant_flow_graph.json`; the vent and scrubber list AQS-EQP-VENT-001; the flow battery page `docs-authority/FLOW_BATTERY.md`. Measurement is metric.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. | 2026-09-27 |
| B | Rewritten against the plant graph and the documentation style guide (AQS-DOC-002): purpose, scope and terms added; the tower names mapped to the units on the graph; the reactions and controls kept; arrows and fragments written as sentences. The acid-gas and caustic headers of revision A are not units on the graph, and the caustic branch is now an owner question. | 2026-10-29 |

## Purpose and scope

The plant scrubs acid gas, chlorine and bromine out of its vents with caustic liquor made on site, and it reuses the spent liquor instead of discharging it. This page explains the chemistry that sets which liquor may go where: the reactions in each scrubber, the controls that keep them on the intended path, the destination of each liquor, and the materials each liquor needs. The sizes and rates of the scrubbers are in AQS-EQP-VENT-001 and on the graph; this page gives none.

The rule that governs the whole page is that liquors are kept apart. The scrubbers may share the supply of sodium hydroxide from the bipolar-membrane stack, but each spent liquor has one destination, because mixing them mixes oxidisers and sends the wrong salt to the wrong unit.

## 1. Terms

- BMED: the bipolar-membrane electrodialysis stack, which makes hydrochloric acid and sodium hydroxide from salt.
- CRU: the chlorate unit, a heated hold in which hypochlorite turns into chlorate for the leach.
- ORP: oxidation-reduction potential, a measure of the oxidiser content of a liquor.
- Lean liquor: liquor entering a scrubber; rich liquor: liquor leaving it with the absorbed gas.

## 2. Scrubbers on the graph

Table 2.1 maps the scrubbers of this page to the units on the graph.

Table 2.1. Scrubbers and their liquors

| Duty | Units on the graph | Gas in | Liquor in | Liquor to |
| --- | --- | --- | --- | --- |
| Hydrogen chloride and chlorine | ALK_SCRUBBER, then ACID_POLISH_SCRUB (S65) | Off-gas of the acid evaporator vacuum system (IA-VS-OFF) into ALK_SCRUBBER; leach reactor headspace (IA-SCRUB-SRC) into ACID_POLISH_SCRUB | BMED sodium hydroxide | CRU (S66) |
| Chlorate finish | CRU | — | Polish liquor (S66) and the chlorine of the molten-salt cells | Leach reactor (IA-CRU-01) |
| Bromine | ZNBR2_BR2_REGEN | Headspace of the positive tank of the zinc-bromine battery (S69) | BMED sodium hydroxide | Back to the battery as bromide (S69B) |
| Metal-aisle fume | MET_SCRUB | Metal-aisle air (S62, S71) | Scrubber water | Leach (S72) and oil line (S72B) |
| Nitrogen oxides | NOX_SCRUB | Flue and exhaust gases | — | Nutrient dosing and roof tank |

The metal-aisle and nitrogen-oxide scrubbers are listed for completeness; their chemistry is in AQS-EQP-VENT-001. Hydrogen is not scrubbed: it goes from the dryer to the hydrogen store CRYO_H2 (S64), and the relief route to RELIEF_H2 (S24) carries flow only in an upset. The afterburner flue goes to the flue knockout FLUE_KO (S67), not to these scrubbers.

## 3. Hydrogen chloride and chlorine

### 3.1 Hydrogen chloride

Hydrogen chloride reacts with sodium hydroxide to give salt and water:

    HCl + NaOH → NaCl + H2O

The reaction is fast, so the rate is set by the wetted area of the packing, not by the chemistry. The packed height is set by chlorine, not by hydrogen chloride.

### 3.2 Chlorine, absorbed cold

At the top of the tower, where the liquor is lean and cool, chlorine gives chloride and hypochlorite:

    Cl2 + 2 NaOH → NaCl + NaClO + H2O

This is the first step of industrial hypochlorite manufacture. The inlet liquor is kept below about 40 °C so that chlorine is not driven back out of a hot sump.

### 3.3 Chlorate, in the chlorate unit

Hypochlorite disproportionates to chlorate when the liquor is held hot and slightly alkaline:

    3 NaClO → 2 NaCl + NaClO3

That hold is the chlorate unit CRU, not the packed bed: the tower makes chloride and hypochlorite, and CRU finishes the chlorate that the leach uses as oxidant with BMED acid. Chlorate is not made in the BMED stack. The liquor of CRU is never sent to a drain.

### 3.4 Side reactions to avoid

Air leaking into the header brings carbon dioxide, which takes up sodium hydroxide as carbonate:

    2 NaOH + CO2 → Na2CO3 + H2O

Carbonate uses up base, adds salt that does nothing, and makes no oxidant, so the reactor lid stays closed, the header stays tight, and make-up air enters only through the designed breather. Free chlorine that meets ammonia or organics forms chloramines and chlorinated organics, so only the anode hoods are connected to this tower; the cathode hydrogen stays on the hydrogen header HDR_H2. Liquor that has seen bromide forms mixed chlorine and bromine oxyanions and must not go to CRU (Section 5).

### 3.5 Controls

- The lean liquor enters at pH 12 or above at the top distributor.
- The sump is held between pH 10 and 12. Below pH 9 chlorine slips through; above about pH 13 and hot, the liquor attacks the packing and takes up carbonate faster.
- A rising ORP at a fixed pH means hypochlorite is building up, and the liquor is transferred to CRU rather than recirculated.
- Transfer is started on the level or on the ORP band, not on a timer alone.
- If the chlorine or hydrogen chloride at the outlet rises, the liquor rate is raised first, not the fan speed.

One mole of chlorine needs two moles of sodium hydroxide in the cold step, and one mole of hydrogen chloride needs one. The base supply is sized from the anode current of the electrowinning cells and the chlorate unit by Faraday's law, plus the reactor headspace load, with a margin for carbon dioxide and slip.

## 4. Caustic vents

Revision A described a separate caustic branch for the vents of the glass digest and the BMED base tank: the sodium hydroxide mist is caught in water and trimmed with BMED acid to a neutral salt solution for the salt feed of the BMED stack,

    NaOH + HCl → NaCl + H2O

with a target of pH 6 to 8 and no free caustic sent to the stack. This branch and its header are not units on the present graph. Whether these vents need their own scrubber, or are covered by another unit, is an owner question in `REWRITE_TODO.md`. The rule stands either way: caustic vents are not joined to the acid-gas scrubber, because that would spend base on neutralising base and send the wrong salt to CRU.

## 5. Bromine

The bromine regenerator ZNBR2_BR2_REGEN takes the headspace and seal gas of the positive tank of the zinc-bromine battery ZNBR2. It is a separate unit with its own liquor; it shares only the base supply. Bromine and hydrogen bromide are absorbed cold:

    Br2 + 2 NaOH → NaBr + NaOBr + H2O
    HBr + NaOH → NaBr + H2O

Hypobromite turns into bromate if it is held hot,

    3 NaOBr → 2 NaBr + NaBrO3

and bromate is not a battery chemical, so this sump is never held hot as CRU is. The liquor goes to a hold tank, is checked by ORP, and returns to the positive tank as bromide. If the ORP shows too much hypobromite or bromate, the liquor is reduced, preferably on zinc granules from the electrowinning scrap, since zinc is already in the battery; a metered sulfite also works but adds a salt. This liquor never goes to CRU. The size of the regenerator is in `docs-authority/sizing/ZNBR2_BR2_REGEN.md` and `docs-authority/FLOW_BATTERY.md`.

## 6. What each liquor is after the scrubber

Table 6.1. Liquors and their destinations

| Liquor | Main solutes | Goes to | Must not contain |
| --- | --- | --- | --- |
| Acid-gas scrubber sump | NaCl, NaClO, remaining NaOH | CRU | bromide, organics, ammonia |
| CRU product | NaClO3, NaCl | Leach reactor, with BMED acid | bromate; never to a drain |
| Caustic vent liquor (Section 4) | NaCl after the acid trim | BMED salt feed | free chlorine, chlorate |
| Bromine regenerator sump | NaBr, NaOBr | Hold tank, then the battery as bromide | chlorate |

## 7. Pressure and routing

- The acid-gas and dust headers run below atmospheric pressure at the source, so leaks go inward, and the fan sits after the treatment so that its impeller sees clean gas.
- The battery tanks run a little above atmospheric pressure, so bromine leaks into the bromine header and not onto the pad (`docs-authority/FLOW_BATTERY.md`). The two headers have opposite signs and are never joined.
- Hydrogen is not washed with water: a water wash adds a wet explosion hazard. It passes a flame arrestor and the dryer to the store.

## 8. Materials

Table 8.1. Materials for each liquor

| Stream | Wall |
| --- | --- |
| Chlorine and hydrogen chloride gas with caustic liquor | Polypropylene or glass-reinforced plastic tower; PVDF pump |
| Hot chlorate liquor in CRU | CPVC or PVDF, because the liquor is becoming an oxidiser |
| Caustic mist with a dilute acid trim | Polypropylene |
| Bromine gas with caustic liquor | PVDF only |

Titanium is not used for a scrubber wall, 316L stainless steel pits in wet chlorine, and polypropylene is not suitable for the hot chlorate hold.
