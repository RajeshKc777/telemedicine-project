FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files and migrate
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Expose port
EXPOSE $PORT

# Start the application
CMD python manage.py runserver 0.0.0.0:$PORT