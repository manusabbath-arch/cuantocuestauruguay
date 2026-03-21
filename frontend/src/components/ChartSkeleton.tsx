import { Loader } from 'lucide-react'

interface ChartSkeletonProps {
  height?: number
}

export default function ChartSkeleton({ height = 400 }: ChartSkeletonProps) {
  return (
    <div
      className="bg-gradient-to-r from-gray-100 to-gray-50 rounded-lg animate-pulse flex items-center justify-center"
      style={{ height }}
    >
      <div className="flex flex-col items-center gap-3">
        <Loader className="w-8 h-8 text-gray-400 animate-spin" />
        <p className="text-gray-500">Cargando gráfico...</p>
      </div>
    </div>
  )
}
