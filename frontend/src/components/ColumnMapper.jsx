function ColumnMapper({ columns, mapping, onMappingChange, onNext, onBack }) {
  const handleChange = (field, value) => {
    onMappingChange({
      ...mapping,
      [field]: value
    })
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-semibold mb-4">Mapeamento de Colunas</h2>
      <p className="text-gray-600 mb-6">
        Selecione as colunas do seu arquivo CSV que correspondem a cada campo necessário.
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ID do Cliente *
          </label>
          <select
            value={mapping.id_cliente}
            onChange={(e) => handleChange('id_cliente', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Selecione uma coluna</option>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ID da Transação *
          </label>
          <select
            value={mapping.id_transacao}
            onChange={(e) => handleChange('id_transacao', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Selecione uma coluna</option>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data *
          </label>
          <select
            value={mapping.data}
            onChange={(e) => handleChange('data', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Selecione uma coluna</option>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Valor Monetário *
          </label>
          <select
            value={mapping.valor}
            onChange={(e) => handleChange('valor', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Selecione uma coluna</option>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
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
          onClick={onNext}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Continuar
        </button>
      </div>
    </div>
  )
}

export default ColumnMapper



