import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { TrendingUp, Menu, X } from 'lucide-react'
import { trackEvent } from '../lib/analytics'

interface LayoutProps {
  children: React.ReactNode
}

const NAV_LINKS = [
  { to: '/', label: 'Inicio' },
  { to: '/servicios', label: 'Servicios' },
  { to: '/mi-factura', label: 'Mi Factura', highlight: true },
  { to: '/comparador', label: 'Comparador' },
  { to: '/sobre-nosotros', label: 'Sobre Nosotros' },
  { to: '/contacto', label: 'Contacto' },
]

export default function Layout({ children }: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  // Close mobile menu on navigation
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [mobileMenuOpen])

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

            {/* Desktop nav */}
            <nav className="hidden md:flex items-center gap-6">
              {NAV_LINKS.map(({ to, label, highlight }) => (
                <Link
                  key={to}
                  to={to}
                  className={
                    highlight
                      ? 'text-blue-600 hover:text-blue-800 font-medium transition-colors'
                      : 'text-gray-600 hover:text-primary transition-colors'
                  }
                  onClick={() => trackEvent('nav_click', { to })}
                >
                  {label}
                </Link>
              ))}
            </nav>

            {/* Mobile hamburger button */}
            <button
              className="md:hidden flex items-center justify-center w-11 h-11 -mr-2 rounded-lg hover:bg-gray-100 transition-colors"
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen)
                trackEvent('mobile_menu_toggle', { open: !mobileMenuOpen })
              }}
              aria-label={mobileMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu overlay */}
        {mobileMenuOpen && (
          <>
            <div
              className="fixed inset-0 bg-black/30 z-40 md:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            <nav className="fixed top-16 left-0 right-0 bg-white border-b border-gray-200 z-50 md:hidden shadow-lg">
              <div className="container mx-auto px-4 py-2">
                {NAV_LINKS.map(({ to, label, highlight }) => {
                  const isActive = location.pathname === to
                  return (
                    <Link
                      key={to}
                      to={to}
                      className={`
                        flex items-center min-h-[48px] px-3 rounded-lg text-base font-medium transition-colors
                        ${isActive
                          ? 'bg-blue-50 text-blue-700'
                          : highlight
                            ? 'text-blue-600 hover:bg-blue-50'
                            : 'text-gray-700 hover:bg-gray-100'
                        }
                      `}
                      onClick={() => trackEvent('nav_click', { to, source: 'mobile' })}
                    >
                      {label}
                    </Link>
                  )
                })}
              </div>
            </nav>
          </>
        )}
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12 sm:mt-16">
        <div className="container mx-auto px-4 py-6 sm:py-8">
          <div className="grid gap-6 sm:gap-8 md:grid-cols-3">
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

          <div className="mt-6 sm:mt-8 pt-6 sm:pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            © {new Date().getFullYear()} PreciosRegulados.uy - Código abierto bajo licencia MIT
          </div>
        </div>
      </footer>
    </div>
  )
}
