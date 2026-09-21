#!/usr/bin/env python3
"""gpu_compute.py — Detección de CUDA y selección de backend de cómputo (RULES.md §7).

Backends soportados (ninguno reemplaza permanentemente a `local`):
  local            GPU/CPU de la máquina donde corre el proceso.
  colab            Genera/actualiza un notebook companion; flujo ASISTIDO,
                   no una invocación remota automática (Colab no expone esa API).
  cloud-api        Llama a un servicio gestionado (ej. Replicate) vía API key.
  cloud-serverless Invoca un contenedor propio en una plataforma serverless GPU
                   (ej. RunPod) para modelos/checkpoints custom.

Uso típico en un proyecto:

    from gpu_compute import add_compute_arg, resolve_backend, cuda_status_tag

    parser.add_argument(...)
    add_compute_arg(parser)
    args = parser.parse_args()
    backend = resolve_backend(args.compute)

En un dashboard/backend HTTP, usar `cuda_status_tag()` para el tag de Settings.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

BACKENDS = ("local", "colab", "cloud-api", "cloud-serverless")

# Cada proyecto declara su propio subconjunto según su carga de trabajo
# (RULES.md §7.2). No todos los proyectos ofrecen los 4 backends:
#   - Carga pesada con checkpoints/modelos custom (demucs entrenado, MusicGen):
#     local + cloud-serverless + colab (colab es la última prioridad, pero
#     debe existir). No se ofrece cloud-api: no hay endpoint gestionado para
#     un checkpoint propio.
#   - Carga moderada con modelos estándar hospedados en algún proveedor
#     (whisper/faster-whisper, clasificadores): local + cloud-api +
#     cloud-serverless. No se ofrece colab: la llamada a un API gestionado
#     ya es más simple que un notebook manual.
HEAVY_BACKENDS = ("local", "cloud-serverless", "colab")
MODERATE_BACKENDS = ("local", "cloud-api", "cloud-serverless")


def detect_cuda() -> bool:
    """True si hay una GPU CUDA utilizable. Nunca lanza: si torch no está
    instalado, o falla la detección por cualquier motivo, devuelve False."""
    try:
        import torch  # noqa: PLC0415 (import perezoso: torch puede no estar instalado)

        return bool(torch.cuda.is_available())
    except Exception:
        return False


@dataclass(frozen=True)
class StatusTag:
    label: str
    color: str  # "green" | "gray" | "red"


def cuda_status_tag() -> StatusTag:
    """Tag para el panel de Settings (RULES.md §7.3)."""
    if detect_cuda():
        return StatusTag(label="Local GPU CUDA available", color="green")
    return StatusTag(label="No local GPU (CUDA not detected)", color="gray")


def add_compute_arg(
    parser: argparse.ArgumentParser,
    available: tuple = BACKENDS,
    default: Optional[str] = None,
) -> None:
    """Agrega el flag --compute a un parser de CLI, limitado a los backends
    que este proyecto realmente soporta (`available`, ver HEAVY_BACKENDS /
    MODERATE_BACKENDS)."""
    parser.add_argument(
        "--compute",
        choices=available,
        default=default,
        help=f"Backend de cómputo (RULES.md §7). Opciones de este proyecto: {available}. "
        "Default: local si hay CUDA disponible.",
    )


def resolve_backend(
    requested: Optional[str],
    *,
    available: tuple = BACKENDS,
    allow_diffusion_models: bool = False,
) -> str:
    """Resuelve el backend a usar dentro de los soportados por el proyecto (`available`).

    Precedencia: `requested` explícito (flag/setting) > auto-detección.
    Si no se pide nada y no hay CUDA, no cae en silencio a CPU: informa las
    alternativas y termina, salvo que el llamador maneje el ValueError.
    """
    if requested:
        if requested not in available:
            raise ValueError(f"Backend {requested!r} no soportado por este proyecto. Opciones: {available}")
        return requested

    if detect_cuda():
        return "local"

    raise ValueError(
        "No se detectó GPU CUDA local y no se especificó --compute. "
        f"Opciones disponibles: {', '.join(available)}. "
        "Ver RULES.md §7.3 — no se ejecuta silenciosamente en CPU para cargas pesadas."
    )


def colab_badge(notebook_path: str, repo: str, branch: str = "main") -> str:
    """Badge Markdown 'Open in Colab' para el notebook companion (RULES.md §7.2)."""
    url = f"https://colab.research.google.com/github/{repo}/blob/{branch}/{notebook_path}"
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


def require_colab_notebook(notebook_path: Path) -> None:
    """Falla con un mensaje claro si se pidió --compute colab pero el proyecto
    todavía no generó su notebook companion."""
    if not notebook_path.exists():
        raise FileNotFoundError(
            f"Backend 'colab' pedido pero falta el notebook companion en {notebook_path}. "
            "Generalo antes de ofrecer esta opción (RULES.md §7.2)."
        )


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_compute_arg(parser)
    parser.add_argument("--allow-diffusion-models", action="store_true")
    args = parser.parse_args()

    tag = cuda_status_tag()
    print(f"[{tag.color}] {tag.label}")
    try:
        backend = resolve_backend(args.compute, allow_diffusion_models=args.allow_diffusion_models)
        print(f"Backend resuelto: {backend}")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
