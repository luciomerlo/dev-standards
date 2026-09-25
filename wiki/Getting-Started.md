# Getting Started — dev-standards

## Requisitos

- Bash (bootstrap) y Python 3.10+ (auditor)
- Git inicializado en el directorio del repo nuevo (`git init` ya hecho)
- Para adoptar en un repo existente: poder añadir archivos sin pisar los que ya están bien

## Arrancar un repositorio nuevo

Ejecutar **dentro** de la carpeta del repo:

```bash
bash /ruta/a/dev-standards/scripts/bootstrap-project.sh \
  --lang python \
  --name "Mi Proyecto" \
  --desc "Descripción breve"
```

`--lang` acepta `python`, `node`, `go` o `rust`. Sin `--name` usa el basename del directorio.

El script genera README, CHANGELOG, manifiesto con `0.1.0`, `.gitignore`, Dockerfile, CI, `.env.example`, `config.yaml`, `wiki/` con las cuatro páginas mínimas (§5.9) y `contexto_proyecto.md` (§5.10).

Después del scaffold:

1. Completar badges y capturas en `README.md`.
2. Reescribir `wiki/` con el propósito real del proyecto (no dejar el texto genérico).
3. Poner la descripción del hosting en inglés, ≤350 caracteres, alineada al README (§5.8).
4. Añadir código en `src/` y tests en `tests/`.
5. Regenerar `contexto_proyecto.md` (`python scripts/generate-contexto.py`) en el mismo cambio que toque código, configuración o documentación normativa (§5.10).
6. Conectar Graft si el bootstrap no lo hizo: `graft init --agents claude --no-global` y versionar el wiring (§9, [Graft](Graft.md)).
7. Si el proyecto tiene interfaz web: al cerrar el desarrollo inicial (primera versión usable de punta a punta, antes del primer release), correr `/fix` para medir y corregir los caminos lentos. Adjuntar el reporte, con los números de antes y después, al PR o al release (§3.4).

## Adoptar en un repo que ya existe

No hace falta re-bootstrap si el árbol ya tiene manifiesto, CI y README. Falta lo que el auditor marque en rojo:

1. Crear `wiki/Home.md`, `Architecture.md`, `Getting-Started.md` y `Operations.md` rellenos.
2. Enlazar `wiki/Home.md` desde el README.
3. Añadir la fila de Wiki al checklist de estándares del README.
4. Copiar `scripts/check-secrets.py`, el hook de pre-commit y el job
   `secret-scan` de CI (§6.2) — obligatorio en todo repositorio, tenga o
   no carga GPU.
5. Si el proyecto corre algo pesado en GPU localmente (`torch`, `demucs`,
   `whisper`, `transformers`): copiar `scripts/gpu_compute.py` y sumar el
   backend de cómputo web que corresponda a su tier — ver [Compute](Compute.md) (§7).
6. Copiar `scripts/generate-contexto.py` y generar `contexto_proyecto.md`
   (`python scripts/generate-contexto.py`). Regenerarlo cada vez que cambie
   código, configuración o documentación normativa (§5.10).
7. Instalar Graft (`npm install -g @nanonets/graft@0.19.0`), correr
   `graft init --agents claude --no-global` y versionar `.claude/`, `.mcp.json`,
   `.ignore` y `.gitignore` (§9).

## Añadir o cambiar un estándar

1. Editar `RULES.md` (un solo hogar por regla).
2. Si el estándar es comprobable: extender `scripts/audit-standards.py`.
3. Si nace con el repo: extender `scripts/bootstrap-project.sh`.
4. Actualizar esta Wiki y el checklist del README en el mismo cambio.
