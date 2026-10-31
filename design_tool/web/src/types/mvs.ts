// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
/** Types aligned to aqs-mvs-0.3 / P0 FastAPI (subset used by P1 UI). */

export interface Quantity {
  value: number | null
  unit: string
  status?: string
  note?: string | null
}

export interface Sector {
  sector_id: string
  sector_definition: string
  enabled: boolean
  required_for_mvs_closure: boolean
  notes?: string | null
}

export interface Unit {
  unit_id: string
  sector_id: string
  enabled: boolean
  class?: string | null
  tags?: string[]
}

export interface Stream {
  stream_id: string
  from_unit_id: string
  to_unit_id: string
  phase: string
  carries?: string | null
  from_sector_id?: string | null
  to_sector_id?: string | null
  open_boundary?: boolean
  rate?: Quantity | null
  null_rate_kind?: string | null
  note?: string | null
}

export interface Site {
  site_id: string
  site_lat_deg: number | null
  crew: number | null
  jurisdiction_theme?: string
}

export interface UiHints {
  cycle_views: string[]
  sector_toggles: boolean
  gap_panel: boolean
  export_modules: string[]
}

export interface MvsModel {
  schema_version: string
  doc_id: string
  revision: string
  licence: string
  scale_m: number
  status: string
  site: Site
  sectors: Sector[]
  units: Unit[]
  streams: Stream[]
  ui: UiHints
  notes?: string | null
}

export interface Gap {
  sector_definition?: string | null
  sector_id?: string | null
  stream_id?: string | null
  reason: string
  detail?: string | null
}

export interface UnclosedStream {
  stream_id: string
  reason: string
  from_unit_id?: string | null
  to_unit_id?: string | null
}

export interface SurplusItem {
  value: number | null
  unit: string
  status?: string
  note?: string | null
  pass_study?: boolean | null
  threshold?: number | null
}

export interface ElectricalMatch {
  generation_kw_study?: number | null
  storage_power_kw_study?: number | null
  load_kw_study?: number | null
  need_kw?: number | null
  target_kw?: number | null
  pv_nameplate_kw_study?: number | null
  enabled_storage_options?: string[]
  status?: string
  note?: string
}

export interface SolveResponse {
  status: string
  mvs_equivalent: boolean
  sandbox_id?: string | null
  gaps: Gap[]
  unclosed_streams: UnclosedStream[]
  surplus: Record<string, SurplusItem>
  electrical_match?: ElectricalMatch
  notes: string[]
  solved_at?: string

  residuals?: {
    mass?: { id: string; kind: string; residual?: number; unit?: string; status: string; detail?: string }[]
  }}

export interface FlagsResponse {
  sandbox_id: string
  gaps: Gap[]
  unclosed_streams: UnclosedStream[]
  bottlenecks: unknown[]
  redundant_paths: unknown[]
  code_flags: unknown[]
  last_solve_status?: string | null
}

export interface SandboxOverrides {
  sector_enabled?: Record<string, boolean>
  /** U4a system tree: sector-root or train node ids (dotted, e.g. 'FOUNDRY.form-train'). */
  system_enabled?: Record<string, boolean>
  /** U4a system tree: subsystem node ids (e.g. 'FOUNDRY.melt-and-cast-train.cast'). */
  subsystem_enabled?: Record<string, boolean>
  unit_enabled?: Record<string, boolean>
  scale_m?: number | null
  crew?: number | null
  site_lat_deg?: number | null
}

export interface ExportResponse {
  pack_dir: string
  files: string[]
  notes: string[]
}

export interface SandboxRecord {
  sandbox_id: string
  label?: string
  created_at?: string
  updated_at?: string
  parent_mvs_revision?: string
  model: MvsModel
  last_solve?: SolveResponse | null
}
