# PreciosRegulados.uy 🇺🇾

[![CI/CD](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/ci.yml/badge.svg)](https://github.com/manusabbath-arch/cuantocuestauruguay/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Plataforma web para consultar y comparar precios regulados en Uruguay (combustibles, servicios e índices económicos) con datos oficiales actualizados.

## 📋 Descripción

PreciosRegulados.uy es una aplicación web de código abierto que proporciona acceso fácil y visual a los precios regulados en Uruguay. Los datos provienen de fuentes oficiales del gobierno uruguayo a través del [Catálogo de Datos Abiertos](https://catalogodatos.gub.uy).

### Características principales

- 📊 **Dashboard interactivo** con precios actuales y tendencias
- 📈 **Gráficos históricos** de evolución de precios
- 🔄 **Comparador** para analizar múltiples productos
- 📱 **Diseño responsive** optimizado para móviles
- 🔄 **Actualización automática** diaria mediante ETL
- 🔓 **API REST pública** con documentación OpenAPI

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Usuarios      │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Frontend │ (React + TypeScript)
    │(Cloudflare)│
    └────┬─────┘
         │ API REST
    ┌────▼─────┐
    │  FastAPI │ (Backend)
    │ (Railway)│
    └─┬──┬──┬──┘
      │  │  │
      │  │  └──► PostgreSQL
      │  │
      │  └─────► Scheduler (ETL diario)
      │
      └────────► CKAN API (catalogodatos.gub.uy)
```

### Stack Tecnológico

**Backend:**
- Python 3.11+
- FastAPI (API REST)
- PostgreSQL (base de datos)
- SQLAlchemy (ORM)
- Alembic (migraciones)
- APScheduler (tareas programadas)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (gráficos)
- React Query (estado servidor)

**Infraestructura:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Railway.app / Render.com (backend hosting)
- Cloudflare Pages (frontend hosting)

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

### Instalación con Docker

1. Clonar el repositorio:
```bash
git clone https://github.com/manusabbath-arch/cuantocuestauruguay.git
cd cuantocuestauruguay
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Levantar los servicios:
```bash
docker-compose up -d
```

4. Ejecutar migraciones de base de datos:
```bash
docker-compose exec backend alembic upgrade head
```

5. Cargar datos iniciales (ETL):
```bash
docker-compose exec backend python -c "from app.etl.combustibles import CombustiblesETL; from app.core.database import SessionLocal; import asyncio; db = SessionLocal(); etl = CombustiblesETL(db); asyncio.run(etl.run())"
```

La aplicación estará disponible en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Desarrollo Local

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar base de datos PostgreSQL local
createdb preciosregulados

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

La API REST está documentada con OpenAPI/Swagger. Una vez ejecutando el backend, visita:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints principales

- `GET /api/v1/productos` - Lista todos los productos
- `GET /api/v1/precios/{producto_id}` - Obtiene histórico de precios
- `GET /api/v1/variacion/{producto_id}` - Calcula variación porcentual
- `GET /api/v1/comparar` - Compara múltiples productos
- `GET /api/v1/estadisticas/{producto_id}` - Obtiene estadísticas

## 🧪 Tests

**Backend:**
```bash
cd backend
pytest tests/ -v --cov=app
```

**Frontend:**
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend (Railway.app)

1. Crear nuevo proyecto en Railway
2. Conectar repositorio de GitHub
3. Configurar variables de entorno
4. Railway detectará automáticamente el Dockerfile

### Frontend (Cloudflare Pages)

1. Conectar repositorio en Cloudflare Pages
2. Configurar:
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
3. Añadir variables de entorno: `VITE_API_URL`

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚖️ Licencia y Legal

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

### Fuentes de Datos

Los datos utilizados provienen del Catálogo de Datos Abiertos del Uruguay bajo la "Licencia de DAG de Uruguay", que permite uso comercial con atribución.

**Atribución requerida:** "Fuente: catalogodatos.gub.uy"

### Disclaimer

Los datos presentados provienen de fuentes oficiales (ANCAP, MEF, URSEA) y se actualizan periódicamente. PreciosRegulados.uy no se responsabiliza por decisiones tomadas en base a esta información. Para datos oficiales, consulte directamente las fuentes gubernamentales.

## 📞 Contacto

- GitHub Issues: [Reportar problema](https://github.com/manusabbath-arch/cuantocuestauruguay/issues)
- Email: [Contacto](mailto:contact@preciosregulados.uy)

## 🙏 Agradecimientos

- Gobierno de Uruguay por proporcionar datos abiertos
- Comunidad open source de Python y React
- Todos los contribuidores del proyecto

---

Hecho con ❤️ en Uruguay