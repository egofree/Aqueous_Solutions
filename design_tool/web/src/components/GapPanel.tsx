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
  const elec = solve?.electrical_match
  const elecStatus = elec?.status ?? null
  const elecClass =
    elecStatus === 'envelope_ok_study'
      ? 'ok'
      : elecStatus === 'shortfall_study'
        ? 'bad'
        : 'warn'
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
      {elec && (
        <div className={`elec-envelope ${elecClass}`}>
          <span className="elec-status">
            electrical envelope:{' '}
            <strong>{elecStatus ?? '—'}</strong>
          </span>
          <span className="elec-nums">
            gen {elec.generation_kw_study ?? '—'} · storage{' '}
            {elec.storage_power_kw_study ?? '—'} · load{' '}
            {elec.load_kw_study ?? '—'} · need {elec.need_kw ?? '—'} kW ·
            target {elec.target_kw ?? '—'} kW
            {elec.pv_nameplate_kw_study != null
              ? ` · PV ${elec.pv_nameplate_kw_study} kWp`
              : ''}
          </span>
          {elec.note && <span className="elec-note">{elec.note}</span>}
        </div>
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
