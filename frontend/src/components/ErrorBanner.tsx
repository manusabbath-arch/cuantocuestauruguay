import { AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { cn } from './cn'

interface ErrorBannerProps {
  message: string
  variant?: 'error' | 'warning' | 'info'
}

const variantStyles = {
  error: {
    container: 'bg-red-50 border-red-200',
    icon: 'text-red-600',
    text: 'text-red-800',
    Icon: AlertCircle,
  },
  warning: {
    container: 'bg-amber-50 border-amber-200',
    icon: 'text-amber-600',
    text: 'text-amber-800',
    Icon: AlertTriangle,
  },
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon: 'text-blue-600',
    text: 'text-blue-800',
    Icon: Info,
  },
}

export default function ErrorBanner({ message, variant = 'error' }: ErrorBannerProps) {
  const styles = variantStyles[variant]
  const { Icon } = styles

  return (
    <div className={cn('border rounded-lg p-4 flex gap-3', styles.container)}>
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', styles.icon)} />
      <p className={cn('text-sm', styles.text)}>{message}</p>
    </div>
  )
}
