// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useEffect, useMemo, useRef } from 'react'
import type { ReactNode } from 'react'
import type { TreeNodeDto, SystemTreeResponse } from '../types/design'
import type { MvsModel } from '../types/mvs'

interface Props {
  tree: SystemTreeResponse | null
  model: MvsModel | null
  busy?: boolean
  onToggle: (node: TreeNodeDto, enabled: boolean) => void
}

type CheckState = boolean | 'indeterminate'

/** Checkbox that can render the parent 'some children on' state. */
function TreeCheckbox({
  state,
  disabled,
  onChange,
  title,
}: {
  state: CheckState
  disabled?: boolean
  onChange: (next: boolean) => void
  title: string
}) {
  const ref = useRef<HTMLInputElement>(null)
  useEffect(() => {
    if (ref.current) ref.current.indeterminate = state === 'indeterminate'
  }, [state])
  return (
    <input
      ref={ref}
      type="checkbox"
      checked={state === 'indeterminate' ? false : state}
      disabled={disabled}
      title={title}
      aria-label={title}
      onChange={(e) => onChange(e.target.checked)}
    />
  )
}

/**
 * U4a containment tree (sector → train → subsystem → unit) with sandbox
 * toggles. Root clicks PATCH sector_enabled; trains system_enabled;
 * subsystems subsystem_enabled; leaves unit_enabled. Most-specific wins
 * is resolved server-side (store.apply_overrides).
 */
export function TreeTogglePanel({ tree, model, busy, onToggle }: Props) {
  const byId = useMemo(() => {
    const m = new Map<string, TreeNodeDto>()
    if (tree) for (const n of tree.nodes) m.set(n.id, n)
    return m
  }, [tree])

  const unitEnabled = useMemo(() => {
    const m = new Map<string, boolean>()
    if (model) for (const u of model.units) m.set(u.unit_id, u.enabled)
    return m
  }, [model])

  const sectorEnabled = useMemo(() => {
    const m = new Map<string, boolean>()
    if (model) for (const s of model.sectors) m.set(s.sector_id, s.enabled)
    return m
  }, [model])

  /** Leaf state = the unit's own flag; parents derive from descendants. */
  function stateOf(node: TreeNodeDto): CheckState {
    if (node.unit_id != null) {
      return unitEnabled.get(node.unit_id) ?? true
    }
    if (node.level === 0) {
      // Root mirrors the sector row (a root click patches sector_enabled).
      return sectorEnabled.get(node.id) ?? true
    }
    const leaves = node.unit_ids ?? []
    let on = 0
    for (const uid of leaves) if (unitEnabled.get(uid) ?? true) on += 1
    if (on === 0) return false
    return on === leaves.length ? true : 'indeterminate'
  }

  function renderNode(node: TreeNodeDto): ReactNode {
    const st = stateOf(node)
    const agg = node.aggregate
    const shortName = node.id.split('.').pop() ?? node.id
    const isLeaf = node.unit_id != null
    return (
      <li
        key={node.id}
        className={`tree-node lv${node.level} ${isLeaf ? 'leaf' : 'branch'}`}
      >
        <label className="tree-row" style={{ paddingLeft: `${node.level * 14}px` }}>
          <TreeCheckbox
            state={st}
            disabled={busy}
            title={`${node.id} — patch ${
              node.level === 0
                ? 'sector_enabled'
                : isLeaf
                  ? 'unit_enabled'
                  : node.level === 1
                    ? 'system_enabled'
                    : 'subsystem_enabled'
            }`}
            onChange={(next) => onToggle(node, next)}
          />
          <span className="tree-name" title={node.description ?? node.id}>
            {shortName}
          </span>
          <span className="tree-meta">
            {agg.count}u
            {agg.kw_sum ? ` · ${agg.kw_sum.toFixed(1)} kW` : ''}
          </span>
          {agg.presence && agg.presence !== 'present' && (
            <span className={`badge presence-${agg.presence}`}>
              {agg.presence}
            </span>
          )}
        </label>
        {node.children.length > 0 && (
          <ul>{node.children.map((cid) => byId.get(cid) ?? null).filter(Boolean).map((c) => renderNode(c as TreeNodeDto))}</ul>
        )}
      </li>
    )
  }

  const roots = useMemo(
    () => (tree ? tree.nodes.filter((n) => n.level === 0) : []),
    [tree],
  )

  return (
    <section className="panel tree-toggle-panel">
      <h2>System tree (train / unit toggles)</h2>
      <p className="hint">
        AQS-SYS-TREE-001 · patches sandbox system/subsystem/unit overrides —
        most-specific wins (server-side); graph stays authority.
      </p>
      {!tree || !model ? (
        <p className="empty">Loading system tree…</p>
      ) : (
        <ul className="tree-root-list">{roots.map((r) => renderNode(r))}</ul>
      )}
    </section>
  )
}
