# 📋 Plan Estratégico de Mejoras - CuantoCuestaUruguay
## Versión 1.0 | Enero 2026

---

## 🎯 Visión General

Este plan estratégico define los objetivos de evolución del proyecto PreciosRegulados.uy, priorizando seguridad, privacidad, experiencia de usuario y sostenibilidad técnica.

### Ejes Estratégicos
1. **Seguridad** - Protección de infraestructura y datos
2. **Privacidad** - Cumplimiento normativo y ética de datos
3. **Funcionalidad** - Ampliar servicios y valor para usuarios
4. **Rendimiento** - Optimizar experiencia y costos
5. **Sostenibilidad** - Escalabilidad y mantenibilidad

---

## 🔴 PRIORIDAD 0: SEGURIDAD CRÍTICA (Implementar AHORA)

### SEC-001: Configuración de Seguridad en Cloudflare
**Objetivo:** Proteger el dominio cuantocuestauruguay.com contra ataques comunes

**Acciones:**
- [ ] Activar **Cloudflare WAF** (Web Application Firewall)
  - Reglas OWASP Core Ruleset
  - Protección contra inyección SQL, XSS, CSRF
- [ ] Configurar **SSL/TLS en modo "Full (Strict)"**
  - Validar certificados de origen
  - Habilitar HSTS (HTTP Strict Transport Security)
  - Minimum TLS Version: 1.2
- [ ] Activar **Rate Limiting** para API
  - 100 requests/min por IP para endpoints públicos
  - 10 requests/min para endpoints ETL (POST)
- [ ] Configurar **Bot Fight Mode**
  - Bloquear bots maliciosos
  - Desafío JavaScript para bots sospechosos
- [ ] Habilitar **DDoS Protection** (automático en Free tier)
- [ ] Configurar **Page Rules**:
  - `*.cuantocuestauruguay.com/*` → Always Use HTTPS
  - `cuantocuestauruguay.com/api/*` → Security Level: High
- [ ] Activar **Firewall Rules**:
  - Bloquear IPs de países sospechosos (excepto Uruguay/región)
  - Permitir solo métodos HTTP necesarios (GET, POST, OPTIONS)

**Resultado esperado:** Reducir superficie de ataque en 95%

---

### SEC-002: Hardening del Backend (Render.com)
**Objetivo:** Asegurar aplicación FastAPI y PostgreSQL

**Acciones:**
- [ ] **Secrets Management**
  - Rotar `SECRET_KEY` de JWT (mínimo 256 bits)
  - Usar generador criptográfico: `openssl rand -hex 32`
  - Almacenar en Render Environment Variables (no en código)
- [ ] **Configurar CORS estrictamente**
  - Solo permitir orígenes conocidos:
    ```
    CORS_ORIGINS=https://cuantocuestauruguay.com,https://www.cuantocuestauruguay.com
    ```
  - Eliminar wildcards (`*`)
- [ ] **Headers de Seguridad HTTP**
  - Implementar middleware de seguridad:
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `X-XSS-Protection: 1; mode=block`
    - `Strict-Transport-Security: max-age=31536000`
    - `Content-Security-Policy` con directivas restrictivas
- [ ] **Rate Limiting a nivel de aplicación**
  - Implementar `slowapi` para FastAPI
  - Límites por endpoint:
    - `GET /api/v1/productos`: 60/min
    - `POST /api/v1/etl/*`: 5/min (requiere autenticación)
- [ ] **Input Validation**
  - Validar todos los parámetros con Pydantic
  - Sanitizar inputs para prevenir inyección SQL
  - Límites de tamaño en request body
- [ ] **PostgreSQL Security**
  - Cambiar contraseña de BD (generar segura)
  - Habilitar SSL para conexiones (Render soporta)
  - Configurar `pg_hba.conf` para solo permitir localhost
- [ ] **Logging y Monitoreo**
  - Registrar intentos de acceso no autorizados
  - Alertas para patrones sospechosos
  - No loguear datos sensibles (passwords, tokens)

**Resultado esperado:** Cumplir OWASP Top 10 básico

---

### SEC-003: Gestión de Dependencias
**Objetivo:** Eliminar vulnerabilidades conocidas en librerías

**Acciones:**
- [ ] **Auditoría de dependencias**
  - Backend: `pip install safety && safety check`
  - Frontend: `npm audit`
- [ ] **Actualizar librerías críticas**
  - Priorizar: `fastapi`, `pydantic`, `sqlalchemy`, `psycopg2`
  - Verificar breaking changes
- [ ] **Configurar Dependabot**
  - GitHub Actions para PRs automáticos de seguridad
  - Review semanal de actualizaciones
- [ ] **Pinning de versiones**
  - `requirements.txt` con versiones exactas (`==`)
  - `package-lock.json` en control de versiones

**Resultado esperado:** 0 vulnerabilidades críticas/altas

---

## 🟡 PRIORIDAD 1: PRIVACIDAD Y CUMPLIMIENTO (2-4 semanas)

### PRIV-001: Política de Privacidad y GDPR/LPDP
**Objetivo:** Cumplir Ley de Protección de Datos Personales (Ley N° 18.331) de Uruguay

**Acciones:**
- [ ] **Crear Política de Privacidad**
  - Qué datos recolectamos (analytics, logs)
  - Cómo los usamos
  - Cuánto tiempo los guardamos
  - Derechos de los usuarios (ARCO: Acceso, Rectificación, Cancelación, Oposición)
- [ ] **Cookies y Tracking**
  - Banner de consentimiento (si se usa analytics)
  - Opción de opt-out
  - Clasificar cookies: esenciales vs analytics
- [ ] **Anonimización de Logs**
  - Enmascarar IPs en logs: `192.168.x.x`
  - No guardar información personal identificable (PII)
  - Retención máxima: 90 días
- [ ] **Términos de Servicio**
  - Disclaimer sobre uso de datos
  - Limitación de responsabilidad
  - Contacto para ejercer derechos

**Resultado esperado:** Cumplimiento legal de Ley 18.331

---

### PRIV-002: Analytics Ético (Sin Google Analytics)
**Objetivo:** Medir uso sin invadir privacidad

**Acciones:**
- [ ] Implementar **Plausible Analytics** (GDPR-friendly)
  - Alternativa: **umami** (self-hosted, open source)
  - No cookies, no tracking de usuarios
  - Datos agregados, no individuales
- [ ] Métricas a trackear:
  - Páginas vistas
  - Productos más consultados
  - Fuentes de tráfico (referrers)
  - Dispositivos (móvil vs desktop)
- [ ] Dashboard público de estadísticas
  - Transparencia con usuarios
  - Ejemplos: plausible.io/cuantocuestauruguay.com

**Resultado esperado:** Analytics sin comprometer privacidad

---

## 🟢 PRIORIDAD 2: FUNCIONALIDAD Y VALOR (1-3 meses)

### FUNC-001: ETL de Servicios Públicos
**Objetivo:** Ampliar catálogo con UTE, OSE, Antel

**Acciones:**
- [ ] **UTE (Electricidad)**
  - Implementar scraper de https://portal.ute.com.uy/tarifas
  - Modelos: `TarifaElectricidad` (residencial, comercial, industrial)
  - Campos: potencia, consumo, cargo fijo, energía
- [ ] **OSE (Agua y Saneamiento)**
  - Scraper de https://www.ose.com.uy/tarifas
  - Modelos: `TarifaAgua` (categorías, consumo m³)
  - Cargo fijo + variable por m³
- [ ] **Antel (Telecomunicaciones)**
  - API/scraper de planes (Fibra, Móvil, Telefonía)
  - Comparador de planes por velocidad/precio
- [ ] **Scheduler automático**
  - Ejecutar ETL semanal (viernes 00:00 UTC)
  - Alertas si falla ETL
  - Logs de cambios de precios

**Resultado esperado:** 3 servicios nuevos con datos históricos

---

### FUNC-002: Sistema de Alertas de Precios
**Objetivo:** Notificar a usuarios sobre cambios significativos

**Acciones:**
- [ ] **Backend: Webhook/Email**
  - Endpoint para suscribirse: `POST /api/v1/alertas/subscribe`
  - Almacenar email + productos de interés
  - Disparar cuando cambio > 5%
- [ ] **Frontend: Modal de suscripción**
  - Formulario simple: email + checkbox de productos
  - Confirmación doble opt-in (GDPR)
- [ ] **Integración con servicio de email**
  - Opción 1: SendGrid (free tier: 100 emails/día)
  - Opción 2: Mailgun
  - Template HTML responsive
- [ ] **Funcionalidad de comparación histórica**
  - "El gasoil subió 8% este mes"
  - Gráfico adjunto en email

**Resultado esperado:** Engagement de usuarios +30%

---

### FUNC-003: API Pública con API Keys
**Objetivo:** Permitir uso externo controlado

**Acciones:**
- [ ] **Sistema de API Keys**
  - Endpoint: `POST /api/v1/auth/register` → devuelve API Key
  - Header: `X-API-Key: xxxxx`
  - Rate limiting por key: 1000 req/día (free tier)
- [ ] **Documentación mejorada**
  - Swagger UI con ejemplos de cURL
  - Guía de inicio rápido
  - SDKs básicos (Python, JavaScript)
- [ ] **Tier Premium (opcional futuro)**
  - Free: 1000 req/día
  - Premium: ilimitado + soporte
  - Monetización sostenible

**Resultado esperado:** 50+ desarrolladores usando la API en 6 meses

---

## 🔵 PRIORIDAD 3: RENDIMIENTO Y UX (3-6 meses)

### PERF-001: Optimización de Frontend
**Objetivo:** Mejorar performance y SEO

**Acciones:**
- [ ] **Code Splitting y Lazy Loading**
  - Dividir bundle de React
  - Cargar rutas bajo demanda
  - Reducir First Contentful Paint (FCP) < 1.5s
- [ ] **Optimización de imágenes**
  - WebP para gráficos
  - Lazy loading de charts
  - CDN para assets estáticos
- [ ] **SEO On-Page**
  - Meta tags dinámicos por producto
  - Open Graph para redes sociales
  - Schema.org structured data (Product, PriceSpecification)
  - Sitemap XML automático
- [ ] **PWA (Progressive Web App)**
  - Service worker para offline
  - Manifest.json con íconos
  - Instalable en móviles
- [ ] **Lighthouse Score > 90**
  - Performance, Accessibility, Best Practices, SEO

**Resultado esperado:** Tiempo de carga < 2s, SEO rank +50%

---

### PERF-002: Caché y CDN
**Objetivo:** Reducir latencia y costos de servidor

**Acciones:**
- [ ] **Redis para caché de API**
  - Cachear respuestas de `/productos` (TTL: 1 hora)
  - Cachear históricos (TTL: 24 horas)
  - Invalidar al ejecutar ETL
- [ ] **Cloudflare Page Rules**
  - Cachear assets estáticos: `/*.(js|css|png|jpg|svg)`
  - Edge caching para HTML (TTL: 5 min)
- [ ] **Compresión Gzip/Brotli**
  - Activar en Cloudflare
  - Reducir tamaño de respuestas 70%

**Resultado esperado:** Latencia API < 200ms (p95)

---

### UX-001: Mejoras de Interfaz
**Objetivo:** Experiencia de usuario excepcional

**Acciones:**
- [ ] **Dark Mode**
  - Toggle en header
  - Persistir preferencia en localStorage
  - Colores optimizados (WCAG AA)
- [ ] **Gráficos interactivos avanzados**
  - Zoom en rangos de fechas
  - Tooltips con detalles
  - Exportar a PNG/CSV
- [ ] **Búsqueda inteligente**
  - Autocompletar productos
  - Filtros por categoría, región
  - Sugerencias populares
- [ ] **Comparador multi-producto**
  - Seleccionar hasta 5 productos
  - Gráfico superpuesto
  - Tabla comparativa
- [ ] **Vista móvil mejorada**
  - Bottom sheet para filtros
  - Gestos swipe
  - Optimizar para pantallas pequeñas

**Resultado esperado:** Tasa de rebote < 40%, tiempo en sitio > 3 min

---

## 🟣 PRIORIDAD 4: SOSTENIBILIDAD (6-12 meses)

### SUST-001: Monitoreo y Observabilidad
**Objetivo:** Detectar y resolver problemas proactivamente

**Acciones:**
- [ ] **Sentry para error tracking**
  - Configurar DSN en backend y frontend
  - Alertas de errores críticos
  - Source maps para stack traces legibles
- [ ] **Uptime Monitoring**
  - UptimeRobot (gratis: 50 monitores)
  - Verificar cada 5 minutos
  - Alertas por email/SMS
- [ ] **Logs centralizados**
  - Render logs → external service (Logtail, Papertrail)
  - Retención: 30 días
  - Búsqueda full-text
- [ ] **Dashboards de métricas**
  - Grafana + Prometheus (opcional)
  - Métricas: requests/s, latencia, errores, uptime
  - Alertas por umbrales

**Resultado esperado:** Tiempo de detección de incidentes < 5 min

---

### SUST-002: Documentación y Onboarding
**Objetivo:** Facilitar contribuciones de la comunidad

**Acciones:**
- [ ] **Contributing Guide**
  - CONTRIBUTING.md con guía de estilo
  - Proceso de PR review
  - Code of Conduct
- [ ] **Documentación técnica**
  - ADRs (Architecture Decision Records)
  - Diagramas de arquitectura (mermaid)
  - Guía de deployment local
- [ ] **Videos tutoriales**
  - YouTube: "Cómo contribuir"
  - "Cómo usar la API"
  - "Deploy tu propia instancia"
- [ ] **Issues etiquetados**
  - `good-first-issue` para nuevos
  - `help-wanted` para comunidad
  - Templates de issues/PRs

**Resultado esperado:** 10+ contribuidores externos en 1 año

---

### SUST-003: Testing y CI/CD
**Objetivo:** Garantizar calidad de código

**Acciones:**
- [ ] **Aumentar cobertura de tests**
  - Backend: >80% coverage
  - Frontend: >70% coverage
  - Tests E2E con Playwright
- [ ] **GitHub Actions mejorados**
  - Lint (flake8, eslint)
  - Tests unitarios
  - Tests de integración
  - Security scan (Snyk, Trivy)
  - Deploy automático solo si tests pasan
- [ ] **Pre-commit hooks**
  - Formateo automático (black, prettier)
  - Validación de tipos (mypy, TypeScript)
  - No permitir commits con errores
- [ ] **Staging environment**
  - Rama `develop` → deploy a staging
  - Pruebas antes de prod
  - Smoke tests automáticos

**Resultado esperado:** 0 hotfixes en producción, CI/CD < 5 min

---

## 📊 KPIs y Métricas de Éxito

### Seguridad
- ✅ 0 vulnerabilidades críticas en dependencias
- ✅ SSL Labs Score: A+
- ✅ Uptime: >99.5%
- ✅ Tiempo de respuesta a incidentes: <1 hora

### Privacidad
- ✅ Cumplimiento LPDP (Ley 18.331)
- ✅ 0 quejas de privacidad
- ✅ Política de privacidad accesible en <2 clicks

### Funcionalidad
- ✅ 10+ productos con datos históricos
- ✅ ETL exitoso >95% de ejecuciones
- ✅ API requests: 10K/mes (objetivo: 100K/mes)

### Rendimiento
- ✅ Lighthouse Score: >90
- ✅ Tiempo de carga: <2s
- ✅ API latency p95: <300ms

### Sostenibilidad
- ✅ Documentación completa (README, API docs, ADRs)
- ✅ Test coverage: >75%
- ✅ Contribuidores activos: >5

---

## 🗓️ Cronograma Tentativo

### Mes 1 (Inmediato)
- ✅ SEC-001: Cloudflare security
- ✅ SEC-002: Backend hardening
- ✅ SEC-003: Dependencies audit
- ⏳ PRIV-001: Privacy policy (inicio)

### Mes 2-3
- ⏳ PRIV-001: Privacy policy (finalización)
- ⏳ PRIV-002: Analytics ético
- ⏳ FUNC-001: ETL servicios (UTE, OSE, Antel)

### Mes 4-6
- ⏳ FUNC-002: Sistema de alertas
- ⏳ FUNC-003: API pública con keys
- ⏳ PERF-001: Frontend optimization
- ⏳ UX-001: UI improvements

### Mes 7-12
- ⏳ PERF-002: Caché y CDN
- ⏳ SUST-001: Monitoring
- ⏳ SUST-002: Documentation
- ⏳ SUST-003: Testing & CI/CD

---

## 🚀 Implementación Inmediata

Comenzaremos ahora con las acciones de **PRIORIDAD 0** que no requieren aprobación:

1. **Cloudflare Security Hardening** (SEC-001)
2. **Backend Security Headers** (SEC-002 parcial)
3. **Dependency Audit** (SEC-003)

---

## 📝 Notas Finales

Este roadmap es un documento vivo que se actualizará según:
- Feedback de usuarios
- Evolución de amenazas de seguridad
- Recursos disponibles
- Prioridades del negocio

**Última actualización:** 26 de enero de 2026
**Próxima revisión:** 26 de febrero de 2026
