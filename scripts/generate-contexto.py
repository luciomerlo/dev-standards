#!/usr/bin/env python3
"""generate-contexto.py — Genera contexto_proyecto.md (RULES.md §5.10).

Uso:
  python scripts/generate-contexto.py
  python scripts/generate-contexto.py --root /ruta/al/repo

Recorre el árbol (sin carpetas de build, binarios ni dependencias) y escribe
en la raíz un único archivo con el resumen de arquitectura y el contenido
completo de cada archivo de código, configuración o Markdown normativo.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "bin",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "obj",
    "target",
    "vendor",
    "venv",
}

# Salidas generadas: no se vuelcan (el propio contexto se excluye por ruta).
ROOT_GENERATED = {"AUDIT_REPORT.md", "project_audit_summary.csv"}

BINARY_SUFFIXES = {
    ".7z",
    ".arrow",
    ".bin",
    ".db",
    ".dll",
    ".dylib",
    ".eot",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".model",
    ".mp3",
    ".mp4",
    ".onnx",
    ".otf",
    ".parquet",
    ".pdf",
    ".pkl",
    ".png",
    ".pth",
    ".pyc",
    ".pyo",
    ".safetensors",
    ".so",
    ".sqlite",
    ".tgz",
    ".ttf",
    ".wasm",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}

SUFFIX_LANG = {
    ".bash": "bash",
    ".c": "c",
    ".cfg": "ini",
    ".cjs": "javascript",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".csv": "csv",
    ".go": "go",
    ".h": "c",
    ".hpp": "cpp",
    ".htm": "html",
    ".html": "html",
    ".ini": "ini",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "jsx",
    ".kt": "kotlin",
    ".lua": "lua",
    ".md": "markdown",
    ".mjs": "javascript",
    ".php": "php",
    ".ps1": "powershell",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".scss": "scss",
    ".sh": "bash",
    ".sql": "sql",
    ".svelte": "svelte",
    ".swift": "swift",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".txt": "text",
    ".vue": "vue",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
}

EXT_LANGUAGE = {
    ".css": "CSS",
    ".go": "Go",
    ".html": "HTML",
    ".htm": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".php": "PHP",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Bash",
    ".bash": "Bash",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

DOTFILES = {
    ".continueignore",
    ".dockerignore",
    ".editorconfig",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    ".nvmrc",
    ".python-version",
    ".tool-versions",
}

SPECIAL_NAMES = {"containerfile", "dockerfile", "jenkinsfile", "makefile"}

FRAMEWORKS = {
    "actix-web": "Actix Web",
    "django": "Django",
    "express": "Express",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "gin": "Gin",
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
}


class Tree:
    def __init__(self) -> None:
        self.dirs: dict[str, Tree] = {}
        self.files: list[str] = []


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera contexto_proyecto.md (RULES.md §5.10)")
    parser.add_argument("--root", type=Path, default=None, help="Raíz del repositorio")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Ruta de salida (por defecto <root>/contexto_proyecto.md)",
    )
    return parser.parse_args(argv)


def want(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    if path.name.lower() in SPECIAL_NAMES or path.name.lower() in DOTFILES:
        return True
    return path.suffix.lower() in SUFFIX_LANG


def opening_fence(content: str) -> str:
    longest = 0
    current = 0
    for ch in content:
        if ch == "`":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return "`" * max(3, longest + 1)


def language_for(path: Path) -> str:
    name = path.name.lower()
    if name in {"dockerfile", "containerfile"}:
        return "dockerfile"
    if name == "makefile":
        return "makefile"
    if name in {".gitignore", ".dockerignore", ".continueignore"}:
        return "gitignore"
    if name == ".env.example":
        return "dotenv"
    if name == ".editorconfig":
        return "ini"
    return SUFFIX_LANG.get(path.suffix.lower(), "text")


def collect(
    root: Path, output: Path
) -> tuple[list[tuple[str, str]], list[str], list[str], list[str]]:
    """Devuelve (archivos, dirs excluidos, generados, otros no volcados)."""
    files: list[tuple[str, str]] = []
    skipped_dirs: list[str] = []
    skipped_generated: list[str] = []
    skipped_other: list[str] = []
    output_resolved = output.resolve()

    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        kept: list[str] = []
        for dirname in sorted(dirnames):
            if dirname in EXCLUDE_DIRS:
                skipped_dirs.append((current / dirname).relative_to(root).as_posix())
                continue
            kept.append(dirname)
        dirnames[:] = kept

        for filename in sorted(filenames):
            path = current / filename
            rel = path.relative_to(root).as_posix()
            try:
                if path.resolve() == output_resolved:
                    skipped_generated.append(rel)
                    continue
            except OSError:
                skipped_other.append(rel)
                continue
            if current == root and filename in ROOT_GENERATED:
                skipped_generated.append(rel)
                continue
            if not want(path):
                skipped_other.append(rel)
                continue
            try:
                blob = path.read_bytes()
            except OSError:
                skipped_other.append(rel)
                continue
            if b"\0" in blob:
                skipped_other.append(rel)
                continue
            text = blob.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
            files.append((rel, text))

    files.sort(key=lambda item: item[0].lower())
    return files, skipped_dirs, skipped_generated, skipped_other


def first_paragraph(path: Path) -> str:
    if not path.is_file():
        return ""
    buf: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if buf:
                break
            continue
        structural = (
            stripped.startswith("#")
            or stripped.startswith("![")
            or stripped.startswith("|")
            or stripped.startswith("<!--")
            or stripped.startswith("```")
            or stripped.startswith(">")
        )
        if structural:
            if buf:
                break
            continue
        buf.append(stripped)
    return " ".join(buf)


def quoted_field(text: str, field: str) -> str:
    match = re.search(rf'^{re.escape(field)}\s*=\s*"([^"]*)"', text, re.MULTILINE)
    return match.group(1) if match else ""


def quoted_deps(text: str) -> list[str]:
    return re.findall(
        r'^\s*"([A-Za-z0-9_.-]+(?:\[[^\]]+\])?(?:[<>=!~][^"]*)?)"\s*,?\s*$',
        text,
        re.MULTILINE,
    )


def package_json_deps(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    found: list[str] = []
    if isinstance(data, dict):
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            block = data.get(key)
            if isinstance(block, dict):
                for name, version in block.items():
                    found.append(f"{name}@{version}")
    return found


def cargo_deps(text: str) -> list[str]:
    deps: list[str] = []
    in_deps = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_deps = stripped in {"[dependencies]", "[dev-dependencies]"}
            continue
        if in_deps:
            match = re.match(r"^([A-Za-z0-9_-]+)\s*=", stripped)
            if match:
                deps.append(match.group(1))
    return deps


def go_deps(text: str) -> list[str]:
    deps: list[str] = []
    in_require = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if in_require and stripped == ")":
            in_require = False
            continue
        if in_require or stripped.startswith("require "):
            parts = stripped.replace("require ", "", 1).split()
            if parts and not parts[0].startswith("//"):
                deps.append(parts[0])
    return deps


def canon(text: str) -> str:
    return re.sub(r"[.\s]+$", "", text.strip()).casefold()


def unique(items: list[str]) -> list[str]:
    ordered: list[str] = []
    index: dict[str, int] = {}
    for item in items:
        key = item.strip()
        if not key:
            continue
        token = canon(key)
        if token in index:
            if len(key) > len(ordered[index[token]]):
                ordered[index[token]] = key
            continue
        index[token] = len(ordered)
        ordered.append(key)
    return ordered


def purpose_text(root: Path) -> str:
    parts: list[str] = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        manifest = pyproject.read_text(encoding="utf-8", errors="replace")
        parts.append(quoted_field(manifest, "description"))
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict) and isinstance(data.get("description"), str):
            parts.append(data["description"])
    parts.append(first_paragraph(root / "README.md"))
    parts.append(first_paragraph(root / "wiki" / "Home.md"))
    kept = unique(parts)
    if kept:
        return " ".join(kept)
    return "Propósito pendiente de declarar en el manifiesto o en el README."


def framework_names(deps: list[str]) -> list[str]:
    found: list[str] = []
    for dep in deps:
        base = re.split(r"[<>=@\[]", dep, maxsplit=1)[0].strip().lower()
        label = FRAMEWORKS.get(base)
        if label and label not in found:
            found.append(label)
    return found


def stack_lines(root: Path, rels: list[str]) -> list[str]:
    languages: list[str] = []
    for rel in rels:
        label = EXT_LANGUAGE.get(Path(rel).suffix.lower())
        if label and label not in languages:
            languages.append(label)
    lang_order = [
        "Python",
        "Bash",
        "JavaScript",
        "TypeScript",
        "Go",
        "Rust",
        "Java",
        "Kotlin",
        "Ruby",
        "PHP",
        "HTML",
        "CSS",
        "PowerShell",
    ]
    rank = {name: i for i, name in enumerate(lang_order)}
    languages.sort(key=lambda name: (rank.get(name, len(rank)), name))

    runtime: list[str] = []
    deps: list[str] = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        requires = quoted_field(text, "requires-python")
        if requires:
            runtime.append(f"Python {requires}")
        if "Python" not in languages:
            languages.insert(0, "Python")
        deps.extend(quoted_deps(text))

    package_json = root / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if isinstance(data, dict):
            engines = data.get("engines")
            if isinstance(engines, dict) and engines.get("node"):
                runtime.append(f"Node.js {engines['node']}")
        if "JavaScript" not in languages:
            languages.append("JavaScript")
        deps.extend(package_json_deps(package_json))

    cargo = root / "Cargo.toml"
    if cargo.is_file():
        deps.extend(cargo_deps(cargo.read_text(encoding="utf-8", errors="replace")))
        if "Rust" not in languages:
            languages.append("Rust")
    gomod = root / "go.mod"
    if gomod.is_file():
        deps.extend(go_deps(gomod.read_text(encoding="utf-8", errors="replace")))
        if "Go" not in languages:
            languages.append("Go")

    dockerfile = root / "Dockerfile"
    images: list[str] = []
    if dockerfile.is_file():
        images = re.findall(
            r"^FROM\s+(\S+)",
            dockerfile.read_text(encoding="utf-8", errors="replace"),
            re.MULTILINE | re.IGNORECASE,
        )

    platform: list[str] = []
    platform.extend(framework_names(deps))
    if dockerfile.is_file():
        platform.append("Docker")
    workflows = root / ".github" / "workflows"
    has_workflows = workflows.is_dir() and (
        any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))
    )
    if has_workflows:
        platform.append("GitHub Actions")
    if ".pre-commit-config.yaml" in rels:
        platform.append("pre-commit")
    if any(Path(rel).name.startswith("commitlint") for rel in rels):
        platform.append("commitlint")
    if (root / "config.yaml").is_file():
        platform.append("config.yaml como fuente única de configuración")

    lines: list[str] = []
    if languages:
        lines.append(f"  - Lenguajes: {', '.join(languages)}.")
    if runtime or images:
        bits = list(runtime)
        if images:
            bits.append("imágenes Docker " + ", ".join(unique(images)))
        lines.append(f"  - Runtime: {'; '.join(bits)}.")
    if platform:
        lines.append(f"  - Frameworks y plataforma: {', '.join(platform)}.")
    if deps:
        lines.append(f"  - Dependencias principales: {', '.join(unique(deps))}.")
    if not lines:
        lines.append("  - Stack no declarado en manifiestos ni extensiones de código.")
    return lines


def render_tree(rels: list[str]) -> str:
    root = Tree()
    for rel in rels:
        parts = rel.split("/")
        node = root
        for part in parts[:-1]:
            node = node.dirs.setdefault(part, Tree())
        node.files.append(parts[-1])
    lines = ["."]

    def walk(node: Tree, prefix: str) -> None:
        entries: list[tuple[str, Tree | None]] = []
        for name, child in sorted(node.dirs.items()):
            entries.append((name, child))
        for name in sorted(node.files):
            entries.append((name, None))
        for index, (name, child) in enumerate(entries):
            last = index == len(entries) - 1
            branch = "└── " if last else "├── "
            if child is None:
                lines.append(f"{prefix}{branch}{name}")
                continue
            lines.append(f"{prefix}{branch}{name}/")
            walk(child, prefix + ("    " if last else "│   "))

    walk(root, "")
    return "\n".join(lines)


def code_block(rel: str, content: str) -> str:
    lang = language_for(Path(rel))
    fence = opening_fence(content)
    body = content if content.endswith("\n") or content == "" else content + "\n"
    return f"## Ruta: `{rel}`\n\n{fence}{lang}\n{body}{fence}\n"


def render(
    root: Path,
    files: list[tuple[str, str]],
    skipped_dirs: list[str],
    skipped_generated: list[str],
    skipped_other: list[str],
) -> str:
    rels = [rel for rel, _text in files]
    excluded_bits: list[str] = []
    if skipped_dirs:
        excluded_bits.append("carpetas " + ", ".join(f"`{name}`" for name in skipped_dirs))
    if skipped_generated:
        excluded_bits.append("generados " + ", ".join(f"`{name}`" for name in skipped_generated))
    if skipped_other:
        excluded_bits.append("no relevantes " + ", ".join(f"`{name}`" for name in skipped_other))

    summary = [
        "# RESUMEN Y ARQUITECTURA",
        "",
        f"- Propósito general del proyecto: {purpose_text(root)}",
        "",
        "- Stack tecnológico, lenguajes, frameworks y dependencias principales:",
        *stack_lines(root, rels),
        "",
        "- Árbol de directorios y archivos relevantes "
        f"({len(files)} archivos volcados a continuación; "
        "se excluyen carpetas de build, binarios y dependencias como "
        "node_modules, bin, obj, .git, venv):",
        "",
        "```text",
        render_tree(rels),
        "```",
        "",
    ]
    if excluded_bits:
        summary.append("- Fuera del volcado de contenido: " + "; ".join(excluded_bits) + ".")
        summary.append("")
    summary.append("# ARCHIVOS DEL PROYECTO")
    summary.append("")
    body = "\n".join(summary)
    blocks = "\n".join(code_block(rel, text) for rel, text in files)
    return body + "\n" + blocks


def generate(root: Path, output: Path) -> int:
    root = root.resolve()
    if not root.is_dir():
        sys.stderr.write(f"No existe el directorio: {root}\n")
        return 2
    if not output.is_absolute():
        output = root / output
    files, skipped_dirs, skipped_generated, skipped_other = collect(root, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render(root, files, skipped_dirs, skipped_generated, skipped_other),
        encoding="utf-8",
        newline="\n",
    )
    sys.stdout.write(f"Escrito {output} ({len(files)} archivos)\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root if args.root is not None else Path.cwd()
    output = args.output if args.output is not None else Path("contexto_proyecto.md")
    return generate(root, output)


if __name__ == "__main__":
    sys.exit(main())
