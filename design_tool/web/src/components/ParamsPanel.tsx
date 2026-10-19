// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useMemo, useState } from 'react'
import type { ParamRow, ParamsResponse } from '../types/design'

const MAX_ROWS = 400

interface Props {
  params: ParamsResponse | null
}

function fmtValue(v: unknown): string {
  if (v == null) return '—'
  if (typeof v === 'number') return String(v)
  if (typeof v === 'string') return v
  const s = JSON.stringify(v)
  return s.length > 90 ? `${s.slice(0, 87)}…` : s
}

/** Read-only drivers.json table — searchable / filterable (GET /api/v1/params). */
export function ParamsPanel({ params }: Props) {
  const [query, setQuery] = useState('')
  const [nvOnly, setNvOnly] = useState(false)

  const rows = useMemo(() => {
    if (!params) return []
    const q = query.trim().toLowerCase()
    return params.params.filter((p) => {
      if (nvOnly && !p.needs_verification) return false
      if (!q) return true
      const basis = (p.ref ?? p.owner ?? '').toLowerCase()
      return (
        p.key.toLowerCase().includes(q) ||
        basis.includes(q) ||
        (p.units ?? '').toLowerCase().includes(q)
      )
    })
  }, [params, query, nvOnly])

  const shown = rows.slice(0, MAX_ROWS)

  return (
    <section className="panel params-panel">
      <h2>
        Design parameters — drivers.json{' '}
        <span className="badge ro" title="read-only">
          read-only
        </span>
      </h2>
      <p className="hint">
        Values live in <code>flow_graph/param/drivers.json</code> (X-PAR-01).
        The write path is edit + <code>python3 -m flow_graph.param.regen</code>
        — this panel never mutates them.
        {params && (
          <>
            {' '}
            {params.count} keys · {params.needs_verification_count} need
            verification · sha {params.drivers_sha256.slice(0, 12)}
          </>
        )}
      </p>
      <div className="params-controls">
        <input
          type="search"
          placeholder="filter by key / basis / units…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Filter parameters"
        />
        <label className="nv-toggle">
          <input
            type="checkbox"
            checked={nvOnly}
            onChange={(e) => setNvOnly(e.target.checked)}
          />
          needs verification only
        </label>
      </div>
      {!params ? (
        <p className="empty">Loading drivers…</p>
      ) : rows.length === 0 ? (
        <p className="empty">No parameters match the filter.</p>
      ) : (
        <div className="params-table-wrap">
          <table>
            <thead>
              <tr>
                <th>key</th>
                <th>value</th>
                <th>units</th>
                <th>basis (ref / owner)</th>
                <th>reg</th>
                <th>nv</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((p: ParamRow) => (
                <tr key={p.key} className={p.needs_verification ? 'nv' : ''}>
                  <td className="key" title={p.key}>
                    {p.key}
                  </td>
                  <td className="val" title={fmtValue(p.value)}>
                    {fmtValue(p.value)}
                  </td>
                  <td>{p.units ?? '—'}</td>
                  <td
                    className="basis"
                    title={(p.ref ?? p.owner ?? '') + (p.verification_test ? `\nnv test: ${p.verification_test}` : '')}
                  >
                    {p.ref ? <span className="badge ref">ref</span> : null}
                    {p.owner ? <span className="badge own">owner</span> : null}
                    {p.ref ?? p.owner ?? '—'}
                  </td>
                  <td>{p.register ?? '—'}</td>
                  <td>
                    {p.needs_verification ? (
                      <span
                        className="badge gap"
                        title={p.verification_test ?? 'needs verification'}
                      >
                        nv
                      </span>
                    ) : (
                      ''
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > MAX_ROWS && (
            <p className="hint">
              showing {MAX_ROWS} of {rows.length} matching — refine the filter.
            </p>
          )}
        </div>
      )}
    </section>
  )
}
