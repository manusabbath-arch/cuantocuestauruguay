import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from './cn'

interface StatCardProps {
  label: string
  value: string
  subValue?: string
  trend?: { value: number; label: string }
  colorOverride?: string
  onClick?: () => void
  className?: string
}

export default function StatCard({
  label,
  value,
  subValue,
  trend,
  colorOverride,
  onClick,
  className,
}: StatCardProps) {
  const TrendIcon =
    trend && trend.value > 0
      ? TrendingUp
      : trend && trend.value < 0
        ? TrendingDown
        : Minus

  const trendColor =
    trend && trend.value > 0
      ? 'text-red-600'
      : trend && trend.value < 0
        ? 'text-green-600'
        : 'text-gray-500'

  return (
    <div
      className={cn(
        'bg-white rounded-xl border border-gray-200 p-5',
        onClick && 'cursor-pointer hover:border-blue-300 hover:shadow-sm transition-all',
        className
      )}
      onClick={onClick}
    >
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p
        className="text-2xl font-bold text-gray-900"
        style={colorOverride ? { color: colorOverride } : undefined}
      >
        {value}
      </p>
      {subValue && <p className="text-xs text-gray-400 mt-0.5">{subValue}</p>}
      {trend && (
        <div className={cn('flex items-center gap-1 mt-2 text-xs font-medium', trendColor)}>
          <TrendIcon className="w-3.5 h-3.5" />
          <span>
            {trend.value > 0 ? '+' : ''}
            {trend.value.toFixed(1)}% {trend.label}
          </span>
        </div>
      )}
    </div>
  )
}
