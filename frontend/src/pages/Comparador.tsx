import { useEffect, useRef, useState, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productosService, comparadorService } from '../services/productos'
import type { Comparacion } from '../types/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format, parseISO, subMonths, subYears } from 'date-fns'
import { es } from 'date-fns/locale'
import { trackEvent } from '../lib/analytics'
import { AlertCircle } from 'lucide-react'
import SEO from '../components/SEO'
import ChartSkeleton from '../components/ChartSkeleton'
import { useIsMobile } from '../hooks/useIsMobile'
import * as Tabs from '@radix-ui/react-tabs'

// ---------------------------------------------------------------------------
// Error message
// ---------------------------------------------------------------------------

function ErrorMessage({ error }: { error: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 mb-4">
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div className="text-sm text-red-800">
        <strong>Error:</strong> {error}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Skeleton selector de productos
// ---------------------------------------------------------------------------

function ProductosSkeleton() {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="p-3 rounded-lg border-2 border-gray-200 bg-gray-50 animate-pulse"
        >
          <div className="h-5 bg-gray-300 rounded mb-2 w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Rangos rápidos
// ---------------------------------------------------------------------------

const QUICK_RANGES = [
  { label: '6M', months: 6 },
  { label: '1A', years: 1 },
  { label: '2A', years: 2 },
  { label: '5A', years: 5 },
]

// ---------------------------------------------------------------------------
// Categorías disponibles (derivadas de los datos)
// ---------------------------------------------------------------------------

const CATEGORY_LABELS: Record<string, string> = {
  combustible: 'Combustibles',
  electricidad: 'Servicios',
  agua: 'Servicios',
  telecomunicaciones: 'Servicios',
  indice: 'Índices',
}

const TABS = [
  { value: 'all', label: 'Todos' },
  { value: 'combustible', label: 'Combustibles' },
  { value: 'servicios', label: 'Servicios' },
  { value: 'indice', label: 'Índices' },
]

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function Comparador() {
  const [selectedProductos, setSelectedProductos] = useState<number[]>([])
  const [fechaDesde, setFechaDesde] = useState(
    format(subMonths(new Date(), 6), 'yyyy-MM-dd')
  )
  const [activeTab, setActiveTab] = useState('all')
  const [hasAutoSelected, setHasAutoSelected] = useState(false)
  const isMobile = useIsMobile()

  const { data: productos, isLoading: loadingProductos, error: productosError } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productosService.getAll(),
  })

  const { data: comparacion, isLoading: loadingComparacion, error: comparacionError } = useQuery<Comparacion>({
    queryKey: ['comparacion', selectedProductos, fechaDesde],
    queryFn: () => comparadorService.comparar(selectedProductos, fechaDesde),
    enabled: selectedProductos.length > 0,
    retry: 2,
  })

  // Preseleccionar los primeros 2 combustibles al cargar
  useEffect(() => {
    if (!hasAutoSelected && productos && productos.length > 0 && selectedProductos.length === 0) {
      const combustibles = productos.filter((p) => p.categoria === 'combustible').slice(0, 2)
      if (combustibles.length > 0) {
        setSelectedProductos(combustibles.map((p) => p.id))
      }
      setHasAutoSelected(true)
    }
  }, [productos, hasAutoSelected, selectedProductos.length])

  // Track comparison events
  const prevComparacion = useRef(comparacion)
  useEffect(() => {
    if (comparacion && comparacion !== prevComparacion.current && comparacion.datos?.length) {
      trackEvent('comparacion_realizada', {
        productos: selectedProductos.join(','),
        cantidad_productos: selectedProductos.length,
        fecha_desde: fechaDesde,
        puntos: comparacion.datos.length,
      })
    }
    prevComparacion.current = comparacion
  }, [comparacion, selectedProductos, fechaDesde])

  useEffect(() => {
    if (comparacionError) {
      trackEvent('comparador_error', {
        error: comparacionError instanceof Error ? comparacionError.message : 'Unknown error',
      })
    }
  }, [comparacionError])

  const handleProductoToggle = (productoId: number) => {
    setSelectedProductos((prev) => {
      if (prev.includes(productoId)) {
        const next = prev.filter((id) => id !== productoId)
        trackEvent('comparador_toggle', { producto_id: productoId, seleccionado: false, total: next.length })
        return next
      } else if (prev.length < 5) {
        const next = [...prev, productoId]
        trackEvent('comparador_toggle', { producto_id: productoId, seleccionado: true, total: next.length })
        return next
      }
      return prev
    })
  }

  const handleQuickRange = (range: { months?: number; years?: number }) => {
    const date = range.months
      ? subMonths(new Date(), range.months)
      : subYears(new Date(), range.years!)
    const formatted = format(date, 'yyyy-MM-dd')
    setFechaDesde(formatted)
    trackEvent('comparador_fecha_desde_cambio', { fecha_desde: formatted })
  }

  // Filtrar productos según tab activo
  const productosFiltrados = productos?.filter((p) => {
    if (activeTab === 'all') return true
    if (activeTab === 'servicios') {
      return ['electricidad', 'agua', 'telecomunicaciones'].includes(p.categoria)
    }
    return p.categoria === activeTab
  }) ?? []

  const chartData = comparacion?.datos.map((item) => ({
    fecha: format(parseISO(item.fecha), 'MMM yyyy', { locale: es }),
    ...item.valores,
  })) || []

  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
  const chartHeight = isMobile ? 250 : 400

  return (
    <div className="space-y-8">
      <SEO
        title="Comparador de Precios - Combustibles Uruguay"
        description="Compara la evolución histórica de precios de nafta, gasoil y supergás en Uruguay. Gráficos interactivos con datos oficiales de ANCAP."
        path="/comparador"
      />
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Comparador de Precios
        </h1>
        <p className="text-gray-600">
          Seleccioná hasta 5 productos para comparar su evolución histórica
        </p>
      </div>

      {/* Error messages */}
      {productosError && (
        <ErrorMessage error="Error cargando productos. Por favor intenta de nuevo." />
      )}
      {comparacionError && (
        <ErrorMessage error="Error cargando datos de comparación. Por favor seleccioná otros productos." />
      )}

      {/* Selector de productos */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h2 className="text-lg font-semibold">
            Seleccionar Productos ({selectedProductos.length}/5)
          </h2>
          {selectedProductos.length > 0 && (
            <button
              onClick={() => setSelectedProductos([])}
              className="text-xs text-gray-500 hover:text-red-600 transition-colors"
            >
              Limpiar selección
            </button>
          )}
        </div>

        {/* Tabs de categoría */}
        <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="mb-4">
          <Tabs.List className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit flex-wrap">
            {TABS.map((tab) => (
              <Tabs.Trigger
                key={tab.value}
                value={tab.value}
                className="px-3 py-1.5 text-sm font-medium rounded-md transition-colors data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:shadow-sm text-gray-600 hover:text-gray-900"
              >
                {tab.label}
              </Tabs.Trigger>
            ))}
          </Tabs.List>
        </Tabs.Root>

        {loadingProductos ? (
          <ProductosSkeleton />
        ) : productosFiltrados.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {productosFiltrados.map((producto) => (
              <button
                key={producto.id}
                onClick={() => handleProductoToggle(producto.id)}
                disabled={!selectedProductos.includes(producto.id) && selectedProductos.length >= 5}
                className={`p-3 rounded-lg border-2 text-left transition-colors ${
                  selectedProductos.includes(producto.id)
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="font-medium">{producto.nombre}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {CATEGORY_LABELS[producto.categoria] ?? producto.categoria}
                </div>
              </button>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500 py-4">No hay productos en esta categoría.</p>
        )}

        {/* Rangos rápidos + date picker */}
        <div className="mt-5 flex flex-col sm:flex-row gap-4 items-start sm:items-end">
          <div>
            <p className="text-xs font-medium text-gray-600 mb-2">Rango rápido:</p>
            <div className="flex gap-2">
              {QUICK_RANGES.map((r) => {
                const targetDate = r.months
                  ? format(subMonths(new Date(), r.months), 'yyyy-MM-dd')
                  : format(subYears(new Date(), r.years!), 'yyyy-MM-dd')
                const isActive = fechaDesde === targetDate
                return (
                  <button
                    key={r.label}
                    onClick={() => handleQuickRange(r)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {r.label}
                  </button>
                )
              })}
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">
              Fecha desde:
            </label>
            <input
              type="date"
              value={fechaDesde}
              onChange={(e) => {
                setFechaDesde(e.target.value)
                trackEvent('comparador_fecha_desde_cambio', { fecha_desde: e.target.value })
              }}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-full max-w-xs"
            />
          </div>
        </div>
      </div>

      {/* Gráfico */}
      {selectedProductos.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Comparación</h2>

          {loadingComparacion ? (
            <ChartSkeleton height={chartHeight} />
          ) : chartData.length > 0 ? (
            <Suspense fallback={<ChartSkeleton height={chartHeight} />}>
              <ResponsiveContainer width="100%" height={chartHeight}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="fecha"
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                    tickFormatter={(value) => `$${value}`}
                    width={isMobile ? 50 : 60}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                    }}
                    formatter={(value: number) => `$${value.toFixed(2)}`}
                  />
                  <Legend />
                  {comparacion?.productos.map((producto, index) => (
                    <Line
                      key={producto.id}
                      type="monotone"
                      dataKey={producto.id.toString()}
                      stroke={colors[index % colors.length]}
                      strokeWidth={2}
                      dot={false}
                      name={producto.nombre}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Suspense>
          ) : (
            <div style={{ height: chartHeight }} className="flex items-center justify-center">
              <div className="text-gray-500">No hay datos disponibles para este rango de fechas</div>
            </div>
          )}
        </div>
      )}

      {selectedProductos.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">
            Seleccioná al menos un producto para comenzar la comparación
          </p>
        </div>
      )}
    </div>
  )
}
