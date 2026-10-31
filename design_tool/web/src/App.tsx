// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useCallback, useEffect, useState } from 'react'
import {
  createSandbox,
  exportSandbox,
  getFlags,
  getFlowGraphMeta,
  getFlowGraphTopology,
  getFlowGraphView,
  getMvs,
  getParams,
  getSystemTree,
  patchSandbox,
  solveSandbox,
} from './api/client'
import { CycleViews } from './components/CycleViews'
import { ExportButton, P0_MODULES } from './components/ExportButton'
import { GapPanel } from './components/GapPanel'
import { LayerFilters } from './components/LayerFilters'
import { ParamsPanel } from './components/ParamsPanel'
import { RegenStatusBadge } from './components/RegenStatusBadge'
import { SchematicCanvas } from './components/SchematicCanvas'
import { SectorToggles } from './components/SectorToggles'
import { SitePanel } from './components/SitePanel'
import { SiteInputs } from './components/SiteInputs'
import { TreeTogglePanel } from './components/TreeTogglePanel'
import type { TreeNodeDto, ParamsResponse, SystemTreeResponse } from './types/design'
import type { FlowGraphView, LayerViewName } from './types/graph'
import type {
  ExportResponse,
  Gap,
  MvsModel,
  SandboxOverrides,
  SolveResponse,
  UnclosedStream,
} from './types/mvs'

const DEFAULT_LAYER: LayerViewName = 'pfd'

/**
 * Phase B′ graph-layer UI: topology from graph API; sandbox patches
 * graph-backed model (not a divergent master). CERN-OHL-S-2.0.
 */
export default function App() {
  const [mvsRevision, setMvsRevision] = useState<string>('')
  const [sandboxId, setSandboxId] = useState<string | null>(null)
  const [model, setModel] = useState<MvsModel | null>(null)
  const [solve, setSolve] = useState<SolveResponse | null>(null)
  const [gaps, setGaps] = useState<Gap[]>([])
  const [unclosed, setUnclosed] = useState<UnclosedStream[]>([])
  const [cycle, setCycle] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [exportResult, setExportResult] = useState<ExportResponse | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)
  const [flowMeta, setFlowMeta] = useState<string>('')
  const [layer, setLayer] = useState<LayerViewName>(DEFAULT_LAYER)
  const [layerView, setLayerView] = useState<FlowGraphView | null>(null)
  const [layerBusy, setLayerBusy] = useState(false)
  // U6 design-UI state
  const [systemTree, setSystemTree] = useState<SystemTreeResponse | null>(null)
  const [params, setParams] = useState<ParamsResponse | null>(null)
  const [regenRefresh, setRegenRefresh] = useState(0)

  const refreshFlags = useCallback(async (id: string) => {
    const flags = await getFlags(id)
    setGaps(flags.gaps)
    setUnclosed(flags.unclosed_streams)
  }, [])

  const runSolve = useCallback(async (id: string) => {
    const result = await solveSandbox(id)
    setSolve(result)
    setGaps(result.gaps)
    setUnclosed(result.unclosed_streams)
    // Regen badge re-checks after every solve (U6).
    setRegenRefresh((k) => k + 1)
    return result
  }, [])

  const loadLayer = useCallback(async (name: LayerViewName) => {
    setLayerBusy(true)
    try {
      const view = await getFlowGraphView(name)
      setLayerView(view)
      setLayer(name)
    } catch (e) {
      setError(String(e))
    } finally {
      setLayerBusy(false)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setBusy(true)
      setError(null)
      try {
        // WP-Bp1: require graph endpoints (topology sole authority)
        const fg = await getFlowGraphMeta()
        if (cancelled) return
        setFlowMeta(
          `${fg.doc_id} rev ${fg.revision} · ${fg.node_count}u/${fg.edge_count}e · topology sole · mvs_eq=${String(fg.mvs_equivalent_from_topology)}`,
        )
        const topo = await getFlowGraphTopology({
          includePlaceholders: true,
        })
        if (cancelled) return
        // Topology proves graph load; MVS is graph projection for sandbox edits
        void topo
        // U6 read-only views (tree + drivers) load alongside the model.
        const [tree, drv] = await Promise.all([getSystemTree(), getParams()])
        if (cancelled) return
        setSystemTree(tree)
        setParams(drv)
        const mvs = await getMvs()
        if (cancelled) return
        setMvsRevision(mvs.revision)
        const sb = await createSandbox('bprime-graph-ui')
        if (cancelled) return
        setSandboxId(sb.sandbox_id)
        setModel(sb.model)
        await runSolve(sb.sandbox_id)
        if (!cancelled) await loadLayer(DEFAULT_LAYER)
      } catch (e) {
        if (!cancelled) setError(String(e))
      } finally {
        if (!cancelled) setBusy(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [runSolve, loadLayer])

  async function onToggleSector(sectorId: string, enabled: boolean) {
    if (!sandboxId) return
    setBusy(true)
    setError(null)
    try {
      const sb = await patchSandbox(sandboxId, {
        sector_enabled: { [sectorId]: enabled },
      })
      setModel(sb.model)
      await runSolve(sandboxId)
      await refreshFlags(sandboxId)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  /** U4a tree toggle: root→sector, train→system, subsystem, leaf→unit. */
  async function onToggleTree(node: TreeNodeDto, enabled: boolean) {
    if (!sandboxId) return
    const overrides: SandboxOverrides = {}
    if (node.level === 0) overrides.sector_enabled = { [node.id]: enabled }
    else if (node.unit_id != null)
      overrides.unit_enabled = { [node.unit_id]: enabled }
    else if (node.level === 1) overrides.system_enabled = { [node.id]: enabled }
    else overrides.subsystem_enabled = { [node.id]: enabled }
    setBusy(true)
    setError(null)
    try {
      const sb = await patchSandbox(sandboxId, overrides)
      setModel(sb.model)
      await runSolve(sandboxId)
      await refreshFlags(sandboxId)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  async function onApplySite(
    crew: number | null,
    siteLat: number | null,
    clearLat: boolean,
  ) {
    if (!sandboxId) return
    setBusy(true)
    setError(null)
    try {
      const overrides: {
        crew?: number
        site_lat_deg?: number
      } = {}
      if (crew != null) overrides.crew = Math.trunc(crew)
      // Empty SITE_LAT does not invent a latitude (store applies only when set).
      if (!clearLat && siteLat != null) overrides.site_lat_deg = siteLat
      const sb = await patchSandbox(sandboxId, overrides)
      setModel(sb.model)
      await runSolve(sandboxId)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  async function onExport() {
    if (!sandboxId) return
    setBusy(true)
    setExportError(null)
    try {
      const res = await exportSandbox(sandboxId, P0_MODULES)
      setExportResult(res)
    } catch (e) {
      setExportError(String(e))
    } finally {
      setBusy(false)
    }
  }

  const placeholderCount = layerView
    ? layerView.nodes.filter(
        (n) =>
          n.presence === 'placeholder' ||
          (n.diagram_gap != null && n.diagram_gap !== ''),
      ).length
    : null

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Aqueous Design Tool — B′ Graph-layer UI</h1>
          <p className="sub">
            AQS-UI-001 Rev D · unify_then_reshape · U6 design UI · schema
            aqs-mvs-0.3 · CERN-OHL-S-2.0 · Graph sole topology; sandbox
            overlays only
          </p>
        </div>
        <div className="meta">
          <RegenStatusBadge refreshKey={regenRefresh} />
          <div>
            MVS rev (projection): <code>{mvsRevision || '—'}</code>
          </div>
          <div>
            sandbox_id: <code>{sandboxId ?? '…'}</code>
          </div>
          {busy && <div className="busy">working…</div>}
          {flowMeta ? (
            <div className="sub" style={{ fontSize: 12 }}>
              Flow graph: {flowMeta}
            </div>
          ) : null}
        </div>
      </header>

      {error && <div className="banner error">{error}</div>}

      {!model ? (
        <p className="loading">Loading flow graph + sandbox…</p>
      ) : (
        <div className="layout">
          <aside className="sidebar">
            <LayerFilters
              active={layer}
              busy={busy || layerBusy}
              nodeCount={layerView?.node_count ?? null}
              edgeCount={layerView?.edge_count ?? null}
              placeholderCount={placeholderCount}
              sourceRevision={layerView?.source_revision ?? null}
              onChange={(name) => {
                void loadLayer(name)
              }}
            />
            <SectorToggles
              sectors={model.sectors}
              busy={busy}
              onToggle={onToggleSector}
            />
            <SitePanel
              onSandbox={(id, model) => {
                setSandboxId(id)
                setModel(model as MvsModel)
                setSolve(null)
              }}
            />
            <TreeTogglePanel
              tree={systemTree}
              model={model}
              busy={busy}
              onToggle={onToggleTree}
            />
            <CycleViews
              cycles={model.ui?.cycle_views ?? []}
              active={cycle}
              onChange={setCycle}
            />
            <SiteInputs
              crew={model.site.crew}
              siteLatDeg={model.site.site_lat_deg}
              busy={busy}
              onApply={onApplySite}
            />
            <ExportButton
              busy={busy}
              last={exportResult}
              error={exportError}
              onExport={onExport}
            />
          </aside>

          <main className="main">
            <SchematicCanvas
              model={model}
              activeCycle={cycle}
              layerView={layerView}
            />
            <GapPanel solve={solve} gaps={gaps} unclosed={unclosed} />
            <ParamsPanel params={params} />
          </main>
        </div>
      )}
    </div>
  )
}
