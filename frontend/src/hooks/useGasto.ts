/**
 * Custom hook para gestionar estado de Gasto Público
 * 
 * Encapsula:
 * - Queries a API con TanStack Query
 * - Estados de loading/error
 * - Lógica común de filtros
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query'
import {
  gastoService,
  gastoQueryKeys,
  type Organismo,
  type EjecucionPresupuestal,
  type ComparacionAnual,
  type GastoFilters,
} from '../services/gasto'

// ---------------------------------------------------------------------------
// useGasto Hook - Interfaz simplificada
// ---------------------------------------------------------------------------

interface UseGastoReturn {
  organismos: UseQueryResult<Organismo[], Error>
  ejecucion: UseQueryResult<EjecucionPresupuestal[], Error>
  comparacion: UseQueryResult<ComparacionAnual, Error>
  isLoading: boolean
  isError: boolean
  refetch: () => void
}

/**
 * Hook principal para gestionar todas las queries de gasto
 * 
 * @param anio Año para filtrar (opcional)
 * @param inciso Inciso/organismo para filtrar (opcional)
 * @param mes Mes para filtrar (opcional)
 * @returns Objeto con queries de organismos, ejecucion y comparacion
 * 
 * @example
 * const { organismos, ejecucion, isLoading } = useGasto({ anio: 2023 })
 */
export function useGasto(filters?: GastoFilters & { comparisonInciso?: string }): UseGastoReturn {
  const anio = filters?.anio ?? new Date().getFullYear()
  const inciso = filters?.inciso
  const comparisonInciso = filters?.comparisonInciso

  // Organismos disponibles
  const organismos = useQuery({
    queryKey: anio ? gastoQueryKeys.organismosByAño(anio) : gastoQueryKeys.organismos(),
    queryFn: () => gastoService.getOrganismos(anio),
    staleTime: 1000 * 60 * 10, // 10 minutos
    gcTime: 1000 * 60 * 30, // 30 minutos (formerly cacheTime)
  })

  // Ejecución presupuestal
  const ejecucion = useQuery({
    queryKey: gastoQueryKeys.ejecucionWithFilters({
      anio,
      inciso,
      mes: filters?.mes,
      limit: filters?.limit,
    }),
    queryFn: () =>
      gastoService.getEjecucion({
        anio,
        inciso,
        mes: filters?.mes,
        limit: filters?.limit,
      }),
    staleTime: 1000 * 60 * 5, // 5 minutos
    gcTime: 1000 * 60 * 15, // 15 minutos
    enabled: !!anio, // Solo ejecutar si hay año
  })

  // Comparación interanual
  const comparacion = useQuery({
    queryKey: comparisonInciso
      ? gastoQueryKeys.comparacionByInciso(comparisonInciso)
      : ['gasto', 'comparacion', 'disabled'],
    queryFn: () => gastoService.getComparacionAnual(comparisonInciso!),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
    enabled: !!comparisonInciso, // Solo ejecutar si hay inciso
  })

  return {
    organismos,
    ejecucion,
    comparacion,
    isLoading: organismos.isLoading || ejecucion.isLoading || comparacion.isLoading,
    isError: organismos.isError || ejecucion.isError || comparacion.isError,
    refetch: () => {
      organismos.refetch()
      ejecucion.refetch()
      comparacion.refetch()
    },
  }
}

// ---------------------------------------------------------------------------
// useGastoOrganismos Hook - Solo organismos
// ---------------------------------------------------------------------------

/**
 * Hook para obtener solo la lista de organismos
 * 
 * @example
 * const { data: organismos, isLoading } = useGastoOrganismos()
 */
export function useGastoOrganismos(anio?: number) {
  return useQuery({
    queryKey: anio ? gastoQueryKeys.organismosByAño(anio) : gastoQueryKeys.organismos(),
    queryFn: () => gastoService.getOrganismos(anio),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  })
}

// ---------------------------------------------------------------------------
// useGastoEjecucion Hook - Solo ejecución con filtros
// ---------------------------------------------------------------------------

/**
 * Hook para obtener ejecución presupuestal con filtros opcionales
 * 
 * @example
 * const { data, isLoading } = useGastoEjecucion({ anio: 2023, inciso: '05' })
 */
export function useGastoEjecucion(filters: GastoFilters = {}) {
  return useQuery({
    queryKey: gastoQueryKeys.ejecucionWithFilters(filters),
    queryFn: () => gastoService.getEjecucion(filters),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 15,
    enabled: !!filters.anio || Object.keys(filters).length === 0,
  })
}

// ---------------------------------------------------------------------------
// useGastoComparacion Hook - Solo comparación interanual
// ---------------------------------------------------------------------------

/**
 * Hook para obtener comparación interanual de un organismo
 * 
 * @param inciso Código de inciso/organismo
 * @example
 * const { data, isLoading } = useGastoComparacion('02')
 */
export function useGastoComparacion(inciso?: string) {
  return useQuery({
    queryKey: inciso ? gastoQueryKeys.comparacionByInciso(inciso) : ['gasto', 'comparacion', 'disabled'],
    queryFn: () => gastoService.getComparacionAnual(inciso!),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
    enabled: !!inciso,
  })
}
