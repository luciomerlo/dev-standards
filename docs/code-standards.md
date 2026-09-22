# Estándares de código

## 1. Nomenclatura

| Elemento | Convención | Ejemplo |
|---|---|---|
| Variables / funciones | `camelCase` | `getUserData()` |
| Clases / tipos / interfaces | `PascalCase` | `UserRepository` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Archivos | `kebab-case` (excepto componentes de clase, ver stack) | `user-service.ts` |
| Branches | `tipo/descripcion-corta` | `feat/login-oauth` |
| Booleanos | prefijo `is`/`has`/`can` | `isActive`, `hasPermission` |

Nombres descriptivos y pronunciables. Evitar abreviaturas ambiguas (`usr`, `tmp2`, `dataX`).

## 2. Formato y linting

- Formateo automático obligatorio antes de commit (Prettier, Black, gofmt, según stack).
- Linter configurado con reglas estrictas (ESLint, Ruff, golangci-lint). Cero warnings tolerados en CI.
- Indentación: 2 espacios (JS/TS/JSON/YAML) o 4 espacios (Python), sin tabs. Ver `.editorconfig`.
- Longitud de línea: 100 caracteres como límite blando.

## 3. Estructura de proyecto

- Un módulo/paquete = una responsabilidad.
- Separar capas: `domain` / `application` / `infrastructure` / `interfaces` (o equivalente al stack).
- Tests junto al código que prueban (`*.test.ts`, `test_*.py`) o en `tests/` espejando la estructura de `src/`.
- Sin código muerto ni comentado en el repositorio.

## 4. Manejo de errores

- No silenciar excepciones (`catch {}` vacío prohibido).
- Errores de negocio como tipos explícitos, no strings genéricos.
- Logging estructurado (JSON) en producción, nunca `print`/`console.log` residual.
- Validar únicamente en los límites del sistema (entrada de usuario, API externa); confiar en invariantes internas.

## 5. Comentarios y documentación

- Código autoexplicativo por naming; comentarios solo para el **porqué**, no el qué.
- Sin bloques de documentación multi-línea salvo en APIs públicas de librerías.
- README por módulo solo si el módulo se consume fuera del equipo.
- Onboarding, arquitectura, runbook y troubleshooting viven en `wiki/` (RULES.md §5.9), no en comentarios ni en READMEs de módulo.

## 6. Testing

- Cobertura mínima exigida por CI: 80% en lógica de negocio.
- Un test = un comportamiento. Nombres descriptivos: `should_reject_expired_token`.
- Tests deterministas: sin dependencias de red, tiempo real o orden de ejecución.

## 7. Revisión de código (checklist mínimo)

- [ ] Compila / pasa linter y typecheck sin warnings.
- [ ] Tests nuevos para el comportamiento agregado.
- [ ] Sin secretos, credenciales o URLs internas hardcodeadas (verificado por `scripts/check-secrets.py`, RULES.md §6).
- [ ] Si el cambio toca código, configuración o documentación normativa, `contexto_proyecto.md` fue regenerado (`python scripts/generate-contexto.py`, RULES.md §5.10).
- [ ] Sin abstracciones o flags innecesarios para el alcance del cambio.
- [ ] Commits siguen `docs/commit-conventions.md`.
