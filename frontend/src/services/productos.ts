import api from './api'
import type { Producto, Precio, Variacion, Estadisticas, Comparacion } from '../types/api'

export const productosService = {
  getAll: async (categoria?: string): Promise<Producto[]> => {
    const params = categoria ? { categoria } : {}
    const response = await api.get('/api/v1/productos', { params })
    return response.data
  },

  getById: async (id: number): Promise<Producto> => {
    const response = await api.get(`/api/v1/productos/${id}`)
    return response.data
  },

  getPrecioUltimo: async (productoId: number): Promise<Precio> => {
    const response = await api.get(`/api/v1/precios/${productoId}/ultimo`)
    return response.data
  },

  getVariacion: async (productoId: number, dias: number = 30): Promise<Variacion> => {
    const response = await api.get(`/api/v1/variacion/${productoId}`, {
      params: { periodo: dias >= 365 ? 'anio' : dias >= 30 ? 'mes' : 'semana' },
    })
    return response.data
  },
}

export const preciosService = {
  getByProducto: async (
    productoId: number,
    fechaDesde?: string,
    fechaHasta?: string,
    limit?: number
  ): Promise<Precio[]> => {
    const params = { fecha_desde: fechaDesde, fecha_hasta: fechaHasta, limit }
    const response = await api.get(`/api/v1/precios/${productoId}`, { params })
    return response.data
  },

  getUltimo: async (productoId: number): Promise<Precio> => {
    const response = await api.get(`/api/v1/precios/${productoId}/ultimo`)
    return response.data
  },
}

export const variacionService = {
  calcular: async (productoId: number, periodo: string = 'mes'): Promise<Variacion> => {
    const response = await api.get(`/api/v1/variacion/${productoId}`, {
      params: { periodo },
    })
    return response.data
  },
}

export const estadisticasService = {
  get: async (
    productoId: number,
    fechaDesde?: string,
    fechaHasta?: string
  ): Promise<Estadisticas> => {
    const params = { fecha_desde: fechaDesde, fecha_hasta: fechaHasta }
    const response = await api.get(`/api/v1/estadisticas/${productoId}`, { params })
    return response.data
  },
}

export const comparadorService = {
  comparar: async (
    productoIds: number[],
    fechaDesde?: string,
    fechaHasta?: string
  ): Promise<Comparacion> => {
    const params = {
      producto_ids: productoIds.join(','),
      fecha_desde: fechaDesde,
      fecha_hasta: fechaHasta,
    }
    const response = await api.get('/api/v1/comparar', { params })
    return response.data
  },
}
