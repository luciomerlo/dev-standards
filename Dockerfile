# Dockerfile multi-stage — ajuste según lenguaje
# Python example:
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --user --no-cache-dir -e ".[dev]"

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config.yaml pyproject.toml ./
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app/data /app/logs
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import httpx; httpx.get('http://localhost:8080/health', timeout=5)" || exit 1
CMD ["python", "-m", "PROJECT_NAME"]
