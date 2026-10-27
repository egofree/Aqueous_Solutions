// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useEffect, useState } from 'react'
import {
  createSandboxFromSite,
  listSites,
  solveSandboxPipeline,
} from '../api/client'
import type { SolveResponse } from '../types/mvs'

interface SiteInfo {
  site_id: string
  actions: number
  eliminations: number
  error?: string
}

interface SiteSandboxResponse {
  sandbox_id: string
  label: string
  site_id: string
  applied: string[]
  unapplied: string[]
  replacement_of: Record<string, string>
  model: { units: { unit_id: string; enabled: boolean }[] }
}

/** X-UI-002 Phase 1: start a sandbox from a locale scaling profile, then run the
 * real pipeline solve on the fold. A closed subset is reported as closed WITH the
 * function-loss note - never as equivalent to the baseline. CERN-OHL-S-2.0. */
export function SitePanel(props: {
  onSandbox: (sandboxId: string, model: unknown) => void
}) {
  const [sites, setSites] = useState<SiteInfo[]>([])
  const [picked, setPicked] = useState<string>('')
  const [created, setCreated] = useState<SiteSandboxResponse | null>(null)
  const [solve, setSolve] = useState<SolveResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listSites()
      .then((r) => {
        setSites(r.sites)
        if (r.sites.length) setPicked(r.sites[0].site_id)
      })
      .catch((e) => setError(String(e)))
  }, [])

  const create = () => {
    setBusy(true)
    setError(null)
    createSandboxFromSite(picked)
      .then((r) => {
        setCreated(r)
        props.onSandbox(r.sandbox_id, r.model)
      })
      .catch((e) => setError(String(e)))
      .finally(() => setBusy(false))
  }

  const runPipeline = () => {
    if (!created) return
    setBusy(true)
    setError(null)
    solveSandboxPipeline(created.sandbox_id)
      .then(setSolve)
      .catch((e) => setError(String(e)))
      .finally(() => setBusy(false))
  }

  return (
    <section className="panel" aria-label="site profiles">
      <h2>Site profiles</h2>
      <p className="muted">
        A locale scaling profile becomes a sandbox: the scaling engine's own resolved
        plan applies the eliminations and replacements.
      </p>
      <div className="row">
        <select
          value={picked}
          onChange={(e) => setPicked(e.target.value)}
          aria-label="site profile"
        >
          {sites.map((s) => (
            <option key={s.site_id} value={s.site_id}>
              {s.site_id} ({s.actions} actions)
            </option>
          ))}
        </select>
        <button onClick={create} disabled={busy || !picked}>
          New site sandbox
        </button>
        <button onClick={runPipeline} disabled={busy || !created}>
          Solve pipeline
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {created && (
        <>
          <h3>{created.label}</h3>
          <p>
            {created.applied.length} applied
            {created.unapplied.length > 0 && (
              <>; {created.unapplied.length} unapplied (no sandbox equivalent yet)</>
            )}
          </p>
          <details>
            <summary>applied actions</summary>
            <ul>
              {created.applied.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          </details>
          {Object.keys(created.replacement_of).length > 0 && (
            <details>
              <summary>replacements</summary>
              <ul>
                {Object.entries(created.replacement_of).map(([u, r]) => (
                  <li key={u}>
                    {u} → {r}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
      {solve && (
        <>
          <h3>pipeline solve</h3>
          <p>
            status <strong>{solve.status}</strong>
            {(solve.residuals?.mass?.length ?? 0) > 0 && (
              <>; {solve.residuals?.mass?.length} unclosed node(s)</>
            )}
          </p>
          <ul>
            {(solve.residuals?.mass ?? []).slice(0, 8).map((r) => (
              <li key={r.id}>
                {r.id}: {r.residual} {r.unit}
              </li>
            ))}
          </ul>
          {solve.gaps.map((g, i) => (
            <p className="muted" key={i}>
              {g.reason}
            </p>
          ))}
        </>
      )}
    </section>
  )
}
