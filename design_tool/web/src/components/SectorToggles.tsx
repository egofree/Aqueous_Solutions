// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import type { Sector } from '../types/mvs'

interface Props {
  sectors: Sector[]
  busy?: boolean
  onToggle: (sectorId: string, enabled: boolean) => void
}

export function SectorToggles({ sectors, busy, onToggle }: Props) {
  return (
    <section className="panel sector-toggles">
      <h2>Sectors</h2>
      <ul>
        {sectors.map((s) => (
          <li
            key={s.sector_id}
            className={
              !s.enabled && s.required_for_mvs_closure ? 'req-disabled' : ''
            }
          >
            <label>
              <input
                type="checkbox"
                checked={s.enabled}
                disabled={busy}
                onChange={(e) => onToggle(s.sector_id, e.target.checked)}
              />
              <span className="sid">{s.sector_id}</span>
              {s.required_for_mvs_closure && (
                <span className="badge req" title="required_for_mvs_closure">
                  req
                </span>
              )}
              {!s.enabled && s.required_for_mvs_closure && (
                <span className="badge gap" title="Gap — not silently omitted">
                  gap
                </span>
              )}
            </label>
            <span className="def">{s.sector_definition}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
