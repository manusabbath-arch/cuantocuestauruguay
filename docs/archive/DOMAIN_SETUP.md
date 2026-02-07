# Configuración del Dominio cuantocuestauruguay.com

## Estado Actual

- **Dominio adquirido**: cuantocuestauruguay.com
- **DNS configurado**: Cloudflare
- **Tiempo estimado de propagación**: 24-48 horas

## Próximos Pasos

### 1. Desplegar Backend en Railway.app

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas.

Resumen:
```bash
# 1. Crear proyecto en Railway.app conectando este repositorio
# 2. Configurar PostgreSQL
# 3. Ejecutar migraciones: railway run alembic upgrade head
# 4. Obtener URL del backend (ej: https://cuantocuestauruguay.up.railway.app)
```

### 2. Desplegar Frontend en Cloudflare Pages

1. Ir a Cloudflare Dashboard → Pages
2. Crear nuevo proyecto conectando este repositorio
3. Configurar build:
   - Build command: `cd frontend && npm install && npm run build`
   - Output: `frontend/dist`
   - Variable de entorno: `VITE_API_URL=<tu-backend-url>`

### 3. Configurar Dominio Personalizado en Cloudflare Pages

Una vez que los DNS estén propagados:

1. En Cloudflare Pages, ir a tu proyecto
2. Click en "Custom domains"
3. Agregar `cuantocuestauruguay.com` y `www.cuantocuestauruguay.com`
4. Cloudflare configurará automáticamente SSL

### 4. Actualizar CORS en Backend

Actualizar variable de entorno en Railway:
```
CORS_ORIGINS=https://cuantocuestauruguay.com,https://www.cuantocuestauruguay.com
```

## Estructura del Proyecto

```
cuantocuestauruguay/
├── backend/          # API FastAPI + ETL
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # React + TypeScript + Tailwind
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Desarrollo Local

```bash
# Levantar servicios con Docker
docker-compose up -d

# Acceder a:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Comandos Git Útiles

```bash
# Ver estado
git status

# Agregar cambios
git add .

# Commit
git commit -m "descripción del cambio"

# Push a GitHub
git push origin main

# Pull cambios remotos
git pull origin main
```

## Recursos

- [Guía de Despliegue](DEPLOYMENT.md)
- [Inicio Rápido](QUICKSTART.md)
- [Contribución](CONTRIBUTING.md)
- [Documentación Utilities ETL](UTILITIES_ETL.md)
