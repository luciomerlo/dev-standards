# Bases de conocimiento públicas

Catálogos externos de referencia (RULES.md §10). Cada uno es un submódulo fijado: este árbol guarda el commit, no una copia que se edita a mano. No son estándares obligatorios y no se copian a los repos consumidores.

| Base | Ruta | Upstream | Pin | Licencia | Cuándo consultarla |
|------|------|----------|-----|----------|--------------------|
| Public APIs | [`public-apis/`](public-apis/README.md) | [public-apis/public-apis](https://github.com/public-apis/public-apis) | `7598f906a610c6d6ebf7adc2e72b6b5fccc7eba0` | MIT | Al elegir una API HTTP pública |

Clonar con `git clone --recurse-submodules`. En un clon ya existente:

```bash
git submodule update --init knowledge/public/public-apis
```

`scripts/generate-contexto.py` excluye estas rutas (están en `.gitmodules`) y no vuelca el catálogo en `contexto_proyecto.md`.
