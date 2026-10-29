# Rewrite batch 31: silicon for the CZ charge made on site

Date: 2026-10-29

Owner correction (t58u): the plant produces on site, and nothing comes in except waste or raw ore. The imported polysilicon route of batch 23 broke that rule. It is replaced by an on-site route that reduces quartz ore to metallurgical-grade silicon and refines that silicon to electronic grade. Both steps are sized from the CZ charge through the sizing code.

## What changed

- New module `flow_graph/param/si_refine.py`, called from `flow_graph/param/balance.py` after the fab silicon module.
  - SI_REDUCE reduces quartz ore (IA-QUARTZ-MU, raw ore through the dock) with pyrolysis char from OIL_PYRO (CHAR_TO_SI) in a small arc furnace. As on an open-top furnace, the carbon monoxide burns to carbon dioxide in the hood with room air, and the silica fume is caught in the baghouse and sent to the acid leach.
  - The new unit SI_REFINE refines the silicon on a closed chlorosilane loop. The hydrogen, hydrogen chloride and silicon tetrachloride of the reactor off-gas are recycled, so only chlorine is consumed. It is drawn as Cl2 from the AL_POT cell gas, so the chlorine export at the dock falls by the same amount.
  - The loop bleeds the impurity chlorides and the unrecovered silicon as silicon tetrachloride to the acid leach. There it hydrolyses to silica and hydrogen chloride, which joins the plant acid loop.
- Two refining technologies can be selected with the driver `si_refine_route`. TCS_SIEMENS (trichlorosilane on Siemens rods) is the default, and SILANE_FBR (silane in a fluidised bed) is the backup of a different technology. The new drivers carry assumption A-M-419.
- IA-SI-IMPORT is set to presence retired. The driver `si_resupply_d` of the import is removed, and METAL_STORE now holds one charge until the pull.
- `docs-authority/WAFER_FAB_EQUIPMENT.md` is now revision G, with a new Section 4.2. A-M-417 no longer describes an import.
- Supporting changes for the new unit:
  - an entry in the system tree;
  - a material selection in `flow_graph/param/materials3.py`, with the SI_REDUCE selection updated;
  - two instrument loops in `docs-authority/_instr_index.py`;
  - sizing coverage from the fab equipment list.
- In `docs-authority/_duty_basis.py`, an undefined name only reached when a new unit's duty sheet is authored now uses the node passed in.
- `docs-authority/_task_plan_gen.py`:
  - X-RTE-SI-BACKUP is moved to done.
  - X-RTE-CHAR_TO_SI drops out, because the route now carries flow.
  - Every dock import that is neither waste nor raw ore is generated as an open X-RTE-IMPORT task.

## Values

The charge stays at 0.2264 kg/d of electronic-grade silicon. On the Siemens route:

- Quartz: 0.7176 kg/d.
- Char: 0.2278 kg/d.
- Metallurgical silicon: 0.2717 kg/d.
- Chlorine make-up: 0.2137 kg/d.
- Chloride purge: 0.2590 kg/d.
- Hood carbon dioxide: 0.8346 kg/d, from 0.3034 kg/d of hood-air oxygen.
- Silica fume: 0.1424 kg/d.
- Average loads: SI_REDUCE 0.1472 kW and SI_REFINE 0.5659 kW.

The new loads carry through to the bus:

| Quantity | Before | After |
|---|---|---|
| PV continuous rating | 350.0702 kW | 351.3442 kW |
| Battery (ZNBR2) | 216.2517 kW | 217.5226 kW |
| Chlorine export IA-CL2-SHIP | 39.4192 kg/d | 39.2056 kg/d |
| Char to the shop, IA-CHAR (by difference) | 5.5 kg/d | 5.2722 kg/d |

The balance closes within its tolerance.

## Other imports against the rule

These dock imports are neither waste nor raw ore. They are now open tasks on the task list:

- IA-C-TI, IA-C-MO and IA-C-CR: carbon reductant, for which the plant char could serve.
- IA-H2O-MU: water make-up.
- IA-H2SO4-MU: sulfuric acid.
- IA-NAOH-MU: sodium hydroxide flake.
- IA-SOLV-MU: ethanol and acetone.
- IA-WAX-MU: pattern wax.

The ore concentrates, the mining-waste brines and chlorides, the foundry silica, the quartz and the intake air are allowed.
