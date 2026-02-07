import { Users, Target, Heart, Code2, Globe, Zap } from 'lucide-react'
import SEO from '../components/SEO'

export default function SobreNosotros() {
  return (
    <div className="max-w-6xl mx-auto space-y-12">
      <SEO
        title="Sobre Nosotros"
        description="PreciosRegulados.uy es un proyecto open source que brinda acceso transparente a precios regulados en Uruguay con datos oficiales del gobierno."
        path="/sobre-nosotros"
      />
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
          Sobre Nosotros
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Somos un equipo comprometido con la transparencia y el acceso libre a la información 
          de precios regulados en Uruguay
        </p>
      </div>

      {/* Mission & Vision */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-600 p-3 rounded-lg">
              <Target className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Nuestra Misión</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            Democratizar el acceso a información sobre precios regulados en Uruguay, 
            proporcionando datos actualizados, precisos y fáciles de entender para 
            todos los uruguayos. Creemos que la información transparente empodera a 
            las personas para tomar mejores decisiones.
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-8 shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-purple-600 p-3 rounded-lg">
              <Heart className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Nuestra Visión</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">
            Convertirnos en la plataforma de referencia para consultar precios regulados 
            en Uruguay, expandiendo nuestros servicios para incluir más categorías y 
            herramientas de análisis que beneficien a toda la comunidad uruguaya.
          </p>
        </div>
      </div>

      {/* Values */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Nuestros Valores
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow">
            <div className="bg-blue-100 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Globe className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Transparencia</h3>
            <p className="text-gray-600">
              Operamos con total apertura, mostrando claramente nuestras fuentes de datos 
              y metodología de actualización.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow">
            <div className="bg-green-100 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Code2 className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Código Abierto</h3>
            <p className="text-gray-600">
              Todo nuestro código está disponible en GitHub para que cualquiera pueda 
              revisarlo, auditarlo y contribuir.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow">
            <div className="bg-purple-100 w-14 h-14 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-gray-900">Innovación</h3>
            <p className="text-gray-600">
              Utilizamos las últimas tecnologías para ofrecer una experiencia rápida, 
              confiable y accesible desde cualquier dispositivo.
            </p>
          </div>
        </div>
      </div>

      {/* Team Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-10 text-white shadow-2xl">
        <div className="flex items-center gap-4 mb-6">
          <Users className="w-12 h-12" />
          <h2 className="text-3xl font-bold">Nuestro Equipo</h2>
        </div>
        <p className="text-lg leading-relaxed mb-6">
          Somos desarrolladores, diseñadores y entusiastas de los datos abiertos que trabajamos 
          para hacer la información pública más accesible. Este proyecto nació de la necesidad 
          de tener un lugar centralizado donde consultar precios regulados de forma clara y 
          actualizada.
        </p>
        <p className="text-lg leading-relaxed">
          Si compartís nuestra visión y querés contribuir al proyecto, ¡tu ayuda es bienvenida! 
          Podés encontrarnos en GitHub o contactarnos a través de nuestro formulario.
        </p>
      </div>

      {/* Tech Stack */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Tecnologías que Usamos
        </h2>
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-lg mb-3 text-gray-900">Frontend</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                  React 18 + TypeScript
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                  Vite (Build tool ultrarrápido)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                  TailwindCSS (Diseño responsive)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                  React Query (Gestión de datos)
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-3 text-gray-900">Backend</h3>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                  FastAPI (Python 3.11+)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                  PostgreSQL (Base de datos)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                  SQLAlchemy (ORM)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                  Procesos ETL automatizados
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
          <div className="text-gray-600 text-sm">Código Abierto</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">Diario</div>
          <div className="text-gray-600 text-sm">Actualización</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">API</div>
          <div className="text-gray-600 text-sm">REST Pública</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-orange-600 mb-2">0</div>
          <div className="text-gray-600 text-sm">Tracking</div>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-gray-50 rounded-2xl p-8 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          ¿Querés formar parte del proyecto?
        </h3>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Estamos siempre buscando colaboradores que quieran contribuir con código, 
          diseño, ideas o reportando problemas. ¡Toda ayuda es bienvenida!
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://github.com/manusabbath-arch/cuantocuestauruguay"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gray-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors"
          >
            Ver en GitHub
          </a>
          <a
            href="/contacto"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Contactanos
          </a>
        </div>
      </div>
    </div>
  )
}
