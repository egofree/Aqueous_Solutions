// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
import type { ExportResponse } from '../types/mvs'

interface Props {
  busy?: boolean
  last: ExportResponse | null
  error?: string | null
  onExport: () => void
}

const P0_MODULES = ['params', 'streams', 'gaps', 'compliance_flags']

export function ExportButton({ busy, last, error, onExport }: Props) {
  return (
    <section className="panel export-panel">
      <h2>Export</h2>
      <p className="hint">
        Pack from <strong>graph snapshot</strong> + sandbox overlay. Modules:{' '}
        {P0_MODULES.join(', ')}. Writes under <code>exports/</code> — never
        overwrites plant_flow_graph or MVS gold.
      </p>
      <button type="button" disabled={busy} onClick={onExport}>
        Export pack
      </button>
      {error && <p className="error">{error}</p>}
      {last && (
        <div className="export-ok">
          <p>
            Pack: <code>{last.pack_dir}</code>
          </p>
          <ul>
            {last.files.map((f) => (
              <li key={f}>
                <code>{f}</code>
              </li>
            ))}
          </ul>
          {last.notes?.length > 0 && (
            <ul className="notes">
              {last.notes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  )
}

export { P0_MODULES }
