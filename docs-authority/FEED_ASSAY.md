# Feed assay

Document number: AQS-ASSAY-001
Revision: B
Date: 2026-10-14
Authority: graph Rev BH. Not a PE stamp. Not a weighed sample.

This is the design-basis assay. The fractions are already in `ELECTRICAL.md` and `EDGE_RATING_DUTY.md`. They are not a laboratory result. No rate changes. Nothing is resized.

## IA-FEED-01

HOPPER to LEACH_CSTR_1, 102.68 kg/d, phase L. The rate stays. The 150 kg/d dock feed is not restored.

Source: `ELECTRICAL.md`, mixed WEEE, wet, as published. `EDGE_RATING_DUTY.md` calls that table the design-day feed. The published percentages sum to 0.85025. The remainder is `unassigned`. It is the 15 % the duty book already calls unassigned. It is not identified here.

| Fraction | Value |
| --- | --- |
| moisture | 0.05 |
| Fe | 0.25 |
| Cu | 0.07 |
| Al | 0.05 |
| other_plateable | 0.03 |
| Au | 0.00005 |
| Ag | 0.0002 |
| plastic_paper | 0.22 |
| glass_silicate | 0.18 |
| unassigned | 0.14975 |

`other_plateable` is the published 3 % blend of Ni, Zn, Sn, and Pb. It is not split. Al is in the assay and is not electrowon.

The edge is named mineral feedstock and returned scrap. The assay is the whole wet WEEE average, which includes plastic and glass. That is a mismatch. No hopper split was invented to remove it.

## S08

LEACH_CSTR_1 to MFG_SHOP, 42.0021 kg/d, phase S. The rate stays.

Source: `EDGE_RATING_DUTY.md` cathode deposits booked on S08. The nine deposits sum to 42.0000 kg/d. The edge is 42.0021 kg/d. The difference is left on the rate.

| Metal | kg/d | Fraction |
| --- | --- | --- |
| Au | 0.0063 | 0.00015000 |
| Ag | 0.0251 | 0.00059762 |
| Cu | 8.7841 | 0.20914524 |
| Pb | 0.7111 | 0.01693095 |
| Sn | 0.7111 | 0.01693095 |
| Ni | 0.7111 | 0.01693095 |
| Fe | 29.6290 | 0.70545239 |
| Cd | 0.7111 | 0.01693095 |
| Zn | 0.7111 | 0.01693095 |

The carries line says metals and silicon. Silicon is not in this split. None was added. `assay_g_L` on this edge is the 50 g/L liquor stencil. It was not used.

## S16

MFG_SHOP to LEACH_CSTR_1, 12.0 kg/d, phase S. The rate stays.

`EDGE_RATING_DUTY.md` says the composition is unstated and S08 governs. The fractions are the S08 fractions. The rate note calls the stream a polymer and metal band. No polymer fraction was added.

## What this is not

Not a weighed sample. Not a reason to change a bore, a cell, or a holdup. `assay_g_L` is not this assay. A later weighed sample replaces these fractions. It does not resize in the same commit.
