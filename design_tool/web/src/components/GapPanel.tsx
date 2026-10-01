// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import type { Gap, SolveResponse, UnclosedStream } from '../types/mvs'

interface Props {
  solve: SolveResponse | null
  gaps: Gap[]
  unclosed: UnclosedStream[]
}

export function GapPanel({ solve, gaps, unclosed }: Props) {
  const energy = solve?.surplus?.energy
  return (
    <section className="panel gap-panel">
      <h2>Gaps / unclosed</h2>
      {solve && (
        <p className="solve-meta">
          Solve: <strong>{solve.status}</strong> · mvs_equivalent=
          <strong>{String(solve.mvs_equivalent)}</strong>
          {energy && (
            <>
              {' '}
              · energy surplus: {energy.value ?? 'null'} {energy.unit} (
              {energy.status}
              {energy.note ? ` — ${energy.note}` : ''})
            </>
          )}
        </p>
      )}
      <h3>Gaps ({gaps.length})</h3>
      {gaps.length === 0 ? (
        <p className="empty">No gaps from last solve/flags.</p>
      ) : (
        <ul>
          {gaps.map((g, i) => (
            <li key={i} className={g.reason === 'unreclaimed_resource' ? 'unreclaimed' : ''}>
              <code>{g.sector_id ?? g.stream_id ?? '—'}</code>{' '}
              <span className="reason">{g.reason}</span>
              {g.sector_definition && (
                <span className="muted"> / {g.sector_definition}</span>
              )}
              {g.detail && <div className="detail">{g.detail}</div>}
            </li>
          ))}
        </ul>
      )}
      <h3>Unclosed streams ({unclosed.length})</h3>
      {unclosed.length === 0 ? (
        <p className="empty">None reported.</p>
      ) : (
        <ul className="compact">
          {unclosed.map((u) => (
            <li key={u.stream_id}>
              <code>{u.stream_id}</code> {u.reason}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
