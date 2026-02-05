import { Zap, Calendar, DollarSign, BarChart3, Target } from 'lucide-react'
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
  // Position on the gauge (0-100%)
  const position = Math.min(100, Math.max(0, (consumo / CONSUMO_PROMEDIOS.muy_alto) * 100))

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Tu consumo vs. promedio uruguayo</h3>
      </div>

      {/* Gauge bar */}
      <div className="relative mt-6 mb-2">
        <div className="h-4 rounded-full bg-gradient-to-r from-green-200 via-yellow-200 to-red-200" />
        {/* User marker */}
        <div
          className="absolute top-0 -mt-1 w-0 h-0"
          style={{ left: `${position}%`, transform: 'translateX(-50%)' }}
        >
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-md flex items-center justify-center">
              <span className="text-white text-xs font-bold">T</span>
            </div>
          </div>
        </div>
      </div>

      {/* Labels */}
      <div className="flex justify-between text-xs text-gray-500 mb-4">
        <span>Bajo (&lt;150)</span>
        <span>Promedio (~225)</span>
        <span>Alto (&gt;400)</span>
      </div>

      <div className="text-center">
        <span className="text-2xl font-bold text-gray-900">{consumo.toLocaleString('es-UY')}</span>
        <span className="text-gray-500 ml-1">kWh/mes</span>
        <p className="text-sm text-gray-500 mt-1">
          Consum{'\u00ed'}s m\u00e1s que el {percentil}% de los hogares uruguayos
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

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Desglose de cargos</h3>
      </div>

      <div className="flex items-center gap-6">
        <div className="w-32 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={50}
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

        <div className="flex-1 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-sm text-gray-600">Cargo fijo</span>
            </div>
            <span className="font-medium">${fijo.toLocaleString('es-UY')}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-600">Cargo variable</span>
            </div>
            <span className="font-medium">${variable.toLocaleString('es-UY')}</span>
          </div>
          <div className="border-t pt-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-900">Total</span>
            <span className="text-lg font-bold text-gray-900">${total.toLocaleString('es-UY')}</span>
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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-6 h-6" />
              <h2 className="text-2xl font-bold">An\u00e1lisis de tu factura {servicio}</h2>
            </div>
            <div className="flex items-center gap-2 text-blue-200 text-sm">
              <Calendar className="w-4 h-4" />
              <span>{formatDate(periodoDesde)} - {formatDate(periodoHasta)}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-blue-200 text-sm">Total facturado</p>
            <p className="text-4xl font-bold">${cargos.total.toLocaleString('es-UY')}</p>
          </div>
        </div>

        {/* Quick metrics */}
        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t border-blue-500">
          <div>
            <p className="text-blue-200 text-xs">Consumo</p>
            <p className="text-xl font-semibold">{consumo.valor.toLocaleString('es-UY')} {consumo.unidad}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs">Precio por kWh</p>
            <p className="text-xl font-semibold">${metricas.precio_unitario.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-blue-200 text-xs">Costo por d\u00eda</p>
            <p className="text-xl font-semibold">${metricas.costo_diario.toFixed(0)}</p>
          </div>
        </div>
      </div>

      {/* Savings banner */}
      {ahorro_potencial > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="font-semibold text-green-900">Podr\u00edas ahorrar hasta ${ahorro_potencial.toLocaleString('es-UY')}/mes</p>
              <p className="text-sm text-green-700">Mir\u00e1 las recomendaciones abajo</p>
            </div>
          </div>
        </div>
      )}

      {/* Charts row */}
      <div className="grid md:grid-cols-2 gap-6">
        <ConsumptionGauge consumo={consumo.valor} percentil={percentil_consumo} />
        <ChargeBreakdown fijo={cargos.fijo} variable={cargos.variable} total={cargos.total} />
      </div>

      {/* Recommendations */}
      {recomendaciones.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recomendaciones para tu hogar</h3>
          <div className="space-y-4">
            {recomendaciones.map((rec, i) => (
              <RecommendationCard key={i} recomendacion={rec} />
            ))}
          </div>
        </div>
      )}

      {/* Reset button */}
      <div className="text-center pt-4">
        <button
          onClick={onReset}
          className="text-blue-600 hover:text-blue-800 font-medium text-sm underline"
        >
          Analizar otra factura
        </button>
      </div>
    </div>
  )
}
