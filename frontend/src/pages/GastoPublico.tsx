import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Line,
  Cell,
} from 'recharts'
import { Building2, AlertCircle, ExternalLink, ChevronLeft } from 'lucide-react'
import { api } from '../services/api'
import StatCard from '../components/StatCard'
import ErrorBanner from '../components/ErrorBanner'
import ChartSkeleton from '../components/ChartSkeleton'
import { useIsMobile } from '../hooks/useIsMobile'

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

interface ComparacionAnual {
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

type DrilldownState =
  | { level: 'global' }
  | { level: 'organismo'; inciso: string; nombre: string }

// ---------------------------------------------------------------------------
// Service
// ---------------------------------------------------------------------------

const gastoService = {
  getEjecucion: async (anio?: number, inciso?: string): Promise<EjecucionRow[]> => {
    const params: Record<string, unknown> = { limit: 200 }
    if (anio) params.anio = anio
    if (inciso) params.inciso = inciso
    const { data } = await api.get('/api/v1/gasto/ejecucion', { params })
    return data
  },
  getOrganismos: async (anio?: number): Promise<Organismo[]> => {
    const params = anio ? { anio } : {}
    const { data } = await api.get('/api/v1/gasto/organismos', { params })
    return data
  },
  getComparacionAnual: async (inciso: string, anioBase?: number): Promise<ComparacionAnual> => {
    const params: Record<string, unknown> = { inciso }
    if (anioBase) params.anio_base = anioBase
    const { data } = await api.get('/api/v1/gasto/comparacion-anual', { params })
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

function shortenName(name: string, maxLen = 32): string {
  return name.length > maxLen ? name.slice(0, maxLen - 1) + '…' : name
}

const MONTH_NAMES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

// ---------------------------------------------------------------------------
// Sub-components — Nivel 1
// ---------------------------------------------------------------------------

interface StackedTooltipProps {
  active?: boolean
  payload?: Array<{ payload: EjecucionRow & { no_ejecutado: number } }>
}

function StackedTooltip({ active, payload }: StackedTooltipProps) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm max-w-xs">
      <p className="font-semibold text-gray-900 mb-2 leading-tight">{row.nombre_organismo}</p>
      <p className="text-gray-600">Crédito vigente: <span className="font-medium text-gray-800">{formatMillones(row.credito_vigente)}</span></p>
      <p className="text-gray-600">Ejecutado: <span className="font-medium text-green-700">{formatMillones(row.ejecutado)}</span></p>
      <p className="font-semibold mt-1.5" style={{ color: pctColor(row.porcentaje_ejecucion) }}>
        Ejecución: {row.porcentaje_ejecucion !== null ? `${row.porcentaje_ejecucion.toFixed(1)}%` : 'N/D'}
      </p>
      <p className="text-xs text-gray-400 mt-1">Clic para ver detalle mensual</p>
    </div>
  )
}

interface GastoGlobalChartProps {
  data: Array<EjecucionRow & { no_ejecutado: number; nombre_corto: string }>
  onSelect: (inciso: string, nombre: string) => void
  isMobile: boolean
}

function GastoGlobalChart({ data, onSelect, isMobile }: GastoGlobalChartProps) {
  const handleClick = (barData: { activePayload?: Array<{ payload: EjecucionRow }> }) => {
    if (!barData?.activePayload?.length) return
    const row = barData.activePayload[0].payload
    onSelect(row.inciso, row.nombre_organismo)
  }

  if (isMobile) {
    return (
      <div className="overflow-x-auto">
        <div style={{ minWidth: Math.max(data.length * 40, 360) }}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={data}
              margin={{ top: 10, right: 16, left: 8, bottom: 40 }}
              onClick={handleClick}
              style={{ cursor: 'pointer' }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="inciso"
                tick={{ fontSize: 10 }}
                angle={-45}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                tickFormatter={(v) => formatMillones(v)}
                tick={{ fontSize: 10 }}
                width={55}
              />
              <Tooltip content={<StackedTooltip />} />
              <Bar dataKey="ejecutado" stackId="a" fill="#16a34a" name="Ejecutado" radius={[0, 0, 0, 0]} />
              <Bar dataKey="no_ejecutado" stackId="a" fill="#e5e7eb" name="Pendiente" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(data.length * 28 + 60, 480)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 80, left: 10, bottom: 0 }}
        onClick={handleClick}
        style={{ cursor: 'pointer' }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={(v) => formatMillones(v)}
          tick={{ fontSize: 11 }}
        />
        <YAxis
          type="category"
          dataKey="nombre_corto"
          width={200}
          tick={{ fontSize: 11 }}
        />
        <Tooltip content={<StackedTooltip />} />
        <Bar dataKey="ejecutado" stackId="a" fill="#16a34a" name="Ejecutado" />
        <Bar dataKey="no_ejecutado" stackId="a" fill="#e5e7eb" name="Pendiente" radius={[0, 3, 3, 0]}>
          {data.map((entry) => (
            <Cell
              key={entry.inciso}
              fill="#e5e7eb"
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

interface TablaOrganismosProps {
  data: EjecucionRow[]
  onSelect: (inciso: string, nombre: string) => void
}

function TablaOrganismos({ data, onSelect }: TablaOrganismosProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900">Detalle por Organismo</h2>
        <p className="text-xs text-gray-500 mt-0.5">Clic en una fila para ver la evolución mensual</p>
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
            {data.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-blue-50 transition-colors cursor-pointer"
                onClick={() => onSelect(row.inciso, row.nombre_organismo)}
              >
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
  )
}

// ---------------------------------------------------------------------------
// Sub-components — Nivel 2
// ---------------------------------------------------------------------------

interface ComparacionAnualPanelProps {
  inciso: string
  anio: number
}

function ComparacionAnualPanel({ inciso, anio }: ComparacionAnualPanelProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['gasto', 'comparacion-anual', inciso, anio],
    queryFn: () => gastoService.getComparacionAnual(inciso, anio),
  })

  if (isLoading) return <div className="h-20 bg-gray-100 rounded-lg animate-pulse" />
  if (isError || !data) return null

  const variacion = data.variacion_ejecutado
  const varColor = variacion === null ? '#6b7280' : variacion >= 0 ? '#16a34a' : '#dc2626'

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">Comparación interanual</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">{data.anio_comparacion}</p>
          <p className="text-xl font-bold text-gray-600">{formatMillones(data.ejecutado_comparacion)}</p>
          <p className="text-xs text-gray-400">de {formatMillones(data.credito_comparacion)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">{data.anio_base} (actual)</p>
          <p className="text-xl font-bold text-gray-900">{formatMillones(data.ejecutado_base)}</p>
          <p className="text-xs text-gray-400">de {formatMillones(data.credito_base)}</p>
        </div>
      </div>
      {variacion !== null && (
        <p className="mt-3 text-sm font-medium" style={{ color: varColor }}>
          {variacion >= 0 ? '↑' : '↓'} {Math.abs(variacion).toFixed(1)}% vs año anterior
        </p>
      )}
    </div>
  )
}

interface MensualTooltipProps {
  active?: boolean
  payload?: Array<{ value: number; dataKey: string; fill?: string }>
  label?: string | number
}

function MensualTooltip({ active, payload, label }: MensualTooltipProps) {
  if (!active || !payload?.length) return null
  const mes = typeof label === 'number' ? MONTH_NAMES[label - 1] ?? label : label
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm">
      <p className="font-semibold text-gray-800 mb-1 capitalize">{mes}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.fill ?? '#374151' }} className="text-xs">
          {p.dataKey === 'ejecutado' ? 'Ejecutado' : 'Crédito'}: {formatMillones(p.value)}
        </p>
      ))}
    </div>
  )
}

interface EjecucionMensualChartProps {
  inciso: string
  anio: number
  isMobile: boolean
}

function EjecucionMensualChart({ inciso, anio, isMobile }: EjecucionMensualChartProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['gasto', 'mensual', inciso, anio],
    queryFn: () => gastoService.getEjecucion(anio, inciso),
  })

  if (isLoading) return <ChartSkeleton height={isMobile ? 220 : 320} />
  if (isError) return <ErrorBanner message="No se pudieron cargar los datos mensuales." />

  const mensual = (data ?? [])
    .filter((r) => r.mes !== null)
    .sort((a, b) => (a.mes ?? 0) - (b.mes ?? 0))
    .map((r) => ({
      ...r,
      mes_label: MONTH_NAMES[(r.mes ?? 1) - 1],
    }))

  if (mensual.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-8 text-center text-gray-500 text-sm">
        No hay datos mensuales disponibles para este organismo y año.
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-base font-semibold text-gray-900 mb-1">Ejecución mensual</h3>
      <p className="text-xs text-gray-500 mb-5">Crédito vigente (línea) vs. ejecutado (barras)</p>
      <ResponsiveContainer width="100%" height={isMobile ? 220 : 320}>
        <ComposedChart data={mensual} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="mes_label" tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(v) => formatMillones(v)} tick={{ fontSize: 11 }} width={60} />
          <Tooltip content={<MensualTooltip />} />
          <Bar dataKey="ejecutado" fill="#16a34a" radius={[3, 3, 0, 0]} name="Ejecutado" />
          <Line
            type="monotone"
            dataKey="credito_vigente"
            stroke="#9ca3af"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
            name="Crédito"
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="flex gap-6 mt-3 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-green-600 inline-block" /> Ejecutado
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-8 border-t-2 border-dashed border-gray-400 inline-block" /> Crédito vigente
        </span>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Year selector
// ---------------------------------------------------------------------------

function YearSelector({
  years,
  selected,
  onChange,
}: {
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
  const [drilldown, setDrilldown] = useState<DrilldownState>({ level: 'global' })
  const isMobile = useIsMobile()

  const { data: ejecucion, isLoading, isError } = useQuery({
    queryKey: ['gasto', 'ejecucion', anioSeleccionado],
    queryFn: () => gastoService.getEjecucion(anioSeleccionado),
  })

  const aniosDisponibles = ejecucion
    ? [...new Set(ejecucion.map((r) => r.anio))].sort((a, b) => b - a)
    : []

  const anioActivo = anioSeleccionado ?? aniosDisponibles[0]

  // Totales anuales por organismo (mes === null)
  const totalesAnuales = (ejecucion ?? [])
    .filter((r) => r.mes === null && (anioSeleccionado === undefined || r.anio === anioSeleccionado))
    .sort((a, b) => b.credito_vigente - a.credito_vigente)

  // Datos para el gráfico apilado
  const chartData = totalesAnuales.map((r) => ({
    ...r,
    no_ejecutado: Math.max(0, r.credito_vigente - r.ejecutado),
    nombre_corto: shortenName(r.nombre_organismo),
  }))

  // Resumen global
  const totalCredito = totalesAnuales.reduce((s, r) => s + r.credito_vigente, 0)
  const totalEjecutado = totalesAnuales.reduce((s, r) => s + r.ejecutado, 0)
  const pctGlobal = totalCredito > 0 ? (totalEjecutado / totalCredito) * 100 : null

  const handleSelectOrganismo = (inciso: string, nombre: string) => {
    setDrilldown({ level: 'organismo', inciso, nombre })
  }

  const handleVolver = () => {
    setDrilldown({ level: 'global' })
  }

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="bg-gradient-to-r from-violet-600 to-violet-700 rounded-xl shadow-lg p-6 sm:p-8 text-white">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-3">
            <Building2 className="w-7 h-7 sm:w-8 sm:h-8" />
            <h1 className="text-2xl sm:text-4xl font-bold">Gasto Público</h1>
          </div>
          <p className="text-base sm:text-xl text-violet-100 mb-1">
            Ejecución presupuestal por organismo
          </p>
          <p className="text-violet-200 text-sm">
            Datos oficiales del MEF y OPP — histórico desde 1999. Hacé clic en un organismo para ver su evolución mensual.
          </p>
        </div>
      </div>

      {/* Fuente */}
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
          {' '}y OPP. Actualización mensual automática.
        </div>
      </div>

      {/* Selector de año */}
      {aniosDisponibles.length > 1 && (
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-sm font-medium text-gray-700">Año:</span>
          <YearSelector
            years={aniosDisponibles}
            selected={anioSeleccionado}
            onChange={(y) => {
              setAnioSeleccionado(y)
              setDrilldown({ level: 'global' })
            }}
          />
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      )}

      {/* Error */}
      {isError && (
        <ErrorBanner message="No se pudieron cargar los datos de gasto público. Verificá la conexión o intentá más tarde." />
      )}

      {/* Empty */}
      {!isLoading && !isError && ejecucion?.length === 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-10 text-center">
          <Building2 className="w-10 h-10 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">Sin datos disponibles</p>
          <p className="text-gray-500 text-sm mt-1">
            Los datos de gasto público se cargan mensualmente.
          </p>
        </div>
      )}

      {/* Tarjetas resumen */}
      {!isLoading && totalesAnuales.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            label="Crédito Vigente Total"
            value={formatMillones(totalCredito)}
            subValue={anioActivo ? `Año ${anioActivo}` : 'Todos los años'}
          />
          <StatCard
            label="Total Ejecutado"
            value={formatMillones(totalEjecutado)}
            colorOverride="#16a34a"
          />
          <StatCard
            label="Ejecución Global"
            value={pctGlobal !== null ? `${pctGlobal.toFixed(1)}%` : 'N/D'}
            colorOverride={pctColor(pctGlobal)}
          />
        </div>
      )}

      {/* NIVEL 1 — Vista global */}
      {!isLoading && chartData.length > 0 && drilldown.level === 'global' && (
        <>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-1">
              Presupuesto por Organismo
            </h2>
            <p className="text-sm text-gray-500 mb-5">
              Ordenado por crédito vigente — <span className="text-green-700 font-medium">verde</span> = ejecutado, <span className="text-gray-400 font-medium">gris</span> = pendiente. Hacé clic en una barra para el detalle.
            </p>
            <GastoGlobalChart
              data={chartData}
              onSelect={handleSelectOrganismo}
              isMobile={isMobile}
            />
            <div className="flex gap-6 mt-4 text-xs text-gray-500">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-green-600 inline-block" /> Ejecutado
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm bg-gray-200 inline-block" /> Pendiente
              </span>
            </div>
          </div>

          <TablaOrganismos data={totalesAnuales} onSelect={handleSelectOrganismo} />
        </>
      )}

      {/* NIVEL 2 — Detalle de organismo */}
      {!isLoading && drilldown.level === 'organismo' && (
        <div className="space-y-5">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleVolver}
              className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              Gasto Global
            </button>
            <span className="text-gray-400">/</span>
            <span className="text-sm text-gray-700 font-semibold">{drilldown.nombre}</span>
          </div>

          {/* Comparación interanual */}
          {anioActivo && (
            <ComparacionAnualPanel inciso={drilldown.inciso} anio={anioActivo} />
          )}

          {/* Evolución mensual */}
          <EjecucionMensualChart
            inciso={drilldown.inciso}
            anio={anioActivo ?? new Date().getFullYear()}
            isMobile={isMobile}
          />
        </div>
      )}
    </div>
  )
}
