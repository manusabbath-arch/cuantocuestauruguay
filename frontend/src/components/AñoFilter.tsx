/**
 * Filtro reutilizable para seleccionar años
 * 
 * - Soporte para rango de años
 * - Valor por defecto = año actual
 */

import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

interface AñoFilterProps {
  selectedYear: number
  onChangeYear: (year: number) => void
  minYear?: number
  maxYear?: number
}

export function AñoFilter({
  selectedYear,
  onChangeYear,
  minYear = 2020,
  maxYear = new Date().getFullYear(),
}: AñoFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const years = Array.from({ length: maxYear - minYear + 1 }, (_, i) => maxYear - i)

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="text-sm font-semibold text-gray-900">Año</div>
          <div className="text-sm text-blue-600 font-medium">{selectedYear}</div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200 p-3">
          <div className="grid grid-cols-3 gap-2">
            {years.map((year) => (
              <button
                key={year}
                onClick={() => {
                  onChangeYear(year)
                  setIsExpanded(false)
                }}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  selectedYear === year
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {year}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
