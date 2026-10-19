// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
/** U6 design-UI types: system tree, drivers, regen status (read-only views). */

/** Rolled-up aggregate of a tree node's unit set (graph continuous_kw). */
export interface TreeAggregate {
  count: number
  kw_sum: number
  kw_count: number
  presence: string | null
  unknown_unit_ids: string[]
}

/** One node of AQS-SYS-TREE-001 (sector → train → subsystem → unit). */
export interface TreeNodeDto {
  id: string
  parent: string | null
  level: number
  children: string[]
  unit_id: string | null
  description: string | null
  unit_ids: string[] | null
  aggregate: TreeAggregate
}

export interface SystemTreeStats {
  nodes: number
  by_level: Record<string, number>
  roots: number
  trains: number
  subsystems: number
  leaves: number
  units_per_root: Record<string, number>
}

/** GET /api/v1/system-tree — read-only partition of the graph unit set. */
export interface SystemTreeResponse {
  source: string
  graph_authority: string
  read_only: boolean
  schema_version: string
  doc_id: string
  revision: string
  date: string
  sector_exceptions: Record<string, string>
  stats: SystemTreeStats
  node_count: number
  nodes: TreeNodeDto[]
}

/** GET /api/v1/params row — one drivers.json key (READ-ONLY). */
export interface ParamRow {
  key: string
  value: unknown
  units: string | null
  ref: string | null
  owner: string | null
  register: string | null
  needs_verification: boolean
  verification_test?: string | null
}

/** GET /api/v1/params — drivers.json listing (values live in the file). */
export interface ParamsResponse {
  source: string
  read_only: boolean
  note: string
  count: number
  needs_verification_count: number
  drivers_sha256: string
  params: ParamRow[]
}

/** Last full-regen provenance receipt (flow_graph/derived/_regen_receipt.json). */
export interface RegenReceipt {
  graph_sha256: string | null
  passes: number | null
  converged: boolean | null
  vouched_count: number
  failed: string[]
  generated_by?: string | null
}

/** GET /api/v1/regen-status — derived-artefact staleness vs the graph. */
export interface RegenStatus {
  ok: boolean
  stale_count: number | null
  gated_stale: string[]
  files_checked: number | null
  last_receipt: RegenReceipt | null
  checked_at?: string
  command?: string
  error?: string
  returncode?: number
  receipt_error?: string
}
