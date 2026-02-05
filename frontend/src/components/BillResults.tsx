import { Zap, Calendar, DollarSign, Target, TrendingDown } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import type { BillAnalysisResponse } from '../types/factura'
import RecommendationCard from './RecommendationCard'

interface BillResultsProps {
  analysis: BillAnalysisResponse
  onReset: () => void
}

const CONSUMO_PROMEDIOS = {
  muy_bajo: 100,
  bajo: 150,
  promedio: 225,
  alto: 400,
  muy_alto: 600,
}

function ConsumptionGauge({ consumo, percentil }: { consumo: number; percentil: number }) {
  const position = Math.min(100, Math.max(0, (consumo / CONSUMO_PROMEDIOS.muy_alto) * 100))

  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900 text-sm sm:text-base">Tu consumo vs. promedio uruguayo</h3>
      </div>

      {/* Gauge bar */}
      <div className="relative mt-4 sm:mt-6 mb-2">
        <div className="h-3 sm:h-4 rounded-full bg-gradient-to-r from-green-200 via-yellow-200 to-red-200" />
        {/* User marker */}
        <div
          className="absolute top-0 -mt-1 w-0 h-0"
          style={{ left: `${position}%`, transform: 'translateX(-50%)' }}
        >
          <div className="flex flex-col items-center">
            <div className="w-5 h-5 sm:w-6 sm:h-6 bg-blue-600 rounded-full border-2 border-white shadow-md flex items-center justify-center">
              <span className="text-white text-[10px] sm:text-xs font-bold">T</span>
            </div>
          </div>
        </div>
      </div>

      {/* Labels */}
      <div className="flex justify-between text-[10px] sm:text-xs text-gray-500 mb-3 sm:mb-4">
        <span>Bajo (&lt;150)</span>
        <span>Promedio (~225)</span>
        <span>Alto (&gt;400)</span>
      </div>

      <div className="text-center">
        <span className="text-xl sm:text-2xl font-bold text-gray-900">{consumo.toLocaleString('es-UY')}</span>
        <span className="text-gray-500 ml-1 text-sm">kWh/mes</span>
        <p className="text-xs sm:text-sm text-gray-500 mt-1">
          Consumís más que el {percentil}% de los hogares uruguayos
        </p>
      </div>
    </div>
  )
}

function ChargeBreakdown({ fijo, variable, total }: { fijo: number; variable: number; total: number }) {
  const data = [
    { name: 'Cargo fijo', value: fijo, color: '#3B82F6' },
    { name: 'Cargo variable', value: variable, color: '#10B981' },
  ]
  const porcentajeFijo = total > 0 ? Math.round((fijo / total) * 100) : 0
  const porcentajeVariable = total > 0 ? Math.round((variable / total) * 100) : 0

  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900 text-sm sm:text-base">Desglose de cargos</h3>
      </div>

      {/* Stack vertically on mobile, horizontal on sm+ */}
      <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6">
        <div className="w-28 h-28 sm:w-32 sm:h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={25}
                outerRadius={45}
                paddingAngle={2}
              >
                {data.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `$${value.toLocaleString('es-UY')}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="flex-1 w-full space-y-2 sm:space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-sm text-gray-600">Cargo fijo ({porcentajeFijo}%)</span>
            </div>
            <span className="font-medium text-sm sm:text-base">${fijo.toLocaleString('es-UY')}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-600">Cargo variable ({porcentajeVariable}%)</span>
            </div>
            <span className="font-medium text-sm sm:text-base">${variable.toLocaleString('es-UY')}</span>
          </div>
          <div className="border-t pt-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-900">Total</span>
            <span className="text-base sm:text-lg font-bold text-gray-900">${total.toLocaleString('es-UY')}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function BillResults({ analysis, onReset }: BillResultsProps) {
  const { servicio, periodo, consumo, cargos, metricas, percentil_consumo, recomendaciones, ahorro_potencial } = analysis

  const periodoDesde = new Date(periodo.desde + 'T00:00:00')
  const periodoHasta = new Date(periodo.hasta + 'T00:00:00')
  const formatDate = (d: Date) => d.toLocaleDateString('es-UY', { day: 'numeric', month: 'short', year: 'numeric' })
  const ahorroAnual = ahorro_potencial * 12

  return (
    <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
      {/* Header - stacks vertically on mobile */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-4 sm:p-6 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1 sm:mb-2">
              <Zap className="w-5 h-5 sm:w-6 sm:h-6" />
              <h2 className="text-lg sm:text-2xl font-bold">Análisis de tu factura {servicio}</h2>
            </div>
            <div className="flex items-center gap-2 text-blue-200 text-xs sm:text-sm">
              <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>{formatDate(periodoDesde)} - {formatDate(periodoHasta)}</span>
            </div>
          </div>
          <div className="sm:text-right">
            <p className="text-blue-200 text-xs sm:text-sm">Total facturado</p>
            <p className="text-2xl sm:text-4xl font-bold">${cargos.total.toLocaleString('es-UY')}</p>
          </div>
        </div>

        {/* Quick metrics - 1 col on mobile, 3 on sm+ */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-blue-500">
          <div>
            <p className="text-blue-200 text-[10px] sm:text-xs">Consumo</p>
            <p className="text-sm sm:text-xl font-semibold">{consumo.valor.toLocaleString('es-UY')} <span className="text-xs sm:text-base">{consumo.unidad}</span></p>
          </div>
          <div>
            <p className="text-blue-200 text-[10px] sm:text-xs">$/kWh</p>
            <p className="text-sm sm:text-xl font-semibold">${metricas.precio_unitario.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-[10px] sm:text-xs">$/día</p>
            <p className="text-sm sm:text-xl font-semibold">${metricas.costo_diario.toFixed(0)}</p>
          </div>
        </div>
      </div>

      {/* Savings banner - enhanced with annual projection */}
      {ahorro_potencial > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4">
          <div className="flex items-start sm:items-center gap-3">
            <div className="w-9 h-9 sm:w-10 sm:h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <TrendingDown className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-green-900 text-sm sm:text-base">
                Podrías ahorrar hasta ${ahorro_potencial.toLocaleString('es-UY')}/mes
              </p>
              <p className="text-xs sm:text-sm text-green-700">
                Eso es <strong>${ahorroAnual.toLocaleString('es-UY')}</strong> al año. Mirá las recomendaciones abajo.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Charts - stack on mobile */}
      <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
        <ConsumptionGauge consumo={consumo.valor} percentil={percentil_consumo} />
        <ChargeBreakdown fijo={cargos.fijo} variable={cargos.variable} total={cargos.total} />
      </div>

      {/* Recommendations */}
      {recomendaciones.length > 0 && (
        <div>
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Recomendaciones para tu hogar</h3>
          <div className="space-y-3 sm:space-y-4">
            {recomendaciones.map((rec, i) => (
              <RecommendationCard key={i} recomendacion={rec} />
            ))}
          </div>
        </div>
      )}

      {/* Reset button - proper touch target */}
      <div className="text-center pt-2 sm:pt-4 pb-4">
        <button
          onClick={onReset}
          className="inline-flex items-center justify-center min-h-[44px] px-6 text-blue-600 hover:text-blue-800 hover:bg-blue-50 font-medium text-sm rounded-lg transition-colors"
        >
          Analizar otra factura
        </button>
      </div>
    </div>
  )
}
