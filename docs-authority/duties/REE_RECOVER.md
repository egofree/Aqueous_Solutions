# REE_RECOVER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.3000 kW. In: none. Out: none.

2. Size.
- Envelope 800×600×1400 mm, 0.672 m³.
- Envelope: bench campaign skid: demag oven + 10 L leach reactor + filter + muffle on one frame (fume-hood class, MET_SYN row); A-M-433 X-END-02 rare-earth route (Q-013): REE_RECOVER batch campaign.
- Sizing study pending (study): vessel 10 L glass-lined leach reactor (55 C jacket, stirrer, H2 vent to the acid-scrubber header); demag oven 350 C 5 L; vacuum filter PP-H; calcining muffle 900 C 2 L; basis largest installed-family campaign MF-02 55 x 28.7 g = 1.578 kg; full-fleet campaign 1.618 kg (A-M-433); reserved families (MF-23 555.2 g/unit) ride the same batch capacity.

3. Material. glass-lined reactor, PTFE transfer, PP-H filter wetted (HCl service per AQS-STD-002 thermoplastic rules; no metal wetted part below 60 C); 316L muffle shell (dry oxide, 900 C). Basis: X-MAT-22 section-3 selection for the REE_RECOVER campaign bench: HCl leach at < 60 C (thermoplastic/glass class per AQS-STD-002 M-rules); the 900 C muffle is dry oxide service (316L shell). The campaign chemistry is dilute 30 wt% HCl at 55 C with PTFE/PP-H wetted faces (A-M-433). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Hastelloy C-276 wetted parts if the campaign moves above 60 C (AQS-STD-002 metal-acid rule); not required at the bench campaign scale. X-MAT-22 issued selection for the campaign bench; thermoplastic/glass wetted class (X-MAT-22)

4. Nozzles. No piped process connection on the graph yet (no kg/d rated edge); `nozzles/REE_RECOVER.csv` carries only the drain and vent utilities. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet. Manufacturing model `models/mfg/REE_RECOVER/ree_recover.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
