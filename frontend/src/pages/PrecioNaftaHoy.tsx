import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productosService, preciosService, variacionService } from '../services/productos'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { trackEvent } from '../lib/analytics'
import SEO from '../components/SEO'

export default function PrecioNaftaHoy() {
  const { data: combustibles } = useQuery({
    queryKey: ['productos', 'combustible'],
    queryFn: () => productosService.getAll('combustible'),
  })

  const mapa = useMemo(() => {
    const premium = combustibles?.find(p => p.nombre.toLowerCase().includes('premium'))
    const super95 = combustibles?.find(p => p.nombre.toLowerCase().includes('súper') || p.nombre.toLowerCase().includes('super'))
    return { premium, super95 }
  }, [combustibles])

  const { data: ultimoPremium } = useQuery({
    queryKey: ['ultimo', mapa.premium?.id],
    queryFn: () => preciosService.getUltimo(mapa.premium!.id),
    enabled: !!mapa.premium?.id,
  })
  const { data: varPremium } = useQuery({
    queryKey: ['variacion', mapa.premium?.id, 'mes'],
    queryFn: () => variacionService.calcular(mapa.premium!.id, 'mes'),
    enabled: !!mapa.premium?.id,
  })

  const { data: ultimoSuper } = useQuery({
    queryKey: ['ultimo', mapa.super95?.id],
    queryFn: () => preciosService.getUltimo(mapa.super95!.id),
    enabled: !!mapa.super95?.id,
  })
  const { data: varSuper } = useQuery({
    queryKey: ['variacion', mapa.super95?.id, 'mes'],
    queryFn: () => variacionService.calcular(mapa.super95!.id, 'mes'),
    enabled: !!mapa.super95?.id,
  })

  const fechaFmt = (d?: string | Date) => (d ? format(new Date(d), "d 'de' MMMM, yyyy", { locale: es }) : '')

  const handleShare = () => {
    trackEvent('share_click', { page: 'precio_nafta_hoy' })
    const url = typeof window !== 'undefined' ? window.location.href : ''
    if (navigator.share) {
      navigator.share({ title: 'Precio nafta hoy', url }).catch(() => {})
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).catch(() => {})
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      <SEO
        title="Precio de la Nafta en Uruguay Hoy - Actualizado"
        description="Precio oficial de la nafta Súper 95 y Premium 97 en Uruguay hoy. Datos de ANCAP actualizados diariamente. Variación mensual y tendencia histórica."
        path="/precio-nafta-hoy"
        jsonLd={{
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: [
            {
              '@type': 'Question',
              name: '¿Cuál es el precio de la nafta en Uruguay hoy?',
              acceptedAnswer: {
                '@type': 'Answer',
                text: 'Consulta los precios oficiales actualizados diariamente para Nafta Súper 95 y Nafta Premium 97.',
              },
            },
          ],
        }}
      />

      <div className="text-center space-y-2 mb-8">
        <h1 className="text-4xl font-bold">Precio de la nafta en Uruguay hoy</h1>
        <p className="text-gray-600">Datos oficiales actualizados diariamente (CKAN - ANCAP)</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Nafta Súper 95</h2>
          {ultimoSuper ? (
            <>
              <div className="text-3xl font-bold">${Number(ultimoSuper.valor).toFixed(2)}</div>
              <div className="text-sm text-gray-600">Actualizado: {fechaFmt(ultimoSuper.fecha)}</div>
              {varSuper && (
                <div className={`mt-2 text-sm font-medium ${Number(varSuper.variacion_porcentual) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {Number(varSuper.variacion_porcentual).toFixed(2)}% en 30 días
                </div>
              )}
            </>
          ) : (
            <div className="text-gray-500">Cargando...</div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Nafta Premium 97</h2>
          {ultimoPremium ? (
            <>
              <div className="text-3xl font-bold">${Number(ultimoPremium.valor).toFixed(2)}</div>
              <div className="text-sm text-gray-600">Actualizado: {fechaFmt(ultimoPremium.fecha)}</div>
              {varPremium && (
                <div className={`mt-2 text-sm font-medium ${Number(varPremium.variacion_porcentual) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {Number(varPremium.variacion_porcentual).toFixed(2)}% en 30 días
                </div>
              )}
            </>
          ) : (
            <div className="text-gray-500">Cargando...</div>
          )}
        </div>
      </div>

      <div className="mt-8 flex items-center gap-3">
        <button onClick={handleShare} className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700">Compartir</button>
        <a href="/servicios" className="text-blue-700 hover:underline">Ver más precios →</a>
      </div>

      <section className="mt-12 prose max-w-none">
        <h2>Preguntas frecuentes</h2>
        <h3>¿Cada cuánto se actualizan los precios?</h3>
        <p>Diariamente, a partir de los datos oficiales publicados en el Catálogo de Datos Abiertos del gobierno.</p>
        <h3>¿Qué diferencia hay entre Súper 95 y Premium 97?</h3>
        <p>La principal diferencia está en el octanaje. La Premium 97 suele tener un precio mayor por sus características.</p>
      </section>
    </div>
  )
}
