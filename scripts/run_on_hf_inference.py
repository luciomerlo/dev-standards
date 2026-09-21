#!/usr/bin/env python3
"""run_on_hf_inference.py — Cliente para el backend `cloud-api` (RULES.md §7.2)
usando la Inference API de Hugging Face, para modelos que no son Whisper
(ej. el clasificador de audio de PiazzollaMidiGenerator).

Requiere HUGGINGFACE_TOKEN en el entorno (nunca hardcodear, RULES.md §6.4).

Uso como librería:
    from run_on_hf_inference import infer
    result = infer(model_id="MIT/ast-finetuned-audioset-10-10-0.4593", data=open("clip.wav","rb").read())

Uso por CLI:
    python scripts/run_on_hf_inference.py --model MIT/ast-finetuned-audioset-10-10-0.4593 --file clip.wav
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

HF_API_BASE = "https://api-inference.huggingface.co/models"


class HFInferenceError(RuntimeError):
    pass


def infer(
    *,
    model_id: str,
    data: bytes,
    content_type: Optional[str] = None,
    api_token: Optional[str] = None,
) -> Any:
    """Manda `data` (bytes crudos de audio/imagen) al endpoint de Inference API
    de `model_id`. Devuelve el JSON de respuesta ya decodificado."""
    api_token = api_token or os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")
    if not api_token:
        raise HFInferenceError(
            "Falta HUGGINGFACE_TOKEN en el entorno. Configuralo en .env antes de usar --compute cloud-api."
        )

    headers = {"Authorization": f"Bearer {api_token}"}
    if content_type:
        headers["Content-Type"] = content_type

    req = urllib.request.Request(f"{HF_API_BASE}/{model_id}", data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 503:
            raise HFInferenceError(
                f"Modelo cargando en el servidor de HF (cold start), reintentar en unos segundos: {body}"
            ) from e
        raise HFInferenceError(f"HF Inference API error {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise HFInferenceError(f"No se pudo contactar la Inference API de HF: {e}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, dest="model_id")
    parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()

    if not args.file.exists():
        print(f"No existe el archivo: {args.file}", file=sys.stderr)
        return 1

    content_type = mimetypes.guess_type(str(args.file))[0] or "application/octet-stream"
    try:
        result = infer(model_id=args.model_id, data=args.file.read_bytes(), content_type=content_type)
    except HFInferenceError as e:
        print(str(e), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
