# Stage 1: Base Image (deps only)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_HTTP_TIMEOUT=300
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /opt/base

# Dependency manifests only
COPY pyproject.toml uv.lock ./

# Install Python deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r uv.lock --system --no-cache


# Stage 2: App Image
FROM eswardudi/veritas-base:latest AS app

WORKDIR /backend

COPY . .

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
