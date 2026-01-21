import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import type { Precio } from '../types/api'

interface PriceChartProps {
  data: Precio[]
  productName?: string
}

export default function PriceChart({ data, productName }: PriceChartProps) {
  // Sort data by date ascending
  const sortedData = [...data].sort((a, b) => 
    new Date(a.fecha).getTime() - new Date(b.fecha).getTime()
  )

  // Transform data for recharts
  const chartData = sortedData.map(item => ({
    fecha: format(parseISO(item.fecha), 'MMM yyyy', { locale: es }),
    fechaFull: item.fecha,
    precio: Number(item.valor),
  }))

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">
        {productName ? `Histórico de ${productName}` : 'Histórico de Precios'}
      </h3>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="fecha" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
            }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Precio']}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="precio" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
            name="Precio"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
