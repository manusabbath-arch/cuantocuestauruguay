import { useQuery } from '@tanstack/react-query'
import { productosService, preciosService, variacionService } from '../services/productos'
import PriceCard from '../components/PriceCard'
import SEO from '../components/SEO'
import { Fuel, AlertCircle, TrendingUp, BarChart3, FileText, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { trackEvent } from '../lib/analytics'

export default function Home() {
  const navigate = useNavigate()
  const { data: productos, isLoading: loadingProductos } = useQuery({
    queryKey: ['productos', 'combustible'],
    queryFn: () => productosService.getAll('combustible'),
  })

  const handleNavigate = (path: string, eventName: string) => {
    trackEvent(eventName, { source: 'home_cta' })
    navigate(path)
  }

  return (
    <div className="space-y-8">
      <SEO
        title="PreciosRegulados.uy - Precios Regulados en Uruguay"
        description="Consulta precios actualizados de nafta, gasoil, UTE, OSE y Antel en Uruguay. Datos oficiales del gobierno actualizados diariamente. Analizá tu factura de UTE gratis."
        path="/"
      />
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg p-5 sm:p-8 text-white">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-3 sm:mb-4">
            <Fuel className="w-8 h-8 sm:w-10 sm:h-10" />
            <h1 className="text-2xl sm:text-4xl font-bold">PreciosRegulados.uy</h1>
          </div>
          <p className="text-base sm:text-xl text-blue-100 mb-3 sm:mb-4">
            Consulta precios de combustibles y servicios regulados en Uruguay
          </p>
          <p className="text-sm sm:text-base text-blue-100 mb-4 sm:mb-6">
            Datos oficiales actualizados desde ANCAP, MEF y URSEA
          </p>

          {/* Quick Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => handleNavigate('/precio-nafta-hoy', 'home_cta_nafta')}
              className="bg-white text-blue-600 px-4 py-2.5 sm:py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 min-h-[44px]"
            >
              <TrendingUp className="w-5 h-5" />
              Ver Precio Nafta HOY
            </button>
            <button
              onClick={() => handleNavigate('/comparador', 'home_cta_comparador')}
              className="bg-blue-700 text-white px-4 py-2.5 sm:py-2 rounded-lg font-medium hover:bg-blue-800 transition-colors flex items-center justify-center gap-2 min-h-[44px]"
            >
              <BarChart3 className="w-5 h-5" />
              Comparar Precios
            </button>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-800">
          <strong>Importante:</strong> Los datos presentados provienen de fuentes oficiales 
          (ANCAP, MEF, URSEA) y se actualizan periódicamente. PreciosRegulados.uy no se 
          responsabiliza por decisiones tomadas en base a esta información. Para datos 
          oficiales, consulte directamente las fuentes gubernamentales.
        </div>
      </div>

      {/* Mi Factura CTA */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl shadow-lg p-5 sm:p-8 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
          <div className="w-12 h-12 sm:w-14 sm:h-14 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <Zap className="w-6 h-6 sm:w-7 sm:h-7" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg sm:text-xl font-bold mb-1">
              ¿Estás pagando de más en tu factura de UTE?
            </h2>
            <p className="text-blue-200 text-sm sm:text-base">
              Subí tu factura en PDF y descubrí si podés ahorrar con un cambio de tarifa. Gratis, sin registro, sin guardar tus datos.
            </p>
          </div>
          <button
            onClick={() => handleNavigate('/mi-factura', 'home_cta_mi_factura')}
            className="bg-white text-blue-700 px-5 py-2.5 rounded-lg font-semibold hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 min-h-[44px] whitespace-nowrap"
          >
            <FileText className="w-5 h-5" />
            Analizar mi factura
          </button>
        </div>
      </div>

      {/* Precios Actuales */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Precios de Combustibles
        </h2>

        {loadingProductos ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <PriceCard 
                key={i} 
                producto={{ id: i, nombre: '', categoria: '', unidad: '', activo: true }} 
                loading 
              />
            ))}
          </div>
        ) : productos && productos.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {productos.map((producto) => (
              <ProductoCard key={producto.id} producto={producto} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">
              No hay datos disponibles. Por favor, ejecute el ETL para cargar datos.
            </p>
          </div>
        )}
      </section>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg shadow-md p-8 border-l-4 border-amber-400">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-amber-500" />
              Precio Nafta HOY
            </h2>
            <p className="text-gray-600 mb-4">
              Consulta el precio actual de todos los combustibles con variación del mes
            </p>
            <button
              onClick={() => handleNavigate('/precio-nafta-hoy', 'home_cta_nafta_detail')}
              className="inline-block bg-amber-500 text-white px-6 py-2 rounded-lg hover:bg-amber-600 transition-colors font-medium"
            >
              Ver Detalles
            </button>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-500" />
              Comparador Histórico
            </h2>
            <p className="text-gray-600 mb-4">
              Compara precios de múltiples productos en el tiempo y descubre tendencias
            </p>
            <button
              onClick={() => handleNavigate('/comparador', 'home_cta_comparador_detail')}
              className="inline-block bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
              Abrir Comparador
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Component to fetch and display individual product data
function ProductoCard({ producto }: { producto: any }) {
  const { data: ultimoPrecio } = useQuery({
    queryKey: ['precio-ultimo', producto.id],
    queryFn: () => preciosService.getUltimo(producto.id),
    retry: false,
  })

  const { data: variacion } = useQuery({
    queryKey: ['variacion', producto.id],
    queryFn: () => variacionService.calcular(producto.id, 'mes'),
    retry: false,
  })

  return (
    <PriceCard
      producto={producto}
      precio={ultimoPrecio?.valor}
      variacion={variacion}
    />
  )
}
