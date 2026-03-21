/**
 * Servicio centralizado para API de Gasto Público (MEF)
 * 
 * Patrones:
 * - Uso de URL params en lugar de body
 * - Tipificación completa
 * - Manejo consistente de errores
 * - Compatible con TanStack Query
 */

import { api } from './api'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Organismo {
  inciso: string
  nombre_organismo: string
  ultimo_anio: number
}

export interface EjecucionPresupuestal {
  id: number
  anio: number
  mes: number | null
  inciso: string
  nombre_organismo: string
  credito_vigente: number
  ejecutado: number
  porcentaje_ejecucion: number | null
  fuente: string
}

export interface ComparacionAnual {
  inciso: string
  nombre_organismo: string
  anio_base: number
  anio_comparacion: number
  ejecutado_base: number
  ejecutado_comparacion: number
  credito_base: number
  credito_comparacion: number
  variacion_ejecutado: number | null
}

export interface GastoFilters {
  anio?: number
  inciso?: string
  mes?: number | null
  limit?: number
}

// ---------------------------------------------------------------------------
// API Service
// ---------------------------------------------------------------------------

export const gastoService = {
  /**
   * Obtener lista de organismos con sus últimos años disponibles
   */
  getOrganismos: async (anio?: number): Promise<Organismo[]> => {
    const params = anio ? { anio } : {}
    const { data } = await api.get<Organismo[]>('/api/v1/gasto/organismos', { params })
    return data
  },

  /**
   * Obtener registros de ejecución presupuestal con filtros opcionales
   */
  getEjecucion: async (filters: GastoFilters = {}): Promise<EjecucionPresupuestal[]> => {
    const params: Record<string, unknown> = { limit: filters.limit ?? 200 }
    if (filters.anio) params.anio = filters.anio
    if (filters.inciso) params.inciso = filters.inciso
    if (filters.mes !== undefined) params.mes = filters.mes

    const { data } = await api.get<EjecucionPresupuestal[]>('/api/v1/gasto/ejecucion', { params })
    return data
  },

  /**
   * Obtener comparación interanual de ejecución para un organismo
   */
  getComparacionAnual: async (inciso: string): Promise<ComparacionAnual> => {
    const params = { inciso }
    const { data } = await api.get<ComparacionAnual>('/api/v1/gasto/comparacion-anual', { params })
    return data
  },

  /**
   * Ejecutar ETL manual de gasto público (si autorizado)
   */
  runETL: async (): Promise<{ success: boolean; message: string }> => {
    const { data } = await api.post<{ success: boolean; message: string }>('/api/v1/etl/gasto/run')
    return data
  },
}

// ---------------------------------------------------------------------------
// Query Key Factory (para TanStack Query)
// ---------------------------------------------------------------------------

export const gastoQueryKeys = {
  all: ['gasto'] as const,
  
  organismos: () => [...gastoQueryKeys.all, 'organismos'] as const,
  organismosByAño: (anio: number) => [...gastoQueryKeys.organismos(), anio] as const,
  
  ejecucion: () => [...gastoQueryKeys.all, 'ejecucion'] as const,
  ejecucionWithFilters: (filters: GastoFilters) =>
    [...gastoQueryKeys.ejecucion(), filters] as const,
  
  comparacion: () => [...gastoQueryKeys.all, 'comparacion'] as const,
  comparacionByInciso: (inciso: string) =>
    [...gastoQueryKeys.comparacion(), inciso] as const,
}
