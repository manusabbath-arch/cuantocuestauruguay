import { Database, TrendingUp, Shield, Code } from 'lucide-react'

export default function About() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Acerca de PreciosRegulados.uy
        </h1>
        <p className="text-xl text-gray-600">
          Información transparente sobre precios regulados en Uruguay
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-semibold mb-4">Nuestra Misión</h2>
        <p className="text-gray-600 mb-4">
          PreciosRegulados.uy es una plataforma de acceso público que proporciona información
          actualizada sobre precios de combustibles y servicios regulados en Uruguay. Nuestro
          objetivo es hacer que estos datos sean accesibles de manera clara y visual para todos
          los uruguayos.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Database className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Fuentes de Datos</h3>
          </div>
          <p className="text-gray-600">
            Los datos provienen de fuentes oficiales del gobierno uruguayo a través del
            Catálogo de Datos Abiertos (catalogodatos.gub.uy), incluyendo información de
            ANCAP, MEF y URSEA.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Actualización</h3>
          </div>
          <p className="text-gray-600">
            Los datos se actualizan automáticamente de forma diaria mediante procesos ETL
            que extraen, transforman y cargan la información desde las APIs oficiales.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Code className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Código Abierto</h3>
          </div>
          <p className="text-gray-600">
            Este proyecto es de código abierto y está disponible en GitHub. Cualquier persona
            puede revisar el código, reportar problemas o contribuir con mejoras.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold">Transparencia</h3>
          </div>
          <p className="text-gray-600">
            Operamos con total transparencia, mostrando claramente nuestras fuentes y
            metodología. No almacenamos datos personales ni utilizamos cookies de tracking.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-semibold mb-4">Tecnología</h2>
        <div className="space-y-4 text-gray-600">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Backend:</h3>
            <p>Python 3.11+ con FastAPI, PostgreSQL, SQLAlchemy, Alembic y APScheduler</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Frontend:</h3>
            <p>React 18 + TypeScript, Tailwind CSS, Recharts y React Query</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Infraestructura:</h3>
            <p>Docker, GitHub Actions, Railway.app y Cloudflare Pages</p>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Disclaimer Legal</h2>
        <p className="text-sm text-gray-700 mb-4">
          Los datos presentados provienen de fuentes oficiales (ANCAP, MEF, URSEA) y se
          actualizan periódicamente. PreciosRegulados.uy no se responsabiliza por decisiones
          tomadas en base a esta información.
        </p>
        <p className="text-sm text-gray-700">
          Para datos oficiales y actualizaciones en tiempo real, consulte directamente las
          fuentes gubernamentales.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h2 className="text-xl font-semibold mb-4">¿Preguntas o Sugerencias?</h2>
        <p className="text-gray-600 mb-4">
          Este proyecto es mantenido por la comunidad. Si tienes preguntas, encuentras algún
          error o tienes sugerencias de mejora, puedes abrir un issue en GitHub.
        </p>
        <a
          href="https://github.com/manusabbath-arch/cuantocuestauruguay"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors font-medium"
        >
          Ver en GitHub
        </a>
      </div>
    </div>
  )
}
