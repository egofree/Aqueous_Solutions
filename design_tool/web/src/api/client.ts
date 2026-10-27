// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import type {
  FlowGraphMeta,
  FlowGraphTopology,
  FlowGraphView,
  LayerViewName,
} from '../types/graph'
import type {
  ParamsResponse,
  RegenStatus,
  SystemTreeResponse,
} from '../types/design'
import type {
  ExportResponse,
  FlagsResponse,
  MvsModel,
  SandboxOverrides,
  SandboxRecord,
  SolveResponse,
} from '../types/mvs'

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (body.detail != null) detail = String(body.detail)
    } catch {
      /* keep statusText */
    }
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json() as Promise<T>
}

/** Graph-projected MVS (sole authority via plant_flow_graph). */
export async function getMvs(): Promise<MvsModel> {
  return jsonOrThrow(await fetch('/api/v1/mvs'))
}

export async function createSandbox(
  label?: string,
  overrides?: SandboxOverrides,
): Promise<SandboxRecord> {
  return jsonOrThrow(
    await fetch('/api/v1/sandbox', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ label, overrides: overrides ?? {} }),
    }),
  )
}

export async function getSandbox(id: string): Promise<SandboxRecord> {
  return jsonOrThrow(await fetch(`/api/v1/sandbox/${id}`))
}

export async function patchSandbox(
  id: string,
  overrides: SandboxOverrides,
  label?: string,
): Promise<SandboxRecord> {
  return jsonOrThrow(
    await fetch(`/api/v1/sandbox/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ overrides, label }),
    }),
  )
}

export async function solveSandbox(id: string): Promise<SolveResponse> {
  return jsonOrThrow(
    await fetch(`/api/v1/sandbox/${id}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }),
  )
}

export async function getFlags(id: string): Promise<FlagsResponse> {
  return jsonOrThrow(await fetch(`/api/v1/sandbox/${id}/flags`))
}

export async function exportSandbox(
  id: string,
  modules: string[] = ['params', 'streams', 'gaps', 'compliance_flags'],
): Promise<ExportResponse> {
  return jsonOrThrow(
    await fetch(`/api/v1/sandbox/${id}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ export_modules: modules }),
    }),
  )
}

export type { FlowGraphMeta }

export async function getFlowGraphMeta(): Promise<FlowGraphMeta> {
  return jsonOrThrow(await fetch('/api/v1/flow-graph'))
}

export async function getFlowGraphTopology(opts?: {
  includePlaceholders?: boolean
  includeIntraAisle?: boolean
}): Promise<FlowGraphTopology> {
  const q = new URLSearchParams()
  if (opts?.includePlaceholders === false) {
    q.set('include_placeholders', 'false')
  }
  if (opts?.includeIntraAisle === false) {
    q.set('include_intra_aisle', 'false')
  }
  const qs = q.toString()
  const url = qs
    ? `/api/v1/flow-graph/topology?${qs}`
    : '/api/v1/flow-graph/topology'
  return jsonOrThrow(await fetch(url))
}

export async function getFlowGraphView(
  name: LayerViewName,
): Promise<FlowGraphView> {
  return jsonOrThrow(await fetch(`/api/v1/flow-graph/views/${name}`))
}

/** U6: read-only system tree (AQS-SYS-TREE-001) with unit sets + aggregates. */
export async function getSystemTree(): Promise<SystemTreeResponse> {
  return jsonOrThrow(await fetch('/api/v1/system-tree'))
}

/** X-UI-002: the locale scaling profiles a site sandbox can start from. */
export interface SiteInfo {
  site_id: string
  actions: number
  eliminations: number
  error?: string
}

export interface SiteSandboxResponse {
  sandbox_id: string
  label: string
  site_id: string
  applied: string[]
  unapplied: string[]
  replacement_of: Record<string, string>
  model: MvsModel
}

export async function listSites(): Promise<{ sites: SiteInfo[] }> {
  return jsonOrThrow(await fetch('/api/v1/sites'))
}

export async function createSandboxFromSite(
  siteId: string,
  label?: string,
): Promise<SiteSandboxResponse> {
  return jsonOrThrow(
    await fetch('/api/v1/sandbox/from-site', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ site_id: siteId, label }),
    }),
  )
}

/** The REAL X-PAR-02 reconciliation on the sandbox fold. */
export async function solveSandboxPipeline(id: string): Promise<SolveResponse> {
  return jsonOrThrow(
    await fetch(`/api/v1/sandbox/${id}/solve-pipeline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }),
  )
}

/** U6: drivers.json listing — READ-ONLY (values live in drivers.json). */
export async function getParams(): Promise<ParamsResponse> {
  return jsonOrThrow(await fetch('/api/v1/params'))
}

/** U6: derived-artefact staleness vs the graph (read-only check). */
export async function getRegenStatus(): Promise<RegenStatus> {
  return jsonOrThrow(await fetch('/api/v1/regen-status'))
}
