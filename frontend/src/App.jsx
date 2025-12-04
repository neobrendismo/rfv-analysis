import { useState } from 'react'
import UploadArea from './components/UploadArea'
import ColumnMapper from './components/ColumnMapper'
import OutlierSettings from './components/OutlierSettings'
import Dashboard from './components/Dashboard'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function App() {
  const [step, setStep] = useState(1) // 1: Upload, 2: Mapeamento, 3: Outliers, 4: Dashboard
  const [fileId, setFileId] = useState(null)
  const [columns, setColumns] = useState([])
  const [columnMapping, setColumnMapping] = useState({
    id_cliente: '',
    id_transacao: '',
    data: '',
    valor: ''
  })
  const [outlierStats, setOutlierStats] = useState(null)
  const [outlierTreatment, setOutlierTreatment] = useState({
    method: 'keep',
    lower_limit: null,
    upper_limit: null
  })
  const [rfvResults, setRfvResults] = useState(null)

  const handleFileUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await axios.post(`${API_URL}/upload`, formData)
      setFileId(response.data.file_id)
      setColumns(response.data.columns)
      setStep(2)
    } catch (error) {
      console.error('Erro ao fazer upload:', error)
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        alert('Erro: Backend não está rodando!\n\nPor favor:\n1. Abra um terminal\n2. Execute: cd backend && python main.py\n3. Aguarde ver "Uvicorn running"\n4. Tente novamente')
      } else {
        alert(`Erro ao fazer upload do arquivo: ${error.response?.data?.detail || error.message}`)
      }
    }
  }

  const handleColumnMapping = () => {
    if (!columnMapping.id_cliente || !columnMapping.id_transacao || 
        !columnMapping.data || !columnMapping.valor) {
      alert('Por favor, mapeie todas as colunas necessárias')
      return
    }
    setStep(3)
    analyzeOutliers()
  }

  const analyzeOutliers = async () => {
    try {
      const response = await axios.post(`${API_URL}/analyze-outliers`, {
        column_mapping: {
          ...columnMapping,
          file_id: fileId
        },
        outlier_treatment: outlierTreatment
      })
      setOutlierStats(response.data.statistics)
    } catch (error) {
      console.error('Erro ao analisar outliers:', error)
      alert('Erro ao analisar outliers')
    }
  }

  const handleOutlierTreatment = async () => {
    await analyzeOutliers()
  }

  const handleProcessRFV = async () => {
    try {
      const response = await axios.post(`${API_URL}/process-rfv`, {
        column_mapping: {
          ...columnMapping,
          file_id: fileId
        },
        outlier_treatment: outlierTreatment
      })
      setRfvResults(response.data)
      setStep(4)
    } catch (error) {
      console.error('Erro ao processar RFV:', error)
      alert('Erro ao processar RFV: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDownload = () => {
    if (rfvResults?.file_id) {
      window.open(`${API_URL}/download/${rfvResults.file_id}`, '_blank')
    }
  }

  const handleDownloadPDF = async () => {
    if (rfvResults?.file_id) {
      try {
        const response = await axios.get(`${API_URL}/generate-pdf/${rfvResults.file_id}`, {
          responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `relatorio_rfv_${new Date().toISOString().split('T')[0]}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Erro ao baixar PDF:', error)
        alert('Erro ao gerar PDF')
      }
    }
  }

  const resetApp = () => {
    setStep(1)
    setFileId(null)
    setColumns([])
    setColumnMapping({
      id_cliente: '',
      id_transacao: '',
      data: '',
      valor: ''
    })
    setOutlierStats(null)
    setOutlierTreatment({
      method: 'keep',
      lower_limit: null,
      upper_limit: null
    })
    setRfvResults(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Análise RFV</h1>
          <p className="text-gray-600">Análise de Recência, Frequência e Valor Monetário</p>
        </header>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4].map((s) => (
              <div key={s} className="flex items-center flex-1">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  step >= s ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  {s}
                </div>
                {s < 4 && (
                  <div className={`flex-1 h-1 mx-2 ${
                    step > s ? 'bg-blue-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-600">
            <span>Upload</span>
            <span>Mapeamento</span>
            <span>Outliers</span>
            <span>Dashboard</span>
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {step === 1 && (
            <UploadArea onFileUpload={handleFileUpload} />
          )}
          
          {step === 2 && (
            <ColumnMapper
              columns={columns}
              mapping={columnMapping}
              onMappingChange={setColumnMapping}
              onNext={handleColumnMapping}
              onBack={() => setStep(1)}
            />
          )}
          
          {step === 3 && (
            <OutlierSettings
              stats={outlierStats}
              treatment={outlierTreatment}
              onTreatmentChange={setOutlierTreatment}
              onProcess={handleProcessRFV}
              onBack={() => setStep(2)}
            />
          )}
          
          {step === 4 && (
            <Dashboard
              results={rfvResults}
              onDownload={handleDownload}
              onDownloadPDF={handleDownloadPDF}
              onReset={resetApp}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default App

