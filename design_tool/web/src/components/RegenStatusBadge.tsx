// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useEffect, useState } from 'react'
import { getRegenStatus } from '../api/client'
import type { RegenStatus } from '../types/design'

interface Props {
  /** Bump to re-check (e.g. after every solve). */
  refreshKey: number
}

/** Green/red regen staleness indicator for the header (GET /regen-status). */
export function RegenStatusBadge({ refreshKey }: Props) {
  const [status, setStatus] = useState<RegenStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getRegenStatus()
      .then((s) => {
        if (!cancelled) setStatus(s)
      })
      .catch((e) => {
        if (!cancelled) setError(String(e))
      })
    return () => {
      cancelled = true
    }
  }, [refreshKey])

  const ok = status?.ok === true
  const sha = status?.last_receipt?.graph_sha256 ?? null
  const passes = status?.last_receipt?.passes ?? null
  const title = status
    ? [
        status.command,
        `${status.files_checked ?? '?'} files checked, ${status.stale_count ?? '?'} stale`,
        status.gated_stale.length
          ? `gated stale: ${status.gated_stale.join(', ')}`
          : null,
        status.error ?? null,
        sha ? `receipt graph ${sha.slice(0, 12)} · ${passes ?? '?'} pass(es)` : null,
        status.receipt_error ?? null,
      ]
        .filter(Boolean)
        .join('\n')
    : (error ?? 'checking regen status…')

  return (
    <div
      className={`regen-badge ${ok ? 'ok' : 'bad'}`}
      title={title}
      aria-label={`regen status: ${ok ? 'current' : 'stale or unavailable'}`}
    >
      <span className="dot" aria-hidden="true" />
      {error ? (
        <span>regen check failed</span>
      ) : !status ? (
        <span>regen…</span>
      ) : ok ? (
        <span>
          regen current · {status.stale_count ?? 0} stale
          {sha ? ` · ${sha.slice(0, 8)}` : ''}
          {passes != null ? ` · ${passes} pass` : ''}
        </span>
      ) : (
        <span>
          regen STALE
          {status.stale_count != null ? ` · ${status.stale_count} stale` : ''}
          {status.error ? ' · check error' : ''}
        </span>
      )}
    </div>
  )
}
