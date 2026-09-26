# AGENTS.md — dev-standards

Este repositorio es la base de conocimiento de ingeniería del ecosistema. La fuente de verdad es [RULES.md](RULES.md). Todo repositorio que lo use como base aplica las reglas de RULES.md y, además, los **estándares externos** de esta tabla, en las versiones fijadas.

## Estándares externos a aplicar en repos consumidores

| Estándar | Regla | Aplica a | Versión fijada | Cómo se instala en el repo consumidor |
|----------|-------|----------|----------------|---------------------------------------|
| [`dickwu/apple-design-skill`](https://github.com/dickwu/apple-design-skill) | §8 | Repos con dashboard, panel o vista de datos | commit `39ea3fbab3011e0798c076dbeabf4917001499da` | `git submodule add https://github.com/dickwu/apple-design-skill.git .claude/skills/apple-design` y luego `git -C .claude/skills/apple-design checkout 39ea3fb…`; o `bootstrap-project.sh --dashboard` |
| [`trailhq/Graft`](https://github.com/trailhq/Graft) (`@nanonets/graft`) | §9 | Todo repo con código fuente | `0.19.0` | `npm install -g @nanonets/graft@0.19.0 && graft init --agents claude --no-global` |
| Skill `/fix` | §3.4 | Repos con interfaz web | — | Se corre al cerrar el desarrollo inicial, antes del primer release |

Cambiar una versión fijada es un cambio explícito en este repo: actualizar esta tabla, la regla correspondiente de RULES.md, las constantes de `scripts/bootstrap-project.sh` (`APPLE_DESIGN_COMMIT`, `GRAFT_VERSION`) y el CHANGELOG, todo en el mismo cambio.

## Qué hacer como agente

- **Trabajando en un repo consumidor:** leer su `AGENTS.md` (§5.11) y aplicar los estándares de la tabla que correspondan. Si el repo tiene un dashboard y no tiene `.claude/skills/apple-design`, proponer instalarlo en el mismo cambio. Todo PR que toque un dashboard lleva la revisión de `/apple-design`, y sus hallazgos Critical bloquean el merge.
- **Trabajando en dev-standards:** este repo aplica sus propios estándares. `apple-design-skill` está como submódulo en `.claude/skills/apple-design` (clonar con `--recurse-submodules`) y Graft está conectado (`graft ask` antes de leer código). Todo cambio de reglas actualiza `wiki/`, `CHANGELOG.md` y `contexto_proyecto.md` en el mismo commit.
