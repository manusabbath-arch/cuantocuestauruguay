import { useState } from 'react'
import { AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react'
import { useGastoAnomalias } from '../hooks/useGasto'
import type { AnomaliaPresupuestal, AnomalíaSeveridad, AnomalíaTipo } from '../services/gasto'

interface Props {
  anio?: number
}

const SEVERIDAD_CONFIG: Record<AnomalíaSeveridad, {
  color: string
  bg: string
  border: string
  icon: typeof AlertTriangle
  label: string
}> = {
  CRITICA: {
    color: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: AlertTriangle,
    label: 'Crítica',
  },
  ALTA: {
    color: 'text-orange-700',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: AlertCircle,
    label: 'Alta',
  },
  MEDIA: {
    color: 'text-amber-700',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    icon: AlertCircle,
    label: 'Media',
  },
  BAJA: {
    color: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-100',
    icon: Info,
    label: 'Baja',
  },
}

const TIPO_LABEL: Record<AnomalíaTipo, string> = {
  ejecucion_baja: 'Ejecución baja',
  variacion_atipica: 'Variación atípica',
  dato_faltante: 'Dato faltante',
}

function SeveridadBadge({ severidad }: { severidad: AnomalíaSeveridad }) {
  const cfg = SEVERIDAD_CONFIG[severidad]
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${cfg.bg} ${cfg.color} ${cfg.border} border`}>
      {cfg.label}
    </span>
  )
}

function AnomaliaRow({ anomalia }: { anomalia: AnomaliaPresupuestal }) {
  const cfg = SEVERIDAD_CONFIG[anomalia.severidad]
  const Icon = cfg.icon
  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${cfg.bg} ${cfg.border}`}>
      <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${cfg.color}`} />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap mb-0.5">
          <span className="text-xs font-semibold text-gray-800 truncate">
            {anomalia.nombre_organismo}
          </span>
          <SeveridadBadge severidad={anomalia.severidad} />
          <span className="text-xs text-gray-400">{TIPO_LABEL[anomalia.tipo]}</span>
        </div>
        <p className="text-xs text-gray-600 leading-relaxed">{anomalia.descripcion}</p>
      </div>
    </div>
  )
}

export default function AnomaliasBanner({ anio }: Props) {
  const [expanded, setExpanded] = useState(false)
  const { data, isLoading } = useGastoAnomalias(anio ? { anio } : {})

  if (isLoading) return null
  if (!data || data.length === 0) return null

  const criticas = data.filter((a) => a.severidad === 'CRITICA')
  const altas = data.filter((a) => a.severidad === 'ALTA')
  const resto = data.filter((a) => a.severidad !== 'CRITICA' && a.severidad !== 'ALTA')

  // Mostrar siempre críticas + altas; el resto bajo toggle
  const visibles = expanded ? data : [...criticas, ...altas].slice(0, 5)
  const hayMas = data.length > visibles.length

  const resumenColor = criticas.length > 0
    ? 'text-red-700'
    : altas.length > 0
      ? 'text-orange-700'
      : 'text-amber-700'

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-4 h-4 ${resumenColor}`} />
          <span className="text-sm font-semibold text-gray-800">
            Señales detectadas
          </span>
          <span className={`text-xs font-medium ${resumenColor}`}>
            {data.length} señal{data.length !== 1 ? 'es' : ''}
            {criticas.length > 0 && ` · ${criticas.length} crítica${criticas.length !== 1 ? 's' : ''}`}
          </span>
        </div>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        >
          {expanded ? (
            <><ChevronUp className="w-3.5 h-3.5" /> Contraer</>
          ) : (
            <><ChevronDown className="w-3.5 h-3.5" /> Ver {expanded ? '' : `${data.length}`}</>
          )}
        </button>
      </div>

      {/* Filas */}
      <div className="p-3 space-y-2">
        {visibles.map((a) => (
          <AnomaliaRow key={a.id} anomalia={a} />
        ))}
        {hayMas && !expanded && (
          <button
            onClick={() => setExpanded(true)}
            className="w-full text-xs text-gray-400 hover:text-gray-600 py-1 transition-colors"
          >
            + {resto.length} señal{resto.length !== 1 ? 'es' : ''} de severidad media/baja
          </button>
        )}
      </div>

      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
        <p className="text-xs text-gray-400">
          Detección automática · datos MEF · actualización mensual
        </p>
      </div>
    </div>
  )
}
