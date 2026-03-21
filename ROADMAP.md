# Roadmap — PreciosRegulados.uy / CuantoCuestaUruguay

**Última actualización:** Marzo 2026
**Visión:** Convertir `cuantocuestauruguay.com` en el dashboard de referencia de datos públicos de Uruguay — precios regulados, gasto fiscal, e indicadores económicos, con fuentes oficiales verificables.

---

## Estado actual (baseline)

### Lo que está en producción hoy

| Componente | Estado | Notas |
|-----------|--------|-------|
| ETL combustibles ANCAP (CKAN API) | ✅ Producción | Paginado, histórico, scheduler diario |
| Tarifas UTE / OSE / Antel | ⚠️ Parcial | Datos hardcodeados en `TARIFF_HISTORY`, scraper URSEA existe pero no es fuente primaria |
| API REST FastAPI | ✅ Producción | Endpoints precios, productos, comparador |
| Frontend React | ✅ Producción | Home, comparador, MiFactura, servicios |
| Scheduler APScheduler | ✅ Producción | ETL diario 02:00 UTC |
| Analizador de facturas UTE | ✅ Producción | `MiFactura.tsx` + `bill_parsers/` |
| Índices económicos (IPC, BCU) | ❌ No existe | Categoría `indice` en DB sin ETL |
| Gasto público MEF | ❌ No integrado | Extractor funcional en repo fiscalizador |
| Indicadores inmobiliarios | ❌ No existe | Fuentes identificadas (INE IAI, DNC) |
| Tests del ETL | ❌ Ausentes | ETL en producción sin cobertura |

### Gaps críticos identificados

1. **Tarifas utilities desactualizadas** — `TARIFF_HISTORY` con valores manuales que se desactualizan silenciosamente
2. **Sin índices económicos** — el modelo de DB los soporta pero no hay ETL
3. **Sin datos de gasto público** — el diferenciador más fuerte vs. sitios similares
4. **Sin tests de ETL** — el único ETL en producción no tiene cobertura
5. **Sin "última actualización" visible** — genera desconfianza en los datos

---

## Capa 1 — Precios y costo de vida (ya existe, mejorar)

Fuente base: `catalogodatos.gub.uy` (CKAN API) + URSEA PDFs

### P1-A: Automatizar tarifas utilities desde URSEA
**Problema:** `TARIFF_HISTORY` en `utilities.py` es un dict manual con valores estimados. Si UTE cambia tarifas (cada ~6 meses), los datos muestran valores incorrectos sin notificación.

**Solución:** Hacer del scraper de PDF URSEA la fuente primaria, con `TARIFF_HISTORY` como fallback.

**Archivos a modificar:**
- `backend/app/etl/utilities.py` — activar `parse_ute_tariff_pdf()` y `parse_ose_tariff_pdf()` como fuente primaria
- `backend/app/etl/pdf_parser.py` — validar parsing actual de PDFs URSEA
- `backend/app/services/scheduler.py` — ajustar frecuencia utilities (semanal es suficiente)

**URL fuente:** `https://www.gub.uy/unidad-reguladora-servicios-energia-agua/`

---

### P1-B: ETL de índices económicos (IPC, dólar BCU)
**Estado actual:** El modelo `Producto` tiene `categoria='indice'` pero no hay ningún ETL que lo alimente.

**Fuentes disponibles (CKAN, gratuitas):**
- IPC mensual INE: `catalogodatos.gub.uy`
- Tipo de cambio BCU: `catalogodatos.gub.uy/dataset/tipo-de-cambio`
- Salario nominal: disponible en CKAN

**Implementación:** Nuevo `IndicesETL` siguiendo el patrón de `CombustiblesETL` — aprox. 80 líneas.

**Archivos a crear:**
- `backend/app/etl/indices.py`
- Agregar job mensual en `backend/app/services/scheduler.py`

---

### P1-C: Indicador "última actualización" en frontend
**Problema:** El usuario no sabe si los precios son de hoy o de hace 3 meses.

**Implementación:** Agregar campo `fecha` visible en cada `PriceCard`. El campo ya existe en el modelo `Precio`.

**Archivos a modificar:**
- `frontend/src/components/PriceCard.tsx`
- `backend/app/models/schemas.py` — asegurar que `fecha` se expone en la respuesta

---

## Capa 2 — Gasto público MEF (nuevo)

Diferenciador único: ningún sitio uruguayo muestra ejecución presupuestal de forma accesible.

### P2-A: Integrar extractor MEF
El extractor ya existe y funciona en `bot-fiscalizador-gastos-publicos-Uruguay/extractors/extractor_mef.py`. Solo necesita portarse al pipeline de cuantocuestauruguay.

**Fuentes oficiales:**
- Rendición de Cuentas PDF Tomo III: `gub.uy/ministerio-economia-finanzas/`
- Portal Presupuesto Abierto: `presupuestouruguay.gub.uy/`
- CKAN MEF: `catalogodatos.gub.uy/organization/ministerio-de-economia-y-finanzas`

**Archivos a crear:**
- `backend/app/etl/gasto_publico.py` — adaptar `MEFExtractor` + `cleaner_mef.py`
- `backend/app/models/models.py` — nuevo modelo `EjecucionPresupuestal`
- `backend/app/routers/gasto.py` — endpoints por ministerio, período, comparación YoY
- `frontend/src/pages/GastoPublico.tsx` — nueva página con barras por ministerio

**Datos a mostrar:**
- Ejecución presupuestal por ministerio (% del presupuesto ejecutado)
- Comparación vs. período anterior
- Fuente citada explícitamente (credibilidad)

---

### P2-B: API Presupuesto Abierto como complemento
`presupuestouruguay.gub.uy` ofrece datos más granulares que el PDF Tomo III. Evaluar como fuente secundaria para datos más frecuentes.

---

## Capa 3 — Mercado inmobiliario (futuro próximo)

Fuentes públicas confirmadas y gratuitas:

| Fuente | Dato | API | Frecuencia |
|--------|------|-----|-----------|
| INE IAI Compraventa | Índices precios/operaciones | CSV/JSON CKAN | Mensual |
| DNC Catastro | Valores catastrales, geometría parcelaria | REST/SHP | Mensual |
| MercadoLibre API | Listados actuales en venta | JSON REST | Tiempo real |

**Limitación conocida:** No existen datos públicos de precios de transacciones individuales (DGR los tiene pero no los publica). La Capa 3 se enfoca en índices agregados (INE) + oferta actual (MercadoLibre).

### P3-A: ETL INE IAI (índice mensual compraventa)
Primer paso de Capa 3. Dataset limpio, formato estándar CKAN, actualización mensual.

**Archivos a crear:**
- `backend/app/etl/inmobiliario.py`
- `frontend/src/pages/Inmobiliario.tsx`

---

## Deuda técnica prioritaria

### DT-1: Tests del ETL de combustibles
El único ETL en producción sin ningún test. Si CKAN cambia un campo o el formato, falla silenciosamente.

**Archivos a crear:**
- `tests/etl/test_combustibles.py` — mockear respuesta CKAN, validar transformación
- `tests/etl/test_utilities.py` — validar parsing de tarifas

**Cobertura mínima objetivo:** funciones `extract()`, `transform()`, `load()` de cada ETL.

---

### DT-2: Migración ARCH-002 pendiente
El roadmap anterior dejó pendiente migrar los ETLs a la arquitectura de packages compartidos (`ETLBase`, `CkanClient`). `combustibles_v2.py` existe pero no está en producción.

**Acción:** Testear en staging y hacer deploy gradual con shadow mode.

---

### DT-3: Alertas de fallo ETL
`alerts.py` existe pero no está claro si notifica fallos de jobs ETL (excepciones) vs. solo cambios de precios. Si el job falla a las 2:00 AM, nadie se entera.

**Acción:** Agregar notificación (Telegram o email) cuando un job ETL lanza excepción.

---

## Backlog sin fecha

- Dark mode — `localStorage` + clases Tailwind
- Export a CSV/PNG desde los gráficos
- Plausible Analytics en reemplazo de Google Analytics (privacidad)
- PWA / Service Worker para uso offline
- API pública con keys para consumo externo controlado
- Staging environment — rama `develop` → deploy preview

---

## Orden de implementación recomendado

```
Sprint 1 (1-2 semanas)
  P1-C  Indicador "última actualización" → impacto visual inmediato, ~2h
  DT-1  Tests ETL combustibles → deuda técnica bloqueante para escalar
  P1-B  ETL índices IPC/BCU → completa la propuesta de valor Capa 1

Sprint 2 (2-4 semanas)
  P1-A  Automatizar tarifas URSEA → elimina riesgo de datos incorrectos
  P2-A  Integrar extractor MEF → diferenciador único, extractor ya listo

Sprint 3 (1-2 meses)
  P3-A  ETL INE IAI inmobiliario → primera pieza de Capa 3
  DT-2  Migración ARCH-002 → deuda técnica arquitectural
  DT-3  Alertas de fallo ETL → observabilidad en producción
```

---

## Fuentes de datos de referencia

| Fuente | URL | Formato | Actualización |
|--------|-----|---------|--------------|
| CKAN Datos Abiertos UY | `catalogodatos.gub.uy/api/3/action` | API REST JSON | Variable |
| ANCAP combustibles | CKAN resource `62bacbab-9bae-4316-af56-7c1bf468f546` | API REST | Semanal |
| URSEA tarifas | `gub.uy/unidad-reguladora-servicios-energia-agua/` | PDFs | Semestral |
| INE IPC | `catalogodatos.gub.uy` | CSV/JSON | Mensual |
| BCU tipo de cambio | `catalogodatos.gub.uy` | CSV/JSON | Diaria |
| INE IAI Compraventa | `ine.gub.uy/actividad-inmobiliaria` | CSV/JSON | Mensual |
| DNC Catastro | `gis.catastro.gub.uy/arcgis/rest/services/` | REST/SHP | Mensual |
| MEF Rendición de Cuentas | `gub.uy/ministerio-economia-finanzas/` | PDF | Anual |
| Portal Presupuesto Abierto | `presupuestouruguay.gub.uy/` | Descarga | Mensual |
| MercadoLibre API | `developers.mercadolibre.com.uy/` | JSON REST | Tiempo real |
