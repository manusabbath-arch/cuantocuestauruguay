export interface ConsumoData {
  valor: number
  unidad: string
}

export interface CargosData {
  fijo: number
  variable: number
  total: number
}

export interface MetricasData {
  precio_unitario: number
  costo_diario: number
  dias_facturados: number
  consumo_diario_kwh: number
}

export interface TarifaOficial {
  valor: number
  fecha: string
  unidad: string
}

export interface Comparacion {
  tu_precio_kwh: number
  tarifas_oficiales: Record<string, TarifaOficial>
  tu_tarifa: string
}

export interface Recomendacion {
  tipo: 'cambio_tarifa' | 'reduccion_consumo' | 'informativo'
  titulo: string
  descripcion: string
  ahorro_estimado: number | null
}

export interface BillAnalysisResponse {
  servicio: string
  periodo: {
    desde: string
    hasta: string
  }
  consumo: ConsumoData
  cargos: CargosData
  metricas: MetricasData
  comparacion: Comparacion
  percentil_consumo: number
  recomendaciones: Recomendacion[]
  ahorro_potencial: number
}
