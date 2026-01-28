import { Routes, Route, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Servicios from './pages/Servicios'
import Comparador from './pages/Comparador'
import ProductoDetalle from './pages/ProductoDetalle'
import About from './pages/About'
import SobreNosotros from './pages/SobreNosotros'
import Contacto from './pages/Contacto'
import { useEffect } from 'react'
import { trackPageview } from './lib/analytics'
import PrecioNaftaHoy from './pages/PrecioNaftaHoy'

function App() {
  const location = useLocation()

  useEffect(() => {
    trackPageview(location.pathname + location.search)
  }, [location])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/servicios" element={<Servicios />} />
        <Route path="/comparador" element={<Comparador />} />
        <Route path="/producto/:id" element={<ProductoDetalle />} />
        <Route path="/about" element={<About />} />
        <Route path="/sobre-nosotros" element={<SobreNosotros />} />
        <Route path="/contacto" element={<Contacto />} />
        <Route path="/precio-nafta-hoy" element={<PrecioNaftaHoy />} />
      </Routes>
    </Layout>
  )
}

export default App
