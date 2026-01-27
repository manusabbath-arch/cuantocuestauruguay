# URSEA Tariff PDF Storage

Este directorio almacena archivos PDF de tarifas reguladas descargados manualmente desde URSEA.

## Estructura

```
pdfs/
├── ute/          # Tarifas de UTE (Administración Nacional de Usinas y Trasmisiones Eléctricas)
├── ose/          # Tarifas de OSE (Obras Sanitarias del Estado)
└── antel/        # Tarifas de Antel (Administración Nacional de Telecomunicaciones)
```

## Proceso de Actualización

### 1. Descargar PDFs

Visita el sitio de **URSEA** (Unidad Reguladora de Servicios de Energía y Agua):
- **URL**: https://www.ursea.gub.uy/

En el menú principal, busca las secciones para cada servicio:
- **UTE**: "Energía Eléctrica" → "Tarifas"
- **OSE**: "Agua Potable" → "Tarifas"
- **Antel**: "Telecomunicaciones" → "Tarifas"

### 2. Nomenclatura de Archivos

Usa el siguiente formato para nombrar los archivos:
- UTE: `ute_tarifas_2024_12.pdf` (año_mes)
- OSE: `ose_tarifas_2024_12.pdf`
- Antel: `antel_tarifas_2024_12.pdf`

### 3. Colocar en Directorio

Coloca el PDF en la carpeta correspondiente:
```bash
mv ute_tarifas_2024_12.pdf backend/pdfs/ute/
```

### 4. Procesamiento Automático

El ETL ejecutará automáticamente:
1. **Escanea** `backend/pdfs/{ute,ose,antel}/` en cada ejecución
2. **Parsea** tablas de tarifas usando pdfplumber
3. **Extrae** valores, fechas de vigencia, y fuentes
4. **Almacena** en la base de datos con marca de auditoría

Ejemplo de logs esperados:
```
INFO: Successfully parsed 5 records from PDF: ute_tarifas_2024_12.pdf
INFO: Extracted UTE tarifas (source: URSEA - PDF parsed 2024-12-15)
```

### 5. Fallback a Datos Históricos

Si no se encuentra PDF para una fecha:
- El sistema usa **TARIFF_HISTORY** (datos verificados históricos)
- Se registra: `"fuente": "URSEA - Historical (verified)"`
- Garantiza continuidad de datos sin interrupciones

## Formato de Datos Extraídos

Los PDFs deben contener tablas con al menos estas columnas:
| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Producto/Plan | Nombre del plan tarifario | "Fibra 100 Mbps" |
| Valor/Tarifa | Precio en pesos uruguayos | "1.299,99" |
| Vigencia | Fecha de validez | "01/01/2024" |

## Frecuencia de Actualización

- **Recomendado**: Mensual (primer día del mes)
- **Máximo**: 30 días sin actualización (se puede tolerar)
- **Crítico**: Si > 60 días sin PDF, revisar cambios regulatorios

## Troubleshooting

### PDF no se parsea correctamente
- Verifica que la tabla tenga encabezados claros
- Intenta con un PDF más reciente (URSEA puede cambiar formato)
- Revisa los logs: `docker logs backend`

### Falta producto en extracción
- El PDF debe tener coincidencias con palabras clave:
  - **UTE**: "tarifa", "kwh", "kwh/mes", "$"
  - **OSE**: "tarifa", "m³", "metro cúbico", "$"
  - **Antel**: "tarifa", "mbps", "velocidad", "$"

### ¿Cómo sé si está funcionando?
1. Revisa el endpoint de alertas: `GET /api/v1/etl/alerts`
2. Busca logs: `"Successfully parsed X records from PDF"`
3. Verifica BD: `SELECT * FROM precios WHERE fuente LIKE 'URSEA - PDF%'`

## Archivos de Ejemplo

Actualmente no hay PDFs en el repositorio. Para las pruebas iniciales:
1. Descarga el PDF más reciente desde URSEA
2. Coloca en la carpeta correspondiente
3. Ejecuta el ETL: `POST /api/v1/etl/execute`
4. Verifica resultados en `/api/v1/etl/alerts`

## Notas de Seguridad

- Los PDFs se **almacenan localmente**, no se envían a terceros
- Los datos extraídos se **validan** antes de almacenar en BD
- La **auditoría completa** (fecha extracción, fuente, versión) se mantiene
- Sin PDFs disponibles, el sistema mantiene **integridad data** con valores históricos verificados
