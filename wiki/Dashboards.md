# Dashboards — dev-standards

Estética y revisión de dashboards según RULES.md §8. El estándar es el skill [`dickwu/apple-design-skill`](https://github.com/dickwu/apple-design-skill), que revisa diseños contra las Human Interface Guidelines de Apple (123 páginas) y además aplica un lente de *craft* que detecta UI de plantilla.

Commit fijado: `39ea3fbab3011e0798c076dbeabf4917001499da` (2026-09-22).

## Por qué no se copia a los repos

El texto de las guías es de Apple Inc. y el repositorio del skill no incluye archivo de licencia. Por eso cada proyecto lo instala o lo referencia en vez de vendorizarlo.

## Instalación en un proyecto

Opción A, con el CLI de skills (Claude Code, Cursor, Codex y otros agentes):

```bash
npx skills add dickwu/apple-design-skill -a claude-code
```

Opción B, como submódulo fijado. Es la variante que usa este repo, en `.claude/skills/apple-design`, donde Claude Code detecta el skill sin configuración:

```bash
git submodule add https://github.com/dickwu/apple-design-skill.git .claude/skills/apple-design
git -C .claude/skills/apple-design checkout 39ea3fbab3011e0798c076dbeabf4917001499da
git add .gitmodules .claude/skills/apple-design
```

Al clonar un repo con el submódulo: `git clone --recurse-submodules …` o, en un clon existente, `git submodule update --init`.

Opción C, submódulo en `.design-rules/`, para agentes que leen `AGENTS.md` o archivos de reglas:

```bash
git submodule add https://github.com/dickwu/apple-design-skill.git .design-rules
git -C .design-rules checkout 39ea3fbab3011e0798c076dbeabf4917001499da
git add .gitmodules .design-rules
```

Con la opción B, agregar al `AGENTS.md` o `CLAUDE.md` del proyecto:

```markdown
## Revisión de dashboards (RULES.md §8)

Seguir `.design-rules/SKILL.md`. Rutear temas con `.design-rules/references/hig-lookup.md` y cargar
los `.design-rules/references/hig/*.md` relevantes antes de dar feedback de diseño.
```

## Flujo en un PR que toca un dashboard

1. Pedir la revisión: en Claude Code, `/apple-design` o *"Review this dashboard against Apple's HIG"*.
2. Además del set que el skill carga siempre, cargar `charting-data.md`, `charts.md` y `dark-mode.md`, y según lo que haya en pantalla `gauges.md`, `lists-and-tables.md`, `sidebars.md`, `widgets.md`, `materials.md` o `loading.md`.
3. Pegar el reporte en la descripción del PR, con estas secciones: Summary, Critical, Improvements, Craft notes, What works, Platform notes.
4. Resolver todo hallazgo **Critical** antes del merge. Los High se resuelven o se justifican en el PR.

## Checklist rápido (§8.5)

| Ítem | Criterio |
|------|----------|
| Contraste | 4.5:1 para texto de hasta 17 pt; 3:1 para ≥18 pt o negrita. Calculado a partir del hex |
| Texto mínimo | 10 pt en escritorio, 11 pt en móvil |
| Controles | 28×28 pt en escritorio (mínimo 20×20); 44×44 pt en móvil (mínimo 28×28) |
| Color | Un color, un significado; nunca como único canal; separadores entre áreas contiguas |
| Claro / oscuro | Ambos modos con tokens semánticos; *reduced motion* y *increased contrast* respetados |
| Blur / vidrio | Solo en la capa flotante (barras, paneles), nunca sobre datos |
| Tipo de gráfico | Barra, línea o punto salvo razón explícita; barras con eje Y desde 0 |
| Ejes | Ticks en secuencias familiares (0, 5, 10…); grid liviano que no compita con los datos |
| Texto | Título + resumen del mensaje principal por gráfico; etiquetas accesibles con valores reales |
| Interacción | Nada crítico escondido detrás de hover o scrub |
| Consistencia | Mismo propósito → mismo estilo; misma serie → mismo color en todo el dashboard |
| Tabla vs. gráfico | Si solo se muestran valores, tabla ordenable/buscable |
| Plantilla | Ninguno de los tres looks genéricos de §8.6; un solo elemento distintivo |
| Tokens | 4–6 colores con rol y variante clara/oscura, y escala tipográfica, definidos en el SSoT (§8.7) |

## Alcance

- **Web / Android** (incluye Looker Studio, Grafana, Streamlit): principios y fundamentos. Las convenciones de plataforma de Apple no aplican.
- **iOS / iPadOS / macOS nativo, Tauri, Electron**: todo lo anterior más las convenciones de plataforma (menu bar, sidebars, toolbars).
- Herramientas con tema cerrado (por ejemplo, Looker Studio): se aplican los mínimos que la herramienta permita controlar (paleta, contraste, tipos de gráfico, títulos y resúmenes) y lo que no se pueda controlar se anota como limitación en la revisión.

## Actualizar el pin

1. Revisar los cambios upstream (`git log` del skill) y el changelog de las páginas HIG afectadas.
2. Cambiar el commit en RULES.md §8.1 y en esta página.
3. Registrar el cambio en `CHANGELOG.md`.
