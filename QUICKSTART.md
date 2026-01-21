# Quick Start Guide - PreciosRegulados.uy

This guide will help you get the application running in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git installed

## Steps

### 1. Clone the Repository

```bash
git clone https://github.com/manusabbath-arch/cuantocuestauruguay.git
cd cuantocuestauruguay
```

### 2. Start the Application

```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker-compose up -d

# Wait about 30 seconds for services to initialize
```

### 3. Initialize the Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

### 4. Load Initial Data

```bash
# Execute ETL to load combustibles data
docker-compose exec backend python -c "
from app.etl.combustibles import CombustiblesETL
from app.core.database import SessionLocal
import asyncio

db = SessionLocal()
etl = CombustiblesETL(db)
result = asyncio.run(etl.run())
print(result)
db.close()
"
```

### 5. Access the Application

Open your browser and navigate to:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db
```

### Backend Issues

```bash
# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Frontend Issues

```bash
# View frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

## Manual API Testing

Once running, you can test the API:

```bash
# Get all products
curl http://localhost:8000/api/v1/productos

# Get latest price for a product
curl http://localhost:8000/api/v1/precios/1/ultimo

# Calculate monthly variation
curl http://localhost:8000/api/v1/variacion/1?periodo=mes
```

## Development Mode

For active development:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Check out the comparador at http://localhost:3000/comparador
3. View detailed product information on individual product pages
4. Read the full README.md for deployment and contribution guidelines

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Open an issue on GitHub if you encounter problems
- Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide

Happy coding! 🇺🇾
