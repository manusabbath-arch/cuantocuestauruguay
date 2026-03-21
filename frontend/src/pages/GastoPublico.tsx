import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Building2, AlertCircle, ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { api } from '../services/api'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Organismo {
  inciso: string
  nombre_organismo: string
  ultimo_anio: number
}

interface EjecucionRow {
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

// ---------------------------------------------------------------------------
// Service functions
// ---------------------------------------------------------------------------

const gastoService = {
  getOrganismos: async (anio?: number): Promise<Organismo[]> => {
    const params = anio ? { anio } : {}
    const { data } = await api.get('/api/v1/gasto/organismos', { params })
    return data
  },
  getEjecucion: async (anio?: number): Promise<EjecucionRow[]> => {
    const params: Record<string, unknown> = { limit: 200 }
    if (anio) params.anio = anio
    const { data } = await api.get('/api/v1/gasto/ejecucion', { params })
    return data
  },
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatMillones(value: number): string {
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`
  return `$${value.toFixed(0)}`
}

function pctColor(pct: number | null): string {
  if (pct === null) return '#6b7280'
  if (pct >= 90) return '#16a34a'
  if (pct >= 70) return '#ca8a04'
  return '#dc2626'
}

function shortenName(name: string): string {
  return name.length > 30 ? name.slice(0, 28) + '…' : name
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function EjecucionTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: EjecucionRow }> }) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm">
      <p className="font-semibold text-gray-900 mb-1">{row.nombre_organismo}</p>
      <p className="text-gray-600">Crédito vigente: {formatMillones(row.credito_vigente)}</p>
      <p className="text-gray-600">Ejecutado: {formatMillones(row.ejecutado)}</p>
      <p className="font-medium mt-1" style={{ color: pctColor(row.porcentaje_ejecucion) }}>
        Ejecución: {row.porcentaje_ejecucion !== null ? `${row.porcentaje_ejecucion.toFixed(1)}%` : 'N/D'}
      </p>
    </div>
  )
}

function YearSelector({ years, selected, onChange }: {
  years: number[]
  selected: number | undefined
  onChange: (y: number | undefined) => void
}) {
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

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function GastoPublico() {
  const [anioSeleccionado, setAnioSeleccionado] = useState<number | undefined>(undefined)

  const { data: ejecucion, isLoading, isError } = useQuery({
    queryKey: ['gasto', 'ejecucion', anioSeleccionado],
    queryFn: () => gastoService.getEjecucion(anioSeleccionado),
  })

  // Derive available years from data
  const aniosDisponibles = ejecucion
    ? [...new Set(ejecucion.map((r) => r.anio))].sort((a, b) => b - a)
    : []

  // Filter to annual totals (mes === null) for the chart
  const totalesAnuales = (ejecucion ?? [])
    .filter((r) => r.mes === null)
    .sort((a, b) => b.porcentaje_ejecucion! - a.porcentaje_ejecucion!)
    .slice(0, 20)

  const chartData = totalesAnuales.map((r) => ({
    ...r,
    nombre_corto: shortenName(r.nombre_organismo),
  }))

  // Summary stats
  const totalCredito = totalesAnuales.reduce((s, r) => s + r.credito_vigente, 0)
  const totalEjecutado = totalesAnuales.reduce((s, r) => s + r.ejecutado, 0)
  const pctGlobal = totalCredito > 0 ? (totalEjecutado / totalCredito) * 100 : null

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-gradient-to-r from-violet-600 to-violet-700 rounded-xl shadow-lg p-8 text-white">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-4">
            <Building2 className="w-8 h-8" />
            <h1 className="text-4xl font-bold">Gasto Público</h1>
          </div>
          <p className="text-xl text-violet-100 mb-2">
            Ejecución presupuestal por organismo
          </p>
          <p className="text-violet-200 text-sm">
            Datos oficiales del Ministerio de Economía y Finanzas (MEF) y la Oficina de Planeamiento y Presupuesto (OPP)
          </p>
        </div>
      </div>

      {/* Source disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
        <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-800">
          <strong>Fuente:</strong> CSV de ejecución presupuestal publicado en el{' '}
          <a
            href="https://catalogodatos.gub.uy/organization/ministerio-de-economia-y-finanzas"
            target="_blank"
            rel="noopener noreferrer"
            className="underline inline-flex items-center gap-1"
          >
            Catálogo de Datos Abiertos — MEF <ExternalLink className="w-3 h-3" />
          </a>
          {' '}y OPP (Portal Transparencia Presupuestaria). Actualización mensual automática.
        </div>
      </div>

      {/* Year selector */}
      {aniosDisponibles.length > 1 && (
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-700">Año:</span>
          <YearSelector
            years={aniosDisponibles}
            selected={anioSeleccionado}
            onChange={setAnioSeleccionado}
          />
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-800 font-medium">No se pudieron cargar los datos de gasto público.</p>
          <p className="text-red-600 text-sm mt-1">Verificá la conexión o intentá más tarde.</p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && ejecucion?.length === 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-10 text-center">
          <Building2 className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">Sin datos disponibles</p>
          <p className="text-gray-500 text-sm mt-1">
            Los datos de gasto público se cargan mensualmente. Si es la primera vez, ejecutá el ETL manualmente.
          </p>
        </div>
      )}

      {/* Summary cards */}
      {!isLoading && totalesAnuales.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Crédito Vigente Total</p>
            <p className="text-2xl font-bold text-gray-900">{formatMillones(totalCredito)}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Total Ejecutado</p>
            <p className="text-2xl font-bold text-gray-900">{formatMillones(totalEjecutado)}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">Ejecución Global</p>
            <div className="flex items-center gap-2">
              <p
                className="text-2xl font-bold"
                style={{ color: pctColor(pctGlobal) }}
              >
                {pctGlobal !== null ? `${pctGlobal.toFixed(1)}%` : 'N/D'}
              </p>
              {pctGlobal !== null && pctGlobal >= 90 && <TrendingUp className="w-5 h-5 text-green-600" />}
              {pctGlobal !== null && pctGlobal >= 70 && pctGlobal < 90 && <Minus className="w-5 h-5 text-yellow-600" />}
              {pctGlobal !== null && pctGlobal < 70 && <TrendingDown className="w-5 h-5 text-red-600" />}
            </div>
          </div>
        </div>
      )}

      {/* Bar chart */}
      {!isLoading && chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            Ejecución por Organismo
          </h2>
          <p className="text-sm text-gray-500 mb-6">
            % ejecutado respecto al crédito vigente — top 20 organismos
          </p>
          <ResponsiveContainer width="100%" height={480}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 0, right: 40, left: 10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis
                type="number"
                domain={[0, 120]}
                tickFormatter={(v) => `${v}%`}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                type="category"
                dataKey="nombre_corto"
                width={170}
                tick={{ fontSize: 11 }}
              />
              <Tooltip content={<EjecucionTooltip />} />
              <Bar dataKey="porcentaje_ejecucion" radius={[0, 4, 4, 0]}>
                {chartData.map((entry) => (
                  <Cell
                    key={entry.inciso}
                    fill={pctColor(entry.porcentaje_ejecucion)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-6 mt-4 text-xs text-gray-500">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-green-600 inline-block" /> ≥ 90%
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-yellow-600 inline-block" /> 70–89%
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-red-600 inline-block" /> &lt; 70%
            </span>
          </div>
        </div>
      )}

      {/* Detail table */}
      {!isLoading && totalesAnuales.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900">Detalle por Organismo</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600 text-xs uppercase tracking-wide">
                <tr>
                  <th className="px-4 py-3 text-left">Organismo</th>
                  <th className="px-4 py-3 text-right">Crédito Vigente</th>
                  <th className="px-4 py-3 text-right">Ejecutado</th>
                  <th className="px-4 py-3 text-right">% Ejecución</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {totalesAnuales.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      <span className="text-gray-400 text-xs mr-2">{row.inciso}</span>
                      {row.nombre_organismo}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      {formatMillones(row.credito_vigente)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      {formatMillones(row.ejecutado)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span
                        className="font-semibold"
                        style={{ color: pctColor(row.porcentaje_ejecucion) }}
                      >
                        {row.porcentaje_ejecucion !== null
                          ? `${row.porcentaje_ejecucion.toFixed(1)}%`
                          : 'N/D'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
