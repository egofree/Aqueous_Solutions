// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
/**
 * Deterministic schematic layout: grid units by sector.
 * No invented coordinates in MVS — layout is UI-only.
 */
import type { Sector, Stream, Unit } from '../types/mvs'

export interface Point {
  x: number
  y: number
}

export interface LayoutResult {
  unitPos: Record<string, Point>
  sectorBands: { sector_id: string; x: number; label: string }[]
  width: number
  height: number
}

const BOX_W = 110
const BOX_H = 36
const COL_GAP = 28
const ROW_GAP = 18
const PAD = 40
const COLS_PER_SECTOR = 2

export { BOX_W, BOX_H }

export function layoutBySector(
  units: Unit[],
  sectors: Sector[],
): LayoutResult {
  const sectorOrder = sectors.map((s) => s.sector_id)
  const bySector = new Map<string, Unit[]>()
  for (const u of units) {
    const list = bySector.get(u.sector_id) ?? []
    list.push(u)
    bySector.set(u.sector_id, list)
  }
  // Stable sort units within sector
  for (const list of bySector.values()) {
    list.sort((a, b) => a.unit_id.localeCompare(b.unit_id))
  }

  const unitPos: Record<string, Point> = {}
  const sectorBands: LayoutResult['sectorBands'] = []
  let col = 0
  let maxY = PAD

  for (const sid of sectorOrder) {
    const list = bySector.get(sid) ?? []
    if (list.length === 0) continue
    const bandX = PAD + col * (BOX_W * COLS_PER_SECTOR + COL_GAP * 2 + 24)
    sectorBands.push({ sector_id: sid, x: bandX, label: sid })
    list.forEach((u, i) => {
      const localCol = i % COLS_PER_SECTOR
      const localRow = Math.floor(i / COLS_PER_SECTOR)
      const x = bandX + localCol * (BOX_W + COL_GAP)
      const y = PAD + 28 + localRow * (BOX_H + ROW_GAP)
      unitPos[u.unit_id] = { x, y }
      maxY = Math.max(maxY, y + BOX_H)
    })
    col += 1
  }

  // Orphan units (sector not in sector list)
  const placed = new Set(Object.keys(unitPos))
  const orphans = units.filter((u) => !placed.has(u.unit_id))
  if (orphans.length) {
    const bandX = PAD + col * (BOX_W * COLS_PER_SECTOR + COL_GAP * 2 + 24)
    sectorBands.push({ sector_id: '_OTHER', x: bandX, label: 'OTHER' })
    orphans
      .sort((a, b) => a.unit_id.localeCompare(b.unit_id))
      .forEach((u, i) => {
        const localCol = i % COLS_PER_SECTOR
        const localRow = Math.floor(i / COLS_PER_SECTOR)
        const x = bandX + localCol * (BOX_W + COL_GAP)
        const y = PAD + 28 + localRow * (BOX_H + ROW_GAP)
        unitPos[u.unit_id] = { x, y }
        maxY = Math.max(maxY, y + BOX_H)
      })
    col += 1
  }

  const width = Math.max(
    800,
    PAD * 2 + col * (BOX_W * COLS_PER_SECTOR + COL_GAP * 2 + 24),
  )
  const height = Math.max(480, maxY + PAD)
  return { unitPos, sectorBands, width, height }
}

/** Map cycle view id → substrings matched against stream.carries (case-insensitive). */
const CYCLE_MATCH: Record<string, string[]> = {
  C: ['co2', 'carbon', 'organics', 'meoh', 'methanol', 'food', 'scrap'],
  O: ['o2', 'oxygen', 'photosynthetic'],
  H2O: ['h2o', 'upw', 'water', 'potable', 'distillate', 'brine', 'grey', 'sump', 'overflow', 'tower', 'pem product'],
  H2: ['h2', 'hydrogen'],
  N: ['n2', 'nitrogen'],
  heat: ['heat', 'q4', 'thermal'],
}

export function streamMatchesCycle(
  stream: Stream,
  cycle: string | null,
): boolean {
  if (!cycle) return true
  const carries = (stream.carries ?? '').toLowerCase()
  const keys = CYCLE_MATCH[cycle] ?? [cycle.toLowerCase()]
  // H2 must not match H2O falsely — check H2O cycle separately
  if (cycle === 'H2') {
    if (/\bh2o\b/.test(carries) || carries.includes('water') || carries.includes('upw')) {
      // only match if also has H2 fuel / process H2 etc without being pure water
      return /\bh2\b/.test(carries) && !/^(upw|potable|.*water.*)$/.test(carries)
    }
    return keys.some((k) => carries.includes(k))
  }
  return keys.some((k) => carries.includes(k))
}
