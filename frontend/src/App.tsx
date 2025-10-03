import { useState } from 'react'
import FileUploader from './components/FileUploader'

function App() {
  const [dataFile, setDataFile] = useState<File | null>(null)
  const [templateFile, setTemplateFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleProcess = async () => {
    if (!dataFile || !templateFile) {
      setError('Please upload both files')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('data_file', dataFile)
      formData.append('template_file', templateFile)

      const response = await fetch('http://localhost:8000/fill-templates', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to process files')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'filled_documents.zip'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsProcessing(false)
    }
  }

  const canProcess = dataFile && templateFile && !isProcessing

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Template Filler</h1>
          <p className="text-gray-600">Upload your data and template to generate filled documents</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <FileUploader
            label="Data File"
            description="Excel or CSV"
            accept=".xlsx,.xls,.csv"
            file={dataFile}
            onFileSelect={setDataFile}
            disabled={isProcessing}
          />
          <FileUploader
            label="Template File"
            description="Word Document"
            accept=".docx"
            file={templateFile}
            onFileSelect={setTemplateFile}
            disabled={isProcessing}
          />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <button
          onClick={handleProcess}
          disabled={!canProcess}
          className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all ${
            canProcess
              ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isProcessing ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Generate Documents'
          )}
        </button>
      </div>
    </div>
  )
}

export default App
