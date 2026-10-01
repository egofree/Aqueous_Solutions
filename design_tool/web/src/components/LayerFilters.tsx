// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import {
  LAYER_VIEW_LABELS,
  LAYER_VIEWS,
  type LayerViewName,
} from '../types/graph'

interface Props {
  active: LayerViewName
  busy?: boolean
  nodeCount?: number | null
  edgeCount?: number | null
  placeholderCount?: number | null
  sourceRevision?: string | null
  onChange: (layer: LayerViewName) => void
}

/**
 * Layer filters matching API views (locks: layered_views, efd_three_layers).
 * Placeholders are shown by the canvas — rates are never invented here.
 */
export function LayerFilters({
  active,
  busy,
  nodeCount,
  edgeCount,
  placeholderCount,
  sourceRevision,
  onChange,
}: Props) {
  return (
    <section className="panel layer-filters">
      <h2>Layer view</h2>
      <div className="tabs" role="tablist" aria-label="Flow-graph layer">
        {LAYER_VIEWS.map((name) => (
          <button
            key={name}
            type="button"
            role="tab"
            aria-selected={active === name}
            className={active === name ? 'active' : ''}
            disabled={busy}
            onClick={() => onChange(name)}
          >
            {LAYER_VIEW_LABELS[name]}
          </button>
        ))}
      </div>
      <p className="hint">
        Graph views from{' '}
        <code>/api/v1/flow-graph/views/&#123;pfd|mfd|efd-*&#125;</code>. Placeholders
        visible (dashed); null rates stay null — no invented streams.
        {sourceRevision != null && (
          <>
            {' '}
            · view rev <code>{sourceRevision}</code>
          </>
        )}
        {nodeCount != null && edgeCount != null && (
          <>
            {' '}
            · {nodeCount}u / {edgeCount}e
            {placeholderCount != null && placeholderCount > 0
              ? ` · ${placeholderCount} placeholder`
              : ''}
          </>
        )}
      </p>
    </section>
  )
}
