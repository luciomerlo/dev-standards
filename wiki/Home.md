# Wiki — dev-standards

Manual de estándares de ingeniería del ecosistema: arquitectura, resiliencia, calidad y forma de los repositorios.

El [README](../README.md) es la puerta de entrada (qué es el repo, cómo instalarlo, checklist visual). Esta Wiki es el conocimiento operativo vivo: cómo se aplican las reglas, cómo se arranca un proyecto nuevo y cómo se audita el cumplimiento.

## Qué hay en este repositorio

| Artefacto | Rol |
|-----------|-----|
| [RULES.md](../RULES.md) | Fuente de verdad de las directivas (§1–§7) |
| [docs/code-standards.md](../docs/code-standards.md) | Nomenclatura, lint, testing, review |
| [docs/commit-conventions.md](../docs/commit-conventions.md) | Conventional Commits, branches, PRs |
| `scripts/bootstrap-project.sh` | Scaffold obligatorio de un repo nuevo (§5.6) |
| `scripts/audit-standards.py` | Auditoría periódica de cumplimiento (§5.7) |
| `scripts/check-secrets.py` | Escaneo de secretos, árbol + historial (§6.2) |
| `scripts/gpu_compute.py` | Detección de CUDA, tag de estado, selección de backend (§7.1–§7.3) |
| `scripts/make_colab_notebook.py` | Genera el notebook companion del backend `colab` (§7.2) |
| `scripts/run_on_runpod.py` | Cliente del backend `cloud-serverless` (RunPod) (§7.2) |
| `scripts/run_on_hf_inference.py` | Cliente del backend `cloud-api` (HF Inference API) (§7.2) |
| `scripts/transcribe_via_groq.py` | Cliente del backend `cloud-api` para Whisper (Groq) (§7.2) |
| `scripts/run_on_modal.py` | Cliente del backend `modal` (Modal, ~$30 USD/mes gratis) (§7.2) |
| `config.yaml` | SSoT de configuración de dominio (§1.1) |
| `wiki/` | Esta Wiki, versionada con el código (§5.9) |

## Mapa de páginas

| Página | Contenido |
|--------|-----------|
| [Architecture](Architecture.md) | Cómo se codifican y hacen cumplir los estándares |
| [Getting Started](Getting-Started.md) | Bootstrap de un repo nuevo y adopción en uno existente |
| [Operations](Operations.md) | Cómo correr la auditoría, el escaneo de secretos, baseline y CI |
| [Compute](Compute.md) | Cómputo local vs. web: los 5 backends (local/colab/cloud-api/cloud-serverless/modal) y cómo elegir uno por proyecto |

## Regla de actualización

Cualquier cambio que altere propósito, arquitectura, uso, operación o forma de contribuir **actualiza esta Wiki en el mismo cambio** (RULES.md §5.9). Plantillas vacías no cumplen el estándar.
