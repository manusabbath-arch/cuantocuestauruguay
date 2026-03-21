import { TrendingUp, TrendingDown, Building2, AlertCircle } from 'lucide-react'
import { useGastoNarrativa } from '../hooks/useGasto'

interface Props {
  anio?: number
}

export default function NarrativaGasto({ anio }: Props) {
  const { data, isLoading, isError } = useGastoNarrativa(anio)

  if (isLoading) {
    return (
      <div className="bg-blue-50 border border-blue-100 rounded-xl p-5 animate-pulse">
        <div className="h-4 bg-blue-200 rounded w-3/4 mb-3" />
        <div className="h-4 bg-blue-200 rounded w-1/2" />
      </div>
    )
  }

  if (isError || !data) return null

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-5 space-y-3">
      {/* Resumen global */}
      <p className="text-sm font-medium text-blue-900 leading-relaxed">
        {data.resumen_global}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
        {/* Mayor gasto */}
        <div className="flex items-start gap-2 bg-white/60 rounded-lg p-3">
          <Building2 className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-700">{data.mayor_gasto.frase}</p>
        </div>

        {/* Menor ejecucion */}
        {data.menor_ejecucion && (
          <div className="flex items-start gap-2 bg-white/60 rounded-lg p-3">
            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-700">{data.menor_ejecucion.frase}</p>
          </div>
        )}

        {/* Mayor crecimiento */}
        {data.mayor_crecimiento && (
          <div className="flex items-start gap-2 bg-white/60 rounded-lg p-3">
            <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-700">
              Mayor crecimiento vs año anterior:{' '}
              <span className="font-medium">{data.mayor_crecimiento.nombre}</span>
              {' '}(+{data.mayor_crecimiento.variacion_pct}%).
            </p>
          </div>
        )}

        {/* Mayor caida */}
        {data.mayor_caida && (
          <div className="flex items-start gap-2 bg-white/60 rounded-lg p-3">
            <TrendingDown className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-700">
              Mayor caída vs año anterior:{' '}
              <span className="font-medium">{data.mayor_caida.nombre}</span>
              {' '}({data.mayor_caida.variacion_pct}%).
            </p>
          </div>
        )}
      </div>

      <p className="text-xs text-blue-400">
        Basado en {data.organismos_analizados} organismos · datos MEF
      </p>
    </div>
  )
}
