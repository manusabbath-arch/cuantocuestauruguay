# Tarifas OSE (Agua y Saneamiento)

Este directorio contiene documentos PDF con las tarifas vigentes de Obras Sanitarias del Estado (OSE).

## Actualización de Tarifas

### Fuente Oficial
- **URSEA (Ente Regulador de Servicios de Agua)**: https://www.ursea.gub.uy/inicio/agua-y-saneamiento/tarifas/
- **Documentos históricos**: https://www.ose.com.uy/tarifas

### Procedimiento de Actualización

1. **Descargar documento PDF más reciente** desde URSEA
2. **Renombrar según convención**: `ose_tarifas_YYYY_MM.pdf`
   - Ejemplo: `ose_tarifas_2026_01.pdf` para Enero 2026
3. **Guardar en este directorio** (`backend/pdfs/ose/`)
4. **Ejecutar ETL** para extraer tarifas automáticamente:
   ```bash
   cd backend
   PYTHONPATH=. python3 -c "
   import asyncio
   from app.core.database import SessionLocal
   from app.etl.ose_v2 import OSEETLv2
   
   db = SessionLocal()
   result = asyncio.run(OSEETLv2(db).run())
   print(result)
   "
   ```

### Formato del PDF

El parser busca automáticamente:
- Tablas con columnas "Concepto", "Valor", "Costo"
- Categorías: "Residencial" o "Comercial"
- Formato de moneda: `$ XX.XX` (con punto decimal)

**Nota**: Si el PDF no se puede parsear automáticamente, el ETL utiliza `TARIFF_HISTORY` como fallback (ver `ose_v2.py`).

### Historial de Actualizaciones

| Documento | Período | Residencial (m³) | Comercial (m³) | Estado |
|-----------|---------|------------------|----------------|--------|
| ose_tarifas_2026_01.pdf | Enero 2026 | $47.60 | $88.25 | ❓ (Necesario) |
| ose_tarifas_2021_04.pdf | Abril 2021 | (datos desactualizados) | (datos desactualizados) | ⚠️ Obsoleto |

## Integración con ETL

El proceso automático de ETL (`ose_v2.py`):

1. **Extract**: Busca PDFs en este directorio
2. **Parse**: Intenta extraer tarifas con `parse_ose_tariff_pdf()`
3. **Fallback**: Si no encuentra datos válidos, usa `TARIFF_HISTORY`
4. **Load**: Crea registros en la base de datos

Ver `backend/app/etl/ose_v2.py` para detalles técnicos.

---

**Última actualización**: 28 de enero de 2026
**Mantenedor**: Proyecto CuantoCuestaUruguay
