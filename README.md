# PreciosRegulados.uy 🇺🇾

[![CI/CD](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/ci.yml/badge.svg)](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/ci.yml)
[![Security Audit](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/security-audit.yml/badge.svg)](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/security-audit.yml)
[![Smoke Tests](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/smoke-prod.yml/badge.svg)](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/smoke-prod.yml)
[![codecov](https://codecov.io/gh/manusabbath-arch/cuantocuestauruguay/branch/main/graph/badge.svg)](https://codecov.io/gh/manusabbath-arch/cuantocuestauruguay)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Cloudflare](https://img.shields.io/badge/deployed-cloudflare-orange.svg)](https://cuantocuestauruguay.com)
[![Live Site](https://img.shields.io/badge/live-cuantocuestauruguay.com-brightgreen.svg)](https://cuantocuestauruguay.com)

> Plataforma web para consultar y comparar precios regulados en Uruguay (combustibles, servicios e índices económicos) con datos oficiales actualizados.

## 📋 Descripción

PreciosRegulados.uy es una aplicación web de código abierto que proporciona acceso fácil y visual a los precios regulados en Uruguay. Los datos provienen de fuentes oficiales del gobierno uruguayo a través del [Catálogo de Datos Abiertos](https://catalogodatos.gub.uy), URSEA, y otros organismos oficiales.

### Características principales

- 📊 **Dashboard interactivo** con precios actuales y tendencias
- 📈 **Gráficos históricos** de evolución de precios
- 🔄 **Comparador** para analizar múltiples productos
- 📱 **Diseño responsive** optimizado para móviles
- 🔄 **Actualización automática** diaria mediante ETL
- 🔓 **API REST pública** con documentación OpenAPI
- ⚡ **Servicios públicos** - UTE (electricidad), OSE (agua), Antel (telecomunicaciones)
- ⛽ **Combustibles** - ANCAP (nafta, gasoil, supergás)

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Usuarios      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Frontend │ (React + TypeScript)
    │(Cloudflare)│
    └────┬─────┘
         │ API REST
    ┌────▼─────┐
    │  FastAPI │ (Backend)
    │ (Render) │
    └─┬──┬──┬──┘
      │  │  │
      │  │  └──► PostgreSQL
      │  │
      │  └─────► Scheduler (ETL diario)
      │
      └────────► CKAN API (catalogodatos.gub.uy)
```

### Nueva Arquitectura de Backend (Monorepo)

El backend está evolucionando hacia una arquitectura de **paquetes compartidos** para soportar múltiples apps:

```
backend/
├── packages/              # 📦 Código compartido (nuevo)
│   ├── etl_core/         # Base común para ETL
│   ├── ckan_client/      # Cliente CKAN reutilizable
│   └── shared_models/    # Modelos compartidos
└── app/                   # App de Precios Regulados
    ├── api/              # Endpoints FastAPI
    ├── models/           # Modelos de DB
    └── etl/              # ETL jobs

# Próximamente:
# └── apps/
#     ├── precios/       # Precios Regulados
#     ├── transparencia/ # Datos Abiertos
#     └── gastos/        # Gastos Públicos
```

📖 Ver [INTEGRACION_BACKEND.md](docs/INTEGRACION_BACKEND.md) para más detalles.

### Stack Tecnológico

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- PostgreSQL (base de datos)
- SQLAlchemy (ORM)
- Alembic (migraciones)
- APScheduler (tareas programadas)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (gráficos)
- React Query (estado servidor)

**Infraestructura:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Railway.app / Render.com (backend hosting)
- Cloudflare Pages (frontend hosting)

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### Instalación con Docker

1. Clonar el repositorio:
```bash
git clone https://github.com/manusabbath-arch/cuantocuestauruguay.git
cd cuantocuestauruguay
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Levantar los servicios:
```bash
docker-compose up -d
```

4. Ejecutar migraciones de base de datos:
```bash
docker-compose exec backend alembic upgrade head
```

5. Cargar datos iniciales (ETL):
```bash
docker-compose exec backend python -c "from app.etl.combustibles import CombustiblesETL; from app.core.database import SessionLocal; import asyncio; db = SessionLocal(); etl = CombustiblesETL(db); asyncio.run(etl.run())"
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Desarrollo Local

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar base de datos PostgreSQL local
createdb preciosregulados

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

La API REST está documentada con OpenAPI/Swagger. Una vez ejecutando el backend, visita:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints principales

**Productos y Precios:**
- `GET /api/v1/productos` - Lista todos los productos
- `GET /api/v1/precios/{producto_id}` - Obtiene histórico de precios
- `GET /api/v1/variacion/{producto_id}` - Calcula variación porcentual
- `GET /api/v1/comparar` - Compara múltiples productos
- `GET /api/v1/estadisticas/{producto_id}` - Obtiene estadísticas

**ETL (Extracción de Datos):**
- `POST /api/v1/etl/run` - Ejecuta ETL de combustibles
- `POST /api/v1/etl/utilities/run?service={ute|ose|antel}` - Ejecuta ETL de servicios públicos
- `POST /api/v1/etl/run-all` - Ejecuta todos los ETL
- `GET /api/v1/etl/status` - Estado de los procesos ETL

## 🧪 Tests

**Backend:**
```bash
cd backend
pytest tests/ -v --cov=app
```

**Frontend:**
```bash
cd frontend
npm test
```

## 🦋 Pre-commit Hooks

Para garantizar calidad de código, instala los pre-commit hooks:

```bash
./scripts/install-hooks.sh
```

Esto ejecutará automáticamente antes de cada commit:
- **Backend**: black (formateo), isort (imports), flake8 (linting)
- **Frontend**: eslint (auto-fix), tsc (type checking)

**Saltar hooks** (no recomendado):
```bash
git commit --no-verify
```

## 📦 Deployment

### Backend (Render.com)

**Prerequisitos:**
- Cuenta en [render.com](https://render.com) (free tier)
- Este repositorio con `render.yaml` en la rama `main`

**Pasos:**

1. **Conectar repo a Render:**
   - Ve a [Dashboard de Render](https://dashboard.render.com)
   - Click en "+ New" → "Blueprint"
   - Selecciona tu repositorio GitHub `manusabbath-arch/cuantocuestauruguay`
   - Elige rama: `main`
   - Dale un nombre: `preciosregulados-api`

2. **Review y Deploy:**
   - Render leerá `render.yaml` automáticamente
   - Mostrará: 1 Web Service + 1 PostgreSQL Database (free)
   - Click "Deploy Blueprint"
   - Espera ~5 min a que termine el build

3. **Obtener URL del backend:**
   - Una vez deployed, irá a servicio → Environment
   - Copia la URL como: `https://preciosregulados-api.onrender.com` (o la que te asigne)

4. **Verificar estado:**
   - Backend API Docs: `https://preciosregulados-api.onrender.com/docs`
   - Debe mostrar endpoints de la API

**Nota:** Si el build falla, revisa los logs en "Logs" del servicio.

---

### Frontend (Cloudflare Pages)

**Prerequisitos:**
- Cuenta en [Cloudflare](https://dash.cloudflare.com) (free tier)
- Dominio `cuantocuestauruguay.com` ya apuntando a Cloudflare DNS

**Pasos:**

1. **Crear proyecto en Pages:**
   - Ve a [Cloudflare Dashboard](https://dash.cloudflare.com)
   - "Pages" → "+ Create a project"
   - "Connect to Git" → Selecciona tu repo
   - Elige rama: `main`

2. **Configurar build:**
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
   - Root directory: `/` (dejar vacío o `/`)
   - Click "Save and Deploy"

3. **Agregar variable de entorno:**
   - Proyecto → Settings → "Environment variables"
   - Click "+ Add variable"
   - Variable name: `VITE_API_URL`
   - Value: `https://preciosregulados-api.onrender.com`
   - Environments: Production
   - Click "Save"

4. **Trigger redeploy (para aplicar env var):**
   - Vuelve a "Deployments"
   - Click en el último deployment → "Rollback"
   - O espera al próximo push a `main`

5. **Conectar dominio personalizado:**
   - Proyecto → Custom domains → "+ Add custom domain"
   - Añade:
     - `cuantocuestauruguay.com`
     - `www.cuantocuestauruguay.com`
   - Cloudflare auto-configura SSL; espera propagación DNS (24-48h)

6. **Verificar acceso:**
   - `https://cuantocuestauruguay.com` debe mostrar tu app
   - API debe funcionar (verifica conexión en DevTools → Network)

---

### Configuración del Dominio (Cloudflare)

**Estado:**
- ✅ Dominio `cuantocuestauruguay.com` registrado
- ✅ DNS configurado en Cloudflare
- ⏳ Esperando propagación global (24-48h)

**Si aún no apunta correctamente:**
1. Dashboard Cloudflare → Domain → DNS
2. Verifica que Cloudflare nameservers están activos (consulta con registrador del dominio)

**Después de Pages + Render:**
1. Cloudflare añade records A/CNAME automáticamente
2. En Render, actualiza `CORS_ORIGINS`:
   ```
   https://cuantocuestauruguay.com,https://www.cuantocuestauruguay.com
   ```
3. Prueba: `curl https://preciosregulados-api.onrender.com/api/v1/productos`

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚖️ Licencia y Legal

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

### Fuentes de Datos

Los datos utilizados provienen del Catálogo de Datos Abiertos del Uruguay bajo la "Licencia de DAG de Uruguay", que permite uso comercial con atribución.

**Atribución requerida:** "Fuente: catalogodatos.gub.uy"

### Disclaimer

Los datos presentados provienen de fuentes oficiales (ANCAP, MEF, URSEA) y se actualizan periódicamente. PreciosRegulados.uy no se responsabiliza por decisiones tomadas en base a esta información. Para datos oficiales, consulte directamente las fuentes gubernamentales.

## 📞 Contacto

- GitHub Issues: [Reportar problema](https://github.com/manusabbath-arch/cuantocuestauruguay/issues)
- Email: [Contacto](mailto:contact@preciosregulados.uy)

## 🙏 Agradecimientos

- Gobierno de Uruguay por proporcionar datos abiertos
- Comunidad open source de Python y React
- Todos los contribuidores del proyecto

---

Hecho con ❤️ en Uruguay