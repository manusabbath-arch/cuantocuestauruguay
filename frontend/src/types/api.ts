// API Types
export interface Producto {
  id: number
  nombre: string
  categoria: string
  unidad: string
  activo: boolean
}

export interface Precio {
  id: number
  producto_id: number
  fecha: string
  valor: number
  fuente: string | null
  created_at?: string
}

export interface PrecioConProducto extends Precio {
  producto: Producto
}

export interface Variacion {
  producto_id: number
  nombre_producto: string
  precio_actual: number
  precio_anterior: number
  variacion_absoluta: number
  variacion_porcentual: number
  fecha_actual: string
  fecha_anterior: string
}

export interface Estadisticas {
  producto_id: number
  nombre_producto: string
  minimo: number
  maximo: number
  promedio: number
  cantidad_registros: number
  fecha_desde: string | null
  fecha_hasta: string | null
}

export interface ComparacionItem {
  fecha: string
  valores: Record<number, number>
}

export interface Comparacion {
  productos: Producto[]
  datos: ComparacionItem[]
}
