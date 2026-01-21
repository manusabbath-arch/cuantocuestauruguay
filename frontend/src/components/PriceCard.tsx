import { ArrowUp, ArrowDown, Minus } from 'lucide-react'
import type { Producto, Variacion } from '../types/api'
import { Link } from 'react-router-dom'

interface PriceCardProps {
  producto: Producto
  precio?: number
  variacion?: Variacion
  loading?: boolean
}

export default function PriceCard({ producto, precio, variacion, loading }: PriceCardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
      </div>
    )
  }

  const variacionPositiva = variacion && variacion.variacion_porcentual > 0
  const variacionNegativa = variacion && variacion.variacion_porcentual < 0
  const variacionNula = variacion && variacion.variacion_porcentual === 0

  return (
    <Link to={`/producto/${producto.id}`} className="block">
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{producto.nombre}</h3>
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
            {producto.categoria}
          </span>
        </div>

        {precio !== undefined && (
          <div className="mb-2">
            <span className="text-3xl font-bold text-primary">
              ${precio.toFixed(2)}
            </span>
            <span className="text-gray-500 ml-2">/ {producto.unidad}</span>
          </div>
        )}

        {variacion && (
          <div className="flex items-center gap-2 text-sm">
            {variacionPositiva && (
              <>
                <ArrowUp className="w-4 h-4 text-red-500" />
                <span className="text-red-500 font-medium">
                  +{variacion.variacion_porcentual.toFixed(2)}%
                </span>
              </>
            )}
            {variacionNegativa && (
              <>
                <ArrowDown className="w-4 h-4 text-green-500" />
                <span className="text-green-500 font-medium">
                  {variacion.variacion_porcentual.toFixed(2)}%
                </span>
              </>
            )}
            {variacionNula && (
              <>
                <Minus className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400 font-medium">Sin cambios</span>
              </>
            )}
            <span className="text-gray-500">vs. mes anterior</span>
          </div>
        )}
      </div>
    </Link>
  )
}
