import { useEffect, useMemo, useState } from 'react'
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
  LabelList,
} from 'recharts'
import {
  Building2,
  ChevronLeft,
  Download,
  HelpCircle,
  Search,
} from 'lucide-react'
import StatCard from '../components/StatCard'
import ErrorBanner from '../components/ErrorBanner'
import ChartSkeleton from '../components/ChartSkeleton'
import DataTrustPanel from '../components/DataTrustPanel'
import { GastoHelpPanel, GastoSortSelector, GastoYearSelector } from '../components/gasto/GastoControls'
import ViewModeToggle from '../components/ViewModeToggle'
import { usePersistentViewMode } from '../hooks/usePersistentViewMode'
import { useIsMobile } from '../hooks/useIsMobile'
import { useGastoEjecucion, useGastoComparacion } from '../hooks/useGasto'
import NarrativaGasto from '../components/NarrativaGasto'
import AnomaliasBanner from '../components/AnomaliasBanner'
import type { EjecucionPresupuestal } from '../services/gasto'
import { buildAnnualRowsWithVariation, sortAnnualRows, type GastoSortMode } from '../lib/gasto'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type DrilldownState =
  | { level: 'global' }
  | { level: 'organismo'; inciso: string; nombre: string }

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
// Tooltip del gráfico apilado
// ---------------------------------------------------------------------------

interface StackedTooltipProps {
  active?: boolean
  payload?: Array<{ payload: EjecucionPresupuestal & { no_ejecutado: number } }>
}

function StackedTooltip({ active, payload }: StackedTooltipProps) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm max-w-xs">
      <p className="font-semibold text-gray-900 mb-2 leading-tight">{row.nombre_organismo}</p>
      <p className="text-gray-600">
        Crédito vigente: <span className="font-medium text-gray-800">{formatMillones(row.credito_vigente)}</span>
      </p>
      <p className="text-gray-600">
        Ejecutado: <span className="font-medium text-green-700">{formatMillones(row.ejecutado)}</span>
      </p>
      <p className="font-semibold mt-1.5" style={{ color: pctColor(row.porcentaje_ejecucion) }}>
        Ejecución: {row.porcentaje_ejecucion !== null ? `${row.porcentaje_ejecucion.toFixed(1)}%` : 'N/D'}
      </p>
      <p className="text-xs text-blue-600 mt-1">Clic para ver detalle mensual →</p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Vista mobile: lista rankeada con micro-barras
// ---------------------------------------------------------------------------

interface MobileRankListProps {
  data: Array<EjecucionPresupuestal & { no_ejecutado: number; variacion_interanual: number | null }>
  onSelect: (inciso: string, nombre: string) => void
  topN?: number
}

function MobileRankList({ data, onSelect, topN = 10 }: MobileRankListProps) {
  const [showAll, setShowAll] = useState(false)
  const [search, setSearch] = useState('')

  const filtered = search.trim()
    ? data.filter(
        (r) =>
          r.nombre_organismo.toLowerCase().includes(search.toLowerCase()) ||
          r.inciso.includes(search)
      )
    : data

  const visible = showAll || search.trim() ? filtered : filtered.slice(0, topN)
  const hasMore = !showAll && !search.trim() && filtered.length > topN

  return (
    <div className="space-y-2">
      {/* Buscador mobile */}
      <div className="relative mb-3">
        <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar organismo..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {visible.map((row) => {
        const pct = row.porcentaje_ejecucion ?? 0
        const barPct = Math.min(pct, 100)
        return (
          <button
            key={row.inciso}
            onClick={() => onSelect(row.inciso, row.nombre_organismo)}
            className="w-full text-left bg-white border border-gray-200 rounded-xl p-3 hover:border-blue-300 hover:bg-blue-50 transition-all active:scale-[0.99]"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 leading-tight">{row.nombre_organismo}</p>
                <p className="text-xs text-gray-400 mt-0.5">Código {row.inciso}</p>
              </div>
              <span
                className="text-sm font-bold flex-shrink-0 mt-0.5"
                style={{ color: pctColor(row.porcentaje_ejecucion) }}
              >
                {pct.toFixed(0)}%
              </span>
            </div>
            {/* Micro-barra de progreso */}
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${barPct}%`,
                  backgroundColor: pctColor(row.porcentaje_ejecucion),
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>{formatMillones(row.ejecutado)} ejecutado</span>
              <span>de {formatMillones(row.credito_vigente)}</span>
            </div>
          </button>
        )
      })}

      {hasMore && (
        <button
          onClick={() => setShowAll(true)}
          className="w-full py-2 text-sm text-blue-600 font-medium hover:text-blue-800 transition-colors"
        >
          Ver {filtered.length - topN} organismos más
        </button>
      )}

      {visible.length === 0 && (
        <p className="text-center text-sm text-gray-500 py-4">
          No se encontraron organismos para "{search}"
        </p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Gráfico desktop: barras apiladas
// ---------------------------------------------------------------------------

interface DesktopChartProps {
  data: Array<EjecucionPresupuestal & { no_ejecutado: number; nombre_corto: string; variacion_interanual: number | null }>
  onSelect: (inciso: string, nombre: string) => void
}

function DesktopStackedChart({ data, onSelect }: DesktopChartProps) {
  const handleClick = (barData: { activePayload?: Array<{ payload: EjecucionPresupuestal }> }) => {
    if (!barData?.activePayload?.length) return
    const row = barData.activePayload[0].payload
    onSelect(row.inciso, row.nombre_organismo)
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(data.length * 30 + 60, 480)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 70, left: 10, bottom: 0 }}
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
          width={210}
          tick={{ fontSize: 11 }}
        />
        <Tooltip content={<StackedTooltip />} />
        <Bar dataKey="ejecutado" stackId="a" fill="#16a34a" name="Ejecutado">
          <LabelList
            dataKey="porcentaje_ejecucion"
            position="right"
            style={{ fontSize: 10, fill: '#374151' }}
            formatter={(v: number | null) => (v !== null ? `${v.toFixed(0)}%` : '')}
          />
        </Bar>
        <Bar dataKey="no_ejecutado" stackId="a" fill="#e5e7eb" name="Pendiente" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

// ---------------------------------------------------------------------------
// Sub-componente: comparación interanual
// ---------------------------------------------------------------------------

function ComparacionAnualPanel({ inciso }: { inciso: string }) {
  const { data, isLoading, isError } = useGastoComparacion(inciso)

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

// ---------------------------------------------------------------------------
// Sub-componente: evolución mensual
// ---------------------------------------------------------------------------

interface MensualTooltipProps {
  active?: boolean
  payload?: Array<{ value: number; dataKey: string; fill?: string }>
  label?: string | number
}

function MensualTooltip({ active, payload, label }: MensualTooltipProps) {
  if (!active || !payload?.length) return null
  const mes = typeof label === 'string' ? label : MONTH_NAMES[(Number(label) ?? 1) - 1] ?? label
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

function EjecucionMensualChart({
  inciso,
  anio,
  isMobile,
}: {
  inciso: string
  anio: number
  isMobile: boolean
}) {
  const { data, isLoading, isError } = useGastoEjecucion({ anio, inciso, limit: 13 })

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
// Main page
// ---------------------------------------------------------------------------

export default function GastoPublico() {
  const [anioSeleccionado, setAnioSeleccionado] = useState<number | undefined>(undefined)
  const [drilldown, setDrilldown] = useState<DrilldownState>({ level: 'global' })
  const [sortMode, setSortMode] = useState<GastoSortMode>('presupuesto')
  const [showAyuda, setShowAyuda] = useState(false)
  const { viewMode, setViewMode } = usePersistentViewMode('resumen')
  const isMobile = useIsMobile()

  const { data: ejecucionBase, isLoading: isLoadingBase, isError: isErrorBase } = useGastoEjecucion({ limit: 1000 })

  const aniosDisponibles = useMemo(
    () => ejecucionBase
      ? [...new Set(ejecucionBase.map((r) => r.anio))].sort((a, b) => b - a)
      : [],
    [ejecucionBase]
  )

  const anioActivo = anioSeleccionado ?? aniosDisponibles[0]

  const { data: ejecucionActual, isLoading: isLoadingActual, isError: isErrorActual } = useGastoEjecucion(
    anioActivo !== undefined ? { anio: anioActivo, limit: 1000 } : { limit: 1000 }
  )

  const { data: ejecucionAnterior, isLoading: isLoadingAnterior, isError: isErrorAnterior } = useGastoEjecucion(
    anioActivo !== undefined ? { anio: anioActivo - 1, limit: 1000 } : { limit: 1000 }
  )

  const isLoading = isLoadingBase || (anioActivo !== undefined && (isLoadingActual || isLoadingAnterior))
  const isError = isErrorBase || isErrorActual || isErrorAnterior

  useEffect(() => {
    if (viewMode === 'resumen' && sortMode !== 'presupuesto') {
      setSortMode('presupuesto')
    }
  }, [viewMode, sortMode])

  const filasActuales = useMemo(
    () => (ejecucionActual ?? []).filter((r) => r.mes === null && r.anio === anioActivo),
    [ejecucionActual, anioActivo]
  )

  const anterioresPorInciso = useMemo(() => {
    return new Map(
      (ejecucionAnterior ?? [])
        .filter((r) => r.mes === null && r.anio === (anioActivo !== undefined ? anioActivo - 1 : r.anio))
        .map((r) => [r.inciso, r])
    )
  }, [ejecucionAnterior, anioActivo])

  // Solo totales anuales (mes === null), filtrados por año activo y enriquecidos con variación YoY real
  const totalesAnuales = useMemo(() => {
    const base = buildAnnualRowsWithVariation(
      filasActuales,
      Array.from(anterioresPorInciso.values()),
    )

    return sortAnnualRows(base, sortMode)
  }, [filasActuales, anterioresPorInciso, sortMode])

  const hayVariacionDisponible = totalesAnuales.some((r) => r.variacion_interanual !== null)

  const chartData = useMemo(
    () =>
      totalesAnuales.map((r) => ({
        ...r,
        no_ejecutado: Math.max(0, r.credito_vigente - r.ejecutado),
        nombre_corto: shortenName(r.nombre_organismo),
      })),
    [totalesAnuales]
  )

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
            Datos oficiales del MEF y OPP — histórico desde 1999. Seleccioná un organismo para ver su evolución mensual.
          </p>
          <button
            onClick={() => setShowAyuda((v) => !v)}
            className="mt-3 flex items-center gap-1.5 text-violet-200 hover:text-white text-sm underline underline-offset-2 transition-colors"
          >
            <HelpCircle className="w-4 h-4" />
            {showAyuda ? 'Ocultar glosario' : '¿Qué significan estos términos?'}
          </button>
        </div>
      </div>

      {/* Panel de ayuda */}
      {showAyuda && <GastoHelpPanel onClose={() => setShowAyuda(false)} />}

      <DataTrustPanel
        fuenteLabel="catálogo abierto MEF y Presupuesto Fácil UY"
        fuenteUrl="https://catalogodatos.gub.uy/organization/ministerio-de-economia-y-finanzas"
        metodologiaLabel="metodología oficial presupuestal"
        metodologiaUrl="https://presupuestonacional.gub.uy/node/29"
        ultimaActualizacion={anioActivo ? `ejercicio ${anioActivo}` : undefined}
        nota="La ejecución presupuestal se presenta con fuentes oficiales MEF/CGN. La actualización operativa del ETL es mensual y la comparabilidad histórica puede verse afectada por reclasificaciones institucionales."
      />

      {/* Narrativa automatica */}
      {drilldown.level === 'global' && <NarrativaGasto anio={anioActivo} />}

      {/* Señales de anomalías */}
      {drilldown.level === 'global' && <AnomaliasBanner anio={anioActivo} />}

      <ViewModeToggle viewMode={viewMode} onChange={setViewMode} />

      {/* Selector de año + exportación */}
      {aniosDisponibles.length > 1 && (
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-4 flex-wrap">
            <span className="text-sm font-medium text-gray-700">Año:</span>
            <GastoYearSelector
              years={aniosDisponibles}
              selected={anioSeleccionado}
              onChange={(y) => {
                setAnioSeleccionado(y)
                setDrilldown({ level: 'global' })
              }}
            />
          </div>
          {anioActivo !== undefined && (
            <a
              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/gasto/ejecucion/export.csv?anio=${anioActivo}&limit=20000`}
              download
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Descargar CSV {anioActivo}
            </a>
          )}
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
      {!isLoading && !isError && filasActuales.length === 0 && (
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
            subValue={pctGlobal !== null ? `${pctGlobal.toFixed(1)}% del crédito` : undefined}
          />
          <StatCard
            label="Ejecución Global"
            value={pctGlobal !== null ? `${pctGlobal.toFixed(1)}%` : 'N/D'}
            colorOverride={pctColor(pctGlobal)}
            subValue={
              pctGlobal !== null
                ? pctGlobal >= 90
                  ? 'Ejecución alta'
                  : pctGlobal >= 70
                    ? 'Ejecución media'
                    : 'Ejecución baja'
                : undefined
            }
          />
        </div>
      )}

      {/* NIVEL 1 — Vista global */}
      {!isLoading && chartData.length > 0 && drilldown.level === 'global' && (
        <>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex flex-col sm:flex-row sm:items-start gap-3 mb-4">
              <div className="flex-1">
                <h2 className="text-lg font-semibold text-gray-900">
                  Presupuesto por Organismo
                </h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  <span className="inline-block w-2.5 h-2.5 rounded-sm bg-green-600 mr-1" />
                  verde = ejecutado ·
                  <span className="inline-block w-2.5 h-2.5 rounded-sm bg-gray-200 mx-1" />
                  gris = pendiente · el % aparece al final de cada barra
                </p>
              </div>
            </div>

            {/* Selector de ordenamiento */}
            {viewMode === 'explorar' ? (
              <div className="mb-5">
                <GastoSortSelector mode={sortMode} onChange={setSortMode} />
                {sortMode === 'variacion' && (
                  <p className="mt-2 text-xs text-gray-500">
                    {hayVariacionDisponible
                      ? `Ordenado por magnitud de variación interanual del ejecutado para ${anioActivo} vs ${anioActivo - 1}.`
                      : 'No hay datos del año anterior suficientes para calcular variación interanual en este corte.'}
                  </p>
                )}
              </div>
            ) : (
              <div className="mb-5 rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm text-gray-600">
                Vista simplificada: se muestra el panorama general ordenado por presupuesto. Cambiá a <strong>Explorar</strong> para ordenar por ejecución o variación y ver tabla detallada.
              </div>
            )}

            {/* Gráfico desktop vs lista mobile */}
            {isMobile ? (
              <MobileRankList data={chartData} onSelect={handleSelectOrganismo} />
            ) : (
              <DesktopStackedChart data={chartData} onSelect={handleSelectOrganismo} />
            )}
          </div>

          {/* Tabla detalle (solo desktop) */}
          {!isMobile && viewMode === 'explorar' && (
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
                      {sortMode === 'variacion' && (
                        <th className="px-4 py-3 text-right">Δ YoY</th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {totalesAnuales.map((row) => (
                      <tr
                        key={row.id}
                        className="hover:bg-blue-50 transition-colors cursor-pointer"
                        onClick={() => handleSelectOrganismo(row.inciso, row.nombre_organismo)}
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
                        {sortMode === 'variacion' && (
                          <td className="px-4 py-3 text-right">
                            <span
                              className="font-semibold"
                              style={{
                                color:
                                  row.variacion_interanual === null
                                    ? '#6b7280'
                                    : row.variacion_interanual >= 0
                                      ? '#16a34a'
                                      : '#dc2626',
                              }}
                            >
                              {row.variacion_interanual === null
                                ? 'N/D'
                                : `${row.variacion_interanual >= 0 ? '+' : ''}${row.variacion_interanual.toFixed(1)}%`}
                            </span>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* NIVEL 2 — Detalle de organismo */}
      {!isLoading && drilldown.level === 'organismo' && (
        <div className="space-y-5">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={handleVolver}
              className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              Gasto Global
            </button>
            <span className="text-gray-400">/</span>
            <span className="text-sm text-gray-700 font-semibold leading-tight">{drilldown.nombre}</span>
          </div>

          {/* Comparación interanual */}
          <ComparacionAnualPanel inciso={drilldown.inciso} />

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
