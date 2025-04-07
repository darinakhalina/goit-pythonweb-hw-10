# Use a minimal Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

CMD ["/usr/local/bin/run.sh"]