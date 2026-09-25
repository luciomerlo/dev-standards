# dev-standards

_Last updated: 2026-09-25_

Estándares de ingeniería, scaffolding y auditoría automatizada para el ecosistema de proyectos de luciomerlo.

![CI](https://github.com/luciomerlo/dev-standards/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/github/v/release/luciomerlo/dev-standards?label=version)
![License](https://img.shields.io/github/license/luciomerlo/dev-standards)

## Arquitectura

```mermaid
graph TD
  A[RULES.md] --> B[bootstrap-project.sh]
  B --> C[Repo nuevo: README, CHANGELOG, CI, wiki/, contexto_proyecto.md]
  A --> D[audit-standards.py]
  D --> E[Escanea repos existentes]
  E --> F[AUDIT_REPORT.md + score 0-100]
  A --> G[check-secrets.py]
  G --> H[pre-commit hook + CI secret-scan]
```

## Qué contiene este repo

| Archivo / carpeta | Rol |
|---|---|
| [`RULES.md`](RULES.md) | Directivas obligatorias: arquitectura, resiliencia, versionado, capturas con iris (§5.5), "Last updated" (§5.11), catálogo de API keys (§6.5), toggle Dark/Light en dashboards (§8), contexto para LLM (§5.10), seguridad de secretos (§6), cómputo local vs. web (§7), UI y dashboards (§8) |
| [`contexto_proyecto.md`](contexto_proyecto.md) | Base de código consolidada para un LLM posterior (§5.10). Regenerar con `scripts/generate-contexto.py` |
| [`docs/code-standards.md`](docs/code-standards.md) | Nomenclatura, formato, testing, checklist de revisión |
| [`docs/commit-conventions.md`](docs/commit-conventions.md) | Convenciones de commits |
| `scripts/bootstrap-project.sh` | Genera el scaffolding completo en un repo nuevo (README, CHANGELOG, CI, `.gitignore`, Dockerfile, `wiki/`, guardarraíl de secretos) |
| `scripts/audit-standards.py` | Audita repos existentes contra RULES.md (incluye la fecha "Last updated", §5.11) y genera `AUDIT_REPORT.md` con score 0-100 |
| `scripts/generate-contexto.py` | Regenera `contexto_proyecto.md` (RULES.md §5.10) |
| `scripts/check-secrets.py` | Bloquea commits/CI con credenciales hardcodeadas (RULES.md §6) |
| `scripts/gpu_compute.py` | Detección de CUDA + selección de backend de cómputo (RULES.md §7) |
| `scripts/make_colab_notebook.py` | Genera el notebook companion del backend `colab` |
| `scripts/run_on_runpod.py` | Cliente del backend `cloud-serverless` (RunPod) |
| `scripts/run_on_modal.py` | Cliente del backend `modal` ([Modal](https://modal.com), ~$30 USD/mes gratis) |
| `scripts/transcribe_via_groq.py` | Cliente del backend `cloud-api` para proyectos basados en Whisper (Groq) |
| `scripts/run_on_hf_inference.py` | Cliente del backend `cloud-api` para otros modelos hospedados en HF |
| [`templates/theme-toggle.html`](templates/theme-toggle.html) | Implementación de referencia del toggle Dark/Light para dashboards (RULES.md §8) |
| [`wiki/`](wiki/Home.md) | Wiki operativa de este propio repo (onboarding, arquitectura, runbook) |

## Uso rápido

Scaffolding de un repo nuevo:

```bash
bash scripts/bootstrap-project.sh --lang python --name "MiProyecto" --desc "Descripción breve"
```

Auditar todos los proyectos bajo un directorio:

```bash
python scripts/audit-standards.py --root /ruta/a/Projects --fail-on-regression
```

Regenerar el contexto consolidado para un LLM después de cambiar código, configuración o documentación:

```bash
python scripts/generate-contexto.py
```

Escanear secretos hardcodeados (usado por el pre-commit hook y el CI):

```bash
python scripts/check-secrets.py --tree      # árbol versionado
python scripts/check-secrets.py --history   # historial completo
```

## Configuración

Copie `.env.example` a `.env` si va a correr los scripts con credenciales (ej. tokens de GitHub para automatizar el scaffolding).

API keys en proyectos nuevos (RULES.md §6.5): `bootstrap-project.sh` escribe en `.env.example` una línea `APIKEYS_MATCH=` y todo el catálogo central de `luciomerlo/LocalProjectsTracker` como opciones comentadas (solo nombres). Si encuentra `../LocalProjectsTracker/APIKEYS.env` o se le pasa `--apikeys-catalog RUTA`, toma los nombres de ahí; si no, usa el catálogo por defecto. El `.env` se genera luego con `python main.py --target-dir <dir> --sync-apikeys` desde LocalProjectsTracker.

## Estándares aplicados (checklist visual)

| Estándar (RULES.md) | Estado |
|---|---|
| SemVer en manifiesto (`pyproject.toml`) | ✅ |
| CHANGELOG (Keep a Changelog) | ✅ |
| `.gitignore` | ✅ |
| Dockerfile | ✅ |
| CI/CD GitHub Actions | ✅ |
| `.env.example` | ✅ |
| Wiki (`wiki/`, §5.9) | ✅ |
| Contexto LLM (`contexto_proyecto.md`, §5.10) | ✅ |
| Escaneo de secretos (§6) | ✅ |
| "Last updated" en README y wiki (§5.11) | ✅ |
| Catálogo de API keys ofrecido a proyectos nuevos (§6.5) | ✅ |
| Capturas con iris (§5.5c) | N/A — sin UI |
| Toggle Dark/Light en dashboards (§8) | N/A — sin UI; provee `templates/theme-toggle.html` |

## Documentación

- [Wiki](wiki/Home.md) — onboarding, arquitectura y runbook
- [contexto_proyecto.md](contexto_proyecto.md) — base de código consolidada para un LLM (RULES.md §5.10)
- [RULES.md](RULES.md) — estándares de arquitectura, resiliencia, versionado y seguridad
- [Estándares de código](docs/code-standards.md)
- [Convenciones de commits](docs/commit-conventions.md)

## Licencia

MIT — ver `LICENSE`.
