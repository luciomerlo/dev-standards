# AGENTS.md — dev-standards

Este repositorio es la base de conocimiento de ingeniería del ecosistema. La fuente de verdad es [RULES.md](RULES.md). Todo repositorio que lo use como base aplica las reglas de RULES.md y, además, los **estándares externos** de esta tabla, en las versiones fijadas.

## Estándares externos a aplicar en repos consumidores

| Estándar | Regla | Aplica a | Versión fijada | Cómo se instala en el repo consumidor |
|----------|-------|----------|----------------|---------------------------------------|
| [`dickwu/apple-design-skill`](https://github.com/dickwu/apple-design-skill) | §8 | Repos con dashboard, panel o vista de datos | commit `39ea3fbab3011e0798c076dbeabf4917001499da` | `git submodule add https://github.com/dickwu/apple-design-skill.git .claude/skills/apple-design` y luego `git -C .claude/skills/apple-design checkout 39ea3fb…`; o `bootstrap-project.sh --dashboard` |
| [`trailhq/Graft`](https://github.com/trailhq/Graft) (`@nanonets/graft`) | §9 | Todo repo con código fuente | `0.19.0` | `npm install -g @nanonets/graft@0.19.0 && graft init --agents claude --no-global` |
| [`shanraisshan/claude-code-best-practice`](https://github.com/shanraisshan/claude-code-best-practice) | §11 | Todo repo con `CLAUDE.md`, `AGENTS.md` o `.claude/` | commit `bfcf0b5abc7f9bb5da9bd41cbba070d9cef330d2` | No se instala: se consulta el pin en `knowledge/standards/claude-code-best-practice` de este repo y se cumplen los mínimos de §11.3 |
| Skill `/fix` | §3.4 | Repos con interfaz web | — | Se corre al cerrar el desarrollo inicial, antes del primer release |

Cambiar una versión fijada es un cambio explícito en este repo: actualizar esta tabla, la regla correspondiente de RULES.md, las constantes de `scripts/bootstrap-project.sh` (`APPLE_DESIGN_COMMIT`, `GRAFT_VERSION`, `PUBLIC_APIS_COMMIT`, `CLAUDE_BP_COMMIT`) y el CHANGELOG, todo en el mismo cambio.

## Bases de conocimiento públicas

Catálogos de referencia, no estándares. Un agente los consulta cuando el trabajo lo pide. Viven solo en este repo, como submódulos fijados bajo `knowledge/public/`. No se copian a los repos consumidores. `generate-contexto.py` no vuelca su contenido.

| Base | Regla | Para qué | Versión fijada | Dónde está |
|------|-------|----------|----------------|------------|
| [`public-apis/public-apis`](https://github.com/public-apis/public-apis) | §10 | Elegir una API HTTP pública | commit `7598f906a610c6d6ebf7adc2e72b6b5fccc7eba0` | `knowledge/public/public-apis` |

Actualizar un pin es un cambio explícito: esta tabla, RULES.md §10, `PUBLIC_APIS_COMMIT` en `scripts/bootstrap-project.sh` y el CHANGELOG, en el mismo cambio.

## Qué hacer como agente

- **Trabajando en un repo consumidor:** leer su `AGENTS.md` (§5.11) y aplicar los estándares de la tabla que correspondan. Si el repo tiene un dashboard y no tiene `.claude/skills/apple-design`, proponer instalarlo en el mismo cambio. Todo PR que toque un dashboard lleva la revisión de `/apple-design`, y sus hallazgos Critical bloquean el merge. Antes de proponer configuración de Claude Code (skills, subagentes, hooks, settings, memoria), consultar el pin de §11 (`knowledge/standards/claude-code-best-practice`) y citar el archivo. Antes de proponer una API HTTP pública, consultar el catálogo de §10 en este repo con `python scripts/find-public-api.py --category <cat> --https` (o `--query "<texto>"`) y citar la entrada elegida.
- **Trabajando en dev-standards:** este repo aplica sus propios estándares. `apple-design-skill` está como submódulo en `.claude/skills/apple-design` y `public-apis` en `knowledge/public/public-apis` y `claude-code-best-practice` en `knowledge/standards/claude-code-best-practice` (clonar con `--recurse-submodules`). Graft está conectado (`graft ask` antes de leer código). Todo cambio de reglas actualiza `wiki/`, `CHANGELOG.md` y `contexto_proyecto.md` en el mismo commit.
