# Railway Deployment Configuration

Este proyecto está configurado para desplegarse en Railway.app.

## Archivos de Configuración

- **railway.toml**: Configuración principal de Railway
- **Procfile**: Configuración alternativa para el proceso web
- **backend/start.sh**: Script de inicio que ejecuta migraciones y arranca el servidor

## Variables de Entorno Requeridas

Configurar en Railway Dashboard → Variables:

```
DATABASE_URL=<auto-configurado por Railway PostgreSQL>
PORT=<auto-configurado por Railway>
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://cuantocuestauruguay.com
CKAN_API_URL=https://catalogodatos.gub.uy/api/3/action
CKAN_COMBUSTIBLES_RESOURCE_ID=62bacbab-9bae-4316-af56-7c1bf468f546
PROJECT_NAME=PreciosRegulados.uy
DEBUG=False
API_V1_PREFIX=/api/v1
ETL_SCHEDULE_HOUR=2
ETL_SCHEDULE_MINUTE=0
```

## Despliegue

### Primera vez:

1. Conectar repositorio de GitHub a Railway
2. Railway detectará automáticamente el `railway.toml`
3. Agregar PostgreSQL desde Railway Dashboard
4. Configurar variables de entorno
5. El despliegue se ejecutará automáticamente

### Posteriores despliegues:

Cada push a la rama `main` dispara un despliegue automático.

## Troubleshooting

### Build failed - Script not found
- Verificar que `railway.toml` esté en la raíz del proyecto
- Verificar que `backend/start.sh` tenga permisos de ejecución

### Database connection failed
- Verificar que PostgreSQL esté agregado al proyecto
- Verificar variable `DATABASE_URL`

### Migraciones fallan
- Ejecutar manualmente: `railway run alembic upgrade head`
- O desde Railway CLI: `railway shell` y luego ejecutar comandos

## Comandos Útiles

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Vincular proyecto
railway link

# Ver logs
railway logs

# Ejecutar comando en Railway
railway run <comando>

# Abrir shell en Railway
railway shell
```
