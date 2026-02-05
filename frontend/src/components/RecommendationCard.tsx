import { Lightbulb, ArrowRightLeft, TrendingDown, Info } from 'lucide-react'
import type { Recomendacion } from '../types/factura'

interface RecommendationCardProps {
  recomendacion: Recomendacion
}

const TIPO_CONFIG = {
  cambio_tarifa: {
    icon: ArrowRightLeft,
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    iconColor: 'text-amber-600',
    badgeColor: 'bg-amber-100 text-amber-700',
    badgeText: 'Cambio de tarifa',
  },
  reduccion_consumo: {
    icon: TrendingDown,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    iconColor: 'text-blue-600',
    badgeColor: 'bg-blue-100 text-blue-700',
    badgeText: 'Consumo',
  },
  informativo: {
    icon: Info,
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    iconColor: 'text-gray-600',
    badgeColor: 'bg-gray-100 text-gray-700',
    badgeText: 'Info',
  },
}

export default function RecommendationCard({ recomendacion }: RecommendationCardProps) {
  const config = TIPO_CONFIG[recomendacion.tipo] || TIPO_CONFIG.informativo
  const Icon = config.icon

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-lg p-4 sm:p-5`}>
      <div className="flex items-start gap-3 sm:gap-4">
        <div className={`flex-shrink-0 mt-0.5 ${config.iconColor}`}>
          <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h4 className="font-semibold text-gray-900 text-sm sm:text-base">{recomendacion.titulo}</h4>
            <span className={`text-xs px-2 py-0.5 rounded-full ${config.badgeColor}`}>
              {config.badgeText}
            </span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{recomendacion.descripcion}</p>
          {recomendacion.ahorro_estimado != null && recomendacion.ahorro_estimado > 0 && (
            <div className="mt-2 sm:mt-3 flex items-center gap-2 bg-green-100/50 rounded-md px-3 py-1.5">
              <Lightbulb className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span className="text-sm font-medium text-green-700">
                Ahorro estimado: ${recomendacion.ahorro_estimado.toLocaleString('es-UY')}/mes
                <span className="text-green-600 font-normal"> (${(recomendacion.ahorro_estimado * 12).toLocaleString('es-UY')}/año)</span>
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
