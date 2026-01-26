# Roadmap de Integración: TransparenciaUY Ecosystem

## 🎯 Visión
Crear el ecosistema de datos abiertos más completo de Uruguay, unificando:
- **PreciosRegulados.uy** - Precios de servicios públicos
- **FiscalizadorUY** - Gastos públicos y ejecución presupuestal
- **TransparenciaAPI** - API general de datos gubernamentales

---

## 🗺️ Arquitectura Propuesta

### Opción 1: Monorepo (RECOMENDADO)

```
transparencia-uruguay/
├── apps/
│   ├── precios/          # PreciosRegulados.uy (actual)
│   ├── gastos/           # Fiscalizador MEF
│   └── datos/            # API general de datos abiertos
├── packages/             # Código compartido
│   ├── shared-ui/        # Componentes React comunes
│   ├── etl-core/         # ETL utilities compartidas
│   ├── api-client/       # Cliente API común
│   └── types/            # TypeScript types compartidos
├── docs/                 # Documentación unificada
└── infra/                # Terraform/config de infraestructura
```

**Dominio:** `transparenciauruguay.com`
- `/precios` → PreciosRegulados
- `/gastos` → Fiscalizador
- `/api` → API general
- `/docs` → Documentación

**Stack unificado:**
- Frontend: React 18 + TypeScript + Vite
- Backend: FastAPI + PostgreSQL
- Hosting: Cloudflare Pages + Render.com
- CI/CD: GitHub Actions compartidas
- Monorepo: Turborepo o Nx

---

## 📅 Fases de Implementación

### Fase 1: Preparación (1-2 semanas)

#### PREP-001: Análisis de código común
- [ ] Auditar `bot-fiscalizador` y `transparencia` por funcionalidad reutilizable
- [ ] Identificar módulos ETL comunes
- [ ] Mapear endpoints de API duplicados
- [ ] Listar componentes UI reutilizables

#### PREP-002: Definir estructura de monorepo
- [ ] Elegir herramienta: Turborepo vs Nx vs pnpm workspaces
- [ ] Diseñar estructura de carpetas
- [ ] Configurar linting/testing compartido
- [ ] Setup de CI/CD multi-app

#### PREP-003: Branding y dominio
- [ ] Registrar `transparenciauruguay.com`
- [ ] Diseño de logo/identidad visual común
- [ ] Definir paleta de colores unificada
- [ ] Crear guía de estilo

---

### Fase 2: Extracción de Código Común (2-3 semanas)

#### COMMON-001: ETL Core Package
**Objetivo:** Librería compartida de ETL

```python
# packages/etl-core/src/base.py
from abc import ABC, abstractmethod

class ETLBase(ABC):
    """Base class para todos los ETL de TransparenciaUY"""
    
    @abstractmethod
    async def extract(self) -> dict:
        pass
    
    @abstractmethod
    async def transform(self, data: dict) -> dict:
        pass
    
    @abstractmethod
    async def load(self, data: dict) -> None:
        pass
    
    async def run(self):
        data = await self.extract()
        transformed = await self.transform(data)
        await self.load(transformed)
```

**Módulos a extraer:**
- CKAN API client (catalogodatos.gub.uy)
- PDF scraping utilities
- Data validators
- Database connectors
- Scheduler wrappers (APScheduler)

#### COMMON-002: API Client Package
**Objetivo:** Cliente TypeScript para consumir APIs

```typescript
// packages/api-client/src/index.ts
export class TransparenciaClient {
  private baseUrl: string;
  
  async getPrecios() { /* ... */ }
  async getGastos() { /* ... */ }
  async getDatos() { /* ... */ }
}
```

#### COMMON-003: Shared UI Components
**Objetivo:** Componentes React reutilizables

```typescript
// packages/shared-ui/src/components/
├── DataTable/          # Tabla de datos genérica
├── Charts/             # Gráficos Recharts configurados
├── Filters/            # Filtros de fecha, categoría
├── Layout/             # Header, Footer, Nav común
└── LoadingStates/      # Skeletons, spinners
```

---

### Fase 3: Migración de Apps (3-4 semanas)

#### MIG-001: Migrar PreciosRegulados (actual)
- [ ] Mover `cuantocuestauruguay` a `apps/precios/`
- [ ] Reemplazar ETL custom con `etl-core`
- [ ] Usar `shared-ui` components
- [ ] Configurar routing en `/precios`
- [ ] Tests de integración

#### MIG-002: Migrar Fiscalizador MEF
- [ ] Mover `bot-fiscalizador` a `apps/gastos/`
- [ ] Extraer lógica de scraping MEF a `etl-core`
- [ ] Reescribir Streamlit a React (usar `shared-ui`)
- [ ] API FastAPI para datos de gastos
- [ ] Routing en `/gastos`

#### MIG-003: Migrar Transparencia API
- [ ] Mover `transparencia` a `apps/datos/`
- [ ] Consolidar endpoints existentes
- [ ] Agregar OpenAPI docs unificadas
- [ ] Routing en `/api`

---

### Fase 4: Unificación y Deploy (2 semanas)

#### UNIF-001: Frontend unificado
- [ ] Navbar común con links a `/precios`, `/gastos`, `/datos`
- [ ] Homepage en `/` con overview de 3 módulos
- [ ] Buscar global cross-app
- [ ] Tema oscuro/claro compartido

#### UNIF-002: Backend consolidado
- [ ] API Gateway para rutear entre apps
- [ ] Base de datos compartida o separadas?
- [ ] Auth/API keys unificadas
- [ ] Rate limiting global

#### UNIF-003: Deploy a producción
- [ ] Cloudflare Pages para frontend
- [ ] Render.com para backend (o Railway)
- [ ] DNS configurado: `transparenciauruguay.com`
- [ ] SSL/CDN activo
- [ ] CI/CD con deploy selectivo por app

---

## 🎁 Quick Wins Iniciales (1 semana)

### QW-001: Link cruzado entre proyectos actuales
**Acción inmediata** sin migrar código:

1. Añadir banner en PreciosRegulados.uy:
   ```html
   <div class="banner">
     ✨ Nuevo: Explorá también 
     <a href="https://fiscalizador-uy.streamlit.app">Gastos Públicos</a> y
     <a href="https://transparencia-api.onrender.com">API de Datos Abiertos</a>
   </div>
   ```

2. Crear landing page unificada:
   ```
   transparenciauruguay.github.io
   ├── Precios Regulados → cuantocuestauruguay.com
   ├── Gastos Públicos → [URL Streamlit]
   └── API Datos Abiertos → [URL API]
   ```

3. Compartir analytics entre proyectos (Plausible)

### QW-002: Reutilizar CKAN client
Extraer de `transparencia`:
```python
# Ya existe en tu proyecto transparencia
# Copiar a PreciosRegulados.uy/backend/app/utils/ckan_client.py
```

### QW-003: README cruzado
Añadir a cada README:
```markdown
## 🌐 Ecosistema TransparenciaUY
Este proyecto es parte del ecosistema de datos abiertos de Uruguay:
- **PreciosRegulados.uy** - Precios de servicios públicos
- **FiscalizadorUY** - Gastos públicos del MEF
- **TransparenciaAPI** - API general de datos gubernamentales
```

---

## 📊 Comparativa: Monorepo vs Multi-Repo

| Criterio | Monorepo | Multi-Repo |
|----------|----------|------------|
| **Reutilización código** | ✅✅✅ Excelente | ⚠️ Manual |
| **Deploy independiente** | ✅ Posible con Turborepo | ✅✅ Nativo |
| **CI/CD** | ⚠️ Más complejo | ✅ Simple |
| **Onboarding** | ⚠️ Curva aprendizaje | ✅ Directo |
| **Versionado** | ⚠️ Un version.json | ✅ Por proyecto |
| **SEO** | ✅✅ Dominio único fuerte | ⚠️ Disperso |
| **Comunidad** | ✅✅ Unificada | ⚠️ Fragmentada |
| **Mantenimiento** | ✅ Centralizado | ⚠️⚠️ Duplicado |

**Recomendación: Monorepo** (80% de proyectos open source exitosos lo usan)

---

## 🚀 Acción Inmediata Recomendada

### Opción A: Empezar gradual (RECOMENDADO)
1. **Esta semana:** Implementar QW-001 (links cruzados)
2. **Próxima semana:** Crear `transparenciauruguay` GitHub org
3. **Próximo mes:** Migrar un módulo pequeño (ej: CKAN client)

### Opción B: Big bang
1. Pausar desarrollo individual
2. Crear monorepo completo
3. Migrar todo en 4-6 semanas

---

## 💰 Estimación de Recursos

**Tiempo de desarrollo (solo):** 6-8 semanas
**Con ayuda (2 personas):** 3-4 semanas
**Inversión infraestructura:**
- Dominio `transparenciauruguay.com`: $12/año
- Hosting: $0 (free tiers: Cloudflare + Render)
- Total: **~$12/año**

---

## 📚 Referencias

- [Turborepo Handbook](https://turbo.build/repo/docs/handbook)
- [Nx Monorepo](https://nx.dev/)
- [CKAN API](https://docs.ckan.org/en/latest/api/)
- [catalogodatos.gub.uy](https://catalogodatos.gub.uy)

---

**Conclusión:** La integración es **altamente recomendada**. Los 3 proyectos se complementan perfectamente y juntos forman una plataforma única en Uruguay de transparencia de datos gubernamentales.

¿Comenzamos con los Quick Wins o prefieres ir directo al monorepo?
