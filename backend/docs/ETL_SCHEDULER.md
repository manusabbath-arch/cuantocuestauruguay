# Scheduler de ETL - Documentación

## Descripción General

El sistema de scheduler automatiza la ejecución periódica de los procesos ETL para mantener actualizados los datos de precios regulados en Uruguay.

## Configuración

### Variables de Entorno

El scheduler se configura mediante las siguientes variables en el archivo `.env`:

```bash
# Hora de ejecución diaria (24-hour format)
ETL_SCHEDULE_HOUR=2
ETL_SCHEDULE_MINUTE=0

# Modo debug (ejecuta ETL al iniciar la app)
DEBUG=True
```

### Horario de Ejecución

- **Producción**: El ETL se ejecuta automáticamente todos los días a las 2:00 AM UTC
- **Desarrollo**: Además de la ejecución programada, el ETL se ejecuta al iniciar la aplicación cuando `DEBUG=True`

## Componentes

### 1. Scheduler (`app/scheduler.py`)

Utiliza APScheduler para gestionar tareas periódicas:

- **`run_etl_job()`**: Función principal que ejecuta todos los ETLs
- **`start_scheduler()`**: Inicia el scheduler con las tareas configuradas
- **`stop_scheduler()`**: Detiene el scheduler de forma segura

### 2. Integración con FastAPI (`app/main.py`)

El scheduler se integra con el ciclo de vida de FastAPI mediante `lifespan`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar scheduler
    start_scheduler()
    yield
    # Detener scheduler al cerrar
    stop_scheduler()
```

### 3. ETLs Implementados

#### Combustibles
- **Fuente**: CKAN API - catalogodatos.gub.uy
- **Productos**: Nafta Premium 97, Nafta Súper 95, Gasoil 50-S, Gasoil Común, Supergás
- **Frecuencia de actualización**: Diaria
- **Método de inserción**: Individual con verificación de duplicados

#### UTE (Electricidad)
- **Fuente**: Portal UTE (datos aproximados actualizables)
- **Productos**: Tarifas Residenciales BT1/BT2, General BT3, Industrial
- **Frecuencia de actualización**: Diaria con fecha actual
- **Método de inserción**: Individual con verificación de duplicados

#### OSE (Agua)
- **Fuente**: Datos de ejemplo (pendiente implementación real)
- **Productos**: Tarifas Residencial, Comercial
- **Estado**: Estructura lista para datos reales

#### Antel (Telecomunicaciones)
- **Fuente**: Datos de ejemplo (pendiente implementación real)
- **Productos**: Fibra Óptica 100/200/500 Mbps, Plan Móvil
- **Estado**: Estructura lista para datos reales

## Endpoints de Monitoreo

### GET `/api/v1/etl/status`

Obtiene el estado del scheduler y próximas ejecuciones.

**Respuesta de ejemplo:**
```json
{
    "scheduler_running": true,
    "jobs": [
        {
            "id": "etl_daily_job",
            "name": "Daily ETL Job - Combustibles & Utilities",
            "next_run_time": "2026-01-27T02:00:00+00:00",
            "trigger": "cron[hour='2', minute='0']"
        }
    ],
    "available_services": ["combustibles", "ute", "ose", "antel"]
}
```

### GET `/api/v1/etl/debug/db-stats`

Estadísticas de la base de datos para monitoreo.

**Respuesta de ejemplo:**
```json
{
    "productos_por_categoria": {
        "agua": 2,
        "telecomunicaciones": 4,
        "electricidad": 4,
        "combustible": 5
    },
    "total_precios": 103,
    "precios_por_producto": {
        "Gasoil 50-S": 28,
        "Nafta Premium 97": 28,
        ...
    }
}
```

### POST `/api/v1/etl/run-all`

Ejecuta manualmente todos los ETLs (sin esperar al horario programado).

## Logs y Monitoreo

### Logs del Scheduler

El scheduler genera logs detallados de cada ejecución:

```
2026-01-26 16:00:00 - app.scheduler - INFO - ================================================================================
2026-01-26 16:00:00 - app.scheduler - INFO - Starting scheduled ETL job at 2026-01-26T16:00:00
2026-01-26 16:00:00 - app.scheduler - INFO - ================================================================================
2026-01-26 16:00:05 - app.etl.combustibles - INFO - Extracted 1000 records
2026-01-26 16:00:06 - app.etl.combustibles - INFO - Successfully loaded 95 records
...
```

### Métricas a Monitorear

1. **`records_extracted`**: Cantidad de registros obtenidos de la fuente
2. **`records_loaded`**: Cantidad de registros nuevos insertados en BD
3. **Tiempo de ejecución**: Duración total del proceso ETL
4. **Errores**: Excepciones o fallos durante la ejecución

## Manejo de Duplicados

Todos los ETLs implementan verificación de duplicados antes de insertar:

```python
existing = (
    db.query(Precio)
    .filter(Precio.producto_id == producto.id, Precio.fecha == fecha)
    .first()
)

if existing:
    logger.info(f"Skipping existing price for {producto_nombre} on {fecha}")
    continue
```

Esto evita:
- Violaciones de constraints únicos
- Duplicación de datos históricos
- Errores en bulk inserts

## Mejoras Futuras

### Corto Plazo
1. Implementar extracción real para OSE desde URSEA
2. Implementar extracción real para Antel desde su portal
3. Implementar scraping con JavaScript para UTE (Selenium/Playwright)
4. Añadir alertas por email/Slack en caso de fallos

### Mediano Plazo
1. Sistema de retry automático para ETLs fallidos
2. Dashboard de monitoreo con histórico de ejecuciones
3. Notificaciones cuando `records_loaded = 0` por varios días
4. Métricas de calidad de datos (validaciones, outliers)

### Largo Plazo
1. ETL para más categorías (transporte, medicamentos, etc.)
2. Machine Learning para predicción de precios
3. API para suscripciones y alertas de cambios de precio
4. Integración con más fuentes de datos gubernamentales

## Troubleshooting

### El scheduler no arranca

**Problema**: El scheduler no se ejecuta al iniciar la app.

**Solución**:
1. Verificar logs de inicio en Render
2. Confirmar que `start_scheduler()` se llama en `lifespan`
3. Revisar que APScheduler esté instalado: `pip show apscheduler`

### ETL ejecuta pero no carga datos

**Problema**: `records_loaded: 0` en todas las ejecuciones.

**Soluciones**:
1. Verificar que los datos de origen no hayan cambiado de estructura
2. Revisar logs para identificar qué paso falla (extract/transform/load)
3. Ejecutar endpoint de debug: `/api/v1/etl/debug/test-combustibles`
4. Verificar que los nombres de productos mapeen correctamente

### Problemas de memoria en Render

**Problema**: El scheduler consume mucha memoria en el tier gratuito.

**Soluciones**:
1. Procesar datos en chunks más pequeños
2. Liberar memoria después de cada ETL: `df = None; gc.collect()`
3. Usar `db.flush()` en lugar de acumular todas las inserciones

## Contacto y Soporte

Para consultas sobre el scheduler:
- Email: [configurar email de contacto]
- Issues: GitHub repository

---

**Última actualización**: 26 de enero de 2026
**Versión**: 1.0.0
