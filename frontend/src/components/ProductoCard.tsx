import { useQuery } from '@tanstack/react-query'
import { preciosService, variacionService } from '../services/productos'
import PriceCard from './PriceCard'
import type { Producto } from '../types/api'

interface ProductoCardProps {
  producto: Producto
}

export default function ProductoCard({ producto }: ProductoCardProps) {
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
      fechaActualizacion={ultimoPrecio?.fecha}
      variacion={variacion}
    />
  )
}
