# Tickets Técnicos (Enero 2026)

## TKT-001: ETL Combustibles v2 — Robustecer parsing CSV (BOM/;)
- Estado: Implementado
- Archivos:
  - backend/packages/ckan_client/client.py
  - backend/app/etl/combustibles_v2.py
- Cambios:
  - Lectura CSV con `encoding='utf-8-sig'`, autodetección de delimitador y fallback a `sep=';'`.
  - Detección de columna fecha ampliada: `año-mes`, `ano-mes`, variantes.
- Pruebas sugeridas:
  - Ejecutar scheduler en dev y verificar inserciones sin errores.
  - Validar que `fecha` se parsea (yyyy-mm) y no se generan filas nulas.

## TKT-002: Feature Flags — Desactivar canary combustibles
- Estado: Implementado
- Archivo: backend/feature_flags_config.json
- Cambios: `phase: disabled`, `enabled: false`, `v2_percentage: 0` para `combustibles`.
- Pruebas sugeridas:
  - Reiniciar backend y confirmar que no se enruta a v2 en canary.
  - Verificar logs de shadow si aplica.

## TKT-003: Analytics eventos clave
- Estado: Implementado (base)
- Archivos:
  - frontend/src/lib/analytics.ts (helper GA)
  - frontend/src/App.tsx (pageview por ruta)
  - frontend/src/components/Layout.tsx (nav_click)
  - frontend/src/pages/Contacto.tsx (email_submit_* )
- Pendientes:
  - Definir `VITE_GA_MEASUREMENT_ID` real y/o migrar a Plausible.
  - Instrumentar `comparacion_realizada` en `pages/Comparador.tsx` cuando se termine el flujo. ✅ Implementado
  - Añadir `share_click` cuando haya botones de compartir.
- Pruebas sugeridas:
  - Navegar y observar hits en GA/Plausible en tiempo real (debug view).

## Pasos de Verificación
1. Levantar backend y frontend en dev.
2. Forzar ejecución de ETL combustibles en local (o esperar scheduler) y revisar logs.
3. Navegar la app, enviar un formulario de contacto y verificar eventos en analytics.
4. Visitar `/precio-nafta-hoy` y validar JSON-LD y eventos de `share_click`.

## TKT-004: Página SEO "Precio Nafta HOY"
- Estado: Implementado
- Archivos:
  - frontend/src/pages/PrecioNaftaHoy.tsx
  - frontend/src/App.tsx (nueva ruta `/precio-nafta-hoy`)
- Detalles:
  - Consulta productos de Combustibles y muestra último precio y variación 30 días para Súper 95 y Premium 97.
  - Incluye JSON-LD tipo FAQPage y CTA de compartir.

## TKT-005: Caché ligero en endpoints calientes
- Estado: Implementado
- Archivo: backend/app/routers/precios.py
- Detalles:
  - Caché en memoria con TTL para `GET /productos`, `GET /precios/{id}/ultimo` (600s) y `GET /comparar` (900s).
  - Reduce latencia y carga en DB.

## Notas
- Cualquier ajuste de naming de eventos centralizar en `analytics.ts`.
- Si persisten problemas de CSV, considerar `pd.read_csv(..., dtype=str)` y conversión explícita de columnas.
