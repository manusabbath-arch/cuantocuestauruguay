import { useState, useCallback, useRef } from 'react'
import { Upload, FileText, AlertCircle, Shield } from 'lucide-react'

interface BillUploaderProps {
  onFileSelected: (file: File) => void
  isLoading: boolean
  error: string | null
}

const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

export default function BillUploader({ onFileSelected, isLoading, error }: BillUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateAndSubmit = useCallback((file: File) => {
    setValidationError(null)

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setValidationError('Solo se aceptan archivos PDF')
      return
    }

    if (file.size > MAX_SIZE_BYTES) {
      setValidationError(`El archivo es demasiado grande (max ${MAX_SIZE_MB}MB)`)
      return
    }

    if (file.size === 0) {
      setValidationError('El archivo está vacío')
      return
    }

    onFileSelected(file)
  }, [onFileSelected])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) validateAndSubmit(file)
  }, [validateAndSubmit])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) validateAndSubmit(file)
  }, [validateAndSubmit])

  const displayError = validationError || error

  return (
    <div className="max-w-2xl mx-auto">
      {/* Upload zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-xl p-6 sm:p-12 text-center cursor-pointer transition-all
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
          ${isLoading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="hidden"
        />

        {isLoading ? (
          <div className="flex flex-col items-center gap-3 sm:gap-4">
            <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 font-medium">Analizando tu factura...</p>
            <p className="text-sm text-gray-400">Esto toma solo unos segundos</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 sm:gap-4">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-blue-100 rounded-full flex items-center justify-center">
              {isDragging ? (
                <FileText className="w-7 h-7 sm:w-8 sm:h-8 text-blue-600" />
              ) : (
                <Upload className="w-7 h-7 sm:w-8 sm:h-8 text-blue-600" />
              )}
            </div>
            <div>
              {/* Mobile: "Tocá para seleccionar", Desktop: "Arrastrá" */}
              <p className="text-base sm:text-lg font-semibold text-gray-700">
                <span className="sm:hidden">
                  {isDragging ? 'Soltá tu factura aquí' : 'Tocá para seleccionar tu factura'}
                </span>
                <span className="hidden sm:inline">
                  {isDragging ? 'Soltá tu factura aquí' : 'Arrastrá tu factura PDF aquí'}
                </span>
              </p>
              <p className="text-sm text-gray-500 mt-1 hidden sm:block">
                o <span className="text-blue-600 underline">seleccioná un archivo</span> de tu dispositivo
              </p>
            </div>
            <p className="text-xs text-gray-400">PDF de factura de UTE (max {MAX_SIZE_MB}MB)</p>
          </div>
        )}
      </div>

      {/* Error display */}
      {displayError && (
        <div className="mt-4 flex items-start gap-3 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{displayError}</p>
        </div>
      )}

      {/* Privacy notice */}
      <div className="mt-4 sm:mt-6 flex items-start gap-3 p-3 sm:p-4 bg-green-50 border border-green-200 rounded-lg">
        <Shield className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-green-800">
          <p className="font-medium">Tu privacidad es prioridad</p>
          <p className="mt-1 text-green-700">
            Tu factura se procesa en el momento y no se guarda en nuestros servidores.
            Solo extraemos datos de consumo y cargos.
          </p>
        </div>
      </div>
    </div>
  )
}
