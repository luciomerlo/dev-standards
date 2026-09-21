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

### Check de Wiki (§5.9)

El auditor exige `wiki/` con `Home.md`, `Architecture.md`, `Getting-Started.md` y `Operations.md`. Cada archivo debe tener un heading Markdown y al menos 80 caracteres de contenido real.

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

`.github/workflows/ci.yml` corre lint/typecheck, tests con coverage, build de imagen y semantic-release en `main`. El job de auditoría periódica (schedule mensual, §5.7) es el que debe invocar `audit-standards.py` y abrir issue si hay regresiones.

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
| Regresión masiva al añadir un check | Esperado: la línea base se recalcula al correr el auditor; la primera corrida con `--fail-on-regression` fallará hasta que los repos adopten la regla |
