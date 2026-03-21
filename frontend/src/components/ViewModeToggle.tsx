import type { ViewMode } from '../hooks/usePersistentViewMode'

interface ViewModeToggleProps {
  viewMode: ViewMode
  onChange: (mode: ViewMode) => void
  className?: string
}

export default function ViewModeToggle({ viewMode, onChange, className = '' }: ViewModeToggleProps) {
  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-4 ${className}`.trim()}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold text-gray-900">Modo de visualización</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Resumen simplifica la vista; Explorar muestra controles y detalle analítico.
          </p>
        </div>
        <div className="inline-flex rounded-lg bg-gray-100 p-1 w-fit">
          <button
            onClick={() => onChange('resumen')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'resumen'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Resumen
          </button>
          <button
            onClick={() => onChange('explorar')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'explorar'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Explorar
          </button>
        </div>
      </div>
    </div>
  )
}