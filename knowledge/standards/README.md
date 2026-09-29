# Estándares de referencia externos

Repositorios de terceros que fijan un estándar de dev-standards (RULES.md §11). Cada uno es un submódulo fijado: este árbol guarda el commit, no una copia que se edita a mano. No se copian a los repos consumidores; su `AGENTS.md` apunta al pin de acá.

| Estándar | Ruta | Upstream | Pin | Licencia | Regla |
|----------|------|----------|-----|----------|-------|
| Claude Code best practice | [`claude-code-best-practice/`](claude-code-best-practice/README.md) | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | `bfcf0b5abc7f9bb5da9bd41cbba070d9cef330d2` | MIT | §11 |

Clonar con `git clone --recurse-submodules` (el submódulo es superficial, `shallow = true`, pero pesa ~77 MB por el material multimedia). En un clon existente:

```bash
git submodule update --init knowledge/standards/claude-code-best-practice
```

`scripts/generate-contexto.py` excluye estas rutas (están en `.gitmodules`).
