#!/usr/bin/env bash
# bootstrap-project.sh — Scaffolding estándar para nuevos repositorios (RULES.md §5.6)
# Uso:  bash bootstrap-project.sh [--lang python|node|go|rust] [--name "Mi Proyecto"] [--desc "Descripción breve"]
#                                 [--apikeys-catalog RUTA/APIKEYS.env]
#       Se ejecuta DENTRO de la carpeta del nuevo repo (git init ya hecho).

set -euo pipefail

LANG="python"
PROJECT_NAME=""
PROJECT_DESC=""
REPO_ROOT="$(pwd)"
TODAY="$(date +%Y-%m-%d)"   # RULES.md §5.11: fecha "Last updated" de README y wiki/
# RULES.md §6.5: catálogo central de API keys (LocalProjectsTracker). Solo se leen NOMBRES.
APIKEYS_CATALOG="${APIKEYS_CATALOG:-}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --lang) LANG="$2"; shift 2 ;;
    --name) PROJECT_NAME="$2"; shift 2 ;;
    --desc) PROJECT_DESC="$2"; shift 2 ;;
    --apikeys-catalog) APIKEYS_CATALOG="$2"; shift 2 ;;
    *) echo "Opción desconocida: $1"; exit 1 ;;
  esac
done

if [[ -z "$PROJECT_NAME" ]]; then
  PROJECT_NAME="$(basename "$REPO_ROOT")"
fi

if [[ -z "$PROJECT_DESC" ]]; then
  PROJECT_DESC="Proyecto generado con dev-standards bootstrap"
fi

echo "🚀  Bootstrap: $PROJECT_NAME ($LANG)"

# 1) .gitignore
cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Node
node_modules/
dist/
build/
*.log

# Go
vendor/
*.exe
*.test

# Rust
target/
Cargo.lock

# Entornos
.env
.venv
venv/
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Datos y artefactos
data/
*.db
*.sqlite
*.duckdb
*.parquet
*.arrow
*.bin
*.model
*.pth
*.onnx
*.safetensors

# Docker
.docker/
EOF

# 2) README.md plantilla con badges, diagrama Mermaid y checklist
cat > README.md <<EOF
# $PROJECT_NAME

_Last updated: ${TODAY}_

$PROJECT_DESC

<!-- Badges — actualiza los enlaces a tu repo real -->
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/github/v/release/OWNER/REPO?label=version)
![License](https://img.shields.io/github/license/OWNER/REPO)
![Coverage](https://img.shields.io/codecov/c/github/OWNER/REPO)

## Arquitectura

\`\`\`mermaid
graph TD
  A[Config.yaml (SSoT)] --> B[Generator / Core]
  B --> C[Async Pipeline + Retry/Backoff]
  C --> D[Fallback Chain Multi-Model]
  D --> E[Streaming Output]
  E --> F[Progress + status.json]
  F --> G[Observabilidad]
\`\`\`

## Capturas

<!-- RULES.md §5.5(c): capturas generadas con iris (https://github.com/brijr/iris), guardadas en docs/screenshots/.
     iris --full -o docs/screenshots/ http://localhost:8080
     Luego reemplazar este comentario por: ![Pantalla principal](docs/screenshots/<archivo>.png) -->

## Instalación

\`\`\`bash
# Python
pip install -e .

# Node
npm ci

# Go
go build ./...

# Rust
cargo build --release
\`\`\`

## Uso rápido

\`\`\`bash
# Python
python -m $PROJECT_NAME --help

# Node
npx $PROJECT_NAME --help

# Go
./$PROJECT_NAME --help

# Rust
cargo run -- --help
\`\`\`

## Configuración

Copie \`.env.example\` a \`.env\` y ajuste las variables:

\`\`\`bash
cp .env.example .env
\`\`\`

La configuración central vive en \`config.yaml\` (Single Source of Truth).

### API keys disponibles (RULES.md §6.5)

\`.env.example\` lista como opciones comentadas todas las API keys del catálogo central
(repo privado \`luciomerlo/LocalProjectsTracker\`, ver \`HOWTOUSEAPIS.MD\`). Agregue las que use
el proyecto a \`APIKEYS_MATCH\` y genere \`.env\` desde LocalProjectsTracker:

\`\`\`bash
python main.py --target-dir "D:\\Projects" --sync-apikeys
\`\`\`

## Estándares aplicados (checklist visual)

| Estándar (RULES.md) | Estado |
|---------------------|--------|
| ✅ SSoT (\`config.yaml\`) | ✅ |
| ✅ Retry / Backoff exponencial | ✅ |
| ✅ Cadena fallback multi-modelo | ✅ |
| ✅ Async / no-bloqueante | ✅ |
| ✅ Progreso + \`status.json\` | ✅ |
| ✅ Clasificación errores (Auth, RateLimit, ...) | ✅ |
| ✅ Caché LRU + TTL (+Redis opcional) | ✅ |
| ✅ Streaming / Zero-disk I/O | ✅ |
| ✅ Control puertos (EADDRINUSE) | ✅ |
| ✅ Robustez BD (busy_timeout, WAL, migraciones) | ✅ |
| ✅ SemVer en manifiesto | ✅ |
| ✅ CHANGELOG (Keep a Changelog) | ✅ |
| ✅ .gitignore | ✅ |
| ✅ Dockerfile multi-stage | ✅ |
| ✅ CI/CD GitHub Actions | ✅ |
| ✅ .env.example | ✅ |
| ✅ Wiki (\`wiki/\`, RULES.md §5.9) | ✅ |
| ✅ "Last updated" en README y wiki (§5.11) | ✅ |
| ✅ Capturas con iris (§5.5) | ✅ |
| ✅ Catálogo de API keys ofrecido (§6.5) | ✅ |
| ✅ Contexto LLM (\`contexto_proyecto.md\`, §5.10) | ✅ |

## Documentación

- [Wiki](wiki/Home.md) — onboarding, arquitectura, runbook (RULES.md §5.9)
- [Contexto para LLM](contexto_proyecto.md) — base de código consolidada (RULES.md §5.10)
- [CHANGELOG](CHANGELOG.md)

## Licencia

MIT — ver \`LICENSE\`.
EOF

# 3) CHANGELOG.md (Keep a Changelog)
cat > CHANGELOG.md <<EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial scaffold via dev-standards bootstrap script
- Standard project structure with all required files

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Initial release scaffold
EOF

# 4) Manifiesto de versión según lenguaje
case "$LANG" in
  python)
    cat > pyproject.toml <<EOF
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
version = "0.1.0"
description = "$PROJECT_DESC"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Autor", email = "autor@example.com"}]
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.1",
    "ruff>=0.1",
    "mypy>=1.5",
    "pre-commit>=3.3",
]

[tool.setuptools.packages.find]
where = ["src"]
include = ["$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')*"]

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "UP", "B", "C4", "PT", "T20"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
EOF
    mkdir -p src/$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    cat > src/$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')/__init__.py <<'EOF'
"""Paquete generado por dev-standards bootstrap."""
__version__ = "0.1.0"
EOF
    ;;

  node)
    cat > package.json <<EOF
{
  "name": "$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')",
  "version": "0.1.0",
  "description": "$PROJECT_DESC",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "vitest run",
    "lint": "eslint src/",
    "format": "prettier --write .",
    "prepare": "husky install"
  },
  "keywords": [],
  "author": "Autor <autor@example.com>",
  "license": "MIT",
  "devDependencies": {
    "typescript": "^5.3",
    "vitest": "^1.2",
    "eslint": "^8.56",
    "prettier": "^3.2",
    "husky": "^9.0"
  },
  "engines": {
    "node": ">=20"
  }
}
EOF
    cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF
    mkdir -p src
    echo 'export const version = "0.1.0";' > src/index.ts
    ;;

  go)
    MODULE="github.com/owner/$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
    cat > go.mod <<EOF
module $MODULE

go 1.22

// Version is set via -ldflags="-X main.version=0.1.0"
EOF
    mkdir -p cmd/$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    cat > cmd/$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')/main.go <<'EOF'
package main

import (
	"flag"
	"fmt"
)

// version is set at build time via ldflags
var version = "0.1.0"

func main() {
	flag.Parse()
	fmt.Printf("%s v%s\n", "PROJECT_NAME", version)
}
EOF
    ;;

  rust)
    cat > Cargo.toml <<EOF
[package]
name = "$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
version = "0.1.0"
edition = "2021"
description = "$PROJECT_DESC"
license = "MIT"
authors = ["Autor <autor@example.com>"]
repository = "https://github.com/OWNER/REPO"
readme = "README.md"
categories = ["command-line-utilities"]

[dependencies]
clap = { version = "4.5", features = ["derive"] }
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
tokio = { version = "1.38", features = ["full"] }
tracing = "0.1"
tracing-subscriber = "0.3"
anyhow = "1.0"
EOF
    mkdir -p src
    cat > src/main.rs <<'EOF'
use clap::Parser;

#[derive(Parser, Debug)]
#[command(version = "0.1.0", about = "PROJECT_DESC")]
struct Args {}

fn main() {
    Args::parse();
    println!("PROJECT_NAME v0.1.0");
}
EOF
    ;;

  *)
    echo "❌ Lenguaje no soportado: $LANG (python|node|go|rust)"
    exit 1
    ;;
esac

# 5) .env.example (RULES.md §6.4 / §6.5)
# Catálogo por defecto (nombres, sin valores). Si hay un APIKEYS.env accesible, se usan sus nombres.
DEFAULT_APIKEYS="GROQ_API_KEY OPENAI_API_KEY ANTHROPIC_API_KEY GEMINI_API_KEY HF_TOKEN HUGGINGFACE_TOKEN \
COHERE_API_KEY REPLICATE_API_TOKEN GITHUB_TOKEN YOUTUBE_API_KEY DISCOGS_TOKEN SPOTIFY_CLIENT_ID \
SPOTIFY_CLIENT_SECRET PEXELS_API_KEY PIXABAY_API_KEY UNSPLASH_API_KEY SERPAPI_KEY"
if [[ -z "$APIKEYS_CATALOG" ]]; then
  for candidate in "$REPO_ROOT/../LocalProjectsTracker/APIKEYS.env" "$HOME/.localprojectstracker/APIKEYS.env"; do
    if [[ -f "$candidate" ]]; then APIKEYS_CATALOG="$candidate"; break; fi
  done
fi
if [[ -n "$APIKEYS_CATALOG" && -f "$APIKEYS_CATALOG" ]]; then
  CATALOG_KEYS="$(grep -oE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=' "$APIKEYS_CATALOG" \
    | tr -d ' \t=' | sort -u | tr '\n' ' ')"
  CATALOG_SOURCE="$APIKEYS_CATALOG"
else
  CATALOG_KEYS="$DEFAULT_APIKEYS"
  CATALOG_SOURCE="catálogo por defecto de bootstrap-project.sh"
fi
{
  echo "# Variables de entorno — copie a .env y ajuste (o genérelo con LocalProjectsTracker --sync-apikeys)"
  echo "#"
  echo "# API keys (RULES.md §6.5): catálogo central en luciomerlo/LocalProjectsTracker (HOWTOUSEAPIS.MD)."
  echo "# Agregue a APIKEYS_MATCH (separadas por ';') las que use este proyecto. Fuente: $CATALOG_SOURCE"
  echo "APIKEYS_MATCH="
  echo "# Opciones disponibles:"
  for k in $CATALOG_KEYS; do echo "# $k="; done
  echo
} > .env.example
cat >> .env.example <<'EOF'

# Base de datos
DATABASE_PATH=data/app.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Servidor
HOST=0.0.0.0
PORT=8080

# Logging
LOG_LEVEL=INFO

# Configuración por defecto
DEFAULT_DURATION=30
TEMPERATURE=0.8

# Retry
MAX_RETRY_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=30.0

# Concurrencia
MAX_PARALLEL=4
EOF

# 6) Dockerfile multi-stage
cat > Dockerfile <<'EOF'
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
EOF

# 7) GitHub Actions CI
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  release:
    types: [published]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"
  GO_VERSION: "1.22"
  RUST_VERSION: "stable"

jobs:
  secret-scan:
    name: Secret Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Scan tracked files for hardcoded secrets
        run: python3 scripts/check-secrets.py --tree
      - name: Scan full history for hardcoded secrets
        run: python3 scripts/check-secrets.py --history

  lint-and-typecheck:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Ruff lint
        run: ruff check src/ tests/
      - name: Ruff format
        run: ruff format --check src/ tests/
      - name: MyPy
        run: mypy src/

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=src --cov-report=xml --cov-report=term-missing
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

  docker-build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: [lint-and-typecheck, test]
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: ${{ github.repository }}:${{ github.sha }}
          load: true
      - name: Test image
        run: docker run --rm ${{ github.repository }}:${{ github.sha }} python -c "import sys; print('OK')"

  docker-publish:
    name: Publish Docker Image
    runs-on: ubuntu-latest
    needs: docker-build
    if: github.event_name == 'release' && github.event.action == 'published'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ${{ secrets.DOCKERHUB_USERNAME }}/${{ github.repository }}:latest

  semantic-release:
    name: Semantic Release
    runs-on: ubuntu-latest
    needs: [lint-and-typecheck, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install -g semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github conventional-changelog-conventionalcommits
      - env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release --branches main
EOF

# 8) config.yaml (SSoT)
cat > config.yaml <<'EOF'
# Configuración centralizada (Single Source of Truth)
models:
  primary: "model-primary"
  fallback_chain:
    - "model-primary"
    - "model-fallback-1"
    - "model-fallback-2"

generation:
  default_duration_seconds: 30
  temperature: 0.8

retry:
  max_attempts: 3
  base_delay_seconds: 1.0
  max_delay_seconds: 30.0
  exponential_base: 2.0
  jitter: true
  retryable_status_codes: [408, 429, 500, 502, 503, 504]
  non_retryable_status_codes: [401, 403, 404]

concurrency:
  max_parallel: 4

cache:
  lru_max_size: 1000
  ttl_seconds: 3600
  redis_url: "redis://localhost:6379/0"
  enable_redis: false

database:
  path: "data/app.db"
  busy_timeout_ms: 30000
  enable_wal: true

observability:
  status_file: "data/status.json"
  progress_interval_seconds: 5
  log_level: "INFO"

server:
  host: "0.0.0.0"
  port: 8080
  handle_eaddrinuse: true
  max_port_retries: 10

error_codes:
  AUTH: 401
  RATE_LIMIT: 429
  NOT_FOUND: 404
  TIMEOUT: 408
  SERVER_ERROR: [500, 502, 503, 504]
EOF

# 9) Escaneo de secretos: pre-commit + script (RULES.md §6)
mkdir -p scripts
cp "$(dirname "${BASH_SOURCE[0]}")/check-secrets.py" scripts/check-secrets.py 2>/dev/null || \
  curl -fsSL https://raw.githubusercontent.com/luciomerlo/dev-standards/main/scripts/check-secrets.py -o scripts/check-secrets.py

cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: local
    hooks:
      - id: check-secrets
        name: Bloquear secretos hardcodeados (RULES.md §6.1)
        entry: python3 scripts/check-secrets.py
        language: system
        pass_filenames: false
        always_run: true
EOF

# 9a) Carpeta de capturas (RULES.md §5.5c, iris)
mkdir -p docs/screenshots && touch docs/screenshots/.gitkeep

# 9b) Wiki del repositorio (RULES.md §5.9)
mkdir -p wiki
cat > wiki/Home.md <<EOF
# $PROJECT_NAME

_Last updated: ${TODAY}_

$PROJECT_DESC

Esta Wiki es el conocimiento operativo vivo del repositorio (RULES.md §5.9).
El [README](../README.md) es la puerta de entrada; aquí vive onboarding, arquitectura, operación y troubleshooting.

## Mapa de páginas

| Página | Contenido |
|--------|-----------|
| [Architecture](Architecture.md) | Diseño, flujo de datos y decisiones |
| [Getting Started](Getting-Started.md) | Setup local y primer uso |
| [Operations](Operations.md) | Runbook, entorno, deploy y fallos |

Actualizar estas páginas en el **mismo cambio** que altere propósito, arquitectura, uso u operación.
EOF

cat > wiki/Architecture.md <<EOF
# Architecture — $PROJECT_NAME

_Last updated: ${TODAY}_

## Propósito

$PROJECT_DESC

## Vista general

\`\`\`mermaid
graph TD
  A[config.yaml SSoT] --> B[Core]
  B --> C[Async Pipeline + Retry/Backoff]
  C --> D[Fallback Chain]
  D --> E[Streaming Output]
  E --> F[status.json]
  F --> G[Observabilidad]
\`\`\`

## Fuente de verdad

- Configuración de dominio: \`config.yaml\`
- Directivas de ingeniería: RULES.md del ecosistema dev-standards
- Esta página se actualiza cuando cambia el diseño o el flujo de datos

## Decisiones

Documentar aquí las decisiones que no caben en el README (por qué este stack, por qué este límite, qué se descartó).
EOF

cat > wiki/Getting-Started.md <<EOF
# Getting Started — $PROJECT_NAME

_Last updated: ${TODAY}_

## Requisitos

- Lenguaje: $LANG
- Copiar \`.env.example\` a \`.env\` y completar secretos
- Revisar \`config.yaml\` (Single Source of Truth)

## Setup

\`\`\`bash
# Python
pip install -e ".[dev]"

# Node
npm ci

# Go
go build ./...

# Rust
cargo build --release
\`\`\`

## Primer uso

\`\`\`bash
# Python
python -m $PROJECT_NAME --help

# Node
npx $PROJECT_NAME --help

# Go
./$PROJECT_NAME --help

# Rust
cargo run -- --help
\`\`\`

## Contribuir

Commits según Conventional Commits. Un PR por cambio lógico. Si el cambio altera uso o arquitectura, actualizar esta Wiki en el mismo PR.
EOF

cat > wiki/Operations.md <<EOF
# Operations — $PROJECT_NAME

_Last updated: ${TODAY}_

## Entorno

| Variable / archivo | Rol |
|--------------------|-----|
| \`.env\` | Secretos locales (no versionar) |
| \`.env.example\` | Plantilla de variables |
| \`config.yaml\` | Configuración de dominio (SSoT) |
| \`data/status.json\` | Progreso de procesos largos |

## Runbook

1. Health: endpoint \`/health\` o comando de diagnóstico del binario.
2. Logs: nivel \`LOG_LEVEL\` (default INFO), JSON en producción.
3. Reintentos: backoff exponencial ante 429/5xx; no reintentar 401/403/404.
4. Puerto ocupado (\`EADDRINUSE\`): el proceso debe salir con código 1.

## Deploy

Imagen multi-stage vía \`Dockerfile\`. CI en \`.github/workflows/ci.yml\` (lint, test, build).

## Troubleshooting

| Síntoma | Qué revisar |
|---------|-------------|
| Arranque bloqueado | Tareas pesadas deben ser async (§3.2) |
| Rate limit | Cadena de fallback y headers 429 (§2.1–2.2) |
| Proceso interrumpido | Reanudar desde \`status.json\` (§4.3) |
| Drift de config | Un solo \`config.yaml\`, no copias (§1.1) |
EOF

cat > wiki/_Sidebar.md <<EOF
* [Home](Home)
* [Architecture](Architecture)
* [Getting Started](Getting-Started)
* [Operations](Operations)
* [README](../README.md)
* [CHANGELOG](../CHANGELOG.md)
EOF

# 10) LICENSE
cat > LICENSE <<'EOF'
MIT License

Copyright (c) 2024 Autor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 11) contexto_proyecto.md (RULES.md §5.10)
cp "$(dirname "${BASH_SOURCE[0]}")/generate-contexto.py" scripts/generate-contexto.py 2>/dev/null || \
  curl -fsSL https://raw.githubusercontent.com/luciomerlo/dev-standards/main/scripts/generate-contexto.py -o scripts/generate-contexto.py

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/generate-contexto.py --root "$REPO_ROOT"
elif command -v python >/dev/null 2>&1; then
  python scripts/generate-contexto.py --root "$REPO_ROOT"
else
  echo "⚠️  Python no disponible: ejecuta luego python scripts/generate-contexto.py"
fi

echo "✅  Scaffold completado en $REPO_ROOT"
echo "   → Edita README.md (badges, diagrama, capturas con iris → docs/screenshots/)"
echo "   → Elige API keys en .env.example (APIKEYS_MATCH) y corre LocalProjectsTracker --sync-apikeys"
echo "   → Rellena wiki/ (Home, Architecture, Getting-Started, Operations)"
echo "   → Regenera contexto_proyecto.md si cambia código o configuración (python scripts/generate-contexto.py)"
echo "   → Revisa config.yaml y .env.example"
echo "   → Añade tests en tests/ y código en src/"
echo "   → Haz commit y push; CI se activará automáticamente"