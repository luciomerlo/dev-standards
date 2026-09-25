# Getting Started — dev-standards

_Last updated: 2026-09-25_

## Requisitos

- Bash (bootstrap) y Python 3.10+ (auditor)
- Git inicializado en el directorio del repo nuevo (`git init` ya hecho)
- Para adoptar en un repo existente: poder añadir archivos sin pisar los que ya están bien

## Capturas con iris (§5.5c)

```bash
curl -fsSL https://raw.githubusercontent.com/brijr/iris/main/install.sh | sh   # o: cargo install iris-screenshot
iris --full -o docs/screenshots/ http://localhost:8080          # vista principal
iris --size iphone -o docs/screenshots/mobile.png http://localhost:8080
iris --selector '#dashboard' --padding 24 -o docs/screenshots/dashboard.png http://localhost:8080
```

Requiere un navegador Chrome/Chromium (`--chrome RUTA` si no se autodetecta). Ejecutado como root (contenedores/CI), Chromium necesita `--no-sandbox`: usar un wrapper que lo agregue y pasarlo con `--chrome`.

## Dashboards: toggle Dark/Light (§8)

Proyecto nuevo con dashboard: crear con `bootstrap-project.sh --dashboard`. Declara `ui.dashboard: true` en `config.yaml` y deja el toggle de referencia en `ui/index.html`; el dashboard se construye sobre esa base. Si el dashboard llega después, cambiar `ui.dashboard` a `true` y copiar y adaptar [`templates/theme-toggle.html`](../templates/theme-toggle.html): script inline en `<head>` (sin destello), tokens CSS por modo, `<button>` con `aria-pressed` y evento `themechange` para re-renderizar gráficos. En Streamlit/Gradio/Dash usar el theming nativo cumpliendo §8.1–8.5. Capturas del README en ambos modos:

```bash
iris -o docs/screenshots/dashboard-light.png http://localhost:8080
iris --dark -o docs/screenshots/dashboard-dark.png http://localhost:8080
```

## Arrancar un repositorio nuevo

Ejecutar **dentro** de la carpeta del repo:

```bash
bash /ruta/a/dev-standards/scripts/bootstrap-project.sh \
  --lang python \
  --name "Mi Proyecto" \
  --desc "Descripción breve"
```

`--lang` acepta `python`, `node`, `go` o `rust`. Sin `--name` usa el basename del directorio. `--dashboard` marca el proyecto como dashboard y copia el toggle Dark/Light (§8). `--apikeys-catalog RUTA/APIKEYS.env` indica de dónde leer los nombres de las API keys (§6.5); sin él, busca `../LocalProjectsTracker/APIKEYS.env` y, si no existe, usa el catálogo por defecto.

El script genera README, CHANGELOG, manifiesto con `0.1.0`, `.gitignore`, Dockerfile, CI, `.env.example`, `config.yaml`, `wiki/` con las cuatro páginas mínimas (§5.9) y `contexto_proyecto.md` (§5.10).

Después del scaffold:

1. Completar badges y capturas en `README.md`. Capturas con [iris](https://github.com/brijr/iris) en `docs/screenshots/` (§5.5c), solo las pantallas relevantes.
2. Elegir API keys: agregar a `APIKEYS_MATCH` en `.env.example` las del catálogo que use el proyecto y generar `.env` con `python main.py --target-dir <dir> --sync-apikeys` desde LocalProjectsTracker (§6.5).
3. Reescribir `wiki/` con el propósito real del proyecto (no dejar el texto genérico).
4. Poner la descripción del hosting en inglés, ≤350 caracteres, alineada al README (§5.8).
5. Añadir código en `src/` y tests en `tests/`.
6. En cada cambio significativo, actualizar `_Last updated: YYYY-MM-DD_` en el README y en las páginas de `wiki/` afectadas (§5.11).
7. Regenerar `contexto_proyecto.md` (`python scripts/generate-contexto.py`) en el mismo cambio que toque código, configuración o documentación normativa (§5.10).

## Adoptar en un repo que ya existe

No hace falta re-bootstrap si el árbol ya tiene manifiesto, CI y README. Falta lo que el auditor marque en rojo:

1. Crear `wiki/Home.md`, `Architecture.md`, `Getting-Started.md` y `Operations.md` rellenos.
2. Enlazar `wiki/Home.md` desde el README.
3. Añadir la fila de Wiki al checklist de estándares del README.
4. Agregar `_Last updated: YYYY-MM-DD_` debajo del H1 del README y de cada página de `wiki/` (§5.11).
4. Copiar `scripts/check-secrets.py`, el hook de pre-commit y el job
   `secret-scan` de CI (§6.2) — obligatorio en todo repositorio, tenga o
   no carga GPU.
5. Si el proyecto corre algo pesado en GPU localmente (`torch`, `demucs`,
   `whisper`, `transformers`): copiar `scripts/gpu_compute.py` y sumar el
   backend de cómputo web que corresponda a su tier — ver [Compute](Compute.md) (§7).
6. Copiar `scripts/generate-contexto.py` y generar `contexto_proyecto.md`
   (`python scripts/generate-contexto.py`). Regenerarlo cada vez que cambie
   código, configuración o documentación normativa (§5.10).

## Añadir o cambiar un estándar

1. Editar `RULES.md` (un solo hogar por regla).
2. Si el estándar es comprobable: extender `scripts/audit-standards.py`.
3. Si nace con el repo: extender `scripts/bootstrap-project.sh`.
4. Actualizar esta Wiki y el checklist del README en el mismo cambio.
