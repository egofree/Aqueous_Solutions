# 2026-11-08: the EW manufacturing models rebuilt at the element-envelope sizes

This record states what the round changed and why. It completes the work the 2026-11-06
Q-038 sizing record parked: "The EW manufacturing models are NOT rebuilt in this round:
their builders carry pre-existing defects (a non-piped cable row unknown to `lib/dn.py`,
nozzle stations tuned to the old tanks)". The nine EW tracker holds are cleared:
`python3 models/mfg/tracker.py --check EW_1 EW_2 EW_3 EW_4 EW_5 EW_6 EW_7 EW_8 EW_9`
reports no misfit, and the full tracker stands at seven named holds (BEE_HIVE, CRYO_ASU,
GROW_BED, GW_INTAKE, HDR_H2, HDR_N2, HDR_O2 - the set it named before the EW rebuilds,
minus the nine EW entries).

## What the rebuild found and fixed

The interrupted 2026-11-06 rebuild round had converted the nine builders to the shared
graph-node reader (`models/mfg/lib/graph_node.py`) and rebuilt six cells, but left three
states of the nozzle placement logic in the tree: a clamp-up draft in EW_1, EW_4 and EW_9
that refused to build above the cover-gas zone; a re-basing version in EW_2 that dropped
its DN50 launder-discharge row outright (the built check carried 8 of 9 schedule rows),
gave the re-faced rows a bore but no connection hardware, and could stack bores on top
of each other on the discharge-end wall; and drawing scripts whose captions hard-coded
the old tank lengths and electrode counts. This round:

- One algorithm in all nine builders. Side-face connections re-base into the cover gas
  zone band (z 690-748) in OD-aware slots; a wall that runs out of slots re-faces its
  rest to the +X discharge-end wall with full hardware, each row in a radius-aware y/z
  slot. The overflow discharge sits at the 680 mm fill line (the launder datum) on its
  issued face at the discharge end; the drain and the vent keep their issued bottom/top
  datums; the cable power-terminal row is carried verbatim, never drawn; EW_1's
  rectifier row is drawn as the conductor gland (duty section 4). The issued schedule
  datums stay in the CSVs; the drawn stations are the registered layout choice, named
  per tag in `check.nozzles_drawn` and WORK_ORDER W12.
- EW_1's materials completed at the duty section 3 ruling (tank and racks CPVC, X-MAT-09):
  the copied draft mapped the racks and nozzles to PVC-U; the cathode edge strips stay
  PVC-U. The shared `lib/graph_node.py` gains the graph reference its callers read
  edges from (`CHAN_KW`).
- A schedule-coverage assert in every builder: drawn plus carried must equal the
  schedule, so a dropped row fails the build instead of waiting for an audit.
- The drawing scripts read counts, sizes and bus packs from the check report. The nine
  drawing sets regenerated from the new geometry - the stamped sheets still showed the
  old tank lengths and electrode banks - and the DRAWING_REGISTER rows re-hashed
  (AQS-DWG-002).
- The WORK_ORDERs revised to the rebuilt state: graph Rev AD, the graph-node source
  statement, the sized envelopes and electrode counts, the regenerated fastener counts,
  the re-basing hold, and the retired bus holds - the AQS-BUS-001 Rev D packs are sized
  at the element-envelope current, so the "carried verbatim at the old current" holds
  are gone.

## State at the commit

Envelopes and stations come from the sizing stamp on each graph node
(`tracker params.json`); every build bounding box is inside its envelope and every
scheduled row is drawn or carried in all nine `check.json` files. Checks at the commit:
`pytest flow_graph/` 237 passed, tracker 200 units with the seven named holds above,
`scripts/check_all.sh --full` green.
