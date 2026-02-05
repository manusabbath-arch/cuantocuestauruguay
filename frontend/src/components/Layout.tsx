import { Link } from 'react-router-dom'
import { TrendingUp } from 'lucide-react'
import { trackEvent } from '../lib/analytics'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl text-primary">
              <TrendingUp className="w-6 h-6" />
              PreciosRegulados.uy
            </Link>
            
            <nav className="hidden md:flex items-center gap-6">
              <Link to="/" className="text-gray-600 hover:text-primary transition-colors" onClick={() => trackEvent('nav_click', { to: '/' })}>
                Inicio
              </Link>
              <Link to="/servicios" className="text-gray-600 hover:text-primary transition-colors" onClick={() => trackEvent('nav_click', { to: '/servicios' })}>
                Servicios
              </Link>
              <Link to="/mi-factura" className="text-blue-600 hover:text-blue-800 font-medium transition-colors" onClick={() => trackEvent('nav_click', { to: '/mi-factura' })}>
                Mi Factura
              </Link>
              <Link to="/comparador" className="text-gray-600 hover:text-primary transition-colors" onClick={() => trackEvent('nav_click', { to: '/comparador' })}>
                Comparador
              </Link>
              <Link to="/sobre-nosotros" className="text-gray-600 hover:text-primary transition-colors" onClick={() => trackEvent('nav_click', { to: '/sobre-nosotros' })}>
                Sobre Nosotros
              </Link>
              <Link to="/contacto" className="text-gray-600 hover:text-primary transition-colors" onClick={() => trackEvent('nav_click', { to: '/contacto' })}>
                Contacto
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold mb-2">PreciosRegulados.uy</h3>
              <p className="text-sm text-gray-600">
                Información actualizada sobre precios regulados en Uruguay
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Fuentes</h3>
              <p className="text-sm text-gray-600">
                Datos oficiales de ANCAP, MEF y URSEA vía{' '}
                <a 
                  href="https://catalogodatos.gub.uy" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  catalogodatos.gub.uy
                </a>
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Disclaimer</h3>
              <p className="text-sm text-gray-600">
                Los datos se actualizan periódicamente. Para información oficial, consulte las fuentes gubernamentales.
              </p>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            © {new Date().getFullYear()} PreciosRegulados.uy - Código abierto bajo licencia MIT
          </div>
        </div>
      </footer>
    </div>
  )
}
