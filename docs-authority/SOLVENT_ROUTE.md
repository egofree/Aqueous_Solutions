# Solvent and reagent synthesis route

Document number: AQS-DUTY-026  
Revision: D  
Date: 2026-10-29  
Authority: the plant flow graph `flow_graph/plant_flow_graph.json`; the methanol equipment list AQS-EQP-MEOH-001; the fab reagent list AQS-EQP-FAB-RGN-001. This is a study, not a stamped design.

| Rev | Description | Date |
| --- | --- | --- |
| A to C | Reaction route for methanol, the ionic-liquid solvent and the fab reagents, with rates at graph revision BH. | 2026-10-12 |
| D | Rewritten against the present graph and the documentation style guide (AQS-DOC-002). The rates of revision C were from graph revision BH and no longer hold: the methanol train now runs at several times those rates. Rates are no longer stated here. The ionic-liquid chain is not on the present graph, and its status is now an owner question. | 2026-10-29 |

## Purpose and scope

The plant makes its own methanol, its own process solvent and the reagents of its wafer fab, from carbon dioxide, hydrogen, sugar, ammonia and the acid and base of the bipolar-membrane stack. This page gives the reaction route of each and says which parts are on the present plant graph. It gives no rates: the rates of the methanol train are in AQS-EQP-MEOH-001 and those of the fab reagents in AQS-EQP-FAB-RGN-001, both read from the graph.

## 1. Methanol

Methanol is made in MEOH_SYNTH from carbon dioxide (stream S73 from CRYO_CO2, with a top-up IA-HCO2-MEOH from the carbon dioxide header) and hydrogen (S74 from CRYO_H2). The reaction makes one water for each methanol; the water leaves to the condenser MEOH_COND (IA-MEOH-H2O) and the methanol to the tank MEOH_TANK (S75). Carbon dioxide is the limiting feed. The route to olefins (MEOH_TO_OLEFIN) carries no flow at present.

## 2. Ionic-liquid solvent

The process solvent is 1-butyl-3-methylimidazolium acetate. Its route is as follows:

1. Sugar is fermented: yeast at 30 °C gives ethanol, and a Clostridium culture at 35 °C gives butanol with acetone and ethanol.
2. Ethanol is oxidised to acetic acid by Acetobacter, and dehydrogenated over copper to acetaldehyde, which is oxidised to glyoxal.
3. A slip of methanol is oxidised to formaldehyde, and methanol with ammonia gives methylamine.
4. Glyoxal, formaldehyde, methylamine and ammonia condense to 1-methylimidazole and water. Ammonia is the limiting feed.
5. Butanol with hydrochloric acid from the bipolar-membrane stack gives 1-chlorobutane, which quaternises the imidazole at 70 °C to the chloride salt. An anion-exchange resin replaces the chloride with acetate.
6. The spent solvent leaves the pretreatment at the rate it enters, and the fermentation stillage returns to the digester.

Build models exist for these steps in `models/mfg/` (ABE, ACETOX, FORM, GLYOXAL, IMID and BUCL), but none of the units is on the present plant graph. The owner question in `REWRITE_TODO.md` asks whether the chain is to be put back on the graph or retired.

## 3. Fab reagents

The fab reagents are made on site by the reagent forks of AQS-EQP-FAB-RGN-001, which are units on the graph (WS_AMMONIA, WS_HF_ED, WS_KOH, WS_NITRIC, WS_PEROX, WS_PHOS, WS_SLURRY, WS_SOLV and WS_DOPE). Their uses are as follows:

- Ammonia: fertiliser, the first RCA clean, nitric acid and methylamine.
- Hydrofluoric acid: oxide etch and glass etch.
- Potassium hydroxide: anisotropic etch of silicon.
- Nitric acid: aluminium etch, pickling and nitrate fertiliser.
- Hydrogen peroxide: the RCA clean, bleach and sanitation.
- Phosphoric acid: fertiliser, aluminium polish and the dopant.
- Silica slurry: chemical-mechanical polishing.
- Ethanol and acetone: resist strip.
- Bipolar-membrane acid: the leach and chlorobutane. Bipolar-membrane base: the glass digest.
- Chlorate: leach oxidant, made at a graphite anode.
- Dopant: a phosphate slip; boron tribromide is not bought.
