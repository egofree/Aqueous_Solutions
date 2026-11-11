# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Shared CadQuery library for the manufacturing models (AQS-PLAN-006 section 6, T0 item 2).

Modules:
  dn           pipe, flange and bolt dimension tables (pure data, no CadQuery)
  nozzles      nozzle stubs DN15-DN50, flange stubs, hose barbs (needs CadQuery)
  frame        AQS-MOD-002 bay frame members and the load rule (needs CadQuery)
  fasteners    the fastener row schema, the grade rule and the CSV writer (pure data)
  materials    the material table, densities and the corrosion-allowance shop rule (pure data)
  stamp_date   the deterministic stamp date of the current inputs (pure data)
  step_export  byte-stable STEP export: named products, fixed header (needs CadQuery)
  pdf_write    byte-stable drawing PDF pass: fixed creation date and sheet id (needs cairosvg)

Every dimension in this library is either read from an authority named in its module
docstring (a graph field, a duty page, `tables/materials.csv`, a cited standard) or is an
explicit function argument. Where a default is a study proportion rather than a cited
value, the docstring says so.
"""
