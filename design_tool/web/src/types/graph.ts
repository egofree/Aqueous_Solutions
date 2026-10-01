// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
/** Flow-graph layer / topology types (AQS-FLOW-GRAPH-001 / WP-Bp1–Bp2). */

import type { Quantity } from './mvs'

/** Layer view names matching GET /api/v1/flow-graph/views/{name}. */
export const LAYER_VIEWS = [
  'pfd',
  'mfd',
  'efd-elec',
  'efd-thermal',
  'efd-ess',
] as const

export type LayerViewName = (typeof LAYER_VIEWS)[number]

export const LAYER_VIEW_LABELS: Record<LayerViewName, string> = {
  pfd: 'PFD',
  mfd: 'MFD',
  'efd-elec': 'EFD-elec',
  'efd-thermal': 'EFD-thermal',
  'efd-ess': 'EFD-ess',
}

export type Presence = 'present' | 'placeholder' | string

export interface FlowGraphMeta {
  doc_id: string
  revision: string
  node_count: number
  edge_count: number
  path: string
  mvs_equivalent_from_topology: boolean
  note?: string
}

export interface GraphViewNode {
  unit_id: string
  sector_id: string
  presence?: Presence | null
  class?: string | null
  tags?: string[]
  electrical_role?: string | null
  diagram_gap?: string | null
  notes?: string | null
  enabled?: boolean
  continuous_kw?: Quantity | null
}

export interface GraphViewEdge {
  stream_id: string
  from_unit_id: string
  to_unit_id: string
  phase?: string
  layers?: string[]
  presence?: Presence | null
  carries?: string | null
  rate?: Quantity | null
  from_sector_id?: string | null
  to_sector_id?: string | null
  open_boundary?: boolean
  gap_flags?: string[]
  notes?: string | null
  null_rate_kind?: string | null
}

export interface FlowGraphView {
  preset_id: string
  view_mode: string
  source_doc: string
  source_revision: string
  node_count: number
  edge_count: number
  orphan_campus_units?: string[]
  render_note?: string
  nodes: GraphViewNode[]
  edges: GraphViewEdge[]
}

export interface FlowGraphTopology {
  source: string
  mvs_equivalent: boolean
  unit_count: number
  stream_count: number
  gap_count: number
  units: Array<{
    unit_id: string
    sector_id: string
    enabled?: boolean
    class?: string | null
    tags?: string[]
  }>
  streams: Array<{
    stream_id: string
    from_unit_id: string
    to_unit_id: string
    phase: string
    carries?: string | null
    rate?: Quantity | null
    null_rate_kind?: string | null
  }>
  gaps: unknown[]
}
