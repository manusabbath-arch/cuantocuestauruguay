import api from './api'
import type { BillAnalysisResponse, BillHistoryEntry } from '../types/factura'

const HISTORY_KEY = 'bill_history'
const MAX_HISTORY = 12

export const facturasService = {
  analyze: async (file: File): Promise<BillAnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/api/v1/facturas/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    })
    return response.data
  },
}

export const billHistory = {
  save(analysis: BillAnalysisResponse): void {
    const entries = billHistory.getAll()
    const entry: BillHistoryEntry = {
      id: crypto.randomUUID(),
      analyzedAt: new Date().toISOString(),
      servicio: analysis.servicio,
      periodo: analysis.periodo,
      consumo: analysis.consumo.valor,
      unidad: analysis.consumo.unidad,
      total: analysis.cargos.total,
      analysis,
    }
    entries.unshift(entry)
    if (entries.length > MAX_HISTORY) entries.length = MAX_HISTORY
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(entries))
    } catch {
      // localStorage full or unavailable — silently fail
    }
  },

  getAll(): BillHistoryEntry[] {
    try {
      const raw = localStorage.getItem(HISTORY_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  },

  remove(id: string): void {
    const entries = billHistory.getAll().filter((e) => e.id !== id)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(entries))
  },

  clear(): void {
    localStorage.removeItem(HISTORY_KEY)
  },
}
