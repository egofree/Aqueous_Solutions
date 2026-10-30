# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""U4a system tree (AQS-SYS-TREE-001) — structure, drift guard, queries,
and the sandbox toggle stack over it.

Drift guard: ``test_tree_file_passes_validation`` and the bijection tests
run against the live ``flow_graph/plant_flow_graph.json``.  A graph unit
added or removed without a matching ``flow_graph/system_tree.yaml`` edit
fails this module — loudly, not as a skip.

Run: python3 -m pytest flow_graph/param/test_system_tree.py -q
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]  # repo root
FG = ROOT / "flow_graph"
DT = ROOT / "design_tool"
for p in (str(ROOT), str(FG), str(DT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from flow_graph.system_tree import (  # noqa: E402
    SystemTree,
    TreeNode,
    TreeValidationError,
    load,
)

GRAPH_PATH = FG / "plant_flow_graph.json"


@pytest.fixture(scope="module")
def graph() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tree() -> SystemTree:
    return load()


def _disabled_units(model) -> set[str]:
    return {u.unit_id for u in model.units if not u.enabled}


# ----------------------------------------------------------------------
# structure + drift guard (U4a items 1, 2, 4)
# ----------------------------------------------------------------------


def test_tree_file_passes_validation(tree: SystemTree, graph: dict) -> None:
    """The YAML on disk loads and validates against the live graph."""
    report = tree.validate(graph)
    assert report["ok"] is True
    assert report["leaves"] == report["graph_units"] == 198
    assert report["roots"] == report["sector_count"] == 19


def test_bijection_leaf_set_equals_graph_unit_set_both_directions(
    tree: SystemTree, graph: dict
) -> None:
    leaves = {n.unit_id for n in tree.nodes if n.unit_id is not None}
    units = {n["unit_id"] for n in graph["nodes"]}
    assert leaves == units
    # each unit at exactly one leaf
    placed = [n.unit_id for n in tree.nodes if n.unit_id is not None]
    assert len(placed) == len(set(placed)) == 198


def test_drift_guard_graph_unit_removed_without_tree_update_fails(
    tree: SystemTree, graph: dict
) -> None:
    """Simulated drift: graph loses a unit (or grows one) -> validate raises."""
    g = copy.deepcopy(graph)
    g["nodes"] = [n for n in g["nodes"] if n["unit_id"] != "SINTER"]
    with pytest.raises(TreeValidationError, match="SINTER"):
        tree.validate(g)

    g2 = copy.deepcopy(graph)
    g2["nodes"].append({"unit_id": "NEW_SKID", "sector_id": "OIL", "presence": "present"})
    with pytest.raises(TreeValidationError, match="NEW_SKID"):
        tree.validate(g2)


def test_roots_are_exactly_the_mvs_sector_ids(tree: SystemTree, graph: dict) -> None:
    sector_ids = {s["sector_id"] for s in graph["mvs"]["sectors"]}
    roots = {n.id for n in tree.nodes if n.parent is None}
    assert roots == sector_ids
    assert len(roots) == 19


def test_sector_containment_with_recorded_exceptions(
    tree: SystemTree, graph: dict
) -> None:
    """Every unit sits under its graph sector's root (the EVAP_ACID_VS WET exception closed 2026-10-19
    is the pre-rename DIGESTER, recorded in sector_exceptions)."""
    sector_of = {n["unit_id"]: n.get("sector_id") for n in graph["nodes"]}
    for n in tree.nodes:
        if n.unit_id is None:
            continue
        root = n.id.split(".", 1)[0]
        sec = sector_of[n.unit_id]
        assert root == sec or tree.sector_exceptions.get(n.unit_id) == sec, n.id
    assert set(tree.sector_exceptions) == set()   # 2026-10-19: the WET exception closed (stamp fixed)


def test_cycle_free_and_parent_integrity() -> None:
    # unknown parent
    bad = SystemTree.from_nodes(
        [
            TreeNode(id="OIL"),
            TreeNode(id="OIL.t", parent="NOPE"),
        ]
    )
    with pytest.raises(TreeValidationError, match="unknown parent"):
        bad.validate()
    # two-node cycle
    cyc = SystemTree.from_nodes(
        [
            TreeNode(id="A", parent="A.x"),
            TreeNode(id="A.x", parent="A"),
        ]
    )
    with pytest.raises(TreeValidationError, match="cycle"):
        cyc.validate()
    # dotted-id derivation broken
    dot = SystemTree.from_nodes(
        [TreeNode(id="OIL"), TreeNode(id="WRONG.train", parent="OIL")]
    )
    with pytest.raises(TreeValidationError, match="does not derive"):
        dot.validate()
    # unit leaf carrying children
    parenty = SystemTree.from_nodes(
        [
            TreeNode(id="OIL"),
            TreeNode(id="OIL.t", parent="OIL"),
            TreeNode(id="OIL.t.HOPPER", parent="OIL.t", unit_id="HOPPER"),
            TreeNode(id="OIL.t.HOPPER.CHILD", parent="OIL.t.HOPPER"),
        ]
    )
    with pytest.raises(TreeValidationError, match="must not carry children"):
        parenty.validate()


def test_tree_shape(tree: SystemTree) -> None:
    stats = tree.stats()
    assert stats["by_level"] == {0: 19, 1: 31, 2: 107, 3: 112}
    assert stats["nodes"] == 269
    assert stats["trains"] == 31
    assert stats["subsystems"] == 22
    assert stats["leaves"] == 198
    # standby trains are descriptions, never hidden units
    assert sum(stats["units_per_root"].values()) == 198


# ----------------------------------------------------------------------
# queries (U4a item 2)
# ----------------------------------------------------------------------


def test_resolve_units(tree: SystemTree) -> None:
    assert tree.resolve_units("FOUNDRY.form-train") == {
        "ROLL", "EXTRUDE", "DRAW", "FORGE", "SINTER", "STOCK_OUT", "METAL_STORE",
    }
    assert tree.resolve_units("FOUNDRY.melt-and-cast-train") == {
        "IND_MELT", "VAC_IND", "RF_HEAT", "RES_HEAT", "COMB_HEAT", "E_HEAT", "FLUX_PREP",
        "CAST_LINE", "CONT_CAST", "VAC_CAST",
    }
    # subsystem resolution
    assert tree.resolve_units("FOUNDRY.melt-and-cast-train.cast") == {
        "CAST_LINE", "CONT_CAST", "VAC_CAST",
    }
    # leaf resolves to itself
    assert tree.resolve_units("ELEC.distribution-train.EXT_HALL") == {"EXT_HALL"}
    # root resolves to the whole sector (DIGESTER carries EVAP_ACID_VS from WET)
    digester = tree.resolve_units("DIGESTER")
    assert len(digester) == 26 and "EVAP_ACID_VS" in digester and "NAOH_PLANT" in digester
    # all 178 units resolve exactly once across roots
    roots = [n.id for n in tree.nodes if n.parent is None]
    resolved: list[str] = []
    for r in roots:
        resolved += sorted(tree.resolve_units(r))
    assert len(resolved) == len(set(resolved)) == 198
    with pytest.raises(KeyError):
        tree.resolve_units("FOUNDRY.nonexistent-train")


def test_aggregate(tree: SystemTree, graph: dict) -> None:
    # kW sums from continuous_kw
    gen = tree.aggregate(tree.resolve_units("ELEC.generation-train"), graph)
    assert gen["count"] == 3
    assert gen["kw_count"] == 3
    # PV 336.8304 (placeholders-to-real fixed point 2026-10-19/20; X-ELS-02 Rev C 2026-10-21 adds +0.1258:
    # the GEO source-loop circulator enters the AC load at its AQS-DUTY-076 draw (A-M-317, own SF feed on
    # the bus) and +0.0030: the AQS-MFG-010 rev C metering split's 4-dp quantisation (metal tools split out
    # of the MFG_SHOP aggregate) - loads promoted - MFG_SHOP 12 -> tool-list average, LEACH_CSTR_1 2 ->
    # 0.75 agitator, GLASS_DIGEST 1.5 -> 0.09, MEOH_SYNTH 0.5 -> 0.7388, GEO_HP 2 -> S44/COP 0.686 - took
    # the demand 260.96 -> 240.99 kW, the converged EXT_HALL 97.49 -> 90.57 kW and the bus with it)
    # PV 336.8304 -> 336.8121 (2026-10-24): the BACKUP_GEN exercise burns hydrogen first (S45), which needs less O2
    # than the C5-C10 cut, so CRYO_ASU and H2O_ELYZ draw less and the balancing PV average follows (A-M-383)
    # PV 336.8121 -> 336.8116 (2026-10-25): pumps and heads read the profile gravity 9.80665 m/s2 instead of 9.81 (Q-032)
    # PV 336.8116 -> 350.0995 (2026-10-29): the rectifier trim heaters at rated load in the bus demand (A-M-415) grow the
    # array and the extension hall that roofs it, whose HVAC load (EXT_HALL 68.28 -> 81.57 kW) the balancing PV average follows
    # PV 350.0995 -> 350.105 (2026-10-29): the atomiser argon receiver charged to 50 bar raises the atomiser energy (A-M-416).
    # PV 350.105 -> 350.0702 (2026-10-29): the CZ charge and pull interval from the wafer need lower the WAFER_FAB load (A-M-417).
    # PV 350.0702 -> 351.3442 (2026-10-29): on-site silicon reduction and refining for the CZ charge (A-M-419, owner decision t58u).
    # PV 353.877 -> 352.926 (2026-10-29): the acid cake kiln runs in campaigns (Q-034, A-M-425).
    # PV 352.926 -> 351.8354 (2026-10-29): the sodium hydroxide top-up runs on the chlor-alkali cells, with no kilns (Q-035, A-M-426).
    assert gen["kw_sum"] == pytest.approx(351.8354 + 4.0 + 0.0082)   # PV 351.8354 (on-site silicon A-M-419, sulfuric acid A-M-421, sodium hydroxide A-M-422, kiln campaigns A-M-425, chlor-alkali top-up A-M-426)
    assert gen["presence"] == "present"
    # worst presence: retired (S13_CLASS_TREAT) < placeholder (GEO_ORC) < present
    assert tree.aggregate(
        tree.resolve_units("DIGESTER.metals-leach-train.brine-loop"), graph
    )["presence"] == "retired"
    assert tree.aggregate(tree.resolve_units("GEO.ground-loop-train"), graph)[
        "presence"
    ] == "placeholder"
    assert tree.aggregate({"ROLL", "DRAW"}, graph)["presence"] == "present"
    # empty set and unknown ids
    empty = tree.aggregate(set(), graph)
    assert empty == {
        "count": 0, "kw_sum": 0.0, "kw_count": 0, "presence": None,
        "unknown_unit_ids": [],
    }
    assert tree.aggregate({"NOT_A_UNIT"}, graph)["unknown_unit_ids"] == ["NOT_A_UNIT"]


# ----------------------------------------------------------------------
# toggle stack: store.apply_overrides + solver stub (U4a items 3, 5)
# ----------------------------------------------------------------------


def _model():
    from aqs_design_tool.api.store import load_mvs_from_graph

    return load_mvs_from_graph()


def test_override_matrix_melt_and_cast_and_subsystem() -> None:
    from aqs_design_tool.api.store import apply_overrides
    from aqs_design_tool.models import SandboxOverrides

    base = _model()
    assert _disabled_units(base) == set()  # baseline: no unit flags off

    # train off -> flags exactly its 9 units
    m = apply_overrides(base, SandboxOverrides(system_enabled={"FOUNDRY.melt-and-cast-train": False}))
    assert _disabled_units(m) == {
        "IND_MELT", "VAC_IND", "RF_HEAT", "RES_HEAT", "COMB_HEAT", "E_HEAT", "FLUX_PREP",
        "CAST_LINE", "CONT_CAST", "VAC_CAST",
    }

    # subsystem off -> flags exactly its 3 units
    m = apply_overrides(base, SandboxOverrides(subsystem_enabled={"FOUNDRY.melt-and-cast-train.cast": False}))
    assert _disabled_units(m) == {"CAST_LINE", "CONT_CAST", "VAC_CAST"}

    # subsystem-on outranks train-off (most-specific wins, flag level)
    m = apply_overrides(
        base,
        SandboxOverrides(
            system_enabled={"FOUNDRY.melt-and-cast-train": False},
            subsystem_enabled={"FOUNDRY.melt-and-cast-train.cast": True},
        ),
    )
    assert _disabled_units(m) == {
        "IND_MELT", "VAC_IND", "RF_HEAT", "RES_HEAT", "COMB_HEAT", "E_HEAT", "FLUX_PREP",
    }

    # system off + unit on -> the single unit stays on (most-specific wins)
    m = apply_overrides(
        base,
        SandboxOverrides(
            system_enabled={"FOUNDRY.melt-and-cast-train": False},
            unit_enabled={"IND_MELT": True},
        ),
    )
    assert _disabled_units(m) == {
        "VAC_IND", "RF_HEAT", "RES_HEAT", "COMB_HEAT", "E_HEAT", "FLUX_PREP",
        "CAST_LINE", "CONT_CAST", "VAC_CAST",
    }

    # sector toggle stays row-level (P0 semantics: unit flags untouched;
    # the solver's effective set drops the sector via _enabled_units)
    m = apply_overrides(base, SandboxOverrides(sector_enabled={"FOUNDRY": False}))
    assert _disabled_units(m) == set()
    assert not next(s for s in m.sectors if s.sector_id == "FOUNDRY").enabled

    # unknown node id fails loudly instead of no-oping
    with pytest.raises(KeyError):
        apply_overrides(base, SandboxOverrides(system_enabled={"FOUNDRY.ghost-train": False}))


def test_solve_with_form_train_off_reports_its_units() -> None:
    """Battery: sandbox solve with system_enabled {'FOUNDRY.form-train': False}
    reports exactly the form-train units off."""
    from aqs_design_tool.api.store import apply_overrides, load_mvs_from_graph
    from aqs_design_tool.models import SandboxOverrides
    from aqs_design_tool.solver.stub import solve

    m = apply_overrides(
        load_mvs_from_graph(),
        SandboxOverrides(system_enabled={"FOUNDRY.form-train": False}),
    )
    expected = {"ROLL", "EXTRUDE", "DRAW", "FORGE", "SINTER", "STOCK_OUT", "METAL_STORE"}
    assert _disabled_units(m) == expected

    result = solve(m)
    # gaps name the disabled units as unreclaimed resources
    gapped = {
        g.detail.split("'")[1]
        for g in result.gaps
        if g.reason == "unreclaimed_resource" and "disabled" in (g.detail or "")
    }
    assert gapped == expected
    # streams touching the off train are open at that endpoint
    unit_reasons = {
        (u.stream_id, u.reason)
        for u in result.unclosed_streams
        if u.reason in ("upstream_unit_off", "downstream_unit_off")
    }
    assert unit_reasons
    assert result.mvs_equivalent is False
    assert result.status in {"partial", "infeasible"}


def test_enabled_units_helper_effective_set() -> None:
    from aqs_design_tool.solver.stub import _enabled_units

    m = _model()
    on = _enabled_units(m)
    # 178 (2026-10-19): EVAP_ACID_VS sector stamp fixed WET->DIGESTER, so the
    # sector-aware set now includes every unit (the 177 exception is closed).
    assert len(on) == 198
    assert "EVAP_ACID_VS" in on   # sector stamp fixed WET->DIGESTER 2026-10-19: now included
    # unit off leaves the set even with the sector on
    m2 = copy.deepcopy(m)
    for u in m2.units:
        if u.unit_id == "STOCK_OUT":
            u.enabled = False
    assert _enabled_units(m2) == on - {"STOCK_OUT"}
    # sector off drops the whole sector even with unit flags on
    m3 = copy.deepcopy(m)
    for s in m3.sectors:
        if s.sector_id == "GEO":
            s.enabled = False
    assert _enabled_units(m3) == on - load().resolve_units("GEO.ground-loop-train")
