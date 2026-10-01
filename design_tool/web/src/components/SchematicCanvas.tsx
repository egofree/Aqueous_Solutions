// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import type { FlowGraphView } from '../types/graph'
import type { MvsModel, Sector, Stream, Unit } from '../types/mvs'
import {
  BOX_H,
  BOX_W,
  layoutBySector,
  streamMatchesCycle,
} from '../layout/autoLayout'

interface Props {
  model: MvsModel
  activeCycle: string | null
  /** When set, canvas shows only nodes/edges from this graph layer view. */
  layerView: FlowGraphView | null
}

function sectorEnabled(sectors: Sector[], sid: string): boolean {
  const s = sectors.find((x) => x.sector_id === sid)
  return s ? s.enabled : true
}

function isPlaceholder(
  presence: string | null | undefined,
  diagramGap: string | null | undefined,
): boolean {
  if (presence === 'placeholder') return true
  if (diagramGap != null && diagramGap !== '') return true
  return false
}

/**
 * Graph-layer SVG schematic. Topology from sandbox model (graph-backed);
 * optional layer view filters to PFD/MFD/EFD-* without inventing rates.
 */
export function SchematicCanvas({ model, activeCycle, layerView }: Props) {
  const presenceByUnit = new Map<string, string>()
  const gapByUnit = new Map<string, string | null>()
  let units: Unit[] = model.units
  let streams: Stream[] = model.streams

  if (layerView) {
    const unitIds = new Set(layerView.nodes.map((n) => n.unit_id))
    const streamIds = new Set(layerView.edges.map((e) => e.stream_id))
    for (const n of layerView.nodes) {
      presenceByUnit.set(n.unit_id, n.presence ?? 'present')
      gapByUnit.set(n.unit_id, n.diagram_gap ?? null)
    }
    // Prefer sandbox model fields (sector enables) but restrict to view set.
    units = model.units.filter((u) => unitIds.has(u.unit_id))
    // Units only in the view (e.g. placeholders not yet in MVS projection)
    const modelIds = new Set(model.units.map((u) => u.unit_id))
    for (const n of layerView.nodes) {
      if (!modelIds.has(n.unit_id)) {
        units.push({
          unit_id: n.unit_id,
          sector_id: n.sector_id,
          enabled: n.enabled !== false,
          class: n.class ?? null,
          tags: n.tags,
        })
      }
    }
    streams = model.streams.filter((s) => streamIds.has(s.stream_id))
    const modelStreamIds = new Set(model.streams.map((s) => s.stream_id))
    for (const e of layerView.edges) {
      if (!modelStreamIds.has(e.stream_id)) {
        streams.push({
          stream_id: e.stream_id,
          from_unit_id: e.from_unit_id,
          to_unit_id: e.to_unit_id,
          phase: e.phase ?? '?',
          carries: e.carries ?? null,
          from_sector_id: e.from_sector_id ?? null,
          to_sector_id: e.to_sector_id ?? null,
          open_boundary: e.open_boundary,
          rate: e.rate ?? null,
          null_rate_kind: e.null_rate_kind ?? null,
          note: e.notes ?? null,
        })
      }
    }
  }

  const { unitPos, sectorBands, width, height } = layoutBySector(
    units,
    model.sectors,
  )
  const sectorMap = new Map(model.sectors.map((s) => [s.sector_id, s]))
  const viewLabel = layerView
    ? `${layerView.view_mode} (${layerView.preset_id})`
    : 'full graph projection'

  return (
    <div className="schematic-wrap">
      <svg
        className="schematic"
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        role="img"
        aria-label={`Graph-layer schematic — ${viewLabel}`}
      >
        <title>
          Aqueous graph-layer schematic — {viewLabel}; existing units/streams
          only
        </title>
        {sectorBands.map((b) => (
          <text
            key={b.sector_id}
            x={b.x}
            y={24}
            className="sector-label"
            fill={
              sectorMap.get(b.sector_id)?.enabled === false ? '#999' : '#334'
            }
          >
            {b.label}
            {sectorMap.get(b.sector_id)?.required_for_mvs_closure
              ? ' *'
              : ''}
          </text>
        ))}

        {streams.map((st) => {
          const a = unitPos[st.from_unit_id]
          const b = unitPos[st.to_unit_id]
          if (!a || !b) return null
          const onCycle = streamMatchesCycle(st, activeCycle)
          const fromOff = !sectorEnabled(
            model.sectors,
            st.from_sector_id ?? '',
          )
          const toOff = !sectorEnabled(model.sectors, st.to_sector_id ?? '')
          const muted = activeCycle ? !onCycle : fromOff || toOff
          const x1 = a.x + BOX_W / 2
          const y1 = a.y + BOX_H / 2
          const x2 = b.x + BOX_W / 2
          const y2 = b.y + BOX_H / 2
          const rateTxt =
            st.rate == null || st.rate.value == null
              ? 'rate=null'
              : `${st.rate.value} ${st.rate.unit}`
          return (
            <g key={st.stream_id}>
              <line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={muted ? '#c8c8c8' : '#1a5f9e'}
                strokeWidth={muted ? 1 : activeCycle && onCycle ? 3.5 : 1.8}
                opacity={muted ? 0.45 : 0.9}
              />
              <title>{`${st.stream_id}: ${st.carries ?? ''} (${st.from_unit_id} → ${st.to_unit_id}); ${rateTxt}`}</title>
            </g>
          )
        })}

        {units.map((u) => {
          const p = unitPos[u.unit_id]
          if (!p) return null
          const sec = sectorMap.get(u.sector_id)
          const off = sec ? !sec.enabled : false
          const required = sec?.required_for_mvs_closure ?? false
          const ph = isPlaceholder(
            presenceByUnit.get(u.unit_id),
            gapByUnit.get(u.unit_id),
          )
          return (
            <g key={u.unit_id} transform={`translate(${p.x},${p.y})`}>
              <rect
                width={BOX_W}
                height={BOX_H}
                rx={4}
                fill={
                  ph ? '#fff8e7' : off ? '#f0f0f0' : '#e8f1fa'
                }
                stroke={
                  ph
                    ? '#b7791f'
                    : off && required
                      ? '#c0392b'
                      : off
                        ? '#aaa'
                        : '#2c3e50'
                }
                strokeWidth={ph || (off && required) ? 2.2 : 1.2}
                strokeDasharray={ph || off ? '4 2' : undefined}
              />
              <text
                x={BOX_W / 2}
                y={BOX_H / 2 + 4}
                textAnchor="middle"
                fontSize={9}
                fill={ph ? '#7a5a12' : off ? '#888' : '#222'}
              >
                {u.unit_id.length > 14
                  ? u.unit_id.slice(0, 13) + '…'
                  : u.unit_id}
              </text>
              <title>
                {`${u.unit_id} [${u.sector_id}]${required ? ' required' : ''}${off ? ' DISABLED' : ''}${ph ? ' PLACEHOLDER' : ''}`}
              </title>
            </g>
          )
        })}
      </svg>
      <p className="schematic-hint">
        Layer: <strong>{viewLabel}</strong>. * = required_for_mvs_closure.
        Disabled required sectors stay visible (gap, not silent). Amber dashed
        = placeholder (present_plus_placeholders). Streams from graph only —
        rates shown as recorded (null stays null). Layout is deterministic grid
        by sector.
      </p>
    </div>
  )
}
