#!/usr/bin/env python3
"""run_on_modal.py — Cliente genérico para el backend `modal` (RULES.md §7.2)
usando Modal (https://modal.com, ~$30 USD de crédito gratis por mes).

A diferencia de RunPod (una API HTTP genérica contra un endpoint), Modal es
Python-nativo: la función pesada se decora con `@app.function(gpu=...)` en
un `modal_app.py` propio de cada proyecto y se despliega una vez con
`modal deploy modal_app.py`. Este cliente solo hace el `lookup` + `.remote()`
de una función ya deployada -- no reemplaza a `modal_app.py`, lo invoca.

Autenticación: `modal token new` (una vez, guarda credenciales en
`~/.modal.toml`) o las variables de entorno `MODAL_TOKEN_ID`/
`MODAL_TOKEN_SECRET`. No hay API key que pasar a mano en el código.

Uso como librería:
    from run_on_modal import call_modal_function
    result = call_modal_function("mi-app", "mi_funcion", audio_b64="...", model_size="small")

Uso por CLI:
    python scripts/run_on_modal.py --app mi-app --function mi_funcion --payload '{"prompt": "..."}'
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


class ModalError(RuntimeError):
    pass


def call_modal_function(app_name: str, function_name: str, **kwargs: Any) -> Any:
    """Busca `function_name` en la app `app_name` ya deployada en Modal y la
    invoca de forma síncrona (`.remote()`), devolviendo lo que la función
    remota retorne."""
    try:
        import modal
    except ImportError as e:
        raise ModalError(
            "Falta el paquete 'modal' (pip install modal) y correr 'modal token new' "
            "una vez para autenticarte, antes de usar --compute modal."
        ) from e

    try:
        fn = modal.Function.lookup(app_name, function_name)
    except Exception as e:
        raise ModalError(
            f"No se encontró la función '{function_name}' en la app '{app_name}' de Modal. "
            f"¿Corriste 'modal deploy modal_app.py'? Detalle: {e}"
        ) from e

    try:
        return fn.remote(**kwargs)
    except Exception as e:
        raise ModalError(f"Modal error invocando {app_name}/{function_name}: {e}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--app", required=True)
    parser.add_argument("--function", required=True)
    parser.add_argument("--payload", required=True, help="JSON con los kwargs de la función")
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
        result = call_modal_function(args.app, args.function, **payload)
    except (ModalError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False) if not isinstance(result, str) else result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
