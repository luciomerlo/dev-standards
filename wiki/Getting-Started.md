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

El script genera README, CHANGELOG, manifiesto con `0.1.0`, `.gitignore`, Dockerfile, CI, `.env.example`, `config.yaml` y `wiki/` con las cuatro páginas mínimas (§5.9).

Después del scaffold:

1. Completar badges y capturas en `README.md`.
2. Reescribir `wiki/` con el propósito real del proyecto (no dejar el texto genérico).
3. Poner la descripción del hosting en inglés, ≤350 caracteres, alineada al README (§5.8).
4. Añadir código en `src/` y tests en `tests/`.

## Adoptar en un repo que ya existe

No hace falta re-bootstrap si el árbol ya tiene manifiesto, CI y README. Falta lo que el auditor marque en rojo:

1. Crear `wiki/Home.md`, `Architecture.md`, `Getting-Started.md` y `Operations.md` rellenos.
2. Enlazar `wiki/Home.md` desde el README.
3. Añadir la fila de Wiki al checklist de estándares del README.

## Añadir o cambiar un estándar

1. Editar `RULES.md` (un solo hogar por regla).
2. Si el estándar es comprobable: extender `scripts/audit-standards.py`.
3. Si nace con el repo: extender `scripts/bootstrap-project.sh`.
4. Actualizar esta Wiki y el checklist del README en el mismo cambio.
