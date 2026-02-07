import { useState, lazy, Suspense } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileText, Loader, Eye, Clock, Trash2, ChevronRight } from 'lucide-react'
import { facturasService, billHistory } from '../services/facturas'
import { trackEvent } from '../lib/analytics'
import type { BillAnalysisResponse, BillHistoryEntry } from '../types/factura'
import BillUploader from '../components/BillUploader'
import SEO from '../components/SEO'

const BillResults = lazy(() => import('../components/BillResults'))

const DEMO_ANALYSIS: BillAnalysisResponse = {
  servicio: 'UTE',
  periodo: { desde: '2026-01-01', hasta: '2026-01-31' },
  consumo: { valor: 420, unidad: 'kWh' },
  cargos: { fijo: 380, variable: 1730, total: 2110 },
  metricas: { precio_unitario: 5.02, costo_diario: 70, dias_facturados: 30, consumo_diario_kwh: 14 },
  comparacion: {
    tu_precio_kwh: 5.02,
    tarifas_oficiales: {},
    tu_tarifa: 'Residencial Simple',
  },
  percentil_consumo: 75,
  recomendaciones: [
    {
      tipo: 'cambio_tarifa',
      titulo: 'Considerar cambio a Doble Horario',
      descripcion: 'Tu consumo de 420 kWh/mes es alto. Con la tarifa Doble Horario podrías ahorrar ~$253/mes si concentrás el uso en horario valle (23:00 a 07:00 y fines de semana). Eso es $3036 al año. El trámite se hace online en la web de UTE.',
      ahorro_estimado: 253,
    },
    {
      tipo: 'reduccion_consumo',
      titulo: 'Tu consumo es superior al promedio',
      descripcion: 'Tu consumo de 420 kWh/mes está en el percentil 75 (más que el 75% de los hogares uruguayos). El promedio nacional es ~225 kWh/mes.\n\nEstimación de consumo por electrodoméstico:\n• Calefón eléctrico (100L): ~150 kWh ($753/mes)\n• Aire acondicionado (uso diario, 8h): ~120 kWh ($602/mes)\n• Heladera con freezer: ~45 kWh ($226/mes)\n\nTip: Bajar el termostato del calefón de 60°C a 45°C puede ahorrarte ~$226/mes sin perder confort.',
      ahorro_estimado: 226,
    },
    {
      tipo: 'informativo',
      titulo: 'Tu costo diario de electricidad',
      descripcion: 'Estás pagando $70 por día ($2110 en 30 días). Tu precio efectivo es $5.02/kWh. Proyección anual: ~$25,320.',
      ahorro_estimado: null,
    },
  ],
  ahorro_potencial: 479,
}

function HistorySection({ onSelect }: { onSelect: (analysis: BillAnalysisResponse) => void }) {
  const [entries, setEntries] = useState<BillHistoryEntry[]>(() => billHistory.getAll())

  if (entries.length === 0) return null

  const handleRemove = (id: string) => {
    billHistory.remove(id)
    setEntries(billHistory.getAll())
    trackEvent('history_entry_removed', {})
  }

  const handleClear = () => {
    billHistory.clear()
    setEntries([])
    trackEvent('history_cleared', {})
  }

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('es-UY', { day: 'numeric', month: 'short' })

  return (
    <div className="max-w-2xl mx-auto mt-6 sm:mt-8">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-gray-700">
          <Clock className="w-4 h-4" />
          <h3 className="text-sm font-semibold">Análisis anteriores</h3>
        </div>
        <button
          onClick={handleClear}
          className="text-xs text-gray-400 hover:text-red-500 transition-colors min-h-[44px] flex items-center"
        >
          Borrar todo
        </button>
      </div>
      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="bg-white rounded-lg border border-gray-200 p-3 sm:p-4 flex items-center gap-3 hover:border-blue-300 transition-colors"
          >
            <button
              onClick={() => {
                onSelect(entry.analysis)
                trackEvent('history_entry_viewed', { servicio: entry.servicio })
              }}
              className="flex-1 flex items-center gap-3 text-left min-h-[44px]"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm text-gray-900">{entry.servicio}</span>
                  <span className="text-xs text-gray-400">
                    {formatDate(entry.periodo.desde)} - {formatDate(entry.periodo.hasta)}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {entry.consumo} {entry.unidad} &middot; ${entry.total.toLocaleString('es-UY')}
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
            </button>
            <button
              onClick={() => handleRemove(entry.id)}
              className="p-2 text-gray-300 hover:text-red-500 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Eliminar"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MiFactura() {
  const [analysis, setAnalysis] = useState<BillAnalysisResponse | null>(null)
  const [isDemo, setIsDemo] = useState(false)

  const mutation = useMutation({
    mutationFn: (file: File) => facturasService.analyze(file),
    onSuccess: (data) => {
      setAnalysis(data)
      setIsDemo(false)
      billHistory.save(data)
      trackEvent('bill_analyzed', { servicio: data.servicio, consumo: data.consumo.valor })
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Error al procesar la factura. Intentá de nuevo.'
      trackEvent('bill_analysis_error', { error: detail })
    },
  })

  const handleFileSelected = (file: File) => {
    trackEvent('bill_uploaded', { filename: file.name, size: file.size })
    mutation.mutate(file)
  }

  const handleReset = () => {
    setAnalysis(null)
    setIsDemo(false)
    mutation.reset()
  }

  const handleDemo = () => {
    trackEvent('demo_analysis_viewed', {})
    setAnalysis(DEMO_ANALYSIS)
    setIsDemo(true)
  }

  const handleHistorySelect = (savedAnalysis: BillAnalysisResponse) => {
    setAnalysis(savedAnalysis)
    setIsDemo(false)
  }

  const errorMessage = mutation.error
    ? (mutation.error as any)?.response?.data?.detail || 'Error al procesar la factura. Intentá de nuevo.'
    : null

  return (
    <div className="min-h-[60vh]">
      <SEO
        title="Mi Factura UTE - Analizá tu consumo eléctrico"
        description="Subí tu factura de UTE en PDF y recibí un análisis personalizado con recomendaciones de ahorro. Gratis, sin registro, sin guardar datos personales."
        path="/mi-factura"
      />
      {/* Hero section - shown only before results */}
      {!analysis && (
        <div className="text-center mb-6 sm:mb-10">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-sm font-medium px-4 py-1.5 rounded-full mb-3 sm:mb-4">
            <FileText className="w-4 h-4" />
            Nuevo
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 mb-2 sm:mb-3">
            Analizá tu factura de UTE
          </h1>
          <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto px-2">
            Subí tu factura en PDF y recibí un análisis personalizado con recomendaciones
            de ahorro basadas en tu consumo real.
          </p>
        </div>
      )}

      {/* Upload or Results */}
      {analysis ? (
        <Suspense fallback={
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        }>
          {isDemo && (
            <div className="max-w-4xl mx-auto mb-4">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 sm:p-4 flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <div className="flex items-center gap-2 text-amber-800 text-sm font-medium">
                  <Eye className="w-4 h-4 flex-shrink-0" />
                  Esto es un ejemplo. Subí tu factura real para ver tu análisis personalizado.
                </div>
                <button
                  onClick={handleReset}
                  className="text-sm font-semibold text-blue-600 hover:text-blue-800 whitespace-nowrap min-h-[44px] flex items-center"
                >
                  Subir mi factura
                </button>
              </div>
            </div>
          )}
          <BillResults analysis={analysis} onReset={handleReset} />
        </Suspense>
      ) : (
        <>
          <BillUploader
            onFileSelected={handleFileSelected}
            isLoading={mutation.isPending}
            error={errorMessage}
          />
          {/* Demo link */}
          <div className="text-center mt-4 sm:mt-6">
            <button
              onClick={handleDemo}
              className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600 transition-colors min-h-[44px]"
            >
              <Eye className="w-4 h-4" />
              Ver un ejemplo de análisis
            </button>
          </div>
          {/* History from localStorage */}
          <HistorySection onSelect={handleHistorySelect} />
        </>
      )}
    </div>
  )
}
