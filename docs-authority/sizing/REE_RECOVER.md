# Sizing calculation - REE_RECOVER

Document number: AQS-SIZE-REE_RECOVER
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=rare-earth magnet recovery (batch campaign): demag > 320 C, HCl leach, Fe removal, RE oxalate precipitation, 900 C calcine, route=published short-product NdFeB recycling; HCl from the plant acid loop (BMED 30 wt% class), campaign={'ndfeb_kg': 1.618, 're_pct': 31.0, 'fe_pct': 67.8, 'b_pct': 1.2, 'hcl_30_kg': 6.0, 'h2o2_30_kg': 1.11, 'oxalic_kg': 0.46, 'naoh_kg': 2.36, 'wash_kg': 10.0, 'reo_kg': 0.585, 'fe_cake_kg': 2.1, 'brine_kg': 18.8, 'brine_nacl_pct': 16.6, 'h2_kg': 0.04, 'families': 'MF-01 14 x 2.8 g; MF-02 55 x 28.7 g installed; MF-03/22/23 reserved variants'}, campaign_basis=largest installed-family campaign MF-02 55 x 28.7 g = 1.578 kg; full-fleet campaign 1.618 kg (A-M-433); reserved families (MF-23 555.2 g/unit) ride the same batch capacity, closures=Fe(OH)3 cake to MET_MELT remnant; NaCl brine filtrate to the BMED feed class; REO product exported | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=rare-earth magnet recovery (batch campaign): demag > 320 C, HCl leach, Fe removal, RE oxalate precipitation, 900 C calcine, route=published short-product NdFeB recycling; HCl from the plant acid loop (BMED 30 wt% class), campaign={'ndfeb_kg': 1.618, 're_pct': 31.0, 'fe_pct': 67.8, 'b_pct': 1.2, 'hcl_30_kg': 6.0, 'h2o2_30_kg': 1.11, 'oxalic_kg': 0.46, 'naoh_kg': 2.36, 'wash_kg': 10.0, 'reo_kg': 0.585, 'fe_cake_kg': 2.1, 'brine_kg': 18.8, 'brine_nacl_pct': 16.6, 'h2_kg': 0.04, 'families': 'MF-01 14 x 2.8 g; MF-02 55 x 28.7 g installed; MF-03/22/23 reserved variants'}, campaign_basis=largest installed-family campaign MF-02 55 x 28.7 g = 1.578 kg; full-fleet campaign 1.618 kg (A-M-433); reserved families (MF-23 555.2 g/unit) ride the same batch capacity, closures=Fe(OH)3 cake to MET_MELT remnant; NaCl brine filtrate to the BMED feed class; REO product exported | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.000 m3; vessel D 0.00137391 x H 0.00206087 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
