# Dockerfile multi-stage — ajuste según lenguaje
# Python example:
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --user --no-cache-dir ruff mypy pytest pre-commit

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser config.yaml pyproject.toml RULES.md ./
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app/data /app/logs
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
CMD ["python3", "scripts/audit-standards.py", "--help"]
