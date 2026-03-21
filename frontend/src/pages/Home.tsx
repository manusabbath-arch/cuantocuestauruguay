import { useQuery } from '@tanstack/react-query'
import { productosService, preciosService, variacionService } from '../services/productos'
import { api } from '../services/api'
import ProductoCard from '../components/ProductoCard'
import StatCard from '../components/StatCard'
import SEO from '../components/SEO'
import {
  Fuel,
  BarChart3,
  FileText,
  Zap,
  TrendingUp,
  Building2,
  LineChart,
  ArrowRight,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { trackEvent } from '../lib/analytics'
import type { Producto } from '../types/api'

// ---------------------------------------------------------------------------
// Tipos internos
// ---------------------------------------------------------------------------

interface EjecucionRow {
  credito_vigente: number
  ejecutado: number
  mes: number | null
}

// ---------------------------------------------------------------------------
// Servicio de gasto (para el panel resumen del home)
// ---------------------------------------------------------------------------

const gastoHomeService = {
  getResumen: async (): Promise<EjecucionRow[]> => {
    const anio = new Date().getFullYear()
    const { data } = await api.get('/api/v1/gasto/ejecucion', {
      params: { anio, limit: 50 },
    })
    return data
  },
}

// ---------------------------------------------------------------------------
// Sub-componentes del dashboard
// ---------------------------------------------------------------------------

function PrecioStatCard({ producto }: { producto: Producto }) {
  const { data: precio } = useQuery({
    queryKey: ['precio-ultimo', producto.id],
    queryFn: () => preciosService.getUltimo(producto.id),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  const { data: variacion } = useQuery({
    queryKey: ['variacion', producto.id],
    queryFn: () => variacionService.calcular(producto.id, 'mes'),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  const value = precio ? `$${precio.valor.toFixed(2)}` : '—'
  const trend = variacion
    ? { value: variacion.variacion_porcentual, label: 'vs. mes anterior' }
    : undefined

  return (
    <StatCard
      label={producto.nombre}
      value={value}
      subValue={precio?.fecha ? `Al ${precio.fecha}` : undefined}
      trend={trend}
    />
  )
}

function GastoResumenCard({ onClick }: { onClick: () => void }) {
  const { data } = useQuery({
    queryKey: ['gasto', 'home-resumen'],
    queryFn: gastoHomeService.getResumen,
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  const totales = (data ?? []).filter((r) => r.mes === null)
  const totalCredito = totales.reduce((s, r) => s + r.credito_vigente, 0)
  const totalEjecutado = totales.reduce((s, r) => s + r.ejecutado, 0)
  const pct = totalCredito > 0 ? (totalEjecutado / totalCredito) * 100 : null

  const pctColor =
    pct === null ? '#6b7280' : pct >= 90 ? '#16a34a' : pct >= 70 ? '#ca8a04' : '#dc2626'

  return (
    <StatCard
      label="Ejecución presupuestal"
      value={pct !== null ? `${pct.toFixed(1)}%` : '—'}
      subValue={`Año ${new Date().getFullYear()}`}
      colorOverride={pctColor}
      onClick={onClick}
      className="group"
    />
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function Home() {
  const navigate = useNavigate()

  const handleNavigate = (path: string, eventName: string) => {
    trackEvent(eventName, { source: 'home_cta' })
    navigate(path)
  }

  // Combustibles para la sección de cards de producto
  const { data: combustibles, isLoading: loadingCombustibles } = useQuery({
    queryKey: ['productos', 'combustible'],
    queryFn: () => productosService.getAll('combustible'),
  })

  // Productos de índices para el dashboard (IPC, dólar)
  const { data: indices } = useQuery({
    queryKey: ['productos', 'indice'],
    queryFn: () => productosService.getAll('indice'),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  // UTE (electricidad) para el dashboard
  const { data: serviciosElec } = useQuery({
    queryKey: ['productos', 'electricidad'],
    queryFn: () => productosService.getAll('electricidad'),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  // Nafta Súper 95 para el dashboard (primer combustible)
  const naftaSuperProducto = combustibles?.find((p) =>
    p.nombre.toLowerCase().includes('super') || p.nombre.toLowerCase().includes('súper')
  ) ?? combustibles?.[0]

  // UTE BT1 para el dashboard
  const uteBt1 = serviciosElec?.find((p) => p.nombre.toLowerCase().includes('bt1')) ?? serviciosElec?.[0]

  // Primer índice (IPC)
  const ipc = indices?.find((p) => p.nombre.toLowerCase().includes('ipc')) ?? indices?.[0]
  // Dólar
  const dolar = indices?.find((p) =>
    p.nombre.toLowerCase().includes('dólar') || p.nombre.toLowerCase().includes('dolar')
  ) ?? indices?.[1]

  return (
    <div className="space-y-8">
      <SEO
        title="PreciosRegulados.uy - Precios Regulados en Uruguay"
        description="Consulta precios actualizados de nafta, gasoil, UTE, OSE y Antel en Uruguay. Datos oficiales del gobierno actualizados diariamente. Analizá tu factura de UTE gratis."
        path="/"
      />

      {/* Hero compacto */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl shadow-lg p-5 sm:p-8 text-white">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-2 sm:mb-3">
            <TrendingUp className="w-7 h-7 sm:w-9 sm:h-9" />
            <h1 className="text-2xl sm:text-4xl font-bold">PreciosRegulados.uy</h1>
          </div>
          <p className="text-sm sm:text-lg text-blue-100 mb-4">
            Datos oficiales sobre precios, servicios públicos y gasto del Estado uruguayo.
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => handleNavigate('/precio-nafta-hoy', 'home_cta_nafta')}
              className="bg-white text-blue-600 px-4 py-2.5 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base"
            >
              <Fuel className="w-4 h-4" />
              Precio Nafta HOY
            </button>
            <button
              onClick={() => handleNavigate('/comparador', 'home_cta_comparador')}
              className="bg-blue-500 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-400 transition-colors flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base"
            >
              <BarChart3 className="w-4 h-4" />
              Comparar precios
            </button>
            <button
              onClick={() => handleNavigate('/gasto-publico', 'home_cta_gasto')}
              className="bg-violet-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-violet-500 transition-colors flex items-center justify-center gap-2 min-h-[44px] text-sm sm:text-base"
            >
              <Building2 className="w-4 h-4" />
              Gasto Público
            </button>
          </div>
        </div>
      </div>

      {/* Dashboard de datos en vivo — 3 columnas */}
      <section>
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Estado actual</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Columna 1: Combustible + UTE */}
          <div className="space-y-3">
            {naftaSuperProducto && <PrecioStatCard producto={naftaSuperProducto} />}
            {uteBt1 && <PrecioStatCard producto={uteBt1} />}
          </div>

          {/* Columna 2: Índices */}
          <div className="space-y-3">
            {ipc && <PrecioStatCard producto={ipc} />}
            {dolar && <PrecioStatCard producto={dolar} />}
            {!ipc && !dolar && (
              <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-center text-sm text-gray-400 h-full min-h-[80px]">
                Índices no disponibles
              </div>
            )}
          </div>

          {/* Columna 3: Gasto público resumen */}
          <div className="space-y-3">
            <GastoResumenCard onClick={() => handleNavigate('/gasto-publico', 'home_cta_gasto_card')} />
            <button
              onClick={() => handleNavigate('/gasto-publico', 'home_cta_gasto_detail')}
              className="w-full bg-white rounded-xl border border-gray-200 p-4 text-left text-sm text-gray-600 hover:border-violet-300 hover:bg-violet-50 transition-all flex items-center justify-between group"
            >
              <span>Ver ejecución por organismo</span>
              <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-violet-600 transition-colors" />
            </button>
          </div>
        </div>
      </section>

      {/* Acceso rápido diferenciado */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Consultas frecuentes (usuario común) */}
        <div>
          <h2 className="text-base font-semibold text-gray-700 mb-3">Consultas frecuentes</h2>
          <div className="space-y-3">
            <button
              onClick={() => handleNavigate('/precio-nafta-hoy', 'home_quick_nafta')}
              className="w-full bg-amber-50 border border-amber-200 rounded-xl p-5 text-left hover:bg-amber-100 transition-colors flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-amber-400 rounded-lg flex items-center justify-center flex-shrink-0">
                <Fuel className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">¿Cuánto cuesta la nafta hoy?</p>
                <p className="text-sm text-gray-500 mt-0.5">Precios actualizados de ANCAP</p>
              </div>
              <ArrowRight className="w-4 h-4 text-amber-400 ml-auto self-center group-hover:translate-x-0.5 transition-transform" />
            </button>

            <button
              onClick={() => handleNavigate('/mi-factura', 'home_quick_factura')}
              className="w-full bg-blue-50 border border-blue-200 rounded-xl p-5 text-left hover:bg-blue-100 transition-colors flex items-start gap-4 group"
            >
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">¿Estás pagando de más en UTE?</p>
                <p className="text-sm text-gray-500 mt-0.5">Analizá tu factura PDF gratis, sin registro</p>
              </div>
              <ArrowRight className="w-4 h-4 text-blue-400 ml-auto self-center group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>

        {/* Herramientas de análisis (profesional) */}
        <div>
          <h2 className="text-base font-semibold text-gray-700 mb-3">Herramientas de análisis</h2>
          <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
            {[
              {
                icon: BarChart3,
                label: 'Comparador histórico',
                desc: 'Evolución de precios en el tiempo',
                path: '/comparador',
                event: 'home_tool_comparador',
              },
              {
                icon: Building2,
                label: 'Gasto público detallado',
                desc: 'Ejecución presupuestal por organismo',
                path: '/gasto-publico',
                event: 'home_tool_gasto',
              },
              {
                icon: LineChart,
                label: 'Servicios regulados',
                desc: 'Tarifas de UTE, OSE y Antel',
                path: '/servicios',
                event: 'home_tool_servicios',
              },
              {
                icon: FileText,
                label: 'Mi Factura UTE',
                desc: 'Análisis y recomendaciones de tarifa',
                path: '/mi-factura',
                event: 'home_tool_factura',
              },
            ].map(({ icon: Icon, label, desc, path, event }) => (
              <button
                key={path}
                onClick={() => handleNavigate(path, event)}
                className="w-full flex items-center gap-4 px-5 py-4 text-left hover:bg-gray-50 transition-colors group"
              >
                <Icon className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{label}</p>
                  <p className="text-xs text-gray-500">{desc}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-blue-500 transition-colors flex-shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Precios de combustibles */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Combustibles</h2>
          <button
            onClick={() => handleNavigate('/precio-nafta-hoy', 'home_ver_todos_combustibles')}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
          >
            Ver todos <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loadingCombustibles ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : combustibles && combustibles.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {combustibles.map((producto) => (
              <ProductoCard key={producto.id} producto={producto} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">
              No hay datos disponibles. Por favor, ejecuté el ETL para cargar datos.
            </p>
          </div>
        )}
      </section>
    </div>
  )
}
