// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import { useEffect, useState, type FormEvent } from 'react'

interface Props {
  crew: number | null
  siteLatDeg: number | null
  busy?: boolean
  onApply: (crew: number | null, siteLat: number | null, clearLat: boolean) => void
}

/**
 * Crew + SITE_LAT. Empty SITE_LAT does not invent a latitude — leave null
 * so solver keeps energy surplus unknown/study (AQS-UI-001 / AQS-SUR-001).
 */
export function SiteInputs({ crew, siteLatDeg, busy, onApply }: Props) {
  const [crewStr, setCrewStr] = useState(crew != null ? String(crew) : '')
  const [latStr, setLatStr] = useState(
    siteLatDeg != null ? String(siteLatDeg) : '',
  )

  useEffect(() => {
    setCrewStr(crew != null ? String(crew) : '')
  }, [crew])
  useEffect(() => {
    setLatStr(siteLatDeg != null ? String(siteLatDeg) : '')
  }, [siteLatDeg])

  function submit(e: FormEvent) {
    e.preventDefault()
    const c = crewStr.trim() === '' ? null : Number(crewStr)
    const latEmpty = latStr.trim() === ''
    const lat = latEmpty ? null : Number(latStr)
    if (c != null && !Number.isFinite(c)) return
    if (lat != null && !Number.isFinite(lat)) return
    onApply(c, lat, latEmpty)
  }

  return (
    <section className="panel site-inputs">
      <h2>Site</h2>
      <form onSubmit={submit}>
        <label>
          Crew
          <input
            type="number"
            min={0}
            step={1}
            value={crewStr}
            disabled={busy}
            onChange={(e) => setCrewStr(e.target.value)}
          />
        </label>
        <label>
          SITE_LAT (°)
          <input
            type="number"
            step="any"
            placeholder="empty = null / unknown"
            value={latStr}
            disabled={busy}
            onChange={(e) => setLatStr(e.target.value)}
          />
        </label>
        <button type="submit" disabled={busy}>
          Apply + solve
        </button>
      </form>
      <p className="hint">
        Null/empty SITE_LAT keeps energy surplus unknown/study — do not invent
        latitude.
      </p>
    </section>
  )
}
