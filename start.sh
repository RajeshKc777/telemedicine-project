#!/bin/bash

echo "Starting Railway deployment..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

if os.environ.get('DATABASE_URL'):
    url = urlparse(os.environ['DATABASE_URL'])
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                user=url.username,
                password=url.password,
                database=url.path[1:]
            )
            conn.close()
            print('Database connection successful!')
            break
        except Exception as e:
            retry_count += 1
            print(f'Database connection attempt {retry_count}/{max_retries} failed: {e}')
            time.sleep(2)
    
    if retry_count >= max_retries:
        print('Failed to connect to database after maximum retries')
        exit(1)
"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting Django application..."
exec gunicorn telemedicine.wsgi:application --bind 0.0.0.0:$PORT