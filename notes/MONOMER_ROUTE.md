# Monomer route selection — VDF and TFE

Document number: AQS-SEL-FP  
Revision: A  
Date: 2026-10-16  
Authority: notes/FLUOROPOLYMER_DUTY.md, graph Rev K. Not a PE stamp.  
Rates not set.

## Available feeds

- Aqueous HF from HF_GEN (mandatory, recovered fluoride).  
- Methanol from MEOH_SYNTH (existing).  
- Chlorine from CRU (existing closed loop).  
- Pyro char and CO exist but are not required for the selected route.

## Selected route (both monomers)

Methanol → chloromethanes → hydrofluorination → monomer.  
Closes on methanol, Cl₂, and HF. No external carbon or halogen.

### VDF (CH₂=CF₂)

1. Methanol + HCl → methyl chloride (or direct chlorination path to CH₃Cl).  
2. Further chlorination to 1,1,1-trichloroethane or equivalent chlorocarbon.  
3. Hydrofluorination with HF to the corresponding HCFC.  
4. Dehydrochlorination / pyrolysis to VDF.  
5. Purification and feed to POLY_F.

### TFE (CF₂=CF₂)

1. Methanol + Cl₂ → chloroform (CHCl₃).  
2. CHCl₃ + 2 HF → CHClF₂ (R-22) + 2 HCl.  
3. Pyrolysis of CHClF₂ at ~600–800 °C → TFE + HCl.  
4. Quench, purification, feed to POLY_F.  
5. HCl returns to the chloromethane step or to BMED.

Both routes return HCl to the existing acid loop. Net halogen consumption is zero once HF and Cl₂ are regenerated.

## Rejected alternatives

- Acetylene + HF (requires a dedicated carbide or plasma acetylene train not present).  
- Direct electrochemical fluorination (high energy, selectivity poor at this scale, new equipment class).  
- External chlorocarbon feed (violates binding requirement).

## Status

Route locked for both monomers. Vessel envelopes in notes/VESSEL_ENVELOPES.md. Rates remain unset.
