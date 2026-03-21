/**
 * Filtro reutilizable para seleccionar organismos (incisos)
 * 
 * Inspirado en patrón USAspending AutocompleteFilterCheckbox
 * - Soporta búsqueda por nombre
 * - Multiselect con checkboxes
 * - Estados loading/error
 */

import { useState, useMemo } from 'react'
import { Search, ChevronDown, ChevronUp } from 'lucide-react'
import { useGastoOrganismos } from '../hooks/useGasto'

interface OrganismoFilterProps {
  selectedIncisos: string[]
  onToggle: (inciso: string) => void
  onToggleAll?: (incisos: string[]) => void
  anio?: number
  maxHeight?: number
}

export function OrganismoFilter({
  selectedIncisos,
  onToggle,
  onToggleAll,
  anio,
  maxHeight = 400,
}: OrganismoFilterProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const { data: organismos = [], isLoading, isError } = useGastoOrganismos(anio)

  // Filtrar organismos por búsqueda
  const filteredOrganismos = useMemo(() => {
    if (!searchTerm.trim()) return organismos

    const term = searchTerm.toLowerCase()
    return organismos.filter(
      (org) =>
        org.nombre_organismo.toLowerCase().includes(term) ||
        org.inciso.includes(term),
    )
  }, [organismos, searchTerm])

  const allSelected = organismos.length > 0 && selectedIncisos.length === organismos.length
  const someSelected = selectedIncisos.length > 0 && selectedIncisos.length < organismos.length

  const handleToggleAll = () => {
    if (onToggleAll) {
      onToggleAll(allSelected ? [] : organismos.map((o) => o.inciso))
    } else {
      organismos.forEach((org) => {
        if (!allSelected) {
          onToggle(org.inciso)
        } else if (selectedIncisos.includes(org.inciso)) {
          onToggle(org.inciso)
        }
      })
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className="text-sm font-semibold text-gray-900">
            Organismos {selectedIncisos.length > 0 && <span className="text-blue-600">({selectedIncisos.length})</span>}
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {/* Contenido expandible */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-3 space-y-3">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar organismo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Estados */}
          {isLoading && <div className="text-center py-4 text-gray-500 text-sm">Cargando organismos...</div>}

          {isError && (
            <div className="bg-red-50 border border-red-200 rounded p-2 text-sm text-red-700">
              Error al cargar organismos
            </div>
          )}

          {!isLoading && organismos.length === 0 && (
            <div className="text-center py-4 text-gray-500 text-sm">Sin organismos disponibles</div>
          )}

          {!isLoading && organismos.length > 0 && (
            <>
              {/* Seleccionar todos */}
              <label className="flex items-center gap-2 px-2 py-1 hover:bg-gray-50 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) {
                      el.indeterminate = someSelected
                    }
                  }}
                  onChange={handleToggleAll}
                  className="rounded w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">Seleccionar todos</span>
              </label>

              {/* Lista de organismos */}
              <div
                className="space-y-1 overflow-y-auto"
                style={{ maxHeight: `${maxHeight}px` }}
              >
                {filteredOrganismos.map((org) => (
                  <label
                    key={org.inciso}
                    className="flex items-start gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedIncisos.includes(org.inciso)}
                      onChange={() => onToggle(org.inciso)}
                      className="rounded w-4 h-4 mt-0.5"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {org.nombre_organismo}
                      </div>
                      <div className="text-xs text-gray-500">Código: {org.inciso}</div>
                    </div>
                  </label>
                ))}
              </div>

              {filteredOrganismos.length === 0 && searchTerm.trim() && (
                <div className="text-center py-3 text-gray-500 text-sm">
                  No se encontraron organismos
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
