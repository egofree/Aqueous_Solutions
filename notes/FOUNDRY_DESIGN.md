# FOUNDRY sector — process and machine design

Document number: AQS-DES-FOUNDRY  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev L, notes/FOUNDRY_DUTY.md. Not a PE stamp.  
Rates are design assumptions in notes/FOUNDRY_SIZING.md. Not measured.

## Role

Takes concentrated metals and selected salts from the digester / leach / EW / molten-salt train. Outputs metal stock (ingot, billet, plate, rod, wire, powder) to the Manufacturing sector and the Fab sector.

Primary heat: induction and RF. Resistive and combustion remain alternates only.

## Incoming streams

| Source | Form | Metals / salts |
|--------|------|----------------|
| EW cascade | Cathode or powder | Cu, Zn, Ni, Fe, Pb, Sn, Co, etc. |
| Molten-salt pots | Metal or sponge | Al, Mg, Ca |
| TI_CELL | Sponge or powder | Ti |
| MO_CELL / CR_CELL | Powder or deposit | Mo, Cr |
| Digester / leach salts | Dried salt | Fluxes (NaCl, KCl), alloy additives |

## Melt and cast by metal class

Induction (IND_MELT) is a set of coils and crucibles, not one furnace. Frequency and atmosphere change with the metal.

| Class | Metals | Melt method | Atmosphere / cover | Cast form |
|-------|--------|-------------|--------------------|-----------|
| Low-melting | Zn, Pb, Sn | Air or inert induction, graphite or iron crucible | Air or N₂ | Ingot, small billet |
| Light | Al, Mg | Induction, refractory or steel crucible | Flux cover or Ar; Mg under flux or inert | Ingot, billet |
| Base | Cu, Ni, Fe | Induction, refractory crucible | Air or inert; Fe may use slag cover | Ingot, billet |
| Refractory / reactive | Ti, Mo, Cr | Vacuum induction or cold-crucible induction | Vacuum or Ar; no carbon crucible for Ti | Ingot under vacuum, or powder remain |
| Alloy | 304/316, Al alloys, etc. | Same as base metal of the alloy | As required by the most reactive constituent | Ingot, billet |

RF_HEAT is used for:
- Powder preheat and sintering (Ti, Mo, Cr powders that are not remelted).
- Zone refining of small lots.
- Preheat of charges before they enter IND_MELT.

## Machines required

### Melt and hold
- **IND_MELT** — coreless induction, multiple crucible sizes. Primary.  
- **VAC_IND** — vacuum induction furnace for Ti and other reactive metals. Separate from air-melt IND_MELT.  
- **RF_HEAT** — RF coils for preheat, sinter, zone. Primary.  
- **RES_HEAT** — resistive hold or backup. Alternate only.  
- **COMB_HEAT** — combustion hold or backup. Alternate only.

### Cast
- **CAST_LINE** — permanent-mold and sand/ingot casting for Al, Cu, Fe, Zn.  
- **VAC_CAST** — vacuum or inert casting chamber tied to VAC_IND for Ti and reactive alloys.

### Form and shape (foundry output stock)
- **ROLL** — hot/cold rolling of plate and sheet from billet (Al, Cu, Fe, Ni).  
- **EXTRUDE** — extrusion of rod, bar, and simple profiles (Al, Cu, Mg).  
- **DRAW** — wire and rod drawing (Cu, Al, Fe).  
- **FORGE** — open-die or small closed-die for billets and preforms.  
- **SINTER** — RF or induction sinter press for Ti, Mo, Cr powders that stay as powder-metal stock.  
- **ATOM** — optional gas atomizer if powder stock is required by Fab; not baseline.

### Support
- **FLUX_PREP** — dry and blend salt fluxes from digester salts.  
- **SCRAP_RETURN** — internal scrap and sprue back to the appropriate melt unit.  
- **STOCK_OUT** — staged output to MFG and FAB (ingot, plate, rod, wire, powder).

## Outputs to other sectors

| Stock | To | Typical use |
|-------|----|-------------|
| Plate, sheet, rod, wire | MFG | Machine parts, frames, fasteners |
| High-purity or specialty rod/powder | FAB | Targets, fixtures, doping hardware |
| Ingot | MFG or hold | Further working or inventory |

## Advanced casting

See notes/ADVANCED_CASTING.md.  
ISM/CCIM is the method inside VAC_IND. CONT_CAST is the stock path for Al/Cu/Fe. Investment casting is baseline (notes/INVESTMENT_CASTING.md). Rheocasting remains optional.

- Coil kW and frequency per crucible.  
- Crucible material qualification for each metal.  
- Vacuum system capacity for VAC_IND.  
- Rates and crucible campaign schedule.

## Graph implication

Add VAC_IND, VAC_CAST, ROLL, EXTRUDE, DRAW, FORGE, SINTER, FLUX_PREP, STOCK_OUT under sector FOUNDRY. RES_HEAT and COMB_HEAT remain alternates. Existing IND_MELT, RF_HEAT, CAST_LINE stay.
