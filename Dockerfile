# ======================
# Base build
# ======================
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (for layer caching)
COPY requirements/ ./requirements/

# ======================
# Production image
# ======================
FROM base AS prod

# Install only production dependencies
RUN pip install -r requirements/prod.txt

# Copy application code
COPY . .

ENV DJANGO_SETTINGS_MODULE=core.settings.prod

# Default command for prod
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

# ======================
# Development image
# ======================
FROM base AS dev

# Install development dependencies
RUN pip install -r requirements/dev.txt

# Copy application code
COPY . .

ENV DJANGO_SETTINGS_MODULE=core.settings.dev

# Expose pprts for development server
EXPOSE 8000

# Default command for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
