#!/bin/bash
set -e

echo "🚀 Starting PreciosRegulados.uy backend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
python -c "
import time
import psycopg2
from urllib.parse import urlparse
import os

db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Parse DATABASE_URL
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port
            )
            conn.close()
            print('✅ Database is ready!')
            break
        except psycopg2.OperationalError:
            if i < max_retries - 1:
                print(f'⏳ Database not ready, waiting... ({i+1}/{max_retries})')
                time.sleep(2)
            else:
                print('❌ Could not connect to database')
                exit(1)
"

# Run migrations
echo "📦 Running database migrations..."
cd /app
alembic upgrade head

echo "✅ Migrations completed!"

# Start the application
echo "🎯 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
