FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles

# Create startup script
RUN echo '#!/bin/bash\npython manage.py migrate\npython manage.py collectstatic --noinput\npython manage.py runserver 0.0.0.0:${PORT:-8000}' > start.sh
RUN chmod +x start.sh

# Start the application
CMD ["./start.sh"]