import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileText } from 'lucide-react'
import { facturasService } from '../services/facturas'
import { trackEvent } from '../lib/analytics'
import type { BillAnalysisResponse } from '../types/factura'
import BillUploader from '../components/BillUploader'
import BillResults from '../components/BillResults'

export default function MiFactura() {
  const [analysis, setAnalysis] = useState<BillAnalysisResponse | null>(null)

  const mutation = useMutation({
    mutationFn: (file: File) => facturasService.analyze(file),
    onSuccess: (data) => {
      setAnalysis(data)
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
    mutation.reset()
  }

  const errorMessage = mutation.error
    ? (mutation.error as any)?.response?.data?.detail || 'Error al procesar la factura. Intent\u00e1 de nuevo.'
    : null

  return (
    <div className="min-h-[60vh]">
      {/* Hero section - shown only before results */}
      {!analysis && (
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 text-sm font-medium px-4 py-1.5 rounded-full mb-4">
            <FileText className="w-4 h-4" />
            Nuevo
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
            Analizá tu factura de UTE
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Subí tu factura en PDF y recibí un análisis personalizado con recomendaciones
            de ahorro basadas en tu consumo real.
          </p>
        </div>
      )}

      {/* Upload or Results */}
      {analysis ? (
        <BillResults analysis={analysis} onReset={handleReset} />
      ) : (
        <BillUploader
          onFileSelected={handleFileSelected}
          isLoading={mutation.isPending}
          error={errorMessage}
        />
      )}
    </div>
  )
}
