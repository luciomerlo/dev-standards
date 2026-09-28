# Knowledge — bases de conocimiento públicas

Catálogos de referencia según RULES.md §10. No son estándares: un agente los consulta cuando el trabajo lo pide, y cita la entrada que usa.

## Public APIs

[`public-apis/public-apis`](https://github.com/public-apis/public-apis) (MIT) está fijado al commit `7598f906a610c6d6ebf7adc2e72b6b5fccc7eba0` (2026-09-28) en `knowledge/public/public-apis`. El catálogo es el `README.md` de ese submódulo: APIs HTTP públicas por categoría, con autenticación, HTTPS y CORS.

Antes de proponer una API HTTP pública:

1. Abrir `knowledge/public/public-apis/README.md` (hace falta `git clone --recurse-submodules` o `git submodule update --init`).
2. Citar la entrada elegida: nombre, enlace, autenticación y HTTPS.
3. Si ninguna entrada cubre el caso, decirlo. No inventar una fila del catálogo.

El catálogo vive solo en este repositorio. Los repos consumidores no lo copian: su `AGENTS.md`, generado por `bootstrap-project.sh`, apunta al pin de dev-standards.

## Qué no hace el auditor

No hay check en `scripts/audit-standards.py`. El catálogo no es un requisito de cada repo hermano; exigirlo duplicaría un árbol de terceros en todos los proyectos. El pin se revisa en el PR que lo cambia.

## Actualizar el pin

1. `git submodule update --remote knowledge/public/public-apis` y revisar el diff del catálogo.
2. Anotar el commit nuevo en `AGENTS.md`, RULES.md §10.2 y `PUBLIC_APIS_COMMIT` de `scripts/bootstrap-project.sh`.
3. Registrar el cambio en `CHANGELOG.md` y regenerar `contexto_proyecto.md`.
