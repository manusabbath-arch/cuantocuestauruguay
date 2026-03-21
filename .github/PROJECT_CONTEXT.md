# Project Context - CuantoCuestaUruguay

Este es el documento canónico de contexto para asistentes de IA en este repo.

Objetivo:
- Dar a Copilot, Claude y cualquier otro asistente un único lugar desde donde leer el estado real del proyecto.
- Evitar duplicación de instrucciones, decisiones inconsistentes y trabajo paralelo sobre supuestos incorrectos.

Regla principal:
- Si este archivo contradice documentos aspiracionales o reportes viejos, prevalece el código.

Orden de prioridad para entender el proyecto:
1. Código real en backend/app y frontend/src
2. Este archivo
3. ROADMAP.md
4. README.md
5. Documentos históricos o reportes de migración

## Estado actual

Proyecto:
- Plataforma web para consultar precios regulados en Uruguay y expandirse a gasto público e indicadores.

Estado real al 21 de marzo de 2026:
- Combustibles: implementado y operativo
- Utilities UTE/OSE/Antel: implementado pero con dependencia fuerte de TARIFF_HISTORY hardcodeado
- Índices económicos: IPC y dólar BCU implementados recientemente en un ETL dedicado
- Gasto público: ETL + modelo + endpoints + frontend implementados; fuentes CKAN MEF CSV y OPP CKAN; scheduler mensual activo
- Inmobiliario: no implementado en este repo

Advertencia importante:
- ARCH-002_COMPLETION_REPORT.txt y parte del README describen una arquitectura v2/shared packages que no coincide con el código actual.
- No asumir que existen ETLBase, shadow mode, feature flags v2 o archivos *_v2 sólo porque aparecen en documentación histórica.

## Fuente de verdad por tema

Arquitectura backend real:
- backend/app/main.py
- backend/app/routers/
- backend/app/services/scheduler.py
- backend/app/etl/

Arquitectura frontend real:
- frontend/src/App.tsx
- frontend/src/pages/
- frontend/src/components/
- frontend/src/services/

Plan de producto y prioridades:
- ROADMAP.md

Documentación general:
- README.md
- DEPLOYMENT.md
- QUICKSTART.md

Documentos que requieren validación contra código antes de usarse:
- ARCH-002_COMPLETION_REPORT.txt
- documentos en docs/ relacionados con migraciones o integración futura

## Estructura real del repo

Root:
- frontend/: app React + Vite + TypeScript
- backend/: app FastAPI + SQLAlchemy + APScheduler + tests
- docs/: documentos de soporte, estrategia y notas históricas
- .github/: workflows, seguridad, contexto compartido e instrucciones para agentes

Backend:
- backend/app/main.py: arranque FastAPI, lifespan, scheduler, middlewares
- backend/app/routers/precios.py: endpoints de productos, precios, variaciones, comparar, estadísticas
- backend/app/routers/etl.py: ejecución manual de ETLs y status del scheduler
- backend/app/routers/facturas.py: endpoints del analizador de facturas
- backend/app/etl/combustibles.py: ETL CKAN de combustibles
- backend/app/etl/utilities.py: ETL de utilities con fallback/manual history
- backend/app/etl/indices.py: ETL de IPC y dólar BCU
- backend/app/services/scheduler.py: jobs programados y alertas operativas
- backend/app/models/models.py: modelos Producto y Precio
- backend/tests/: suite de pytest

Frontend:
- frontend/src/pages/Home.tsx
- frontend/src/pages/Servicios.tsx
- frontend/src/pages/Comparador.tsx
- frontend/src/pages/MiFactura.tsx
- frontend/src/pages/ProductoDetalle.tsx
- frontend/src/pages/PrecioNaftaHoy.tsx
- frontend/src/pages/About.tsx
- frontend/src/pages/Contacto.tsx
- frontend/src/pages/SobreNosotros.tsx
- frontend/src/pages/GastoPublico.tsx
- frontend/src/components/PriceCard.tsx
- frontend/src/services/ — módulos de API (productos.ts, gasto.ts)
- frontend/src/hooks/ — custom hooks (useIsMobile.ts, useGasto.ts)
- frontend/src/hooks/useGasto.ts — (mar-21-2026) hooks para P2-A gasto
- frontend/src/components/OrganismoFilter.tsx — (mar-21-2026) filtro reutilizable
- frontend/src/components/AñoFilter.tsx — (mar-21-2026) filtro reutilizable

## Stack real

Frontend:
- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Recharts

Backend:
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic Settings
- APScheduler
- pandas
- requests
- pytest

Persistencia:
- SQLite en desarrollo por defecto
- PostgreSQL en producción según configuración

Infraestructura:
- Frontend desplegable en Cloudflare Pages
- Backend con configuración compatible con Render/Railway
- Docker Compose para entorno local full stack

## ETLs implementados hoy

### Combustibles
Archivo:
- backend/app/etl/combustibles.py

Fuente:
- CKAN catalogodatos.gub.uy

Características:
- extracción paginada
- transformación a serie histórica
- inserción incremental evitando duplicados
- scheduler activo
- cobertura de tests dedicada

### Utilities
Archivo:
- backend/app/etl/utilities.py

Fuentes:
- mezcla de scraping/parsing y TARIFF_HISTORY manual

Estado:
- funcional pero no plenamente automatizado
- principal riesgo de desactualización silenciosa
- UTE/OSE priorizan parseo de PDF local de URSEA cuando hay datos mapeables
- fallback a TARIFF_HISTORY cuando no hay PDF usable

### Índices
Archivo:
- backend/app/etl/indices.py

Fuentes:
- IPC desde CKAN con URL de recurso oficial configurada
- dólar BCU desde la página oficial de cotizaciones del BCU

Estado:
- implementado
- integrado en router ETL
- integrado en scheduler
- con tests unitarios nuevos

### Gasto Público
Archivo:
- backend/app/etl/gasto_publico.py

Fuente:
- CKAN MEF CSV (ejecución presupuestal por inciso)
- URL configurada en settings.CKAN_MEF_EJECUCION_URL

Modelo:
- EjecucionPresupuestal (tabla separada de Producto/Precio)
- Campos: anio, mes, inciso, nombre_organismo, credito_vigente, ejecutado, fuente
- hybrid_property: porcentaje_ejecucion

Estado:
- ETL implementado con detección dinámica de columnas y limpieza numérica
- Router gasto.py con endpoints: organismos, ejecución, comparación YoY, narrativa, anomalías, exportación CSV
- Scheduler mensual activo (día 1 a las 03:30 UTC); post-ETL dispara detección de anomalías
- Frontend GastoPublico.tsx implementado con narrativa, anomalías, drilldown y botón de descarga CSV
- Detección de anomalías: backend/app/services/analytics.py → tabla anomalias_presupuestales
- Narrativa automática determinista: backend/app/services/narrativa.py
- Watchdog de fuentes ETL: backend/app/services/watchdog.py

### Indicadores Macro
Archivo:
- backend/app/etl/macro_contexto.py

Fuentes (MIDES/CKAN, verificadas con descarga real):
- ISR (Índice de Salario Real) — resource: 805066d4-35a5-4aa4-9fb1-c7d402ebfb85 — 1996–2018
- PIB por industrias (industrial, agropecuario, construcción, servicios) — resource: 856107dd-8b2a-4b3d-b6ec-62c959c2c5f0 — 2005–2018

Advertencia: datos llegan hasta 2018. Mostrar en frontend con nota de cobertura histórica.

Modelo:
- IndicadorMacro (tabla indicadores_macro)
- Campos: codigo, nombre, anio, valor, unidad, fuente
- unique constraint por (codigo, anio)

Estado:
- ETL implementado con upsert
- Router macro.py: GET /api/v1/macro/codigos, /indicadores, /indicadores/export.csv, POST /etl/run
- Scheduler mensual activo (día 2 a las 04:00 UTC, después del gasto)
- Tests: backend/tests/test_macro_contexto_etl.py (13 tests)

---

## Scheduler real

Archivo:
- backend/app/services/scheduler.py

Jobs:
- combustibles: lote diario (02:00 UTC)
- utilities: lote semanal (día configurable, +30min offset)
- índices: lote diario (+60min offset)
- gasto público: lote mensual (día 1 a las 03:30 UTC) + detección de anomalías post-ETL
- macro contexto: lote mensual (día 2 a las 04:00 UTC)
- watchdog: diario a las 06:00 UTC

Notas:
- el scheduler dispara alertas por excepción, tiempos largos, cargas parciales y cero registros
- la lógica real del schedule debe verificarse siempre en scheduler.py, no en documentos viejos

## Modelos de datos actuales

Producto:
- nombre único
- categoría
- unidad
- activo

Precio:
- producto_id
- fecha
- valor
- fuente
- unique constraint por producto_id + fecha

EjecucionPresupuestal:
- anio, mes (nullable=total anual), inciso, nombre_organismo
- credito_vigente, ejecutado, fuente
- unique: (anio, mes, inciso)

AnomaliaPresupuestal:
- anio, mes, inciso, nombre_organismo
- tipo: ejecucion_baja | variacion_atipica | dato_faltante
- severidad: CRITICA | ALTA | MEDIA | BAJA
- descripcion, valor_observado, valor_umbral, detectado_en
- unique: (anio, mes, inciso, tipo)

IndicadorMacro:
- codigo, nombre, anio, valor, unidad, fuente
- unique: (codigo, anio)

Categorías usadas/esperadas en Producto:
- combustible
- indice
- utilities puede convivir con nombres de categoría históricos según datos ya cargados

## Endpoints relevantes

Precios:
- GET /api/v1/productos
- GET /api/v1/productos/{producto_id}
- GET /api/v1/precios/{producto_id}
- GET /api/v1/precios/{producto_id}/ultimo
- GET /api/v1/variacion/{producto_id}
- GET /api/v1/comparar
- GET /api/v1/estadisticas/{producto_id}

ETL:
- POST /api/v1/etl/run
- POST /api/v1/etl/utilities/run
- POST /api/v1/etl/indices/run
- POST /api/v1/etl/gasto/run
- POST /api/v1/etl/gasto/opp/run
- POST /api/v1/etl/run-all
- GET /api/v1/etl/status
- GET /api/v1/etl/alerts

Gasto público:
- GET /api/v1/gasto/organismos
- GET /api/v1/gasto/ejecucion
- GET /api/v1/gasto/comparacion-anual
- GET /api/v1/gasto/narrativa
- GET /api/v1/gasto/anomalias
- POST /api/v1/gasto/anomalias/detectar
- GET /api/v1/gasto/ejecucion/export.csv
- GET /api/v1/gasto/anomalias/export.csv

Precios (export):
- GET /api/v1/precios/export.csv

Indicadores macro:
- GET /api/v1/macro/codigos
- GET /api/v1/macro/indicadores
- GET /api/v1/macro/indicadores/export.csv
- POST /api/v1/macro/etl/run

App:
- GET /
- GET /health
- GET /metrics

## Comandos útiles verificados

Backend local:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend local:
```bash
cd frontend
npm install
npm run dev
```

Tests backend:
```bash
cd backend
venv/bin/python -m pytest tests/
venv/bin/python -m pytest tests/test_combustibles_etl.py
venv/bin/python -m pytest tests/test_indices_etl.py
```

Stack completo con Docker:
```bash
docker-compose up -d
```

Migraciones:
```bash
cd backend
alembic upgrade head
```

## Forma recomendada de colaboración entre agentes

Antes de tocar código:
- leer este archivo
- leer ROADMAP.md si el cambio afecta prioridades o producto
- validar el comportamiento real en código, no en docs históricas

Si un agente implementa algo estructural:
- actualizar este archivo si cambió una fuente, flujo ETL, comando, endpoint o estado del proyecto
- no copiar el mismo contexto en varios archivos

Si hay contradicción entre docs:
- preferir código
- anotar la contradicción en este archivo o limpiar la doc vieja

## Convenciones para evitar duplicación de esfuerzo

- Mantener este archivo corto, factual y orientado a ejecución
- No registrar worklogs temporales aquí
- No usar este archivo para brainstorming o ideas de marketing
- Usar ROADMAP.md para prioridades y fases
- Usar docs/ para análisis largos o documentos específicos de tema

## Riesgos y caveats actuales

- Utilities todavía depende de historia manual
- Parte de la documentación del repo sobre ARCH-002 no describe el estado real del código
- README.md necesita cautela porque mezcla visión futura con implementación actual
- El tipo de cambio BCU hoy no depende de un dataset CKAN confirmado sino de la tabla oficial del BCU

## Cuándo actualizar este archivo

Actualizar si cambia cualquiera de estos puntos:
- ETLs implementados
- fuentes oficiales
- scheduler/jobs
- endpoints públicos
- estructura real del repo
- comandos recomendados de desarrollo/test
- advertencias importantes sobre docs desalineadas

## Referencias Externas e Inspiración Arquitectónica

### USAspending Website
- **Repo**: https://github.com/fedspendingtransparency/usaspending-website
- **Por qué**: Plataforma similar de transparencia de gastos públicos (USA federal spending)
- **Patrones adaptables a nuestro contexto de gasto público MEF**:
  - Componentes de filtro reutilizables (autocomplete, checkboxes, ranges)
  - Arquitectura Redux Toolkit para estado global (filtros + datos)
  - API wrapper centralizado con manejo consistente de errores
  - Custom hooks para reducir boilerplate (useApiCall, useFilters)
  - Visualización con Recharts + D3 (componentes especializados de gasto)
  - Patrón Container + Component para separar lógica Redux de UI

- **Documentación de referencia**:
  - `docs/inspiration-usaspending/resumen_ejecutivo.md` — estructura y patrones
  - `docs/inspiration-usaspending/usaspending_code_examples.md` — código producción-ready
  - `docs/inspiration-usaspending/typescript_tailwind_migration.md` — migración JS→TS, SCSS→ Tailwind
  - `docs/inspiration-usaspending/README_PATRON_GASTO.md` — aplicación específica a P2-A gasto público

- **Uso recomendado**: Al desarrollar frontend para visualización de GastoPublico.tsx (P2-A+)
- **Status**: Consultado en sprint 21-mar-2026; documentación copiada a repo local

### Otros proyectos de referencia (futuros)
- CKAN Data Transparency UI (DTUI): posible librería de componentes reutilizables para portales públicos
- Indicadores.uy (protocolo abierto): si se expande a más indicadores económicos

## Frontend Architecture Updates (mar-21-2026)

### P2-A Refactorización según patrones USAspending

**Objetivo**: Mejorar reutilización de componentes y lógica para visualización de gasto público.

**Implementación (Opción A - TanStack Query):**

1. **API Service** — `frontend/src/services/gasto.ts`
   - Tipificación de endpoints `/api/v1/gasto/*`
   - Query key factory para caching
   - Manejo consistente de errores

2. **Custom Hooks** — `frontend/src/hooks/useGasto.ts`
   - `useGasto(filters)` — acceso simplificado a todas las queries
   - `useGastoOrganismos(anio)` — solo organismos
   - `useGastoEjecucion(filters)` — ejecución presupuestal
   - `useGastoComparacion(inciso)` — comparación YoY

3. **Componentes Reutilizables** — `frontend/src/components/`
   - `OrganismoFilter.tsx` — multiselect con búsqueda
   - `AñoFilter.tsx` — selector de años

**Documentación**: `docs/FRONTEND_REFACTOR_P2A.md`

**Estado**: ✅ Compilando sin errores, opt-in (no breaking changes)
