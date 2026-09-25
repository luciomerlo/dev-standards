# Graft — dev-standards

Grafo de contexto del código para agentes, según RULES.md §9. Usa [`trailhq/Graft`](https://github.com/trailhq/Graft) (npm `@nanonets/graft`, MIT), fijado a la versión `0.19.0`.

## Qué hace

- Con tree-sitter, sin LLM ni key, construye `graft/`: un grafo por símbolo (`graft/.graph/wiring.json`) y tarjetas markdown por archivo.
- Conecta el grafo a Claude Code con un skill, hooks (statusline, blast radius al editar, re-sync al final de cada turno) y un servidor MCP (`graft_find_code`, `graft_file_api`, `graft_trace_calls`, `graft_find_all`, `graft_repo_map`, `graft_check_freshness`).
- Cada consulta refresca el grafo contra el working tree (~3 ms si no cambió nada), así que no hay índice desactualizado que mantener.

## Instalación (una vez por máquina)

```bash
npm install -g @nanonets/graft@0.19.0   # Node >= 20
graft telemetry disable                 # §9.5
```

## Conectar un repositorio

```bash
graft init --agents claude --no-global --dry-run   # revisar qué escribe
graft init --agents claude --no-global
git add .claude .mcp.json .ignore .gitignore
git commit -m "chore: wire in graft (RULES.md §9)"
```

`--no-global` evita escribir en `~/.claude` / `~/.codex`. Para otros agentes: `--agents claude agents cursor` (ids: `graft init --list-agents`).

`bootstrap-project.sh` ejecuta este paso si `graft` está en el `PATH`.

## Qué se versiona y qué no

| Ruta | Versionar | Nota |
|------|-----------|------|
| `.claude/settings.json` | Sí | `init` fusiona sus bloques; no pisa lo existente |
| `.claude/helpers/graft-*.cjs` | Sí | Shims. Contienen la ruta de instalación global de la máquina que corrió `init`; en otras máquinas resuelven el paquete con `npm root -g` |
| `.claude/skills/graft/SKILL.md` | Sí | Skill para Claude Code |
| `.mcp.json` | Sí | Registra el servidor MCP (`graft mcp`) |
| `.ignore` | Sí | Mantiene `graft/` visible para ripgrep aunque esté en `.gitignore` |
| `graft/` | **No** | Caché local; cada colaborador corre `graft build` |

## Uso diario

```bash
graft ask "¿dónde se valida el token?"      # nodos rankeados con file:line
graft callers audit_project -d 2             # quién depende de un símbolo
graft map                                    # orientación del repo
graft blast --base origin/main --format markdown   # radio de impacto de un PR (§9.6)
graft check                                  # exit 1 si el grafo se desvió del código
```

## Capa LLM (opcional)

`graft build --deep` agrega resúmenes por archivo y nodos conceptuales, y para eso envía el código al proveedor configurado. Solo se usa con un proveedor autorizado para el código del proyecto y con la key por entorno (`GRAFT_PROVIDER`, `GRAFT_API_KEY`, `GRAFT_MODEL`), nunca versionada (§6.4).

## Relación con otros estándares

- **`contexto_proyecto.md` (§5.10):** es un volcado estático y portable a cualquier LLM. Graft es un índice vivo para la sesión del agente. Se mantienen los dos, y el generador de contexto excluye `graft/`.
- **Auditoría (§5.7):** `check_graft()` exige el skill o la entrada `graft` en `.mcp.json`, y `/graft/` en `.gitignore`.

## Desinstalar

```bash
graft uninstall -y --no-global
```
