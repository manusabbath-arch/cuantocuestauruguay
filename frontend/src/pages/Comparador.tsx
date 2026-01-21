import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productosService, comparadorService } from '../services/productos'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format, parseISO, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'

export default function Comparador() {
  const [selectedProductos, setSelectedProductos] = useState<number[]>([])
  const [fechaDesde, setFechaDesde] = useState(
    format(subMonths(new Date(), 6), 'yyyy-MM-dd')
  )

  const { data: productos } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productosService.getAll(),
  })

  const { data: comparacion, isLoading: loadingComparacion } = useQuery({
    queryKey: ['comparacion', selectedProductos, fechaDesde],
    queryFn: () => comparadorService.comparar(selectedProductos, fechaDesde),
    enabled: selectedProductos.length > 0,
  })

  const handleProductoToggle = (productoId: number) => {
    setSelectedProductos((prev) => {
      if (prev.includes(productoId)) {
        return prev.filter((id) => id !== productoId)
      } else if (prev.length < 5) {
        return [...prev, productoId]
      }
      return prev
    })
  }

  const chartData = comparacion?.datos.map((item) => ({
    fecha: format(parseISO(item.fecha), 'MMM yyyy', { locale: es }),
    ...item.valores,
  })) || []

  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Comparador de Precios
        </h1>
        <p className="text-gray-600">
          Selecciona hasta 5 productos para comparar su evolución histórica
        </p>
      </div>

      {/* Selector de productos */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">
          Seleccionar Productos ({selectedProductos.length}/5)
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          {productos?.map((producto) => (
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

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha desde:
          </label>
          <input
            type="date"
            value={fechaDesde}
            onChange={(e) => setFechaDesde(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2"
          />
        </div>
      </div>

      {/* Gráfico */}
      {selectedProductos.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Comparación</h2>
          
          {loadingComparacion ? (
            <div className="h-96 flex items-center justify-center">
              <div className="text-gray-500">Cargando datos...</div>
            </div>
          ) : chartData.length > 0 ? (
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
