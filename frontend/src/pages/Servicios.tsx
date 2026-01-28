import { useQuery } from '@tanstack/react-query'
import { productosService } from '../services/productos'
import PriceCard from '../components/PriceCard'
import { Zap, Droplet, Wifi, AlertCircle } from 'lucide-react'

export default function Servicios() {
  // Fetch UTE (electricidad)
  const { data: productosUTE, isLoading: loadingUTE } = useQuery({
    queryKey: ['productos', 'electricidad'],
    queryFn: () => productosService.getAll('electricidad'),
  })

  // Fetch OSE (agua)
  const { data: productosOSE, isLoading: loadingOSE } = useQuery({
    queryKey: ['productos', 'agua'],
    queryFn: () => productosService.getAll('agua'),
  })

  // Fetch Antel (telecomunicaciones)
  const { data: productosAntel, isLoading: loadingAntel } = useQuery({
    queryKey: ['productos', 'telecomunicaciones'],
    queryFn: () => productosService.getAll('telecomunicaciones'),
  })

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl shadow-lg p-8 text-white">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold mb-4">Servicios Públicos</h1>
          <p className="text-xl text-green-100 mb-4">
            Tarifas actualizadas de UTE, OSE y Antel
          </p>
          <p className="text-green-100">
            Datos oficiales desde URSEA y organismos reguladores
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-800">
          <strong>Información:</strong> Las tarifas mostradas corresponden a los valores 
          publicados por URSEA (Unidad Reguladora de Servicios de Energía y Agua). Los 
          cargos finales pueden variar según consumo, ubicación y otros factores. Consulte 
          directamente con cada proveedor para información específica.
        </div>
      </div>

      {/* UTE - Electricidad */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Zap className="w-8 h-8 text-yellow-500" />
          <h2 className="text-2xl font-bold text-gray-900">
            UTE - Tarifas de Electricidad
          </h2>
        </div>

        {loadingUTE ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <PriceCard 
                key={i} 
                producto={{ id: i, nombre: '', categoria: '', unidad: '', activo: true }} 
                loading 
              />
            ))}
          </div>
        ) : productosUTE && productosUTE.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {productosUTE.map((producto) => (
              <ProductoCard key={producto.id} producto={producto} />
            ))}
          </div>
        ) : (
          <EmptyState 
            message="Tarifas de UTE no disponibles. Ejecute el ETL de UTE para cargar datos."
          />
        )}
      </section>

      {/* OSE - Agua y Saneamiento */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Droplet className="w-8 h-8 text-blue-500" />
          <h2 className="text-2xl font-bold text-gray-900">
            OSE - Tarifas de Agua y Saneamiento
          </h2>
        </div>

        {loadingOSE ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2].map((i) => (
              <PriceCard 
                key={i} 
                producto={{ id: i, nombre: '', categoria: '', unidad: '', activo: true }} 
                loading 
              />
            ))}
          </div>
        ) : productosOSE && productosOSE.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {productosOSE.map((producto) => (
              <ProductoCard key={producto.id} producto={producto} />
            ))}
          </div>
        ) : (
          <EmptyState 
            message="Tarifas de OSE no disponibles. Ejecute el ETL de OSE para cargar datos."
          />
        )}
      </section>

      {/* Antel - Telecomunicaciones */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Wifi className="w-8 h-8 text-purple-500" />
          <h2 className="text-2xl font-bold text-gray-900">
            Antel - Planes de Telecomunicaciones
          </h2>
        </div>

        {loadingAntel ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <PriceCard 
                key={i} 
                producto={{ id: i, nombre: '', categoria: '', unidad: '', activo: true }} 
                loading 
              />
            ))}
          </div>
        ) : productosAntel && productosAntel.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {productosAntel.map((producto) => (
              <ProductoCard key={producto.id} producto={producto} />
            ))}
          </div>
        ) : (
          <EmptyState 
            message="Planes de Antel no disponibles. Ejecute el ETL de Antel para cargar datos."
          />
        )}
      </section>

      {/* Call to Action */}
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Compara servicios históricos
        </h2>
        <p className="text-gray-600 mb-6">
          Utiliza nuestro comparador para ver la evolución de tarifas en el tiempo
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
    queryFn: () => productosService.getPrecioUltimo(producto.id),
    retry: false,
  })

  const { data: variacion } = useQuery({
    queryKey: ['variacion', producto.id],
    queryFn: () => productosService.getVariacion(producto.id, 30),
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

// Empty state component
function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-12 bg-white rounded-lg shadow">
      <p className="text-gray-500">{message}</p>
    </div>
  )
}
