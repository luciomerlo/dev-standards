#!/usr/bin/env python3
"""run_on_runpod.py — Cliente genérico para el backend `cloud-serverless`
(RULES.md §7.2) usando RunPod Serverless.

RunPod expone una API REST real (a diferencia de Colab): se manda un job,
se hace polling del estado, y se recibe el resultado sin intervención manual.
Este cliente es agnóstico de la carga de trabajo — cada proyecto define su
propio `payload` (el `input` que espera su endpoint/contenedor) y decide qué
hacer con el `output`.

Requiere en el entorno (nunca hardcodear, RULES.md §6.4):
    RUNPOD_API_KEY       — API key de la cuenta de RunPod
    RUNPOD_ENDPOINT_ID   — id del endpoint serverless de este proyecto
                            (se crea una vez en el dashboard de RunPod,
                            apuntando a la imagen Docker del proyecto)

Uso como librería:
    from run_on_runpod import run_job
    output = run_job(payload={"input_file_b64": "...", "model": "htdemucs_6s"})

Uso por CLI (payload como JSON):
    python scripts/run_on_runpod.py --payload '{"model": "htdemucs_6s"}'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

API_BASE = "https://api.runpod.ai/v2"
TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}


class RunPodError(RuntimeError):
    pass


def _request(url: str, api_key: str, body: Optional[dict] = None, method: str = "POST") -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RunPodError(f"RunPod API error {e.code}: {e.read().decode('utf-8', errors='ignore')}") from e
    except urllib.error.URLError as e:
        raise RunPodError(f"No se pudo contactar la API de RunPod: {e}") from e


def submit_job(endpoint_id: str, api_key: str, payload: Dict[str, Any]) -> str:
    """Encola el job. Devuelve el job id."""
    result = _request(f"{API_BASE}/{endpoint_id}/run", api_key, {"input": payload})
    job_id = result.get("id")
    if not job_id:
        raise RunPodError(f"Respuesta inesperada de RunPod al encolar el job: {result}")
    return job_id


def poll_job(endpoint_id: str, api_key: str, job_id: str) -> dict:
    return _request(f"{API_BASE}/{endpoint_id}/status/{job_id}", api_key, method="GET")


def cancel_job(endpoint_id: str, api_key: str, job_id: str) -> dict:
    return _request(f"{API_BASE}/{endpoint_id}/cancel/{job_id}", api_key, method="POST")


def run_job(
    payload: Dict[str, Any],
    *,
    endpoint_id: Optional[str] = None,
    api_key: Optional[str] = None,
    poll_interval_s: float = 5.0,
    timeout_s: float = 1800.0,
) -> dict:
    """Envía `payload` al endpoint serverless configurado, espera el resultado
    haciendo polling, y devuelve el `output` del job.

    Lee RUNPOD_ENDPOINT_ID / RUNPOD_API_KEY del entorno si no se pasan
    explícitamente. Nunca hardcodear estos valores (RULES.md §6.4).
    """
    endpoint_id = endpoint_id or os.environ.get("RUNPOD_ENDPOINT_ID")
    api_key = api_key or os.environ.get("RUNPOD_API_KEY")
    if not endpoint_id or not api_key:
        raise RunPodError(
            "Falta RUNPOD_ENDPOINT_ID y/o RUNPOD_API_KEY en el entorno. "
            "Configuralos en .env (ver .env.example) antes de usar --compute cloud-serverless."
        )

    job_id = submit_job(endpoint_id, api_key, payload)
    deadline = time.monotonic() + timeout_s

    while True:
        status = poll_job(endpoint_id, api_key, job_id)
        state = status.get("status")
        if state in TERMINAL_STATUSES:
            if state != "COMPLETED":
                raise RunPodError(f"Job {job_id} terminó en estado {state}: {status}")
            return status.get("output", {})
        if time.monotonic() > deadline:
            cancel_job(endpoint_id, api_key, job_id)
            raise RunPodError(f"Job {job_id} superó el timeout de {timeout_s}s; cancelado.")
        time.sleep(poll_interval_s)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--payload", required=True, help="JSON con el input del job")
    parser.add_argument("--timeout", type=float, default=1800.0)
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
        output = run_job(payload, timeout_s=args.timeout)
    except (RunPodError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
