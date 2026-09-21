#!/usr/bin/env python3
"""make_colab_notebook.py — Genera el notebook companion para el backend `colab`
(RULES.md §7.2, §7.5).

Colab no expone una API pública para invocación remota transparente desde un
CLI local; el patrón soportado es un notebook que el usuario abre en el
navegador, sube su input, corre las celdas con la GPU gratuita de Google y
descarga el resultado. Este script genera ese notebook a partir de una
especificación mínima por proyecto — no reimplementar el .ipynb a mano en
cada repo.

Uso:
    python scripts/make_colab_notebook.py \\
      --repo-url https://github.com/luciomerlo/CompleteStemSeparator \\
      --branch main \\
      --title "CompleteStemSeparator — Colab runner" \\
      --pip "torch" "torchaudio" "demucs" \\
      --run 'python -m demucs.separate -n htdemucs_6s "{input_file}" -o output' \\
      --output-glob "output/**/*.wav" \\
      --out notebook/colab_run.ipynb
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _code_cell(source_lines: list) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines,
    }


def _md_cell(source_lines: list) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source_lines}


def build_notebook(
    *,
    title: str,
    repo_url: str,
    branch: str,
    pip_packages: list,
    run_cmd_template: str,
    output_glob: str,
    extra_setup: list = None,
) -> dict:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    pip_line = "!pip install -q " + " ".join(pip_packages) if pip_packages else "# sin deps adicionales"
    setup_lines = list(extra_setup or [])

    cells = [
        _md_cell(
            [
                f"# {title}\n",
                "\n",
                "Generado por `dev-standards/scripts/make_colab_notebook.py` (RULES.md §7.2).\n",
                "Backend `colab`: es un flujo asistido — corré las celdas en orden, "
                "subí tu archivo de entrada cuando se te pida, y descargá el resultado al final.\n",
                "No cierres esta pestaña mientras corre la celda de procesamiento.",
            ]
        ),
        _md_cell(["## 1. Clonar el repositorio y preparar el entorno"]),
        _code_cell(
            [
                f"!git clone --depth 1 --branch {branch} {repo_url}.git\n",
                f"%cd {repo_name}\n",
            ]
        ),
        _code_cell([pip_line + "\n", *[l + "\n" for l in setup_lines]]),
        _md_cell(["## 2. Verificar GPU asignada por Colab"]),
        _code_cell(
            [
                "import torch\n",
                "print('CUDA disponible:', torch.cuda.is_available())\n",
                "if torch.cuda.is_available():\n",
                "    print('GPU:', torch.cuda.get_device_name(0))\n",
                "else:\n",
                "    print(\"Runtime > Change runtime type > GPU, y volvé a correr esta celda.\")\n",
            ]
        ),
        _md_cell(["## 3. Subir el archivo de entrada"]),
        _code_cell(
            [
                "from google.colab import files\n",
                "uploaded = files.upload()\n",
                "input_file = next(iter(uploaded))\n",
                "print('Input:', input_file)\n",
            ]
        ),
        _md_cell(["## 4. Procesar"]),
        # `{input_file}` queda literal a propósito: IPython interpola variables
        # Python dentro de `!comando {var}` en tiempo de ejecución de la celda.
        _code_cell([f"!{run_cmd_template}\n"]),
        _md_cell(["## 5. Descargar el resultado"]),
        _code_cell(
            [
                "import glob\n",
                "from google.colab import files as _files\n",
                f"outputs = glob.glob({output_glob!r}, recursive=True)\n",
                "print(f'{len(outputs)} archivo(s) encontrados')\n",
                "for f in outputs:\n",
                "    _files.download(f)\n",
            ]
        ),
    ]

    return {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"name": title, "provenance": []},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--title", required=True)
    parser.add_argument("--pip", nargs="*", default=[])
    parser.add_argument("--run", required=True, help="Comando a ejecutar; usar {input_file} como placeholder")
    parser.add_argument("--output-glob", required=True)
    parser.add_argument("--extra-setup", nargs="*", default=[], help="Líneas de shell extra antes de correr")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    nb = build_notebook(
        title=args.title,
        repo_url=args.repo_url,
        branch=args.branch,
        pip_packages=args.pip,
        run_cmd_template=args.run,
        output_glob=args.output_glob,
        extra_setup=args.extra_setup,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Notebook generado: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
