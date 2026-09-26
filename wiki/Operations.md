# Operations — dev-standards

## Auditoría de cumplimiento

```bash
python scripts/audit-standards.py \
  --root /ruta/a/Projects \
  --output AUDIT_REPORT.md \
  --baseline audit_baseline.json \
  --fail-on-regression
```

Recorre cada subdirectorio de `--root` (ignora los que empiezan por `.`) y puntúa checks de §5 más patrones de §1–§4. Escribe `AUDIT_REPORT.md` y actualiza la línea base.

`--fail-on-regression` sale con código 1 si algún proyecto baja de score respecto a `audit_baseline.json`.

### Check de descripción (§5.8)

`check_description()` obtiene `owner/repo` del remote `origin` y lee el campo "description" del repositorio en la API de GitHub (`GET /repos/{owner}/{repo}`). Aprueba si no está vacío y tiene 350 caracteres como máximo. Usa `GITHUB_TOKEN` o `GH_TOKEN` si están definidos (necesario para repos privados y para evitar el rate limit de 60 req/h). Sin remote de GitHub o sin respuesta de la API, el check falla y lo avisa por consola.

`bootstrap-project.sh` rechaza un `--desc` de más de 350 caracteres y, si `gh` está disponible y el remote es de GitHub, lo aplica con `gh repo edit --description`. El idioma (inglés) no se valida automáticamente.

### Check de Wiki (§5.9)

El auditor exige `wiki/` con `Home.md`, `Architecture.md`, `Getting-Started.md` y `Operations.md`. Cada archivo debe tener un heading Markdown y al menos 80 caracteres de contenido real.

### Check de contexto para LLM (§5.10)

`check_contexto()` exige `contexto_proyecto.md` en la raíz, con los encabezados `# RESUMEN Y ARQUITECTURA` y `# ARCHIVOS DEL PROYECTO`, y al menos un apartado `## Ruta:`. El archivo lo produce `scripts/generate-contexto.py`; hay que volver a correrlo en el mismo cambio que altere código, configuración o documentación normativa.

```bash
python scripts/generate-contexto.py
```

### Check de AGENTS.md (§5.11)

`check_agents_md()` exige un `AGENTS.md` en la raíz que mencione `dev-standards`. No verifica que el submódulo de `apple-design-skill` exista, porque el auditor no puede saber si el repo tiene un dashboard; esa parte se revisa en el PR.

### Check de Graft (§9)

`check_graft()` exige `.claude/skills/graft/SKILL.md` o una entrada `graft` en `mcpServers` de `.mcp.json`, y `/graft/` en `.gitignore` para que el caché no se versione. No valida la versión instalada ni que el grafo esté actualizado; para eso, `graft check` en local.

### Check de escaneo de secretos (§6)

`check_secret_scan()` verifica que exista `scripts/check-secrets.py` y que
esté referenciado en el pipeline de CI (`.github/workflows/ci.yml`). No
valida que el pre-commit hook esté instalado localmente — eso es
responsabilidad de cada clon (`.pre-commit-config.yaml` + `pre-commit
install`).

### Cómputo (§7) — no auditado automáticamente

A diferencia de Wiki y secretos, `audit-standards.py` **no** puntúa la
adopción de backends de cómputo: es condicional a si el proyecto tiene
carga GPU opcional, así que no aplica parejo a todo el ecosistema. La
verificación es manual — ver [Compute](Compute.md) para el checklist de
adopción y qué backend le toca a cada tier.

## CI

`.github/workflows/ci.yml` corre el escaneo de secretos y lint/typecheck en cada push y PR, y el build de la imagen Docker en `main`. No hay releases automáticas: la versión y el `CHANGELOG.md` se actualizan a mano (§5.1–5.2). El job de auditoría periódica (schedule mensual, §5.7) es el que debe invocar `audit-standards.py` y abrir issue si hay regresiones.

## Entorno de este repo

| Archivo | Rol |
|---------|-----|
| `config.yaml` | SSoT de retry, cache, DB, puertos (plantilla para repos generados) |
| `.env.example` | Plantilla de secretos; `.env` no se versiona |
| `pyproject.toml` | Versión SemVer `0.1.0`, ruff, mypy, pytest |
| `audit_baseline.json` | Scores previos; no editar a mano salvo reset consciente |

## Troubleshooting

| Síntoma | Qué revisar |
|---------|-------------|
| Score 100 con CHANGELOG en rojo | El check exige `## [x.y.z] - YYYY-MM-DD`; el placeholder `$(date ...)` del scaffold no cuenta |
| Wiki en rojo | Falta `wiki/` o alguna página mínima está vacía / sin `#` heading |
| contexto_proyecto.md en rojo | Falta el archivo o no tiene las dos secciones y un `## Ruta:` (§5.10). Regenerar con `python scripts/generate-contexto.py` |
| Regresión masiva al añadir un check | Esperado: la línea base se recalcula al correr el auditor; la primera corrida con `--fail-on-regression` fallará hasta que los repos adopten la regla |
