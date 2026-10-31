// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useState } from 'react'
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
  /** Site-sandbox view: hide units the profile disabled, not just dim them. */
  showDisabled?: boolean
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
 * Unit-level eliminations (a site sandbox) hide units and their streams
 * by default - the site as designed, not the site as excused.
 */
export function SchematicCanvas({ model, activeCycle, layerView, showDisabled }: Props) {
  const [localShowDisabled, setLocalShowDisabled] = useState(false)
  const disabledShown = showDisabled ?? localShowDisabled
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

  // unit-level sandbox eliminations: hidden by default, not silently - the count
  // is stated in the legend so a hidden set is never silent
  const unitOff = new Set(
    units.filter((u) => u.enabled === false).map((u) => u.unit_id),
  )
  const visibleUnits = disabledShown
    ? units
    : units.filter((u) => !unitOff.has(u.unit_id))
  const visibleIds = new Set(visibleUnits.map((u) => u.unit_id))
  const visibleStreams = streams.filter(
    (s) => visibleIds.has(s.from_unit_id) && visibleIds.has(s.to_unit_id),
  )
  const hiddenCount = units.length - visibleUnits.length

  const { unitPos, sectorBands, width, height } = layoutBySector(
    visibleUnits,
    model.sectors,
  )
  const sectorMap = new Map(model.sectors.map((s) => [s.sector_id, s]))
  const viewLabel = layerView
    ? `${layerView.view_mode} (${layerView.preset_id})`
    : 'full graph projection'

  return (
    <div className="schematic-wrap">
      <label className="schematic-toggle">
        <input
          type="checkbox"
          checked={disabledShown}
          onChange={(e) => setLocalShowDisabled(e.target.checked)}
        />{' '}
        show disabled units ({unitOff.size})
      </label>
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
            fontSize={13}
            fontWeight={600}
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

        {visibleStreams.map((st) => {
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
          // attach at the facing box edges, not the centres: fewer crossings
          const forward = b.x >= a.x
          const x1 = forward ? a.x + BOX_W : a.x
          const x2 = forward ? b.x : b.x + BOX_W
          const y1 = a.y + BOX_H / 2
          const y2 = b.y + BOX_H / 2
          const dx = Math.abs(x2 - x1)
          const c = Math.max(30, dx * 0.4)
          const d = `M ${x1} ${y1} C ${x1 + (forward ? c : -c)} ${y1}, ${x2 + (forward ? -c : c)} ${y2}, ${x2} ${y2}`
          const rateTxt =
            st.rate == null || st.rate.value == null
              ? 'rate=null'
              : `${st.rate.value} ${st.rate.unit}`
          return (
            <g key={st.stream_id} className="stream">
              <path
                d={d}
                fill="none"
                stroke={muted ? '#c8c8c8' : '#1a5f9e'}
                strokeWidth={muted ? 1 : activeCycle && onCycle ? 3.5 : 1.8}
                opacity={muted ? 0.4 : 0.85}
              />
              <title>{`${st.stream_id}: ${st.carries ?? ''} (${st.from_unit_id} → ${st.to_unit_id}); ${rateTxt}`}</title>
            </g>
          )
        })}

        {visibleUnits.map((u) => {
          const p = unitPos[u.unit_id]
          if (!p) return null
          const sec = sectorMap.get(u.sector_id)
          const off = (sec ? !sec.enabled : false) || u.enabled === false
          const unitDisabled = u.enabled === false
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
                fontSize={11}
                fill={ph ? '#7a5a12' : off ? '#888' : '#222'}
              >
                {u.unit_id.length > 16
                  ? u.unit_id.slice(0, 15) + '…'
                  : u.unit_id}
              </text>
              {unitDisabled && (
                <text x={BOX_W - 4} y={11} textAnchor="end" fontSize={8} fill='#c0392b' fontWeight={700}>
                  OFF
                </text>
              )}
              <title>
                {`${u.unit_id} [${u.sector_id}]${required ? ' required' : ''}${unitDisabled ? ' DISABLED (site sandbox)' : ''}${ph ? ' PLACEHOLDER' : ''}`}
              </title>
            </g>
          )
        })}
      </svg>
      <p className="schematic-hint">
        Layer: <strong>{viewLabel}</strong>. * = required_for_mvs_closure.
        Disabled required sectors stay visible (gap, not silent). Amber dashed
        = placeholder (present_plus_placeholders).{" "}
        {hiddenCount > 0 && (
          <>
            <strong>{hiddenCount}</strong> unit(s) hidden: disabled by the site
            sandbox (toggle "show disabled").{" "}
          </>
        )}
        Streams from graph only — rates shown as recorded (null stays null).
        Layout is a deterministic reading grid by sector: schematic positions
        carry no dimension.
      </p>
    </div>
  )
}
