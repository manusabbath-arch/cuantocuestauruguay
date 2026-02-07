import { useEffect, useRef, useState, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productosService, comparadorService } from '../services/productos'
import type { Comparacion } from '../types/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format, parseISO, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'
import { trackEvent } from '../lib/analytics'
import { Loader, AlertCircle } from 'lucide-react'
import SEO from '../components/SEO'

// Skeleton loader para gráfico
function ChartSkeleton() {
  return (
    <div className="h-96 bg-gradient-to-r from-gray-100 to-gray-50 rounded-lg animate-pulse flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <Loader className="w-8 h-8 text-gray-400 animate-spin" />
        <p className="text-gray-500">Cargando gráfico...</p>
      </div>
    </div>
  )
}

// Skeleton para selector de productos
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

// Error boundary para manejo de errores
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

export default function Comparador() {
  const [selectedProductos, setSelectedProductos] = useState<number[]>([])
  const [fechaDesde, setFechaDesde] = useState(
    format(subMonths(new Date(), 6), 'yyyy-MM-dd')
  )

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

  // Track comparison events via useEffect (onSuccess/onError removed in React Query v5)
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

  useEffect(() => {
    trackEvent('comparador_fecha_desde_cambio', { fecha_desde: fechaDesde })
  }, [fechaDesde])

  const chartData = comparacion?.datos.map((item) => ({
    fecha: format(parseISO(item.fecha), 'MMM yyyy', { locale: es }),
    ...item.valores,
  })) || []

  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

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
          Selecciona hasta 5 productos para comparar su evolución histórica
        </p>
      </div>

      {/* Error messages */}
      {productosError && (
        <ErrorMessage error="Error cargando productos. Por favor intenta de nuevo." />
      )}
      {comparacionError && (
        <ErrorMessage error="Error cargando datos de comparación. Por favor selecciona otros productos." />
      )}

      {/* Selector de productos */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">
          Seleccionar Productos ({selectedProductos.length}/5)
        </h2>
        
        {loadingProductos ? (
          <ProductosSkeleton />
        ) : productos && productos.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {productos.map((producto) => (
              <button
                key={producto.id}
                onClick={() => handleProductoToggle(producto.id)}
                disabled={!selectedProductos.includes(producto.id) && selectedProductos.length >= 5}
                className={`p-3 rounded-lg border-2 text-left transition-colors ${
                  selectedProductos.includes(producto.id)
                    ? 'border-primary bg-blue-50 text-primary'
                    : 'border-gray-200 hover:border-gray-300'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="font-medium">{producto.nombre}</div>
                <div className="text-sm text-gray-500">{producto.categoria}</div>
              </button>
            ))}
          </div>
        ) : (
          <ErrorMessage error="No hay productos disponibles. Por favor carga datos primero." />
        )}

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha desde:
          </label>
          <input
            type="date"
            value={fechaDesde}
            onChange={(e) => setFechaDesde(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 w-full max-w-xs"
          />
        </div>
      </div>

      {/* Gráfico */}
      {selectedProductos.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Comparación</h2>
          
          {loadingComparacion ? (
            <ChartSkeleton />
          ) : chartData.length > 0 ? (
            <Suspense fallback={<ChartSkeleton />}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="fecha" 
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                    tickFormatter={(value) => `$${value}`}
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
                      dot={{ r: 3 }}
                      name={producto.nombre}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Suspense>
          ) : (
            <div className="h-96 flex items-center justify-center">
              <div className="text-gray-500">No hay datos disponibles para este rango de fechas</div>
            </div>
          )}
        </div>
      )}

      {selectedProductos.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">
            Selecciona al menos un producto para comenzar la comparación
          </p>
        </div>
      )}
    </div>
  )
}
