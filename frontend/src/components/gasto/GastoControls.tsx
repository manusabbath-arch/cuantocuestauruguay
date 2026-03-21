import { AlertCircle, ArrowUpDown, ExternalLink, HelpCircle, X } from 'lucide-react'
import type { GastoSortMode } from '../../lib/gasto'

interface GastoHelpPanelProps {
  onClose: () => void
}

export function GastoHelpPanel({ onClose }: GastoHelpPanelProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 relative">
      <button
        onClick={onClose}
        className="absolute top-3 right-3 text-blue-400 hover:text-blue-700 transition-colors"
        aria-label="Cerrar ayuda"
      >
        <X className="w-4 h-4" />
      </button>
      <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
        <HelpCircle className="w-4 h-4" />
        ¿Qué estoy viendo?
      </h3>
      <dl className="space-y-2 text-sm text-blue-800">
        <div>
          <dt className="font-semibold inline">Crédito vigente</dt>
          <dd className="inline ml-1">— Presupuesto total asignado al organismo para el año. Es el techo de gasto autorizado.</dd>
        </div>
        <div>
          <dt className="font-semibold inline">Ejecutado (Obligado)</dt>
          <dd className="inline ml-1">— Monto que ya generó una obligación de pago. Es el gasto efectivamente comprometido.</dd>
        </div>
        <div>
          <dt className="font-semibold inline">% Ejecución</dt>
          <dd className="inline ml-1">— Qué porcentaje del crédito vigente ya está ejecutado. No indica eficiencia; algunos organismos gastan en forma estacional.</dd>
        </div>
        <div>
          <dt className="font-semibold inline">Variación interanual</dt>
          <dd className="inline ml-1">— Diferencia de ejecutado respecto al mismo año anterior. Útil para detectar cambios de política.</dd>
        </div>
      </dl>
      <div className="mt-3 pt-3 border-t border-blue-200 text-xs text-blue-700">
        <AlertCircle className="w-3 h-3 inline mr-1" />
        <strong>Nota de comparabilidad:</strong> La serie 1999–2025 puede presentar inconsistencias por reclasificaciones institucionales (fusiones, creación de organismos). Se recomienda cautela al comparar períodos anteriores a 2005.
        {' '}<a
          href="https://presupuestonacional.gub.uy/node/29"
          target="_blank"
          rel="noopener noreferrer"
          className="underline inline-flex items-center gap-0.5"
        >
          Metodología oficial <ExternalLink className="w-2.5 h-2.5" />
        </a>
      </div>
    </div>
  )
}

interface GastoSortSelectorProps {
  mode: GastoSortMode
  onChange: (m: GastoSortMode) => void
}

export function GastoSortSelector({ mode, onChange }: GastoSortSelectorProps) {
  const options: { value: GastoSortMode; label: string }[] = [
    { value: 'presupuesto', label: 'Mayor presupuesto' },
    { value: 'ejecucion', label: 'Menor % ejecución' },
    { value: 'variacion', label: 'Mayor variación' },
  ]

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <ArrowUpDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
      <span className="text-sm text-gray-600 flex-shrink-0">Ordenar:</span>
      <div className="flex gap-1 flex-wrap">
        {options.map((o) => (
          <button
            key={o.value}
            onClick={() => onChange(o.value)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
              mode === o.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}

interface GastoYearSelectorProps {
  years: number[]
  selected: number | undefined
  onChange: (y: number | undefined) => void
}

export function GastoYearSelector({ years, selected, onChange }: GastoYearSelectorProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={() => onChange(undefined)}
        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
          selected === undefined
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        Todos
      </button>
      {years.map((y) => (
        <button
          key={y}
          onClick={() => onChange(y)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            selected === y
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {y}
        </button>
      ))}
    </div>
  )
}