#!/usr/bin/env python3
"""transcribe_via_groq.py — Cliente para el backend `cloud-api` (RULES.md §7.2)
en proyectos basados en Whisper (LocalCoursesIndexer, OfflineLucio, YTTranscript,
ars-nova-mpt).

Groq hospeda Whisper (large-v3, large-v3-turbo) como API gestionada: reemplaza
la inferencia local de whisper/faster-whisper sin necesitar GPU propia.
Requiere GROQ_API_KEY en el entorno (nunca hardcodear, RULES.md §6.4) — el
mismo mecanismo ya usado en LocalProjectsTracker/groq_client.py.

Uso como librería:
    from transcribe_via_groq import transcribe
    text = transcribe("audio.mp3")

Uso por CLI:
    python scripts/transcribe_via_groq.py audio.mp3
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Optional

GROQ_TRANSCRIPTIONS_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_MODEL = "whisper-large-v3-turbo"


class GroqTranscriptionError(RuntimeError):
    pass


def _multipart_body(fields: dict, file_field: str, file_path: Path) -> tuple:
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
        )
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
        f"filename=\"{file_path.name}\"\r\nContent-Type: {content_type}\r\n\r\n".encode()
    )
    parts.append(file_path.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    return body, f"multipart/form-data; boundary={boundary}"


def transcribe(
    audio_path: str,
    *,
    model: str = DEFAULT_MODEL,
    language: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Transcribe `audio_path` vía la API de Groq. Devuelve el texto plano."""
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise GroqTranscriptionError(
            "Falta GROQ_API_KEY en el entorno. Configuralo en .env antes de usar --compute cloud-api."
        )

    path = Path(audio_path)
    if not path.exists():
        raise GroqTranscriptionError(f"No existe el archivo de audio: {audio_path}")

    fields = {"model": model, "response_format": "text"}
    if language:
        fields["language"] = language
    body, content_type = _multipart_body(fields, "file", path)

    req = urllib.request.Request(
        GROQ_TRANSCRIPTIONS_URL,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": content_type},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise GroqTranscriptionError(
            f"Groq API error {e.code}: {e.read().decode('utf-8', errors='ignore')}"
        ) from e
    except urllib.error.URLError as e:
        raise GroqTranscriptionError(f"No se pudo contactar la API de Groq: {e}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("audio_path")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--language", default=None)
    args = parser.parse_args()

    try:
        text = transcribe(args.audio_path, model=args.model, language=args.language)
    except GroqTranscriptionError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
