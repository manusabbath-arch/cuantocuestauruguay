import { useEffect, useState } from 'react'

export type ViewMode = 'resumen' | 'explorar'

const STORAGE_KEY = 'ccu:view-mode'

export function usePersistentViewMode(defaultMode: ViewMode = 'resumen') {
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    if (typeof window === 'undefined') return defaultMode

    const stored = window.localStorage.getItem(STORAGE_KEY)
    return stored === 'resumen' || stored === 'explorar' ? stored : defaultMode
  })

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, viewMode)
  }, [viewMode])

  return { viewMode, setViewMode }
}