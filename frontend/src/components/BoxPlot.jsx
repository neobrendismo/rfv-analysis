import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts'

export function Boxplot({ stats }) {
  // Prepara dados para visualização do box plot
  const data = [
    {
      name: 'Min',
      value: stats.min,
      type: 'min',
      color: '#ef4444'
    },
    {
      name: 'Q1',
      value: stats.q1,
      type: 'q1',
      color: '#3b82f6'
    },
    {
      name: 'Mediana',
      value: stats.median,
      type: 'median',
      color: '#10b981'
    },
    {
      name: 'Q3',
      value: stats.q3,
      type: 'q3',
      color: '#3b82f6'
    },
    {
      name: 'Max',
      value: stats.max,
      type: 'max',
      color: '#ef4444'
    }
  ]

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip 
            formatter={(value) => `R$ ${value.toFixed(2)}`}
          />
          <ReferenceLine y={stats.lower_bound} stroke="#f59e0b" strokeDasharray="3 3" label="Limite Inferior" />
          <ReferenceLine y={stats.upper_bound} stroke="#f59e0b" strokeDasharray="3 3" label="Limite Superior" />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600">
        <p><span className="font-semibold">IQR:</span> R$ {stats.iqr.toFixed(2)}</p>
        <p><span className="font-semibold">Limites:</span> R$ {stats.lower_bound.toFixed(2)} - R$ {stats.upper_bound.toFixed(2)}</p>
        <p><span className="font-semibold">Outliers detectados:</span> {stats.outliers_count} de {stats.total_count} registros</p>
      </div>
    </div>
  )
}

