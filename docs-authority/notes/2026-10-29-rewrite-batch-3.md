# Rewrite batch 3: fuel cell, hydrogen embrittlement review and weld map

Date: 2026-10-29

AQS-FC-001 (`FUEL_CELL.md`), AQS-REV-H2-001 (`H2_EMBRITTLEMENT_REVIEW.md`) and AQS-WLD-001 (`WELD_MAP.md`) were rewritten by hand against graph Rev AC and AQS-STD-002.

The hydrogen review had fallen behind the design. It did not include the electrolyser or the hydrogen compressor, it described the electrowinning cathodes as 316L although AQS-STD-002 section 9 changed them to titanium, it described the hydrogen store as cryogenic although the graph carries a compressed-gas tube bank, and it stated that the hydrogen edges carry pressure, temperature and purity, which they do not.

The weld map had its joint tags corrupted by a text replacement in the bulk closure of 2026-10-25 (commit 721465e3). No other page carries that corruption.

PROTECTION (AQS-ELEC-006) was found stale and stays pending with the reason recorded in `REWRITE_TODO.md`. Duty sheets for units no longer on the graph are listed as a question for the owner.
