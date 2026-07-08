# knowledge-base-mcp-server — independently deployable Pulse service.
FROM python:3.12-slim

# uv for dependency management.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for layer caching (package = false → deps only).
COPY pyproject.toml ./
RUN uv sync

# Application source.
COPY src ./src
ENV PYTHONPATH=/app/src

EXPOSE 8100

# Config is injected at runtime (env_file / -e); never baked into the image.
CMD ["uv", "run", "uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8100"]
