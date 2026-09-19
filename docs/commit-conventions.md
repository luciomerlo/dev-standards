# Convenciones de commits

Basado en [Conventional Commits 1.0.0](https://www.conventionalcommits.org/).

## 1. Formato

```
<tipo>(<scope opcional>): <descripción corta en imperativo>

<cuerpo opcional>

<footer opcional>
```

## 2. Tipos permitidos

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Cambios solo de documentación |
| `style` | Formato, sin cambio de lógica (espacios, punto y coma) |
| `refactor` | Cambio de código que no agrega feature ni corrige bug |
| `perf` | Mejora de rendimiento |
| `test` | Agregar o corregir tests |
| `build` | Cambios en build system o dependencias |
| `ci` | Cambios en configuración de CI/CD |
| `chore` | Tareas de mantenimiento sin impacto en `src` ni tests |
| `revert` | Revierte un commit previo |

## 3. Reglas

- Descripción en modo imperativo, minúscula inicial, sin punto final: `fix: corrige cálculo de sag en suspensión`, no `Fixed bug`.
- Máximo 72 caracteres en la primera línea.
- Scope opcional entre paréntesis indicando módulo/área: `feat(auth): agrega login con OAuth`.
- Cuerpo (si existe) explica el **por qué**, separado por línea en blanco, envuelto a 100 caracteres.
- Breaking changes: footer `BREAKING CHANGE: <descripción>` o `!` tras el tipo/scope (`feat!:`).
- Referencia a issues en el footer: `Refs: #123` o `Closes: #123`.
- Un commit = un cambio lógico atómico. No mezclar `feat` y `fix` no relacionados.

## 4. Ejemplos

```
feat(billing): agrega soporte para facturación en USD

fix(api): corrige timeout en endpoint de exportación

Refs: #482
```

```
refactor!: elimina soporte de Node 16

BREAKING CHANGE: requiere Node >=18 por uso de fetch nativo.
```

## 5. Branches

- Formato: `tipo/descripcion-corta` (mismo vocabulario de tipos que los commits).
- Ejemplos: `feat/login-oauth`, `fix/timeout-export`, `chore/update-deps`.
- Un PR por branch, título alineado al tipo del cambio principal.

## 6. Pull Requests

- Título en el mismo formato que un commit (`tipo(scope): descripción`).
- Descripción: qué cambia y por qué, no cómo (el diff ya lo muestra).
- Squash merge recomendado; el mensaje final del squash debe cumplir esta convención.
