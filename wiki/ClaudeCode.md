# Claude Code — buenas prácticas de configuración

Cómo se configura Claude Code en todo repositorio, según RULES.md §11. El estándar de referencia es [`shanraisshan/claude-code-best-practice`](https://github.com/shanraisshan/claude-code-best-practice) (MIT), fijado al commit `bfcf0b5abc7f9bb5da9bd41cbba070d9cef330d2` (2026-09-29). Es un repositorio comunitario, no documentación oficial: ante una discrepancia prevalece la [documentación oficial](https://code.claude.com/docs).

## Dónde vive

Como submódulo superficial en `knowledge/standards/claude-code-best-practice`, solo en dev-standards (~77 MB). No se copia a los repos consumidores; su `AGENTS.md` (§5.11) apunta al pin. Clonar con `--recurse-submodules` o, en un clon existente:

```bash
git submodule update --init knowledge/standards/claude-code-best-practice
```

## Mínimos por repositorio (§11.3)

| Elemento | Exigencia | Fuente en el pin |
|----------|-----------|------------------|
| `CLAUDE.md` / `AGENTS.md` | Máximo 200 líneas por archivo. Lo que exceda va a `.claude/rules/*.md` | `README.md › CLAUDE.md + .claude/rules` |
| `.claude/rules/*.md` | Con `paths:` en el frontmatter se cargan solo al tocar archivos que coinciden; sin él, en cada sesión | `CLAUDE.md › Workflow Best Practices` |
| Comandos esenciales | Instalación, build y test, para que "corre los tests" funcione a la primera | `README.md › CLAUDE.md + .claude/rules` |
| Settings | Compartido en `.claude/settings.json`; personal en `.claude/settings.local.json`, ignorado por git. Sin secretos (§6) | `CLAUDE.md › Configuration Hierarchy` |
| Subagentes | `name` y `description` obligatorios. *Criterio propio:* `tools` como allowlist (sin él heredan todas) y `model` explícito si la tarea lo justifica | `best-practice/claude-subagents.md` |
| Skills | `description` que diga cuándo invocarla. *Criterio propio:* `disable-model-invocation: true` si tiene efectos laterales | `best-practice/claude-skills.md` |

## Uso en sesión (recomendado, no auditado)

- Plan mode en tareas complejas.
- `/compact` manual, con una indicación de qué conservar, al llegar a ~50 % del contexto.
- Tarea nueva, sesión nueva.
- Subtareas que quepan en menos del 50 % del contexto.

## Consulta previa (§11.5)

Antes de responder o proponer configuración de Claude Code (skills, subagentes, hooks, settings, memoria, MCP), el agente busca en el pin (`best-practice/`, `tips/`, `reports/`, `README.md`) y cita el archivo. Solo si no está ahí recurre a la documentación oficial.

## Qué no se adopta (§11.6)

Las reglas propias de ese repositorio (un commit por archivo, el sistema de ejemplo del clima, los sonidos de hooks) no son un estándar. Los commits siguen `docs/commit-conventions.md`.

## Auditoría (§11.7)

`check_claude_config()` en `scripts/audit-standards.py` exige `AGENTS.md` o `CLAUDE.md`, ninguno de más de 200 líneas y, si existe `.claude/`, que `.gitignore` excluya `settings.local.json`. El resto (subagentes, skills, `.claude/rules/`) se revisa en el PR que toca la configuración.

## Actualizar el pin

1. `git submodule update --remote knowledge/standards/claude-code-best-practice` y revisar el diff de `best-practice/` y `README.md`.
2. Anotar el commit nuevo en `AGENTS.md`, RULES.md §11.1, `CLAUDE_BP_COMMIT` de `scripts/bootstrap-project.sh`, `knowledge/standards/README.md` y esta página.
3. Registrar el cambio en `CHANGELOG.md` y regenerar `contexto_proyecto.md`.
