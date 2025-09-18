# syntax=docker/dockerfile:1.7-labs

# Base image with Python 3.12
FROM python:3.12-slim AS runtime

# Install system dependencies (curl for fetching uv, build deps for aiodns if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

# Set work directory
WORKDIR /app

# Copy only dependency manifests first for better caching
COPY pyproject.toml uv.lock /app/

# Create virtualenv and sync deps (production only)
RUN uv sync --frozen --no-install-project

# Copy the rest of the project
COPY . /app

# Ensure the app listens on 0.0.0.0:8080 (as per README)
EXPOSE 8080

# Create a non-root user and set permissions
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Optional healthcheck using curl to verify the HTTP endpoint is reachable
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8080/ || exit 1

# Default command: run the application via uv's virtualenv
# Using `uv run` locates the env created by `uv sync` and runs with it
CMD ["uv", "run", "main.py"]
