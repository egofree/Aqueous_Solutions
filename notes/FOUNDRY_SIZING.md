# Foundry sizing — coil, crucible, continuous cast, rates

Document number: AQS-SIZE-FOUNDRY  
Revision: A  
Date: 2026-10-16  
Authority: engineering judgment and published small-furnace data. Not measured. Not a PE stamp.  
All rates are design assumptions. Assays remain deferred.

## Throughput basis (500 kg/day mineral plant)

Self-replication and maintenance stock, not primary metal production.

| Metal / product | Design rate | Notes |
|-----------------|-------------|-------|
| Al stock | 8 kg/d | Frames, housings |
| Cu stock | 3 kg/d | Bus, windings, fab |
| Fe / low-alloy stock | 10 kg/d | Structural, fasteners |
| Stainless (304/316) | 1.5 kg/d | Uses Cr 0.20 + Mo 0.05 from DESIGN_RATES |
| Ti stock | 0.40 kg/d | Anode mesh, shells (DESIGN_RATES) |
| Zn, other EW metals | 1 kg/d | Castings, coatings feed |
| Investment castings | 2 kg/d | Complex parts, all alloys |
| **Total metal through foundry** | **~26 kg/d** | |

Batch size: 10 kg nominal crucible. One to three heats per day per furnace. Not continuous tonne-scale.

## IND_MELT — coreless induction

| Parameter | Value | Basis |
|-----------|-------|-------|
| Crucible capacity | 10 kg (steel equivalent) | Matches daily lot size |
| Power | 25 kW | Small-furnace class (15–50 kW for <20 kg); ~2.5 kW/kg |
| Frequency | 2–3 kHz | Small charge; skin depth suitable for 10 kg steel/Cu |
| Energy | 0.7–0.9 kWh/kg steel; 0.5–0.6 kWh/kg Al/Cu | Published small-furnace range |
| Coil | Water-cooled copper tube | Standard |
| Duty | Batch, cold start acceptable | Medium-frequency coreless |

One furnace body with interchangeable crucibles for Al, Cu, Fe, Zn. Atmosphere: air for Cu/Fe; flux or Ar cover for Al.

## VAC_IND — ISM / cold crucible (Ti)

| Parameter | Value | Basis |
|-----------|-------|-------|
| Capacity | 2 kg | Ti rate is 0.40 kg/d; small skull melt |
| Power | 15 kW | Higher specific power; vacuum and skull losses |
| Frequency | 5–10 kHz | Small pool, water-cooled copper segments |
| Crucible | Segmented water-cooled copper | Skull of Ti; no refractory contact |
| Vacuum | 10⁻²–10⁻³ mbar class | Standard VIM/ISM |
| Energy | ~2–3 kWh/kg | Includes vacuum and skull; not optimized |

## Crucibles (IND_MELT)

| Metal | Crucible | Notes |
|-------|----------|-------|
| Al, Zn | Clay-graphite or SiC | Flux cover |
| Cu | Clay-graphite or SiC | Air ok |
| Fe, Ni, stainless | Alumina or magnesia rammed | Slag cover optional |
| Ti, reactive | None (ISM copper skull) | VAC_IND only |

Crucible life: design for 20–50 heats before reline. Reline material from plant alumina/magnesia where possible.

## CONT_CAST — continuous / semi-continuous

| Parameter | Value | Basis |
|-----------|-------|-------|
| Products | Billet 50–80 mm, slab up to 100×20 mm | Feed to ROLL / EXTRUDE |
| Metals | Al, Cu, Fe (air/inert); Ti via vacuum variant from VAC_IND | |
| Mold | Water-cooled copper, horizontal | Simpler than vertical for this scale |
| Withdrawal | 0.2–0.5 m/min | Small section |
| Length | Cut to 1–2 m billets | |
| Rate | Matches melt batch (10 kg per run) | Not 24 h continuous |
| EMS | Optional small induction stirrer | Later |

Vacuum semi-continuous for Ti: same mold principle inside the VAC_IND chamber; 0.40 kg/d does not justify a separate large caster.

## Other foundry rates (assumptions)

| Unit | Rate / duty |
|------|-------------|
| RF_HEAT | 5 kW, 100–400 kHz; preheat and sinter; <5 kg lots |
| ROLL | 10 kg/d plate/sheet; single stand |
| EXTRUDE | 5 kg/d rod/profile |
| DRAW | 3 kg/d wire to STOCK_OUT |
| SINTER | 0.5 kg/d powder-metal (Ti/Mo/Cr remnants) |
| INV_CAST | 2 kg/d finished castings |
| SHELL_BREAK → GLASS_MILL | ~0.5 kg shell waste per kg casting (assumption) |
| FLUX_PREP | <0.5 kg/d salt |

## Power (order of magnitude)

Peak if IND_MELT and VAC_IND overlap: ~40 kW. Average over the day far lower (batch). Fits existing rectifier/load aggregation; no new power train.

## Forming, shell, pots, shop

Sized in notes/FOUNDRY_MFG_SIZE.md. ROLL/EXTRUDE/DRAW/FORGE forces set. Shell schedule written. Pot rates confirmed. Shop machine list for foundry maintenance included.

Turns, tube size, and water flow: notes/FOUNDRY_COIL_MOLD.md.  
IND_MELT 14 turns / 8–12 L/min. VAC_IND 8 turns. CONT_CAST mold 25 L/min design.

Design assumptions only. Not measured. Coil turns, exact refractory spec, mold water flow, and withdrawal control are the next level of detail. Rates do not close deferred assays.

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
