import { AlertCircle, ExternalLink } from 'lucide-react'

interface DataTrustPanelProps {
  fuenteLabel: string
  fuenteUrl: string
  metodologiaLabel: string
  metodologiaUrl: string
  ultimaActualizacion?: string
  nota?: string
  className?: string
}

export default function DataTrustPanel({
  fuenteLabel,
  fuenteUrl,
  metodologiaLabel,
  metodologiaUrl,
  ultimaActualizacion,
  nota,
  className = '',
}: DataTrustPanelProps) {
  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3 ${className}`.trim()}>
      <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
      <div className="text-sm text-blue-900 space-y-1">
        <p>
          <strong>Fuente:</strong>{' '}
          <a
            href={fuenteUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="underline inline-flex items-center gap-1"
          >
            {fuenteLabel} <ExternalLink className="w-3 h-3" />
          </a>
        </p>
        <p>
          <strong>Metodología:</strong>{' '}
          <a
            href={metodologiaUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="underline inline-flex items-center gap-1"
          >
            {metodologiaLabel} <ExternalLink className="w-3 h-3" />
          </a>
        </p>
        <p>
          <strong>Última actualización:</strong> {ultimaActualizacion ?? 'según último dato disponible'}
        </p>
        {nota && <p className="text-xs text-blue-800">{nota}</p>}
      </div>
    </div>
  )
}