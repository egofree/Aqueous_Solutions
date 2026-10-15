"""AQS-BLD-010 rev B section: CAD solid clash of the new building elements (FR_ rooms, stairs, elevators, apron). Reads
docs-authority/inventory/CAD_CLASH.json written by `freecadcmd models/freecad/clash_check.py` after `freecadcmd build_plant.py`."""
import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
d = json.load(open('docs-authority/inventory/CAD_CLASH.json')); H = d['clashes']
K = collections.defaultdict(list)
for h in H: K[h['a']].append(h)
cause = {'FR_CRYO_ASU': 'CRYO room units sit < 600 mm apart; a 1 h room cannot fit. Action: split the CRYO room with a 1 h partition, H2 side (CRYO_H2, H2_PURIFIER, H2O_ELYZ) from O2 and ignition side (CRYO_O2, CRYO_ASU, CRYO_CO2, FLUE_KO), in models/freecad/cryo.py.',
         'FR_CRYO_CO2': 'as FR_CRYO_ASU', 'FR_FLUE_KO': 'as FR_CRYO_ASU',
         'STAIR_S2': 'pre-existing: GROW_BED (L1) and MET_SCRUB (L0) run into the SE stair. Action: shorten GROW_BED by 3 m or move STAIR_S2.', 'STAIR_CLR_L1_S2': 'as STAIR_S2',
         'FR_BACKUP_GEN': 'room wall at 300 mm minimum touches generator ancillaries (buffer, exhaust stub, clearance zones). Action: group the GEN ancillaries inside the room.',
         'FR_AFTERBURNER': 'room wall touches the oil cut tanks and NaOH digest at 300 mm. Action: move the cut tanks 1 m east.', 'FR_MET_MELT': 'touches WIRE_DRAW. Action: 1 m aisle.',
         'ELEV_SVC': 'BMED_UPW_POLISH (L-1) reaches into the core. Action: move it 0.7 m out of the core.', 'ELEV_DOCK': 'YARD_PAD reaches under the dock. Action: trim the pad to the wall line.',
         'STAIR_SERVICE': 'as ELEV_DOCK', 'DOCK_APRON_N': 'door stub sits on the apron edge; cosmetic.'}
md = ['## CAD solid clash, new building elements (rev B, 2026-10-16)', '', f"Built `models/freecad/plant.FCStd` with the AQS-SAF-007 rated rooms, the widened and extended stairs, the 34 m apron and the re-packed core; `clash_check.py` tested {d['new']} new elements against {d['others']} solids: {len(H)} contacts above 0.001 m3 in {len(K)} elements.", '',
      'Fixed in this build: core re-packed (CORE 8 x 6 m; STAIR_P, ELEV_SVC, STAIR_MAINT and six shafts no longer overlap), CATCH_TANK cut around every stair, elevator and shaft with a dry HYDRO_SET pump room (was full-plate through them), ELEV_DOCK moved to the dock west end, dock door to DOCK_DOOR_H, `stamp_materials.py` path to `tables/materials.csv` (the build had been failing at that step).', '',
      '| Element | Contacts | m3 | Cause and action |', '|---|---|---|---|'] + [f"| {a} | {', '.join(h['b'] for h in v[:6])}{' …' if len(v) > 6 else ''} | {sum(h['m3'] for h in v):.2f} | {cause.get(a, '-')} |" for a, v in K.items()]
s = open('docs-authority/GA_CHECK.md').read().split('## CAD solid clash')[0].rstrip()
open('docs-authority/GA_CHECK.md', 'w').write(s + '\n\n' + '\n'.join(md) + '\n'); print(len(H))
