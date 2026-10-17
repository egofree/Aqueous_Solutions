# LI_RECOVER method and digester placement

Document number: AQS-DUTY-LI-DIG  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev X. Not a PE stamp.  
Assays remain named missing. No composition invented.

## LI_RECOVER — method locked

Feed: polish-bank liquor after the metal cuts (edge POLISH_BANK → LI_RECOVER).

Method: precipitate lithium as Li₂CO₃ with recovered CO₂ (or Na₂CO₃ from BMED), then convert to LiOH with Ca(OH)₂ from P_CA if the grease kettle wants hydroxide.

\[
2\,\mathrm{Li^+} + \mathrm{CO_3^{2-}} \rightarrow \mathrm{Li_2CO_3}
\]
\[
\mathrm{Li_2CO_3} + \mathrm{Ca(OH)_2} \rightarrow 2\,\mathrm{LiOH} + \mathrm{CaCO_3}
\]

CaCO₃ returns to the leach or the Ca loop. LiOH to GREASE_LI.

Not used: solvent extraction (no external extractant), electrolytic Li metal (not required for grease).

Rate: ~0.02 kg/d Li to the kettle (assumption in notes/GREASE_LINES.md). Tenor is not measured.

## Digester sector placement

Sector DIGESTER is the former WET line plus F_RECOVER, LI_RECOVER, and P_CA. Units present: leach CSTR, float-sink, EW-1…9, polish bank, CRU, BMED acid/base, salt feed, F_RECOVER, LI_RECOVER, P_CA.

Biological digester remains `BLACK_DIGEST` in sector WTR. It is not moved. Volatile-solids split is still the missing measurement (plan line 1.2). No rate invented.

Glass digest remains `GLASS_DIGEST` in GLASS.

## Assays still named missing

- Dense-grit Ti/Fe (FLOAT_SINK → TI_CELL).  
- EW_9 Mo + Zn/Fe/Ni.  
- Digester volatile solids (BLACK_DIGEST).  
- Polish-liquor Li tenor.

See notes/ASSAY_TI_MO.md. Edges stay open on composition.
