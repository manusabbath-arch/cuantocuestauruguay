import { useState } from 'react'
import { Mail, MessageSquare, User, Send, CheckCircle, AlertCircle } from 'lucide-react'
import { trackEvent } from '../lib/analytics'

export default function Contacto() {
  const [formState, setFormState] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    asunto: '',
    mensaje: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormState('submitting')
    trackEvent('email_submit_attempt', { location: 'contacto' })

    try {
      const response = await fetch('https://formspree.io/f/xaqoleyk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.nombre,
          email: formData.email,
          subject: formData.asunto,
          message: formData.mensaje,
        }),
      })

      if (response.ok) {
        setFormState('success')
        setFormData({ nombre: '', email: '', asunto: '', mensaje: '' })
        trackEvent('email_submit_success', { location: 'contacto' })
        // Reset success message after 5 seconds
        setTimeout(() => setFormState('idle'), 5000)
      } else {
        setFormState('error')
        trackEvent('email_submit_error', { location: 'contacto', status: response.status })
      }
    } catch (error) {
      setFormState('error')
      trackEvent('email_submit_error', { location: 'contacto', error: true })
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
          Contacto
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          ¿Tenés alguna pregunta, sugerencia o querés reportar un problema? Estamos acá para ayudarte
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Contact Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Envianos un mensaje</h2>
          
          {formState === 'success' && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-green-900">¡Mensaje enviado!</h3>
                <p className="text-green-700 text-sm">Te responderemos a la brevedad.</p>
              </div>
            </div>
          )}

          {formState === 'error' && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Error al enviar</h3>
                <p className="text-red-700 text-sm">Por favor, intentá nuevamente.</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nombre */}
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">
                Nombre completo
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="Tu nombre"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="tu@email.com"
                />
              </div>
            </div>

            {/* Asunto */}
            <div>
              <label htmlFor="asunto" className="block text-sm font-medium text-gray-700 mb-2">
                Asunto
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MessageSquare className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="asunto"
                  name="asunto"
                  value={formData.asunto}
                  onChange={handleChange}
                  required
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="¿De qué se trata tu mensaje?"
                />
              </div>
            </div>

            {/* Mensaje */}
            <div>
              <label htmlFor="mensaje" className="block text-sm font-medium text-gray-700 mb-2">
                Mensaje
              </label>
              <textarea
                id="mensaje"
                name="mensaje"
                value={formData.mensaje}
                onChange={handleChange}
                required
                rows={6}
                className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                placeholder="Contanos tu consulta, sugerencia o reporte..."
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={formState === 'submitting'}
              className="w-full bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {formState === 'submitting' ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Enviando...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Enviar mensaje
                </>
              )}
            </button>
          </form>
        </div>

        {/* Contact Info */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
            <h2 className="text-2xl font-bold mb-4">Información de Contacto</h2>
            <p className="mb-6 leading-relaxed">
              Estamos comprometidos con brindarte la mejor experiencia. Si tenés alguna consulta 
              o sugerencia, no dudes en contactarnos.
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Mail className="w-6 h-6 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-1">Email</h3>
                  <a 
                    href="mailto:contacto@cuantocuestauruguay.com" 
                    className="hover:underline opacity-90"
                  >
                    contacto@cuantocuestauruguay.com
                  </a>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <MessageSquare className="w-6 h-6 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-1">Tiempo de respuesta</h3>
                  <p className="opacity-90">24-48 horas hábiles</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Preguntas Frecuentes</h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">¿De dónde vienen los datos?</h4>
                <p className="text-gray-600 text-sm">
                  Todos los datos provienen de fuentes oficiales del gobierno uruguayo a través 
                  del Catálogo de Datos Abiertos.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">¿Con qué frecuencia se actualizan?</h4>
                <p className="text-gray-600 text-sm">
                  Los datos se actualizan diariamente de forma automática mediante procesos ETL.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">¿Es gratis usar la plataforma?</h4>
                <p className="text-gray-600 text-sm">
                  Sí, PreciosRegulados.uy es completamente gratuito y de código abierto.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-yellow-900 mb-2">¿Encontraste un error?</h3>
            <p className="text-yellow-800 text-sm mb-4">
              Si detectaste algún dato incorrecto o un problema técnico, reportalo usando el 
              formulario o directamente en nuestro repositorio de GitHub.
            </p>
            <a
              href="https://github.com/manusabbath-arch/cuantocuestauruguay/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-yellow-900 font-semibold hover:text-yellow-700 transition-colors"
            >
              Reportar en GitHub →
            </a>
          </div>
        </div>
      </div>

      {/* Additional Help Section */}
      <div className="mt-12 bg-gray-50 rounded-2xl p-8 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          ¿Querés colaborar con el proyecto?
        </h3>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Si sos desarrollador, diseñador o simplemente te interesa contribuir con ideas, 
          tu ayuda es más que bienvenida. Este es un proyecto de código abierto para toda 
          la comunidad uruguaya.
        </p>
        <a
          href="https://github.com/manusabbath-arch/cuantocuestauruguay/blob/main/CONTRIBUTING.md"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center bg-gray-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors"
        >
          Ver guía de contribución
        </a>
      </div>
    </div>
  )
}
