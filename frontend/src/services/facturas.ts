import api from './api'
import type { BillAnalysisResponse } from '../types/factura'

export const facturasService = {
  analyze: async (file: File): Promise<BillAnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/api/v1/facturas/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000,
    })
    return response.data
  },
}
