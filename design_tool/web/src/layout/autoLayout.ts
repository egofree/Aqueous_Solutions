// SPDX-License-Identifier: CERN-OHL-S-2.0
// Copyright 2026 Mike Matthews.
/**
 * Deterministic schematic layout: grid units by sector, adaptive column count
 * (squarer bands read better at 200+ units than a fixed strip). No invented
 * coordinates in MVS — layout is UI-only, a reading aid that carries no dimension.
 */
import type { Sector, Unit } from '../types/mvs'

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

export const BOX_W = 130
export const BOX_H = 36
const COL_GAP = 24
const ROW_GAP = 16
const PAD = 40
const BAND_GAP = 60

/** Cycle filter helper (kept here so the layout module owns the schematic math). */
export function streamMatchesCycle(
  st: { stream_id: string },
  cycle: string | null,
): boolean {
  return cycle == null || st.stream_id.startsWith(cycle)
}

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
  for (const list of bySector.values()) {
    list.sort((a, b) => a.unit_id.localeCompare(b.unit_id))
  }

  const unitPos: Record<string, Point> = {}
  const sectorBands: LayoutResult['sectorBands'] = []
  let bandX = PAD
  let maxY = PAD

  const placed = new Set<string>()
  for (const sid of sectorOrder) {
    const list = (bySector.get(sid) ?? []).filter((u) => !placed.has(u.unit_id))
    if (list.length === 0) continue
    // adaptive columns: a squarer band per sector
    const cols = Math.min(8, Math.max(2, Math.ceil(Math.sqrt((list.length * BOX_W) / 110))))
    const bandW = cols * (BOX_W + COL_GAP)
    sectorBands.push({ sector_id: sid, x: bandX, label: sid })
    list.forEach((u, i) => {
      const localCol = i % cols
      const localRow = Math.floor(i / cols)
      unitPos[u.unit_id] = {
        x: bandX + localCol * (BOX_W + COL_GAP),
        y: PAD + 28 + localRow * (BOX_H + ROW_GAP),
      }
      placed.add(u.unit_id)
      maxY = Math.max(maxY, PAD + 28 + localRow * (BOX_H + ROW_GAP) + BOX_H)
    })
    bandX += bandW + BAND_GAP
  }

  // Orphan units (sector not in the sector list)
  const orphans = units.filter((u) => !placed.has(u.unit_id))
  if (orphans.length) {
    sectorBands.push({ sector_id: '_OTHER', x: bandX, label: 'OTHER' })
    const cols = Math.min(8, Math.max(2, Math.ceil(Math.sqrt((orphans.length * BOX_W) / 110))))
    orphans
      .sort((a, b) => a.unit_id.localeCompare(b.unit_id))
      .forEach((u, i) => {
        unitPos[u.unit_id] = {
          x: bandX + (i % cols) * (BOX_W + COL_GAP),
          y: PAD + 28 + Math.floor(i / cols) * (BOX_H + ROW_GAP),
        }
        maxY = Math.max(maxY, PAD + 28 + Math.floor(i / cols) * (BOX_H + ROW_GAP) + BOX_H)
      })
    bandX += cols * (BOX_W + COL_GAP) + BAND_GAP
  }

  return { unitPos, sectorBands, width: bandX, height: maxY + PAD }
}
