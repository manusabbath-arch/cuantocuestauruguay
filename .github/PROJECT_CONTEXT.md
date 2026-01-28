# Contexto del Proyecto - PreciosRegulados.uy

Este archivo proporciona contexto adicional para asistentes de IA sobre el proyecto.

## 🎯 Objetivo del Proyecto
Plataforma web para consultar y comparar precios regulados en Uruguay (combustibles, servicios públicos e índices económicos) con datos oficiales actualizados.

## 🏗️ Arquitectura

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Estilos**: TailwindCSS
- **Routing**: React Router v6
- **State Management**: React Query (TanStack Query)
- **Icons**: Lucide React
- **Deploy**: Cloudflare Pages

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy
- **Base de Datos**: PostgreSQL (producción), SQLite (desarrollo)
- **Validación**: Pydantic
- **Deploy**: Render.com

### ETL (Extract, Transform, Load)
- **Scheduler**: APScheduler
- **Fuentes de Datos**:
  - ANCAP (combustibles)
  - UTE (electricidad)
  - OSE (agua)
  - Antel (telecomunicaciones)
  - Catálogo de Datos Abiertos (catalogodatos.gub.uy)

## 📂 Estructura de Directorios

```
cuantocuestauruguay/
├── frontend/                 # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   ├── pages/           # Páginas principales
│   │   │   ├── Home.tsx
│   │   │   ├── Servicios.tsx
│   │   │   ├── Comparador.tsx
│   │   │   ├── ProductoDetalle.tsx
│   │   │   ├── About.tsx
│   │   │   ├── SobreNosotros.tsx
│   │   │   └── Contacto.tsx
│   │   ├── services/        # API clients
│   │   └── types/           # TypeScript types
│   ├── public/              # Assets estáticos
│   └── index.html           # Entry point (con Google Analytics)
│
├── backend/                  # FastAPI + Python
│   ├── app/
│   │   ├── api/             # Endpoints REST
│   │   ├── core/            # Config, database, feature flags
│   │   ├── etl/             # ETL processes
│   │   │   ├── combustibles_v2.py
│   │   │   ├── ute_v2.py
│   │   │   ├── ose_v2.py
│   │   │   ├── antel_v2.py
│   │   │   └── utilities.py
│   │   ├── models/          # SQLAlchemy models
│   │   └── schemas/         # Pydantic schemas
│   └── tests/               # Unit & integration tests
│
├── scripts/                  # Utilidades y mantenimiento
│   ├── init_db.py
│   ├── load_historical.py
│   ├── check_db.py
│   └── arch002_*.py         # Scripts de monitoreo ARCH-002
│
└── docs/                     # Documentación adicional
```

## 🔧 Convenciones de Código

### Frontend (TypeScript)
- **Componentes**: PascalCase (ej: `ProductoCard.tsx`)
- **Hooks**: camelCase con prefijo `use` (ej: `useProductos`)
- **Estilos**: TailwindCSS utility classes
- **Exports**: Named exports para componentes
- **Props**: Interfaces con sufijo `Props` (ej: `LayoutProps`)

### Backend (Python)
- **Files**: snake_case (ej: `combustibles_v2.py`)
- **Classes**: PascalCase (ej: `CombustiblesETLv2`)
- **Functions**: snake_case (ej: `get_productos`)
- **Constants**: UPPER_SNAKE_CASE (ej: `DATABASE_URL`)
- **Formateo**: Black (line length 100)
- **Linting**: Flake8 + pylint
- **Type hints**: Obligatorios en funciones públicas

### Git Commits
Formato: `<type>: <description>`

**Types**:
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Documentación
- `style`: Formato (sin cambios de código)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

**Ejemplos**:
```bash
git commit -m "feat: agregar página de contacto con Formspree"
git commit -m "fix: corregir parsing de CSV en combustibles ETL"
git commit -m "docs: actualizar README con nuevas páginas"
```

## 🌐 APIs y Endpoints

### Backend API (http://localhost:8000)
- `GET /api/v1/productos` - Listar todos los productos
- `GET /api/v1/productos?categoria=electricidad` - Filtrar por categoría
- `GET /api/v1/precios/{id}/ultimo` - Último precio de un producto
- `GET /api/v1/precios/{id}/variacion?dias=30` - Variación de precio
- `GET /docs` - Documentación OpenAPI (Swagger)

### Frontend Dev Server (http://localhost:5173)
- `/` - Home
- `/servicios` - UTE, OSE, Antel
- `/comparador` - Comparar productos
- `/producto/:id` - Detalle de producto
- `/sobre-nosotros` - Sobre Nosotros
- `/contacto` - Formulario de contacto

## 🔐 Variables de Entorno

### Backend (`backend/.env`)
```env
DATABASE_URL=sqlite:///./preciosregulados.db  # o PostgreSQL en producción
DEBUG=True
PROJECT_NAME=PreciosRegulados.uy
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (`frontend/.env.local`)
```env
VITE_API_URL=http://localhost:8000
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX  # Google Analytics
```

## 📊 Feature Flags (ARCH-002)

Sistema de rollout gradual implementado para ETL v2:
- **DISABLED**: Funcionalidad desactivada
- **SHADOW**: Ejecuta v1 y v2, retorna v1, loggea v2
- **CANARY**: 10% tráfico a v2
- **GRADUAL**: 25-50% tráfico a v2
- **FULL**: 100% tráfico a v2

**Estado actual**: CANARY 10% para combustibles, UTE, OSE, Antel

## 🧪 Testing

### Backend
```bash
cd backend
pytest                    # Todos los tests
pytest -v                 # Verbose
pytest tests/test_api.py  # Tests específicos
pytest --cov              # Con coverage
```

### Frontend
```bash
cd frontend
npm test                  # Run tests
npm run test:coverage     # Con coverage
```

## 📦 Dependencias Principales

### Frontend
```json
{
  "react": "^18.x",
  "react-router-dom": "^6.x",
  "@tanstack/react-query": "^5.x",
  "lucide-react": "^0.x",
  "tailwindcss": "^3.x"
}
```

### Backend
```python
fastapi==0.104.1
sqlalchemy==2.0.23
pydantic==2.5.0
uvicorn[standard]==0.24.0
pytest==7.4.3
```

## 🚀 Comandos Útiles

### Desarrollo Local
```bash
# Backend
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev -- --host --port 5173

# Base de datos
python scripts/init_db.py
python scripts/load_historical.py
python scripts/check_db.py
```

### Producción
```bash
# Build frontend
cd frontend
npm run build

# Deploy backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🎨 Design System

### Colores (TailwindCSS)
- **Primary**: Blue-600 (`#2563eb`)
- **Secondary**: Purple-600 (`#9333ea`)
- **Success**: Green-600 (`#16a34a`)
- **Error**: Red-600 (`#dc2626`)
- **Warning**: Yellow-600 (`#ca8a04`)

### Tipografía
- **Font Family**: System font stack (Inter, sans-serif)
- **Tamaños**: text-sm, text-base, text-lg, text-xl, text-2xl, text-3xl, text-4xl, text-5xl

### Espaciado
- **Gap**: 2, 4, 6, 8, 12, 16 (en múltiplos de 4px)
- **Padding**: p-4, p-6, p-8
- **Margin**: m-4, m-6, m-8

## 📧 Integraciones Externas

### Formspree (Formulario de Contacto)
- **Endpoint**: https://formspree.io/f/xaqoleyk
- **Plan**: Free (50 mensajes/mes)
- **Dashboard**: https://formspree.io/forms/xaqoleyk

### Google Analytics
- **ID**: G-XXXXXXXXXX (reemplazar con ID real)
- **Script**: Integrado en `frontend/index.html`
- **Dashboard**: https://analytics.google.com/

## 🔗 Links Importantes

- **Repositorio**: https://github.com/manusabbath-arch/cuantocuestauruguay
- **Sitio Web**: https://cuantocuestauruguay.com
- **Catálogo de Datos**: https://catalogodatos.gub.uy
- **API Docs (local)**: http://localhost:8000/docs

## 📝 Roadmap

### Completado ✅
- [x] ARCH-002: Migración ETL con feature flags
- [x] FUNC-001: ETL Servicios Públicos (UTE, OSE, Antel)
- [x] Página de Contacto con Formspree
- [x] Página Sobre Nosotros
- [x] Google Analytics integrado

### En Progreso 🚧
- [ ] ARCH-002 FASE 1: Monitoreo canary 10% (7 días)
- [ ] Testing end-to-end completo

### Próximos ⏭️
- [ ] FUNC-002: Sistema de alertas (email con Resend)
- [ ] PERF-001: Optimizaciones frontend (code splitting, PWA)
- [ ] Gráficos históricos con Chart.js
- [ ] API pública documentada

## 💡 Patrones de Uso Comunes

### Crear una nueva página
1. Crear componente en `frontend/src/pages/MiPagina.tsx`
2. Agregar ruta en `frontend/src/App.tsx`
3. Agregar link en `frontend/src/components/Layout.tsx`

### Agregar un nuevo endpoint
1. Crear función en `backend/app/api/v1/endpoints/mi_endpoint.py`
2. Agregar schema en `backend/app/schemas/mi_schema.py`
3. Registrar router en `backend/app/api/v1/api.py`

### Crear un nuevo ETL
1. Crear clase en `backend/app/etl/mi_etl_v2.py` heredando de `ETLBase`
2. Implementar métodos: `extract()`, `transform()`, `load()`
3. Agregar PRODUCTOS_MAP y TARIFF_HISTORY
4. Registrar en scheduler

## 🐛 Debugging Tips

### Frontend
```bash
# Ver logs en navegador
# Abrir DevTools > Console

# React Query DevTools
# Ya integrado, ver panel en desarrollo
```

### Backend
```bash
# Logs detallados
uvicorn app.main:app --log-level debug

# Ver queries SQL
# En database.py, agregar: echo=True a create_engine()

# Verificar base de datos
python scripts/check_db.py
```

## 🤝 Contribución

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía completa de contribución.

### Quick Start para Contribuir
1. Fork el repositorio
2. Crear rama: `git checkout -b feature/mi-feature`
3. Hacer cambios y commits: `git commit -m "feat: mi nueva funcionalidad"`
4. Push: `git push origin feature/mi-feature`
5. Crear Pull Request en GitHub

---

**Última actualización**: 27 de enero de 2026
**Versión**: 1.1.0
**Estado**: En desarrollo activo
