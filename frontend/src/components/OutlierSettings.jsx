import { useEffect, useState } from 'react'
import { Boxplot } from './BoxPlot'

function OutlierSettings({ stats, treatment, onTreatmentChange, onProcess, onBack }) {
  const [localTreatment, setLocalTreatment] = useState(treatment)

  useEffect(() => {
    if (stats) {
      setLocalTreatment({
        ...treatment,
        lower_limit: stats.lower_bound,
        upper_limit: stats.upper_bound
      })
    }
  }, [stats])

  const handleMethodChange = (method) => {
    setLocalTreatment({
      ...localTreatment,
      method
    })
    onTreatmentChange({
      ...localTreatment,
      method
    })
  }

  const handleLimitChange = (field, value) => {
    const newTreatment = {
      ...localTreatment,
      [field]: parseFloat(value) || null
    }
    setLocalTreatment(newTreatment)
    onTreatmentChange(newTreatment)
  }

  if (!stats) {
    return (
      <div className="w-full text-center py-8">
        <p className="text-gray-600">Carregando análise de outliers...</p>
      </div>
    )
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-semibold mb-4">Análise e Tratamento de Outliers</h2>
      <p className="text-gray-600 mb-6">
        Analise a distribuição dos valores monetários e escolha como tratar os outliers.
      </p>

      {/* Estatísticas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Q1</p>
          <p className="text-xl font-semibold">R$ {stats.q1.toFixed(2)}</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Mediana</p>
          <p className="text-xl font-semibold">R$ {stats.median.toFixed(2)}</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Q3</p>
          <p className="text-xl font-semibold">R$ {stats.q3.toFixed(2)}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Outliers</p>
          <p className="text-xl font-semibold">{stats.outliers_count}</p>
        </div>
      </div>

      {/* Box Plot */}
      <div className="mb-6 bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Box Plot - Distribuição de Valores</h3>
        <Boxplot stats={stats} />
      </div>

      {/* Opções de Tratamento */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-semibold">Método de Tratamento</h3>
        
        <div className="space-y-3">
          <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              name="treatment"
              value="keep"
              checked={localTreatment.method === 'keep'}
              onChange={(e) => handleMethodChange('keep')}
              className="mr-3"
            />
            <div>
              <p className="font-medium">Manter Outliers</p>
              <p className="text-sm text-gray-600">Não altera os dados, mantém todos os valores originais</p>
            </div>
          </label>

          <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              name="treatment"
              value="winsorize"
              checked={localTreatment.method === 'winsorize'}
              onChange={(e) => handleMethodChange('winsorize')}
              className="mr-3"
            />
            <div className="flex-1">
              <p className="font-medium">Winsorização</p>
              <p className="text-sm text-gray-600 mb-2">Limita os valores extremos aos limites especificados</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Limite Inferior</label>
                  <input
                    type="number"
                    value={localTreatment.lower_limit || ''}
                    onChange={(e) => handleLimitChange('lower_limit', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                    placeholder={stats.lower_bound.toFixed(2)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Limite Superior</label>
                  <input
                    type="number"
                    value={localTreatment.upper_limit || ''}
                    onChange={(e) => handleLimitChange('upper_limit', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                    placeholder={stats.upper_bound.toFixed(2)}
                  />
                </div>
              </div>
            </div>
          </label>

          <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
            <input
              type="radio"
              name="treatment"
              value="remove"
              checked={localTreatment.method === 'remove'}
              onChange={(e) => handleMethodChange('remove')}
              className="mr-3"
            />
            <div className="flex-1">
              <p className="font-medium">Remover Outliers</p>
              <p className="text-sm text-gray-600 mb-2">Remove registros que estão fora dos limites especificados</p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Limite Inferior</label>
                  <input
                    type="number"
                    value={localTreatment.lower_limit || ''}
                    onChange={(e) => handleLimitChange('lower_limit', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                    placeholder={stats.lower_bound.toFixed(2)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Limite Superior</label>
                  <input
                    type="number"
                    value={localTreatment.upper_limit || ''}
                    onChange={(e) => handleLimitChange('upper_limit', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                    placeholder={stats.upper_bound.toFixed(2)}
                  />
                </div>
              </div>
            </div>
          </label>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={onBack}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Voltar
        </button>
        <button
          onClick={onProcess}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Processar RFV
        </button>
      </div>
    </div>
  )
}

export default OutlierSettings



