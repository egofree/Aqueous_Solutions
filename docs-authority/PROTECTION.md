# Protection and coordination

Document number: AQS-ELEC-006
Revision: D
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-07; one-line AQS-ELEC-002 Rev C. Script `docs-authority/_protection.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-057 to A-M-059).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Inverter-limited fault, device types and settings, selectivity, DC channels, IEEE 80 check. | 2026-10-15 |
| D | X-ELS-11: five collection sections, 1000 A mains, 750 kVA step-up to 12.47 kV (AQS-ELEC-008). | 2026-10-15 |
| C | X-PAR-09 (D75) and X-PAR-08 (D77): 48 inverters (2880 kW), fault 6928 A, main 5000 A; grid export interconnection; ground grid over the grown building, IEEE 80 mesh and step voltages pass on bare soil. | 2026-10-15 |
| B | X-RSZ-02: three inverters (180 kW). Fault 433 A; main 300 A; GPR 494 V; bare-soil touch fails, crushed rock required everywhere on the grid. | 2026-10-15 |

## 1. Available fault current

All plant AC sources sit behind SOL_ARK_60K, 48 × 60 kW = 2880 kW (X-PAR-09 D75, X-PAR-08 D77; was 4 × 60 kW). Rated 3464 A at 480 V; fault contribution 2 × rated = 6928 A (study; AQS-ELEC-002 Rev B method). The utility connection for export (AQS-ELEC-002 Rev D item 5) adds the utility's available fault current, which is not known until the interconnection study (A-M-110); this study is redone with it. Export protection: UL 1741 SB inverters with IEEE 1547-2018 Category III voltage/frequency ride-through and trip settings, unintentional islanding cleared within 2 s; NEC 2023 705.30 overcurrent device and 705.20 lockable disconnect at the PCC; loss of utility (705.40) trips export and leaves the plant islanded on storage. The inverters are split into five 480 V collection sections (10, 10, 10, 9, 9 inverters), each with a 1000 A breaker (below the NEC 240.87 1200 A threshold) and a 750 kVA transformer to the 12.47 kV collection bus (AQS-ELEC-008, X-ELS-11). The plant bus hangs on CB-1.

## 2. Device rule

A thermal-magnetic breaker clears instantly only if its magnetic pickup is below the available fault. With 5× low-instantaneous trip units, a feeder qualifies when 5 × rating ≤ 0.8 × the available fault (5427 A at 480 V); larger feeders use electronic trip units with short-time pickup 1.5 × rating and 0.1 s delay:

| Bus | Load | Breaker A | Fault A | Device | Pickup |
| --- | --- | --- | --- | --- | --- |
| MCC-1 480 V | HABITATION | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| PP-1 208/120 V | AFTERBURNER | 15 | 833 | thermal-magnetic, instantaneous 5× | 75 A |
| PP-1 208/120 V | WS_PEROX | 15 | 833 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EXT_HALL | 175 | 6928 | thermal-magnetic, instantaneous 5× | 875 A |
| SOL_ARK 480 V | RECT_EW | 70 | 6928 | thermal-magnetic, instantaneous 5× | 350 A |
| SOL_ARK 480 V | BMED_ACID | 50 | 6928 | thermal-magnetic, instantaneous 5× | 250 A |
| SOL_ARK 480 V | RECTIFIER | 40 | 6928 | thermal-magnetic, instantaneous 5× | 200 A |
| SOL_ARK 480 V | CRYO_ASU | 40 | 6928 | thermal-magnetic, instantaneous 5× | 200 A |
| SOL_ARK 480 V | ZNBR2 | 110 | 6928 | thermal-magnetic, instantaneous 5× | 550 A |
| SOL_ARK 480 V | MFG_SHOP | 70 | 6928 | thermal-magnetic, instantaneous 5× | 350 A |
| SOL_ARK 480 V | GROW_BED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | GEO_HP | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | LEACH_CSTR_1 | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | WAFER_FAB | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | GLASS_DIGEST | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EVAP_ACID | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EVAP_BASE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | WET_BENCH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BOARD_MILL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | LIGNO_PRE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EXPANDER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HTC | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_H2 | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MEOH_SYNTH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BLOW_MOLD | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EMETH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ALK_SCRUBBER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | DIGESTER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | FRUIT_GUTTER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | VEG_BED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | H2_DRYER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ELECTRODE_COAT | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | SOLAR_PV_CELL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HNO3 | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CLARIFIER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BIOFILTER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | FISH_SUMP | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | NFT | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MISTER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | DUAL_ROOT | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | AZOLLA_BED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ETOH_STILL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BUOH_STILL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | PEANUT | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | SUNFLOWER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HAB_SLEEP | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HAB_GALLEY | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HAB_MED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | HAB_WASH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | SIC_FURNACE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ANIMAL_PEN | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_HE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_NE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_KR | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_XE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRYO_AR | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | YEAST | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ABE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | NFIX_BED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CLOVER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | SEED_BANK | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | STRUVITE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ASH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | IODIDE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MUSH_STRAW | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MUSH_BLOCK | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | AMF | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | NUTRIENT_DOSE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | LITHO_STUB | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | COMPOST | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ACETOX | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ALD | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | GLYOXAL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | FORM | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MEAM | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | IMID | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | QUAT | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | ACEX | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BUCL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BSFL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | DUCKWEED | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | WORMS | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BEES | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CHICKENS | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | GOATS | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | FISH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CRAYFISH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | AZOLLA | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | MUSHROOM | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | COMPOST_TOILET | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | COMPOST_MYC | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_TOMATO | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_CUCUMBER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_PEPPER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_LETTUCE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_SPINACH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_KALE | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_ALLIUM | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_BASIL | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | CROP_ROSEMARY | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | H2_PURIFIER | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | BMED_UPW_POLISH | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |
| SOL_ARK 480 V | EVAP_ACID_VS | 15 | 6928 | thermal-magnetic, instantaneous 5× | 75 A |

Section mains (CB-1 to CB-5): 1000 A frame, electronic trip, short-time 0.3 s, 65 kA interrupting; selective over the 0.1 s feeders by time. T-1 per NEC 450.3(B); 208 V faults limited by the T-1 5 % impedance (study).

## 3. DC

RECT-EW channels: rectifier current limit at 1.05 × channel rating as primary protection; DC fuses on both poles at 1.25 × channel rating (ungrounded DC, AQS-ELEC-005); insulation monitor alarms on first ground fault. 48 V rails per AQS-PWR-001 (SB350 100 A fuses). ZnBr₂ DC bus: fuse per string, rating from the X-ELS-05 storage sizing.

## 4. Earth fault, touch and step (closes the AQS-ELEC-005 hold)

Earth-fault current is bounded by the inverters, 6928 A (utility contribution held, A-M-110). Grid Rev B (`_grounding_study.py`): 196 x 174 m (building plus 10 m west yard), 12 m mesh of 2/0 AWG at 0.75 m, 74 rods of 3 m; Rg 0.128 Ω, GPR 887 V. GPR exceeds the tolerable touch, so IEEE 80-2013 mesh and step voltages (eqs 85-94) govern: Em 140 V, Es 60 V. Clearing time 0.5 s, 50 kg body, equations 32 and 29:

| Surface | Tolerable touch V | Tolerable step V | Em / Es V | Result |
| --- | --- | --- | --- | --- |
| bare soil | 176 | 213 | 140 / 60 | safe |
| crushed rock 0.1 m, 3000 ohm m | 677 | 2216 | 140 / 60 | safe |

Crushed rock 0.1 m, ≥ 3000 Ω·m, is kept on the outdoor yard (ZNBR2, MeOH train) as margin against the unknown utility contribution. Indoors, slab rebar is bonded to the grid as an equipotential mat (AQS-ELEC-005). Section mains 1000 A (AQS-ELEC-008); MV fuses 65 A per transformer.

## 5. Held

Inverter fault data from the vendor; device time-current curves of the chosen brand; re-run when X-ELS-05 changes the sources or the utility interconnection study gives the available fault current.

## Code basis (X-STD-01)

| Check | Governing clause |
| --- | --- |
| Overcurrent and coordination | NFPA 70-2023 Art. 240; 240.87 |
| Short-circuit method | IEC 60909-0:2016 (inverter-limited study) |
| Grounding, touch and step | IEEE 80-2013; NFPA 70-2023 Art. 250 |
| Arc flash | NFPA 70E-2024 130.5 |
