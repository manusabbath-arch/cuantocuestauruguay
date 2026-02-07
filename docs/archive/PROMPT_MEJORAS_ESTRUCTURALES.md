# Prompt para Claude — Mejoras Estructurales PreciosRegulados.uy

> Copiar todo el contenido debajo de la línea y pegar en una nueva conversación con Claude.

---

## CONTEXTO DEL PROYECTO

Soy el desarrollador de **PreciosRegulados.uy** (dominio: cuantocuestauruguay.com), una plataforma web que consulta y muestra precios regulados en Uruguay (combustibles ANCAP, tarifas UTE/OSE/Antel) con datos oficiales del catálogo de datos abiertos del gobierno (catalogodatos.gub.uy).

### Stack actual
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS, desplegado en Cloudflare Pages (gratis)
- **Backend**: FastAPI (Python 3.11) + SQLAlchemy + SQLite (dev) / PostgreSQL (prod), desplegado en Render.com (free tier)
- **ETL**: APScheduler ejecuta diariamente extracción de datos de CKAN API y parsing de PDFs de tarifas
- **BD en producción**: PostgreSQL free tier en Render (1 GB máximo)

### Qué hace hoy
1. **ETL automatizado** extrae datos de combustibles (API CKAN) y tarifas de servicios (PDFs de URSEA) una vez al día
2. **API REST** (21 endpoints) expone: productos, precios históricos, variaciones, comparaciones, estadísticas
3. **Frontend** con 9 páginas: Home, Servicios, Comparador, Detalle de producto, Precio Nafta Hoy, Mi Factura (análisis de PDFs de UTE), Contacto, Sobre Nosotros
4. **Sistema de feature flags** con rollout gradual (shadow mode, canary, full) para migrar ETL v1→v2
5. **Análisis de facturas**: el usuario sube un PDF de factura UTE, se extrae consumo/cargos en memoria, se compara con tarifas oficiales y se dan recomendaciones de ahorro. No se almacena ningún dato personal.
6. **Cache en memoria** con TTL de 10 minutos en los endpoints más consultados

### Qué datos almacena la base de datos
- Tabla `productos`: ~20-30 filas (nombre, categoría, unidad). Datos estáticos.
- Tabla `precios`: registros históricos de precios (producto_id, fecha, valor, fuente). Un registro por producto por día. Con ~25 productos y 6 años de datos = ~55,000 filas máximo. Cada fila pesa ~100 bytes. **Total estimado: ~5 MB**.
- Tabla `alertas`: vacía (feature futura, modelo existe pero no se usa).
- Logs de shadow mode: archivo JSONL local, no en BD.

### Costos actuales
- Cloudflare Pages: **$0** (frontend estático)
- Render.com free tier: **$0** (backend con spin-down por inactividad, BD PostgreSQL 1 GB)
- Dominio: ~**$12/año**
- **Total: ~$12/año**

### Límites del free tier de Render
- El servicio web se apaga tras 15 minutos de inactividad (cold start de ~30 segundos)
- PostgreSQL free tier: 1 GB almacenamiento, expira tras 90 días sin actividad
- 750 horas/mes de compute (suficiente para 1 servicio 24/7)

---

## MIS PREOCUPACIONES CONCRETAS

### 1. Almacenamiento innecesario
No quiero acumular datos que generen costos o complejidad. Actualmente la BD solo tiene precios históricos (~5 MB) que son datos públicos del gobierno. La tabla `alertas` está vacía. Los PDFs de facturas se procesan en memoria y no se guardan. Pero me preocupa que a futuro se agreguen features que almacenen datos de usuarios (emails, suscripciones, preferencias) que impliquen obligaciones legales (Ley 18.331 de protección de datos) y costos de infraestructura.

### 2. Carga en producción
El proyecto es chico, no espero tráfico masivo. Pero el backend corre en Render free tier con cold starts. Si algún día tiene tracción orgánica (SEO, redes), ¿el sistema aguanta? El scheduler ejecuta ETL diariamente a las 2 AM — ¿eso mantiene el servicio activo o se duerme igual?

### 3. Complejidad innecesaria
El proyecto tiene código preparado para features que no se usan: WhatsApp bot (Twilio), newsletter manager (Resend), sistema de alertas (tabla vacía), sistema de feature flags complejo con shadow mode. ¿Esto suma o resta? ¿Debería limpiar o mantener?

### 4. Posicionamiento y diferenciación
Tengo el dominio cuantocuestauruguay.com. Es una oportunidad real para posicionar algo útil. Pero no sé si el enfoque actual (mostrar precios que el gobierno ya publica) es suficientemente diferenciador. ¿Qué haría que la gente vuelva?

---

## LO QUE NECESITO DE VOS

Necesito que analices el proyecto desde una perspectiva de **arquitecto senior pragmático** y me des:

### A) Diagnóstico honesto del estado actual
- ¿Qué está bien y no se debe tocar?
- ¿Qué es over-engineering para el tamaño del proyecto?
- ¿Qué deuda técnica existe que puede morder en producción?

### B) Plan de mejoras estructurales concretas
Quiero una lista priorizada de mejoras que hagan al proyecto **tangiblemente mejor**, no features cosméticas. Cada mejora debe responder:
- ¿Qué problema resuelve?
- ¿Cuánto esfuerzo lleva? (horas, no semanas)
- ¿Qué impacto tiene en el usuario final?

Enfocarse en:
1. **Eliminar peso muerto** — código y features que no se usan y agregan complejidad
2. **Hardening para producción** — que el deploy en Render free tier sea sólido y no se rompa
3. **SEO y descubribilidad** — que la gente encuentre el sitio buscando "precio nafta uruguay" en Google
4. **Valor diferencial** — features que hagan que la gente prefiera este sitio sobre buscar en Google directo
5. **Arquitectura zero-storage** — estrategia para dar valor sin almacenar datos de usuarios

### C) Análisis de costos y límites
- Con el uso actual (~5 MB en BD, tráfico bajo), ¿cuánto crecimiento aguanta el free tier?
- ¿Cuándo necesitaría pasar a planes pagos y cuánto costaría?
- ¿Hay algo que esté haciendo que queme recursos innecesariamente?

### D) Roadmap realista de 5 puntos
Dame exactamente 5 objetivos concretos para las próximas 4 semanas, ordenados por impacto. Cada uno debe ser completable en 1-2 sesiones de trabajo. No quiero un roadmap de 12 meses — quiero 5 cosas que hagan una diferencia visible YA.

---

## RESTRICCIONES IMPORTANTES

- **Presupuesto: $0-15/mes máximo** para infraestructura
- **Un solo desarrollador** (yo) — las mejoras deben ser mantenibles por una persona
- **No almacenar datos personales** — evitar emails, cuentas de usuario, cualquier PII
- **Priorizar lo que el usuario ve** — no más infraestructura invisible
- **El código actual funciona** — no quiero reescrituras, quiero mejoras incrementales
- **Uruguay es el mercado** — ~3.5 millones de habitantes, nicho pequeño pero sin competencia directa

---

## ARCHIVOS CLAVE PARA CONTEXTO (si necesitas verlos te los puedo compartir)

- `backend/app/main.py` — FastAPI app con middleware de seguridad, Sentry, scheduler
- `backend/app/routers/precios.py` — 278 líneas, 7 endpoints con cache en memoria
- `backend/app/routers/etl.py` — 347 líneas, endpoints ETL + feature flags + shadow mode
- `backend/app/routers/facturas.py` — 96 líneas, análisis de PDFs de UTE
- `backend/app/models/models.py` — 3 tablas: Producto, Precio, Alerta
- `backend/app/scheduler.py` — cron diario ETL a las 2 AM
- `frontend/src/App.tsx` — 9 rutas React
- `frontend/src/pages/Home.tsx` — dashboard con PriceCards y React Query
- `render.yaml` — config de deploy Render (free tier)
- `backend/feature_flags_config.json` — combustibles en "full", servicios en "canary"

---

Sé directo, práctico y honesto. Si algo no tiene sentido para un proyecto de este tamaño, decímelo. Prefiero un proyecto simple que funcione perfecto a uno ambicioso que se rompa.
