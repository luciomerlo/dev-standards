# DeepSeek-V2

Proyecto DeepSeek-V2

<!-- Badges — actualiza los enlaces a tu repo real -->
![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/github/v/release/OWNER/REPO?label=version)
![License](https://img.shields.io/github/license/OWNER/REPO)
![Coverage](https://img.shields.io/codecov/c/github/OWNER/REPO)

## Arquitectura

```mermaid
graph TD
  A[Config.yaml (SSoT)] --> B[Generator / Core]
  B --> C[Async Pipeline + Retry/Backoff]
  C --> D[Fallback Chain Multi-Model]
  D --> E[Streaming Output]
  E --> F[Progress + status.json]
  F --> G[Observabilidad]
```


## Instalación

```bash
# Python
pip install -e .

# Node
npm ci

# Go
go build ./...

# Rust
cargo build --release
```

## Uso rápido

```bash
# Python
python -m DeepSeek-V2 --help

# Node
npx DeepSeek-V2 --help

# Go
./DeepSeek-V2 --help

# Rust
cargo run -- --help
```

## Configuración

Copie `.env.example` a `.env` y ajuste las variables:

```bash
cp .env.example .env
```

La configuración central vive en `config.yaml` (Single Source of Truth).

## Estándares aplicados (checklist visual)

| Estándar (RULES.md) | Estado |
|---------------------|--------|
| ✅ SSoT (`config.yaml`) | ✅ |
| ✅ Retry / Backoff exponencial | ✅ |
| ✅ Cadena fallback multi-modelo | ✅ |
| ✅ Async / no-bloqueante | ✅ |
| ✅ Progreso + `status.json` | ✅ |
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

MIT — ver `LICENSE`.
