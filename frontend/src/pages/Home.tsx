import { useQuery } from '@tanstack/react-query'
import { productosService, preciosService, variacionService } from '../services/productos'
import PriceCard from '../components/PriceCard'
import { Fuel, AlertCircle } from 'lucide-react'

export default function Home() {
  const { data: productos, isLoading: loadingProductos } = useQuery({
    queryKey: ['productos', 'combustible'],
    queryFn: () => productosService.getAll('combustible'),
  })

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg p-8 text-white">
        <div className="max-w-3xl">
          <div className="flex items-center gap-3 mb-4">
            <Fuel className="w-10 h-10" />
            <h1 className="text-4xl font-bold">PreciosRegulados.uy</h1>
          </div>
          <p className="text-xl text-blue-100 mb-4">
            Consulta precios de combustibles y servicios regulados en Uruguay
          </p>
          <p className="text-blue-100">
            Datos oficiales actualizados desde ANCAP, MEF y URSEA
          </p>
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
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Compara precios históricos
        </h2>
        <p className="text-gray-600 mb-6">
          Utiliza nuestro comparador para ver la evolución de precios en el tiempo
        </p>
        <a
          href="/comparador"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors font-medium"
        >
          Ir al Comparador
        </a>
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
