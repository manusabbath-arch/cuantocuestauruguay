import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Comparador from './pages/Comparador'
import ProductoDetalle from './pages/ProductoDetalle'
import About from './pages/About'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/comparador" element={<Comparador />} />
        <Route path="/producto/:id" element={<ProductoDetalle />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Layout>
  )
}

export default App
