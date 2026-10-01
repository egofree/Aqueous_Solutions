#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""CLI: WP-Ap2 graph sole-authority contract check.

Usage (from flow_graph/):
  python3 check_authority_contract.py
  python3 -m pytest test_authority_contract.py -q

Exit 0 if topology identity holds and on-disk candidate matches projection.
Exit 1 on any divergent master / drift.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authority_contract import check_authority_contract  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph", type=Path, default=None)
    ap.add_argument("--candidate", type=Path, default=None)
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print ContractReport as JSON",
    )
    ap.add_argument(
        "--allow-missing-candidate",
        action="store_true",
        help="Warn (do not fail) if candidate_mvs.json is absent",
    )
    args = ap.parse_args(argv)
    report = check_authority_contract(
        graph_path=args.graph,
        candidate_path=args.candidate,
        require_candidate_file=not args.allow_missing_candidate,
    )
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        status = "PASS" if report.ok else "FAIL"
        print(f"{status} authority contract (WP-Ap2)")
        print(f"  graph:     {report.graph_path}")
        print(f"  candidate: {report.candidate_path}")
        print(
            f"  graph units={report.graph_unit_count} streams={report.graph_stream_count}"
        )
        print(
            f"  projection units={report.projection_unit_count} "
            f"streams={report.projection_stream_count}"
        )
        if report.candidate_file_present:
            print(
                f"  on-disk units={report.candidate_unit_count} "
                f"streams={report.candidate_stream_count} "
                f"matches_projection={report.candidate_matches_projection}"
            )
        print(f"  units_hash={report.graph_units_hash[:16]}…")
        print(f"  streams_hash={report.graph_streams_hash[:16]}…")
        for w in report.warnings:
            print(f"  WARN: {w}")
        for i in report.issues:
            print(f"  ISSUE [{i.code}]: {i.detail}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
