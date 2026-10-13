# Feed assay

Document number: AQS-ASSAY-001
Revision: A
Date: 2026-10-13
Authority: graph Rev BH. Not a PE stamp.

The measurement is not in the repo. Nothing in this sheet is a composition. The edges keep the placeholder. No rate is changed. Nothing is resized.

## The three edges

| Edge | From | To | kg/d | Phase | What crosses |
| --- | --- | --- | --- | --- | --- |
| IA-FEED-01 | HOPPER | LEACH_CSTR_1 | 102.68 | L | Mineral feedstock. The rate note says returned scrap, not a dock intake. |
| S16 | MFG_SHOP | LEACH_CSTR_1 | 12.0 | S | Shop scrap. |
| S08 | LEACH_CSTR_1 | MFG_SHOP | 42.0021 | S | Metals and silicon leaving the leach. Not the feed. |

Each composition on the edge is water 0.90, HCl 0.05, Fe 0.02, other_metals 0.03. That is one placeholder, not three assays. S08 is a solids product wearing a liquor fraction.

IA-FEED-01 is phase L. The rate note calls it scrap. The phase is not changed here.

## What a measurement is

A mass fraction of the material that crosses that nozzle, as weighed. The sheet says wet or dry. Moisture is a fraction, not a conversion someone assumes later.

Analytes: moisture, Fe, Cu, Ni, Zn, Sn, Pb, Al, Au, Ag, plastic and paper, glass and silicate, and the balance. Al, Mg, Ca, Li, Ti, Si, and the rare earths are not electrowon. A number for them is still part of the assay. It is not a cell duty.

The measured column is empty.

| Edge | Basis | Measured fractions | Source |
| --- | --- | --- | --- |
| IA-FEED-01 | — | — | — |
| S16 | — | — | — |
| S08 | — | — | — |

## What is not the measurement

`ELECTRICAL.md` "Feedstock assays used" is a working average. Mixed WEEE, PCB-rich, MSW, landfill, and tailings are cases, not a sample. They are not copied onto the edge.

`assay_g_L` on S08 is Fe 20, Cu 8, Ni 3, Zn 4, Al 6, other 9. The same object is on 49 edges, including hydrogen, heat, and a conductor. It is not a feed assay. It is not used.

## When a number exists

It is written in the table above, then onto that edge's composition, in the same commit. The rate stays. The bore stays. The cell stays. A later line may resize from the measurement. This one does not.
