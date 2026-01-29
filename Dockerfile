FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles

# Expose port
EXPOSE $PORT

# Start the application with migrations
CMD python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:$PORT