#!/usr/bin/env python3
"""find-public-api.py — Busca en el catálogo public-apis fijado (RULES.md §10.2).

Lee `knowledge/public/public-apis/README.md` (submódulo fijado) y filtra sus
tablas por categoría, texto, autenticación, HTTPS y CORS. Evita que un agente
cargue las ~2.000 filas del catálogo para elegir una API.

Uso:
    python scripts/find-public-api.py --list-categories
    python scripts/find-public-api.py --category Weather --https --auth none
    python scripts/find-public-api.py --query "exchange rate" --auth apiKey --json

Sin coincidencias, sale con código 1: el catálogo no cubre el caso (§10.2).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_CATALOG = (
    Path(__file__).resolve().parent.parent / "knowledge" / "public" / "public-apis" / "README.md"
)
# Tolera filas sin "|" final y URLs con espacios sobrantes, presentes en el catálogo.
ROW_RE = re.compile(r"^\|\s*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\s*\|(?P<rest>.*)$")
SPONSOR_MARKERS = ("utm_source=", "utm_campaign=")


@dataclass
class Entry:
    category: str
    name: str
    url: str
    description: str
    auth: str
    https: str
    cors: str
    sponsored: bool


def parse_catalog(text: str) -> list[Entry]:
    """Convierte las tablas `### <Categoría>` del README en entradas."""
    entries: list[Entry] = []
    category = ""
    for line in text.splitlines():
        if line.startswith("### "):
            category = line[4:].strip()
            continue
        m = ROW_RE.match(line)
        if not m or not category:
            continue
        cells = [c.strip() for c in m.group("rest").strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        description, auth, https, cors = cells[0], cells[1].strip("`"), cells[2], cells[3]
        url = m.group("url").strip()
        entries.append(
            Entry(
                category=category,
                name=m.group("name"),
                url=url,
                description=description,
                auth=auth,
                https=https,
                cors=cors,
                sponsored=any(s in url for s in SPONSOR_MARKERS),
            )
        )
    return entries


def matches(e: Entry, args: argparse.Namespace) -> bool:
    if args.category and args.category.lower() not in e.category.lower():
        return False
    if args.query:
        haystack = f"{e.name} {e.description}".lower()
        if not all(word in haystack for word in args.query.lower().split()):
            return False
    if args.auth:
        wanted = "no" if args.auth.lower() == "none" else args.auth.lower()
        if e.auth.lower() != wanted:
            return False
    if args.https and e.https.lower() != "yes":
        return False
    if args.cors and e.cors.lower() != "yes":
        return False
    return not (args.no_sponsored and e.sponsored)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Busca en el catálogo public-apis (§10.2)")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="README.md")
    parser.add_argument("--category", help="Subcadena del nombre de categoría (ej. Weather)")
    parser.add_argument("--query", help="Palabras que deben aparecer en nombre o descripción")
    parser.add_argument("--auth", help="none, apiKey, OAuth, X-Mashape-Key, User-Agent")
    parser.add_argument("--https", action="store_true", help="Solo HTTPS = Yes")
    parser.add_argument("--cors", action="store_true", help="Solo CORS = Yes")
    parser.add_argument("--no-sponsored", action="store_true", help="Excluir enlaces con utm_*")
    parser.add_argument("--list-categories", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args(argv)

    if not args.catalog.is_file():
        print(
            f"No existe {args.catalog}. Inicializar el submódulo: "
            "git submodule update --init knowledge/public/public-apis",
            file=sys.stderr,
        )
        return 2
    entries = parse_catalog(args.catalog.read_text(encoding="utf-8"))

    if args.list_categories:
        counts: dict[str, int] = {}
        for e in entries:
            counts[e.category] = counts.get(e.category, 0) + 1
        for cat, n in sorted(counts.items()):
            print(f"{cat} ({n})")
        return 0

    hits = [e for e in entries if matches(e, args)]
    if not hits:
        print("Sin coincidencias en el catálogo (§10.2: no inventar una entrada).", file=sys.stderr)
        return 1
    shown = hits[: args.limit]
    if args.json:
        print(json.dumps([asdict(e) for e in shown], ensure_ascii=False, indent=2))
    else:
        for e in shown:
            flag = " [patrocinado]" if e.sponsored else ""
            print(
                f"[{e.category}] {e.name}{flag} — {e.description}\n"
                f"    {e.url} · auth={e.auth} · https={e.https} · cors={e.cors}"
            )
        if len(hits) > len(shown):
            print(f"… {len(hits) - len(shown)} más (subir --limit)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
