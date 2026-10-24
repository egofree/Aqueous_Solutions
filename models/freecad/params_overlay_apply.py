#!/usr/bin/env python3
"""Safe pack params.json → params_overlay.py applicator.

Copies gold ``params.py`` to an explicit fork path and applies **allow-listed**
overlay keys only. Never writes gold ``params.py``. Null / missing overlay
values keep gold. Unknown paths fail closed (non-zero exit).

Allow-list (AQS-PLAN-3D-001 §5.3 / §7) — applied to params:

    scale_m                      → SCALE_M
    electrical.pv_count          → PV_COUNT
    electrical.znbr_count        → ZNBR_COUNT
    electrical.pv_module_kw      → PV_MODULE_KW
    electrical.znbr_module_kw    → ZNBR_MODULE_KW
    electrical.need_kw.value     → ELEC_NEED_KW_BASE   (D10, 2026-10-18)
    electrical.target_kw.value   → ELEC_TARGET_KW      (D10, 2026-10-18)
    electrical.rect_count        → RECT_COUNT          (D10, 2026-10-18)
    module_bays_x_override       → MODULE_BAYS_X_OVERRIDE  (optional later)
    module_bays_y_override       → MODULE_BAYS_Y_OVERRIDE  (optional later)

D10 precedence rule (which values win): the GRAPH wins, unconditionally.
``electrical`` in the pack params.json is the graph's ``mvs.electrical``
block, written by ``flow_graph/param/write_graph.py power()`` from the live
power chain (A-M-234 replaced_by / A-M-258: need, target = 2.5 x need, PV
module x count, ZNBR2 over the hybrid-inverter block). When those keys are
present in the overlay they override the CAD seeds in the fork, always —
need/target/rect as end-overrides (they are electrical-truth values, not
scale formulas), module kW in place, counts as end-overrides as before. The
gold seeds (ELEC_NEED_KW_BASE 50, ELEC_OVERPROD 1.4, PV_MODULE_KW 70,
ZNBR_MODULE_KW 60, ZNBR_MODULE_KWH 120, RECT_COUNT = cassette count) remain
OFFLINE FALLBACKS only, used when a pack params.json is absent or a key is
null (S4 keep-gold). With target_kw pushed, ELEC_OVERPROD is inert in the
fork; it is deliberately NOT in the apply map.

Pack metadata keys (present in export params.json) are **recognized but not
applied** as CAD drivers: note, topology_authority, site, scale_rules, and
electrical bus_nodes / storage_options / need_kw.unit/.status/.note /
target_kw.unit/.status/.note / notes. Vessel mm (CSTR_L, …) and unknown
paths → refuse.

Usage::

    python3 params_overlay_apply.py --params /path/to/params.json
    python3 params_overlay_apply.py --params pack/params.json -o params_overlay.py
    python3 params_overlay_apply.py --self-test

Licence: CERN-OHL-S-2.0. See the unpublished planning note GRAPH_TO_3D_IMPLEMENTATION_PLAN WP-D2.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GOLD_PARAMS = HERE / "params.py"
DEFAULT_OUT = HERE / "params_overlay.py"

# Overlay dotted path → gold params.py binding name (apply targets only).
# D10: need/target/rect added so the graph's mvs.electrical (via pack
# params.json) pushes over the CAD seeds unconditionally; graph wins.
APPLY_MAP: dict[str, str] = {
    "scale_m": "SCALE_M",
    "electrical.pv_count": "PV_COUNT",
    "electrical.znbr_count": "ZNBR_COUNT",
    "electrical.pv_module_kw": "PV_MODULE_KW",
    "electrical.znbr_module_kw": "ZNBR_MODULE_KW",
    "electrical.need_kw.value": "ELEC_NEED_KW_BASE",
    "electrical.target_kw.value": "ELEC_TARGET_KW",
    "electrical.rect_count": "RECT_COUNT",
    "module_bays_x_override": "MODULE_BAYS_X_OVERRIDE",
    "module_bays_y_override": "MODULE_BAYS_Y_OVERRIDE",
}

# Pack schema keys that may appear but must not drive FreeCAD dims.
# electrical.need_kw / electrical.target_kw stay as recognized dict
# containers; their .value leaves are applied (APPLY_MAP) and their
# .unit/.status/.note leaves remain meta.
RECOGNIZED_META: frozenset[str] = frozenset(
    {
        "note",
        "topology_authority",
        "site",
        "site.site_id",
        "site.site_lat_deg",
        "site.crew",
        "site.jurisdiction_theme",
        "scale_rules",
        "scale_rules.tanks",
        "scale_rules.mfg_cryo",
        "scale_rules.pv_znbr2",
        "scale_rules.dock",
        "electrical",
        "electrical.bus_nodes",
        "electrical.storage_options",
        "electrical.need_kw",
        "electrical.need_kw.unit",
        "electrical.need_kw.status",
        "electrical.need_kw.note",
        "electrical.target_kw",
        "electrical.target_kw.unit",
        "electrical.target_kw.status",
        "electrical.target_kw.note",
        "electrical.notes",
    }
)

# Simple assignment names patched in-place (before derived calcs).
_INPLACE_ASSIGN = frozenset(
    {
        "SCALE_M",
        "MODULE_BAYS_X_OVERRIDE",
        "MODULE_BAYS_Y_OVERRIDE",
        "PV_MODULE_KW",
        "ZNBR_MODULE_KW",
        "ELEC_NEED_KW_BASE",
    }
)

# Counts and formula-derived electrical-truth values are forced at end of
# fork (graph wins over any seed formula; D10).
_END_OVERRIDE = frozenset({"PV_COUNT", "ZNBR_COUNT", "ELEC_TARGET_KW", "RECT_COUNT"})

_BANNER = (
    "# =============================================================================\n"
    "# GENERATED FORK — WP-D2 params overlay (CERN-OHL-S-2.0)\n"
    "# Source: gold params.py copy. Do NOT treat this file as gold.\n"
    "# Regenerated by params_overlay_apply.py; gold params.py is never written.\n"
    "# =============================================================================\n"
)


def allow_list_report() -> dict[str, Any]:
    """Public allow-list summary for bridge / recipe / docs."""
    return {
        "apply": dict(sorted(APPLY_MAP.items())),
        "recognized_meta_prefixes": sorted(
            {
                p.split(".")[0] if "." in p else p
                for p in RECOGNIZED_META
            }
        ),
        "refuse": (
            "unknown overlay paths; vessel/detail millimetre constants; "
            "null values are kept as gold (not invented)"
        ),
        "gold_params": "params.py",
        "fork_params": "params_overlay.py",
        "overlay_rewrites_params_py": False,
    }


def _is_null(v: Any) -> bool:
    return v is None


def _collect_paths(obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten JSON to dotted paths. Dicts expand; lists are leaves."""
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        if prefix:
            out[prefix] = obj  # parent path present
        for k, v in obj.items():
            if not isinstance(k, str) or not k:
                raise ValueError(f"non-string overlay key under {prefix!r}")
            path = f"{prefix}.{k}" if prefix else k
            out.update(_collect_paths(v, path))
    else:
        if not prefix:
            raise ValueError("overlay root must be a JSON object")
        out[prefix] = obj
    return out


def validate_overlay(overlay: dict) -> list[str]:
    """Return list of unknown / refused paths. Empty → OK."""
    if not isinstance(overlay, dict):
        return ["<root>: not an object"]
    flat = _collect_paths(overlay)
    unknown: list[str] = []
    for path in flat:
        if path in APPLY_MAP:
            continue
        if path in RECOGNIZED_META:
            continue
        # Parent of an allow-listed leaf is OK if it's a dict container
        # (e.g. electrical when children are validated individually).
        # electrical is in RECOGNIZED_META; scale_m is APPLY_MAP.
        unknown.append(path)
    return sorted(unknown)


def extract_applies(overlay: dict) -> dict[str, Any]:
    """Map params.py names → non-null overlay values to apply."""
    flat = _collect_paths(overlay)
    applies: dict[str, Any] = {}
    for path, pname in APPLY_MAP.items():
        if path not in flat:
            continue
        val = flat[path]
        if _is_null(val):
            continue  # S4: keep gold
        applies[pname] = val
    return applies


def _format_py_lit(val: Any) -> str:
    if isinstance(val, bool):
        return "True" if val else "False"
    if val is None:
        return "None"
    if isinstance(val, int) and not isinstance(val, bool):
        return str(val)
    if isinstance(val, float):
        # Stable short form; keep .0 for floats that are integral.
        if val == int(val) and abs(val) < 1e15:
            return f"{int(val)}.0" if abs(val - int(val)) < 1e-12 else repr(val)
        return repr(val)
    if isinstance(val, str):
        return json.dumps(val)
    raise TypeError(f"cannot format overlay value as Python literal: {val!r}")


def _patch_inplace_assign(text: str, name: str, lit: str) -> str:
    """Replace first top-level ``NAME = …`` assignment (single line)."""
    # Match start-of-line NAME = ... through end of line (keep trailing comment).
    pat = re.compile(
        rf"^({re.escape(name)}\s*=\s*)([^#\n]+)(.*)$",
        re.MULTILINE,
    )
    m = pat.search(text)
    if not m:
        raise RuntimeError(f"gold params.py missing assignment for {name}")
    # Preserve inline comment if present.
    comment = m.group(3)
    repl = f"{name} = {lit}{comment}"
    new_text, n = pat.subn(repl, text, count=1)
    if n != 1:
        raise RuntimeError(f"failed unique inplace patch for {name}")
    return new_text


def write_overlay_fork(
    overlay: dict,
    *,
    gold_path: Path = GOLD_PARAMS,
    out_path: Path = DEFAULT_OUT,
) -> dict[str, Any]:
    """Validate overlay, copy gold → out_path, apply allow-listed keys.

    Returns a result dict with applied_keys, out_path, etc.
    Raises ValueError on unknown keys / bad types; never touches gold_path
    for writing.
    """
    gold_path = Path(gold_path).resolve()
    out_path = Path(out_path).resolve()
    if out_path.resolve() == gold_path.resolve():
        raise ValueError("refusing to write overlay onto gold params.py")
    if gold_path.name != "params.py" and "params.py" not in str(gold_path):
        # Soft check: still allow alternate gold for tests.
        pass
    if not gold_path.is_file():
        raise FileNotFoundError(f"gold params missing: {gold_path}")

    unknown = validate_overlay(overlay)
    if unknown:
        raise ValueError(
            "unknown / refused overlay path(s): " + ", ".join(unknown)
        )

    # Type checks for apply values (before write).
    applies = extract_applies(overlay)
    for pname, val in applies.items():
        if pname == "SCALE_M":
            fv = float(val)
            if fv <= 0:
                raise ValueError(f"scale_m must be > 0, got {val!r}")
            applies[pname] = fv
        elif pname in ("PV_MODULE_KW", "ZNBR_MODULE_KW", "ELEC_NEED_KW_BASE", "ELEC_TARGET_KW"):
            fv = float(val)
            if fv <= 0:
                raise ValueError(f"{pname} must be > 0, got {val!r}")
            applies[pname] = fv
        elif pname in ("PV_COUNT", "ZNBR_COUNT", "RECT_COUNT"):
            iv = int(val)
            if iv < 1:
                raise ValueError(f"{pname} must be >= 1, got {val!r}")
            applies[pname] = iv
        elif pname in ("MODULE_BAYS_X_OVERRIDE", "MODULE_BAYS_Y_OVERRIDE"):
            if val is None:
                continue
            iv = int(val)
            if iv < 1:
                raise ValueError(f"{pname} must be >= 1, got {val!r}")
            applies[pname] = iv
        else:
            raise ValueError(f"internal: unhandled apply target {pname}")

    gold_text = gold_path.read_text(encoding="utf-8")
    # Guard: never proceed if caller somehow pointed gold at overlay.
    if out_path.exists() and out_path.samefile(gold_path):
        raise ValueError("refusing to overwrite gold params.py")

    text = gold_text
    if not text.startswith("# GENERATED FORK"):
        text = _BANNER + text

    inplace_applied: list[str] = []
    end_applied: list[str] = []
    for pname, val in sorted(applies.items()):
        lit = _format_py_lit(val)
        if pname in _INPLACE_ASSIGN:
            text = _patch_inplace_assign(text, pname, lit)
            inplace_applied.append(pname)
        elif pname in _END_OVERRIDE:
            end_applied.append(pname)
        else:
            raise ValueError(f"internal: no patch strategy for {pname}")

    if end_applied:
        lines = [
            "",
            "# --- WP-D2 overlay end-overrides (counts after formula block) ---",
            "# Applied from pack params.json allow-list; gold params.py untouched.",
        ]
        for pname in end_applied:
            lines.append(f"{pname} = {_format_py_lit(applies[pname])}")
        lines.append("")
        text = text.rstrip() + "\n" + "\n".join(lines) + "\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Write only the fork.
    if out_path.resolve() == gold_path.resolve():
        raise ValueError("refusing to write overlay onto gold params.py")
    out_path.write_text(text, encoding="utf-8")

    # Inverse path map for recipe documentation.
    inv = {v: k for k, v in APPLY_MAP.items()}
    applied_keys = {
        inv[p]: applies[p] for p in (inplace_applied + end_applied) if p in applies
    }

    return {
        "ok": True,
        "gold_path": str(gold_path),
        "out_path": str(out_path),
        "applied_keys": applied_keys,
        "applied_params_names": inplace_applied + end_applied,
        "skipped_null_or_absent": sorted(
            k for k, v in APPLY_MAP.items() if k not in applied_keys
        ),
        "overlay_rewrites_params_py": False,
    }


def load_module(path: Path, mod_name: str = "_aqs_params_probe"):
    """Load a params*.py file as a fresh module (no sys.modules clash)."""
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def roundtrip_equal_gold(
    overlay: dict,
    *,
    gold_path: Path = GOLD_PARAMS,
    out_path: Path | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Apply overlay to a temp/fork and compare effective scale/electrical.

    Pass when SCALE_M, bay counts, PV/ZNBR module kW and counts match gold.
    """
    import tempfile

    gold = load_module(gold_path, "_aqs_gold_params")
    if out_path is None:
        tmp = tempfile.NamedTemporaryFile(
            prefix="params_overlay_",
            suffix=".py",
            dir=str(HERE),
            delete=False,
        )
        out_path = Path(tmp.name)
        tmp.close()
    try:
        result = write_overlay_fork(
            overlay, gold_path=gold_path, out_path=out_path
        )
        fork = load_module(out_path, "_aqs_overlay_params")
        checks = {
            "SCALE_M": (gold.SCALE_M, fork.SCALE_M),
            "MODULE_BAYS_X": (gold.MODULE_BAYS_X, fork.MODULE_BAYS_X),
            "MODULE_BAYS_Y": (gold.MODULE_BAYS_Y, fork.MODULE_BAYS_Y),
            "PV_MODULE_KW": (gold.PV_MODULE_KW, fork.PV_MODULE_KW),
            "ZNBR_MODULE_KW": (gold.ZNBR_MODULE_KW, fork.ZNBR_MODULE_KW),
            "PV_COUNT": (gold.PV_COUNT, fork.PV_COUNT),
            "ZNBR_COUNT": (gold.ZNBR_COUNT, fork.ZNBR_COUNT),
            "ELEC_NEED_KW_BASE": (gold.ELEC_NEED_KW_BASE, fork.ELEC_NEED_KW_BASE),
            "ELEC_TARGET_KW": (gold.ELEC_TARGET_KW, fork.ELEC_TARGET_KW),
            "RECT_COUNT": (gold.RECT_COUNT, fork.RECT_COUNT),
        }
        diffs = {
            k: {"gold": g, "fork": f}
            for k, (g, f) in checks.items()
            if g != f
        }
        ok = not diffs
        return ok, {
            "ok": ok,
            "diffs": diffs,
            "checks": {k: {"gold": g, "fork": f} for k, (g, f) in checks.items()},
            "apply_result": result,
        }
    finally:
        if out_path.name.startswith("params_overlay_") and out_path.is_file():
            # Only auto-delete tempfile probes, not the canonical fork name.
            if out_path != DEFAULT_OUT:
                try:
                    out_path.unlink()
                except OSError:
                    pass


def self_test() -> int:
    """T3/T4/T5 style checks without FreeCAD."""
    failures: list[str] = []

    # T3: scale_m=1.0 + default electrical matching gold → identical.
    baseline = {
        "scale_m": 1.0,
        "site": {"site_id": "AQS_SITE_M1", "site_lat_deg": None, "crew": 4,
                 "jurisdiction_theme": "USA_Dallas_class"},
        "electrical": {
            "bus_nodes": ["SOL_ARK_60K", "ZNBR2", "RECTIFIER"],
            "storage_options": ["ZNBR2", "MEOH", "PUMPED_HYDRO"],
            "need_kw": {
                "value": 50.0, "unit": "kW", "status": "study",
                "note": "ELEC_NEED_KW_BASE at SCALE_M=1",
            },
            "target_kw": {
                "value": 70.0, "unit": "kW", "status": "study",
                "note": "ELEC_NEED × 1.4 overprod",
            },
            "pv_module_kw": 70.0,
            "pv_count": 1,
            "znbr_module_kw": 60.0,
            "znbr_count": 1,
            "rect_count": 1,
            "notes": "study",
        },
        "scale_rules": {
            "tanks": "continuous",
            "mfg_cryo": "discrete",
            "pv_znbr2": "module",
            "dock": "by_cassette",
        },
        "note": "Overlay only — does not rewrite models/freecad/params.py",
        "topology_authority": "AQS-FLOW-GRAPH-001",
    }
    ok, detail = roundtrip_equal_gold(baseline)
    if not ok:
        failures.append(f"T3 round-trip diffs: {detail.get('diffs')}")
    else:
        print("PASS T3: scale_m=1.0 + default electrical ≡ gold effective")

    # scale_m only (no electrical apply keys) also ≡ gold.
    ok2, d2 = roundtrip_equal_gold({"scale_m": 1.0, "note": "x",
                                    "topology_authority": "AQS-FLOW-GRAPH-001"})
    if not ok2:
        failures.append(f"T3b scale_m-only diffs: {d2.get('diffs')}")
    else:
        print("PASS T3b: scale_m=1.0 alone ≡ gold")

    # T6 (D10): a graph-derived electrical overlay (mvs.electrical written by
    # write_graph power()) pushes over the CAD seeds unconditionally: the fork
    # effective electrical values equal the overlay, not the gold seeds.
    graph_electrical = {
        "bus_nodes": ["SOL_ARK_60K", "ZNBR2", "RECTIFIER"],
        "storage_options": ["ZNBR2", "MEOH", "PUMPED_HYDRO"],
        "need_kw": {"value": 281.96, "unit": "kW", "status": "study", "note": "graph"},
        "target_kw": {"value": 704.91, "unit": "kW", "status": "study", "note": "graph"},
        "pv_module_kw": 0.5,
        "pv_count": 7818,
        "znbr_module_kw": 60.0,
        "znbr_count": 55,
        "rect_count": 1,
        "notes": "graph mvs.electrical (write_graph power())",
    }
    r6 = None
    try:
        import tempfile as _tf
        _t = _tf.NamedTemporaryFile(prefix="params_overlay_", suffix=".py",
                                    dir=str(HERE), delete=False)
        _t.close()
        _out6 = Path(_t.name)
        r6 = write_overlay_fork({"scale_m": 1.0, "electrical": graph_electrical},
                                out_path=_out6)
        f6 = load_module(_out6, "_aqs_overlay_params_t6")
        want = {
            "ELEC_NEED_KW_BASE": 281.96,
            "ELEC_TARGET_KW": 704.91,
            "PV_MODULE_KW": 0.5,
            "PV_COUNT": 7818,
            "ZNBR_MODULE_KW": 60.0,
            "ZNBR_COUNT": 55,
            "RECT_COUNT": 1,
        }
        bad6 = {k: (getattr(f6, k), v) for k, v in want.items()
                if abs(float(getattr(f6, k)) - float(v)) > 1e-9}
        if bad6:
            failures.append(f"T6 graph overlay did not win over seeds: {bad6}")
        else:
            print("PASS T6: graph mvs.electrical pushes over CAD seeds (D10)")
        _out6.unlink(missing_ok=True)
    except Exception as exc:  # noqa: BLE001 — self-test must report, not crash
        failures.append(f"T6 raised: {exc}")

    # T4: unknown key fails closed; gold untouched.
    gold_before = GOLD_PARAMS.read_bytes()
    try:
        write_overlay_fork(
            {"scale_m": 1.0, "extra": 1},
            out_path=HERE / "_test_overlay_should_not_exist.py",
        )
        failures.append("T4: unknown key 'extra' did not raise")
    except ValueError as exc:
        if "extra" not in str(exc):
            failures.append(f"T4: ValueError missing 'extra': {exc}")
        else:
            print("PASS T4: unknown key fails closed")
    if GOLD_PARAMS.read_bytes() != gold_before:
        failures.append("T4: gold params.py was modified")
    else:
        print("PASS T4b: gold params.py untouched after refuse")

    # T5: vessel mm key refused.
    try:
        write_overlay_fork(
            {"scale_m": 1.0, "CSTR_L": 9999},
            out_path=HERE / "_test_overlay_should_not_exist.py",
        )
        failures.append("T5: CSTR_L did not raise")
    except ValueError as exc:
        if "CSTR_L" not in str(exc):
            failures.append(f"T5: ValueError missing CSTR_L: {exc}")
        else:
            print("PASS T5: vessel mm key refused")

    # Null scale_m → keep gold (no invention).
    ok3, d3 = roundtrip_equal_gold({"scale_m": None, "note": "null scale"})
    if not ok3:
        failures.append(f"T-null diffs: {d3.get('diffs')}")
    else:
        print("PASS T-null: scale_m=null keeps gold SCALE_M")

    # Refuse writing onto gold path.
    try:
        write_overlay_fork({"scale_m": 1.0}, out_path=GOLD_PARAMS)
        failures.append("T-gold: allowed write onto params.py")
    except ValueError:
        print("PASS T-gold: refuse write onto gold params.py")

    # Cleanup stray test artifacts.
    for p in HERE.glob("_test_overlay_should_not_exist.py"):
        p.unlink(missing_ok=True)

    if failures:
        for f in failures:
            print("FAIL:", f, file=sys.stderr)
        return 1
    print("self-test: all passed")
    print("allow-list apply:", ", ".join(sorted(APPLY_MAP)))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--params",
        type=Path,
        default=None,
        help="export pack params.json overlay",
    )
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="fork output path (default: params_overlay.py beside gold)",
    )
    ap.add_argument(
        "--gold",
        type=Path,
        default=GOLD_PARAMS,
        help="gold params.py (read-only)",
    )
    ap.add_argument(
        "--allow-list",
        action="store_true",
        help="print allow-list JSON and exit 0",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="run round-trip / refuse tests (no FreeCAD)",
    )
    ap.add_argument(
        "--check-roundtrip",
        action="store_true",
        help="with --params, apply to temp fork and require ≡ gold effective",
    )
    args = ap.parse_args(argv)

    if args.allow_list:
        print(json.dumps(allow_list_report(), indent=2))
        return 0

    if args.self_test:
        return self_test()

    if args.params is None:
        print("ERROR: --params required (or --self-test / --allow-list)",
              file=sys.stderr)
        return 2
    if not args.params.is_file():
        print(f"ERROR: --params not found: {args.params}", file=sys.stderr)
        return 2

    overlay = json.loads(args.params.read_text(encoding="utf-8"))

    if args.check_roundtrip:
        ok, detail = roundtrip_equal_gold(
            overlay, gold_path=args.gold, out_path=None
        )
        print(json.dumps(detail, indent=2, default=str))
        return 0 if ok else 1

    try:
        result = write_overlay_fork(
            overlay, gold_path=args.gold, out_path=args.out
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except (FileNotFoundError, TypeError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("wrote", result["out_path"])
    print("applied_keys:", json.dumps(result["applied_keys"], sort_keys=True))
    print("gold untouched:", result["gold_path"])
    print("overlay_rewrites_params_py:", False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
