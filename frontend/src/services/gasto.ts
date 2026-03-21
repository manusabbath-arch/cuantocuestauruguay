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

export type AnomalíaTipo = 'ejecucion_baja' | 'variacion_atipica' | 'dato_faltante'
export type AnomalíaSeveridad = 'CRITICA' | 'ALTA' | 'MEDIA' | 'BAJA'

export interface AnomaliaPresupuestal {
  id: number
  anio: number
  mes: number | null
  inciso: string
  nombre_organismo: string
  tipo: AnomalíaTipo
  severidad: AnomalíaSeveridad
  descripcion: string
  valor_observado: number | null
  valor_umbral: number | null
  detectado_en: string
}

export interface AnomaliaFilters {
  anio?: number
  mes?: number | null
  severidad?: AnomalíaSeveridad
  tipo?: AnomalíaTipo
  limit?: number
}

export interface NarrativaOrganismo {
  nombre: string
  ejecutado?: number
  porcentaje_ejecucion?: number | null
  variacion_pct?: number
  frase?: string
}

export interface NarrativaGasto {
  anio: number
  sin_datos: boolean
  total_presupuestado: number
  total_ejecutado: number
  porcentaje_global: number | null
  organismos_analizados: number
  resumen_global: string
  mayor_gasto: NarrativaOrganismo & { frase: string }
  menor_ejecucion: (NarrativaOrganismo & { frase: string }) | null
  mayor_crecimiento: NarrativaOrganismo | null
  mayor_caida: NarrativaOrganismo | null
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
   * Obtener señales de anomalías detectadas
   */
  getAnomalias: async (filters: AnomaliaFilters = {}): Promise<AnomaliaPresupuestal[]> => {
    const params: Record<string, unknown> = { limit: filters.limit ?? 100 }
    if (filters.anio) params.anio = filters.anio
    if (filters.mes !== undefined) params.mes = filters.mes
    if (filters.severidad) params.severidad = filters.severidad
    if (filters.tipo) params.tipo = filters.tipo
    const { data } = await api.get<AnomaliaPresupuestal[]>('/api/v1/gasto/anomalias', { params })
    return data
  },

  /**
   * Obtener narrativa automatica para un año (usa el mas reciente si no se especifica)
   */
  getNarrativa: async (anio?: number): Promise<NarrativaGasto> => {
    const params = anio ? { anio } : {}
    const { data } = await api.get<NarrativaGasto>('/api/v1/gasto/narrativa', { params })
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

  narrativa: () => [...gastoQueryKeys.all, 'narrativa'] as const,
  narrativaByAnio: (anio?: number) => [...gastoQueryKeys.narrativa(), anio] as const,

  anomalias: () => [...gastoQueryKeys.all, 'anomalias'] as const,
  anomaliasWithFilters: (filters: AnomaliaFilters) =>
    [...gastoQueryKeys.anomalias(), filters] as const,
}
