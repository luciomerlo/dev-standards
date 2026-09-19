# Goodbye Serena — reemplazo por LSP nativo de oh-my-claudecode

## Qué se hizo

Serena removida de `~/.claude.json` (scope user) — no arranca más en ningún proyecto, tray se limpia.

## Reemplazo

Tools `mcp__plugin_oh-my-claudecode_t__lsp_*` del plugin `oh-my-claudecode` (ya instalado como plugin, corre in-process vía `bridge/mcp-server.cjs`, sin proceso `uvx`/dashboard extra por proyecto).

Instalé `ty` (LSP Python de astral-sh, vía `uv tool install ty`) — verificado funcionando en `library.py`.

## Herramienta a instalar en otros proyectos

Plugin `oh-my-claudecode` (ya instalado globalmente, marketplace `omc`). Da:

- `lsp_goto_definition`
- `lsp_find_references`
- `lsp_rename`
- `lsp_document_symbols`
- `lsp_diagnostics`
- etc.

Solo falta instalar el LSP server del lenguaje de cada proyecto — `mcp__plugin_oh-my-claudecode_t__lsp_servers` dice cuál falta y comando de instalación por stack (Go: `gopls`, TS: `typescript-language-server`, Python: `ty`, etc).

## Proyectos con Serena referenciado (`.serena/`)

- `D:\projects\.serena` (root, nivel general)
- `D:\projects\ArtistMusicDownloader`
- `D:\projects\CultsDL`
- `D:\projects\FreeNewsForAll` (+ worktrees en `.claude/worktrees/*`)
- `D:\projects\LocalProjectsTracker`
- `D:\projects\ManualsVault`
- `D:\projects\MusicFolderSorter`
- `D:\projects\PiazzollaMidiGenerator`
- `D:\projects\StoreWishesPurchases`
- `D:\projects\StremioSpeed`
- `D:\projects\youtube-transcript-processor-private`
- `D:\projects\YTTranscript`

## Acción pendiente por proyecto

1. Borrar carpeta `.serena/` (y memories si las tiene).
2. Confirmar plugin `oh-my-claudecode` activo.
3. Correr `lsp_servers` para ver LSP faltante del stack del proyecto.
4. Instalar LSP server correspondiente.
5. Verificar `lsp_goto_definition` / `lsp_diagnostics` funcionando en archivo real del proyecto.
