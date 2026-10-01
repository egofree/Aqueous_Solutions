// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.

interface Props {
  cycles: string[]
  active: string | null
  onChange: (cycle: string | null) => void
}

export function CycleViews({ cycles, active, onChange }: Props) {
  const list = cycles.length ? cycles : ['C', 'O', 'H2O', 'H2', 'N', 'heat']
  return (
    <section className="panel cycle-views">
      <h2>Cycle view</h2>
      <div className="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={active === null}
          className={active === null ? 'active' : ''}
          onClick={() => onChange(null)}
        >
          All
        </button>
        {list.map((c) => (
          <button
            key={c}
            type="button"
            role="tab"
            aria-selected={active === c}
            className={active === c ? 'active' : ''}
            onClick={() => onChange(c)}
          >
            {c === 'H2O' ? 'H₂O' : c}
          </button>
        ))}
      </div>
      <p className="hint">
        Active cycle: heavier stroke. Off-cycle streams grey. Existing streams
        only — no invented edges.
      </p>
    </section>
  )
}
