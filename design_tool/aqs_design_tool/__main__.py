# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Allow `python -m aqs_design_tool` from the design_tool directory."""

from __future__ import annotations


def main() -> None:
    import uvicorn

    uvicorn.run(
        "aqs_design_tool.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
