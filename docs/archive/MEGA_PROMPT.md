# ANÁLISIS INTEGRAL: CuantoCuestaUruguay.com

## CONTEXTO
Proyecto: Plataforma de seguimiento y comparación de precios regulados en Uruguay (combustibles, servicios públicos, índices)
Stack: React 18 + TypeScript + Vite + TailwindCSS (frontend) · FastAPI + SQLAlchemy + PostgreSQL/SQLite (backend)
Estado: MVP en producción (https://cuantocuestauruguay.com) · <500 visitas/mes · 0 usuarios pagos · 0 revenue
Repositorio: https://github.com/manusabbath-arch/cuantocuestauruguay
Infra: Cloudflare Pages (frontend) + Render.com (backend)
Feature flags: ARCH-002 (canary 10% v2 ETL)

Métricas actuales (completa con datos reales si difieren):
- Visitas/mes: <500
- Bounce rate: ~45% (si difiere, actualizar)
- Usuarios registrados: 0
- Emails capturados: 0
- Revenue: 0
- Marketing: $0/mes

Founder: Solo, no-técnico, usando IA para desarrollo
Tiempo disponible: 10–15 horas/semana
Presupuesto: $0–100/mes

## MERCADO
Uruguay: 3.5M habitantes, alta penetración smartphone (~85%), sensibilidad a precios, cultura de ahorro
Competencia: Precios.uy (UI pobre), sitios oficiales (PDFs / datos dispersos), búsquedas en Google
Ventaja actual: UX moderna, agregación multi‑fuente, foco en datos oficiales actualizados

## OBJETIVO
Convertir en negocio sostenible en 12 meses:
- $1000 MRR
- <20 horas/semana de mantenimiento
- Sin equipo, solo automatizaciones y freelancers puntuales

## SOLICITO (ANÁLISIS END‑TO‑END PARA 90 DÍAS)

### 1) ANÁLISIS CRÍTICO
Entregar en el siguiente formato (máx. 500 palabras):
- 3 fortalezas principales del proyecto
- 3 debilidades críticas que frenan crecimiento
- 1 oportunidad de oro poco obvia
- 1 amenaza existencial a mitigar ya

Considerar específicamente:
- Frontend (React + TS + Vite + Tailwind)
  - ¿Best practices React 18? ¿Anti‑patterns? ¿Re‑renders? ¿Code splitting? ¿Dependencias mínimas y actualizadas? ¿Memoization viable?
  - ¿Estructura de carpetas escalable a 50+ componentes? ¿Custom hooks duplican lógica?
- Backend (FastAPI + SQLAlchemy)
  - ¿Modelos normalizados? ¿Riesgo N+1? ¿Uso correcto de async/await? ¿Validación de inputs/rate limiting? ¿Endpoints para cachear?
  - ¿ETL v2 vs v1: feature flags sobre‑ingeniería o razonable? ¿Scheduler resiliente (retries, idempotencia)?
- DevOps
  - Cloudflare Pages + Render: ¿cost‑effective? ¿Falta monitoring (uptime, error rate, p95)? ¿Secretos bien gestionados? ¿CI/CD con tests?

Qué NO quiero: refactorizar todo, microservicios, Kubernetes.
Qué SÍ quiero: 3 archivos con más code smells y refactors puntuales; cambios 80/20 de performance; errores de producción probables sin monitoring.

### 2) PRIORIZACIÓN (TOP 10 POR ROI)
Para cada acción, entregar:
- Título | Esfuerzo: S/M/L (horas) | Impacto: 1–10 | ROI: Impacto/Esfuerzo | Dependencias | Orden sugerido (#)

Tipos de acciones a mezclar: técnicas (FE/BE/infra), UX/UI, crecimiento (SEO, contenido, viralidad), monetización (pricing, paywalls, features Pro).

### 3) QUICK WINS (≤5)
- Cambios que tomen <2 horas
- Impacto inmediato visible
- No requieren conocimiento técnico profundo

### 4) EXPERIMENTOS (≤3, 2 semanas c/u)
Para cada experimento:
- Hipótesis y por qué
- Métrica de éxito (ej: % comparaciones, CTR CTA, emails capturados)
- Duración (fechas) y tamaño de muestra mínimo
- Criterio go/no‑go
- Paso a paso de ejecución con recursos $0–100

### 5) RED FLAGS
- Errores que probablemente estoy cometiendo
- Asunciones falsas
- Riesgos silenciosos (que explotan luego)

### 6) PREGUNTAS CRÍTICAS
- Info que falta para decidir
- Tests a correr antes de invertir tiempo
- Gaps de conocimiento clave

## CONSTRAINTS FIRMES
- NO sugerir: VCs, contratar equipo, migrar todo el stack, soluciones enterprise
- SÍ sugerir: low‑code/no‑code, automatización, MVPs iterativos, foco en 90 días

## CONTEXTO TÉCNICO (AYUDA PARA TU ANÁLISIS)
- Frontend: React 18 + TS + Vite + Tailwind; rutas principales: Home, Servicios (UTE, OSE, Antel), Comparador, Contacto, Sobre Nosotros; React Query y Axios para API; GA pendiente de ID real.
- Backend: FastAPI + SQLAlchemy; SQLite en dev, PostgreSQL en prod; ETL v1 estable para servicios; ETL v2 en canary (10%); problema conocido: CSV de combustibles (BOM/delimitador); scheduler APScheduler.
- DevOps: Cloudflare Pages (FE), Render (BE); WAF y TLS configurados; rate limiting en Cloudflare; falta monitoreo centralizado.

## ENFOQUE DE NEGOCIO Y PRODUCTO (TU EVALUACIÓN)
- Modelo: inicialmente B2C freemium; validar B2B (API/embeds) como alternativa/puente a ingresos
- Persona objetivo: Mujer 35–50, jefa de hogar, busca ahorrar en gastos mensuales, no tech‑savvy
- Propuesta de valor: datos oficiales simples, comparables y accionables; alertas y ahorro

## CRECIMIENTO (URUGUAY‑FOCUSED)
- SEO: identificar 10 keywords uruguayas (≥100 búsquedas/mes, baja competencia) y mapearlas a páginas
- Contenido: priorizar calculadoras/guías prácticas vs artículos genéricos
- Canales: Reddit/Telegram/WhatsApp/medios locales; experimento de tracción con $0
- Viral loops simples: “Comparte cuánto ahorraste” / embed de comparaciones

## DATOS Y ANALYTICS (LIVIANO, ACCIONABLE)
- Definir 5 eventos críticos a instrumentar (comparación, CTA click, email submit, compartir, retorno)
- North Star Metric propuesta: % usuarios que realizan ≥1 comparación + capturan email/alerta
- Dashboard 1‑página con 6 métricas de decisión

## CUMPLIMIENTO LEGAL BÁSICO
- Ley 18.331 (protección de datos), atribución a fuentes públicas, monetización de datos abiertos
- Solicito: disclaimer de 2 párrafos, checklist mínimo de compliance, secciones clave de Términos

## INTEGRACIONES LOCALES A EVALUAR (PRIORIZAR POR ROI)
- BCU: tipo de cambio, UI, inflación
- UTE/OSE/Antel: PDFs/actualizaciones
- Embeds para medios locales
- Bot de Telegram/WhatsApp para consultas rápidas

## RESPUESTA ESPERADA
Formato y límites:
- Máximo 2000 palabras, claro y accionable, ordenado por ROI
- Evitar jerga innecesaria, hablar directo

Entregar secciones:
1) ANÁLISIS EJECUTIVO
2) PRIORIZACIÓN (TOP 10)
3) QUICK WINS (≤5)
4) EXPERIMENTOS (≤3)
5) RED FLAGS
6) PREGUNTAS CRÍTICAS

## META‑PREGUNTA FINAL
Si solo pudieras hacer 3 cosas en los próximos 30 días para maximizar probabilidad de negocio sostenible en 12 meses (con founder solo, tiempo limitado y sin experiencia técnica):
1) ¿Cuáles serían y por qué?
2) Riesgo si NO se hacen
3) Cómo medir éxito
4) Plan B si falla
