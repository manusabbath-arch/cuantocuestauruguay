import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { productosService, preciosService, estadisticasService, variacionService } from '../services/productos'
import PriceChart from '../components/PriceChart'
import { ArrowLeft, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ProductoDetalle() {
  const { id } = useParams<{ id: string }>()
  const productoId = parseInt(id || '0')

  const { data: producto, isLoading: loadingProducto } = useQuery({
    queryKey: ['producto', productoId],
    queryFn: () => productosService.getById(productoId),
  })

  const { data: precios, isLoading: loadingPrecios } = useQuery({
    queryKey: ['precios', productoId],
    queryFn: () => preciosService.getByProducto(productoId, undefined, undefined, 100),
  })

  const { data: estadisticas } = useQuery({
    queryKey: ['estadisticas', productoId],
    queryFn: () => estadisticasService.get(productoId),
  })

  const { data: variacionMes } = useQuery({
    queryKey: ['variacion-mes', productoId],
    queryFn: () => variacionService.calcular(productoId, 'mes'),
  })

  const { data: variacionAno } = useQuery({
    queryKey: ['variacion-ano', productoId],
    queryFn: () => variacionService.calcular(productoId, 'año'),
  })

  if (loadingProducto) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-gray-500">Cargando...</div>
      </div>
    )
  }

  if (!producto) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Producto no encontrado</p>
        <Link to="/" className="text-primary hover:underline">
          Volver al inicio
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <Link to="/" className="inline-flex items-center text-gray-600 hover:text-primary mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver
        </Link>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {producto.nombre}
            </h1>
            <div className="flex items-center gap-3 text-gray-600">
              <span className="text-sm bg-gray-100 px-3 py-1 rounded">
                {producto.categoria}
              </span>
              <span className="text-sm">Precio por {producto.unidad}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Variación Mensual</span>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          {variacionMes ? (
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${
                variacionMes.variacion_porcentual > 0 ? 'text-red-500' : 
                variacionMes.variacion_porcentual < 0 ? 'text-green-500' : 
                'text-gray-500'
              }`}>
                {variacionMes.variacion_porcentual > 0 ? '+' : ''}
                {variacionMes.variacion_porcentual.toFixed(2)}%
              </span>
            </div>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Variación Anual</span>
            <TrendingDown className="w-5 h-5 text-gray-400" />
          </div>
          {variacionAno ? (
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${
                variacionAno.variacion_porcentual > 0 ? 'text-red-500' : 
                variacionAno.variacion_porcentual < 0 ? 'text-green-500' : 
                'text-gray-500'
              }`}>
                {variacionAno.variacion_porcentual > 0 ? '+' : ''}
                {variacionAno.variacion_porcentual.toFixed(2)}%
              </span>
            </div>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Precio Mínimo</span>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          {estadisticas ? (
            <span className="text-2xl font-bold text-gray-900">
              ${estadisticas.minimo.toFixed(2)}
            </span>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Precio Máximo</span>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          {estadisticas ? (
            <span className="text-2xl font-bold text-gray-900">
              ${estadisticas.maximo.toFixed(2)}
            </span>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>
      </div>

      {/* Gráfico */}
      {loadingPrecios ? (
        <div className="bg-white rounded-lg shadow-md p-6 h-96 flex items-center justify-center">
          <div className="text-gray-500">Cargando datos...</div>
        </div>
      ) : precios && precios.length > 0 ? (
        <PriceChart data={precios} productName={producto.nombre} />
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
          No hay datos históricos disponibles
        </div>
      )}

      {/* Información adicional */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">Información</h2>
        <dl className="space-y-2">
          {estadisticas && (
            <>
              <div className="flex justify-between">
                <dt className="text-gray-600">Precio Promedio:</dt>
                <dd className="font-medium">${estadisticas.promedio.toFixed(2)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Registros Históricos:</dt>
                <dd className="font-medium">{estadisticas.cantidad_registros}</dd>
              </div>
            </>
          )}
          <div className="flex justify-between">
            <dt className="text-gray-600">Fuente:</dt>
            <dd className="font-medium">catalogodatos.gub.uy</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
