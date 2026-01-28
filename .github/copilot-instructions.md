# Copilot Instructions for PreciosRegulados.uy (CuantoCuestaUruguay)

## Overview
PreciosRegulados.uy es una plataforma web para consultar y comparar precios regulados en Uruguay (combustibles, servicios públicos e índices económicos) con datos oficiales actualizados del Catálogo de Datos Abiertos (catalogodatos.gub.uy).

**⚠️ IMPORTANTE**: Para contexto completo y actualizado del proyecto, consultar [PROJECT_CONTEXT.md](.github/PROJECT_CONTEXT.md).

## Arquitectura

### Stack Tecnológico
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: FastAPI (Python 3.11+) + SQLAlchemy + PostgreSQL/SQLite
- **ETL**: APScheduler para procesos de extracción de datos
- **Deploy**: Cloudflare Pages (frontend) + Render.com (backend)

### Estructura de Componentes
```
frontend/src/
├── components/     # Componentes reutilizables (Layout, Cards, etc.)
├── pages/          # Páginas principales (Home, Servicios, Contacto, etc.)
├── services/       # API clients y lógica de negocio
└── types/          # TypeScript types y interfaces
```

### Flujo de Datos
1. **ETL** (backend) extrae datos de fuentes oficiales diariamente
2. **API REST** expone datos vía FastAPI endpoints
3. **Frontend** consume API usando React Query
4. **UI** muestra datos en componentes React con TailwindCSS

## Developer Workflows

### Setup Inicial
```bash
# Backend
cd backend
python -m venv ../.venv
source ../.venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python scripts/init_db.py

# Frontend
cd frontend
npm install
```

### Desarrollo Local
```bash
# Terminal 1 - Backend
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev -- --host --port 5173
```

### Testing
```bash
# Backend
cd backend
pytest                    # Todos los tests
pytest -v                 # Verbose
pytest --cov              # Con coverage

# Frontend
cd frontend
npm test                  # Run tests
npm run test:coverage     # Con coverage
```

### Building para Producción
```bash
# Frontend
cd frontend
npm run build             # Output en dist/

# Backend
# Sin build necesario, se ejecuta directamente con uvicorn
```

## Project Conventions

### Code Style

#### Frontend (TypeScript)
- **Componentes**: PascalCase (ej: `ProductoCard.tsx`)
- **Hooks**: camelCase con prefijo `use` (ej: `useProductos`)
- **Estilos**: TailwindCSS utility classes (no CSS inline)
- **Exports**: Named exports para componentes
- **Props**: Interfaces con sufijo `Props`

```typescript
// ✅ Correcto
interface ProductoCardProps {
  producto: Producto
  showPrice?: boolean
}

export default function ProductoCard({ producto, showPrice = true }: ProductoCardProps) {
  // ...
}
```

#### Backend (Python)
- **Files**: snake_case (ej: `combustibles_v2.py`)
- **Classes**: PascalCase (ej: `CombustiblesETLv2`)
- **Functions**: snake_case (ej: `get_productos`)
- **Constants**: UPPER_SNAKE_CASE (ej: `DATABASE_URL`)
- **Formateo**: Black con line length 100
- **Type hints**: Obligatorios en funciones públicas

```python
# ✅ Correcto
def get_productos(
    db: Session,
    categoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> list[Producto]:
    """Obtener lista de productos con filtros opcionales."""
    # ...
```

### Commit Messages
Formato: `<type>: <description>`

**Types**:
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Documentación
- `style`: Formato (sin cambios de código)
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

```bash
# Ejemplos
git commit -m "feat: agregar página de contacto con Formspree"
git commit -m "fix: corregir parsing de CSV en combustibles ETL"
git commit -m "docs: actualizar README con nuevas páginas"
```

## Integration Points

### APIs Externas
- **Catálogo de Datos Abiertos**: https://catalogodatos.gub.uy
  - ANCAP (combustibles)
  - UTE (electricidad) - PDFs
  - OSE (agua) - PDFs
  - Antel (telecomunicaciones) - PDFs

### Servicios Integrados
- **Formspree**: Formulario de contacto (https://formspree.io/f/xaqoleyk)
- **Google Analytics**: Tracking de métricas (configurar ID en `frontend/index.html`)

### Backend API Endpoints
```
GET  /api/v1/productos                    # Listar productos
GET  /api/v1/productos?categoria=agua     # Filtrar por categoría
GET  /api/v1/precios/{id}/ultimo          # Último precio
GET  /api/v1/precios/{id}/variacion       # Variación de precio
GET  /docs                                 # Swagger UI
GET  /health                               # Health check
```

### Comunicación Frontend-Backend
- **React Query** maneja cache, loading states y error handling
- **Axios** como HTTP client (configurado en `services/api.ts`)
- **CORS** configurado en backend para localhost:5173 y dominios de producción

## Key Files

### Frontend
- **`frontend/src/App.tsx`**: Router principal con todas las rutas
- **`frontend/src/components/Layout.tsx`**: Layout global con header/footer y navegación
- **`frontend/src/pages/`**: Páginas principales
  - `Home.tsx`: Dashboard principal
  - `Servicios.tsx`: UTE, OSE, Antel
  - `Comparador.tsx`: Comparar productos
  - `Contacto.tsx`: Formulario de contacto
  - `SobreNosotros.tsx`: Sobre el proyecto
- **`frontend/src/services/productos.ts`**: API client para productos
- **`frontend/index.html`**: Entry point (incluye Google Analytics)

### Backend
- **`backend/app/main.py`**: FastAPI app principal
- **`backend/app/api/v1/`**: Endpoints REST
- **`backend/app/core/database.py`**: Configuración de base de datos
- **`backend/app/core/feature_flags.py`**: Sistema de feature flags (ARCH-002)
- **`backend/app/etl/`**: Procesos ETL
  - `utilities.py`: ETL v1 (UTE, OSE, Antel)
  - `combustibles_v2.py`: ETL v2 para combustibles
  - `ute_v2.py`, `ose_v2.py`, `antel_v2.py`: ETL v2 para servicios
- **`backend/app/models/`**: SQLAlchemy models
- **`backend/app/schemas/`**: Pydantic schemas

### Scripts
- **`scripts/init_db.py`**: Inicializar base de datos
- **`scripts/load_historical.py`**: Cargar datos históricos
- **`scripts/check_db.py`**: Verificar contenido de DB
- **`scripts/arch002_*.py`**: Scripts de monitoreo ARCH-002

## Feature Flags (ARCH-002)

Sistema de rollout gradual implementado:

```python
class RolloutPhase(Enum):
    DISABLED = "disabled"  # v2 no se ejecuta
    SHADOW = "shadow"      # v1 y v2 se ejecutan, v1 retorna, v2 se loggea
    CANARY = "canary"      # 10% tráfico a v2
    GRADUAL = "gradual"    # 25-50% tráfico a v2
    FULL = "full"          # 100% tráfico a v2
```

**Estado actual**: CANARY 10% para combustibles, UTE, OSE, Antel

**Configuración**: `backend/feature_flags_config.json`

## Tareas Recientes Completadas

### ✅ ARCH-002: Migración ETL con Feature Flags
- 8 tareas completadas
- 44 tests pasando (100% success rate)
- Shadow mode implementado
- FASE 1 activada (CANARY 10%)

### ✅ FUNC-001: ETL Servicios Públicos
- UTE, OSE, Antel integrados
- Datos históricos cargados
- Página `/servicios` implementada

### ✅ Nuevas Páginas
- Página Sobre Nosotros (`/sobre-nosotros`)
- Página Contacto (`/contacto`) con Formspree
- Google Analytics integrado

## Próximos Pasos

### En Progreso 🚧
- [ ] ARCH-002 FASE 1: Monitoreo canary 10% (7 días, Jan 26 - Feb 2)
- [ ] Testing end-to-end completo del sitio

### Roadmap ⏭️
- [ ] FUNC-002: Sistema de alertas (email con Resend)
- [ ] PERF-001: Optimizaciones frontend (code splitting, PWA, SEO)
- [ ] Gráficos históricos con Chart.js
- [ ] API pública documentada

## Debugging Tips

### Frontend
```bash
# Ver logs de React Query en DevTools
# Ya integrado, panel visible en desarrollo

# Inspeccionar network requests
# DevTools > Network > filtrar por "api"

# TypeScript errors
npm run type-check
```

### Backend
```bash
# Logs detallados
uvicorn app.main:app --log-level debug

# Ver queries SQL (agregar en database.py)
engine = create_engine(DATABASE_URL, echo=True)

# Verificar base de datos
python scripts/check_db.py

# Ver shadow logs
tail -f backend/logs/shadow_logs.jsonl
```

## Recursos Útiles

### Documentación
- **React**: https://react.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **TailwindCSS**: https://tailwindcss.com/docs
- **React Query**: https://tanstack.com/query/latest

### Herramientas de Desarrollo
- **API Docs (local)**: http://localhost:8000/docs
- **Frontend Dev**: http://localhost:5173
- **Formspree Dashboard**: https://formspree.io/forms/xaqoleyk
- **Google Analytics**: https://analytics.google.com/

### Repositorio
- **GitHub**: https://github.com/manusabbath-arch/cuantocuestauruguay
- **Issues**: https://github.com/manusabbath-arch/cuantocuestauruguay/issues
- **Contributing**: Ver [CONTRIBUTING.md](../CONTRIBUTING.md)

## Convenciones Adicionales

### Variables de Entorno
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./preciosregulados.db
DEBUG=True
CORS_ORIGINS=http://localhost:5173

# Frontend (.env.local)
VITE_API_URL=http://localhost:8000
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Naming Conventions
- **Rutas**: kebab-case (ej: `/sobre-nosotros`, `/contacto`)
- **Archivos**: PascalCase para componentes, snake_case para Python
- **CSS Classes**: TailwindCSS utilities (no custom classes sin motivo)

## Conclusión

Este proyecto está en desarrollo activo. Para contribuir efectivamente:

1. **Leer** [PROJECT_CONTEXT.md](.github/PROJECT_CONTEXT.md) para contexto completo
2. **Revisar** [ROADMAP.md](../ROADMAP.md) para prioridades actuales
3. **Seguir** convenciones de código y commits
4. **Testear** cambios localmente antes de hacer commit
5. **Documentar** nuevas funcionalidades

Para más información, consultar la documentación en el directorio `/docs` o crear un issue en GitHub.

---

**Última actualización**: 27 de enero de 2026
**Estado**: En desarrollo activo (ARCH-002 FASE 1 en curso)
