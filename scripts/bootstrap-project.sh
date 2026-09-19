#!/usr/bin/env bash
# bootstrap-project.sh — Scaffolding estándar para nuevos repositorios (RULES.md §5.6)
# Uso:  bash bootstrap-project.sh [--lang python|node|go|rust] [--name "Mi Proyecto"] [--desc "Descripción breve"]
#       Se ejecuta DENTRO de la carpeta del nuevo repo (git init ya hecho).

set -euo pipefail

LANG="python"
PROJECT_NAME=""
PROJECT_DESC=""
REPO_ROOT="$(pwd)"

while [[ $# -gt 0 ]]; do
  case $1 in
    --lang) LANG="$2"; shift 2 ;;
    --name) PROJECT_NAME="$2"; shift 2 ;;
    --desc) PROJECT_DESC="$2"; shift 2 ;;
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

## Licencia

MIT — ver \`LICENSE\`.
EOF

# 3) CHANGELOG.md (Keep a Changelog)
cat > CHANGELOG.md <<'EOF'
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

# 5) .env.example
cat > .env.example <<'EOF'
# Variables de entorno — copie a .env y ajuste
# API Keys (mínimo una requerida)
API_KEY_1=
API_KEY_2=

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

# 9) LICENSE
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

echo "✅  Scaffold completado en $REPO_ROOT"
echo "   → Edita README.md (badges, diagrama, capturas)"
echo "   → Revisa config.yaml y .env.example"
echo "   → Añade tests en tests/ y código en src/"
echo "   → Haz commit y push; CI se activará automáticamente"