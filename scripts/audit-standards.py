#!/usr/bin/env python3
"""
audit-standards.py — Auditoría automatizada de cumplimiento de dev-standards (RULES.md §5.7)

Uso:
  python audit-standards.py [--root D:\\Projects] [--output AUDIT_REPORT.md] [--fail-on-regression]

Escanea todos los proyectos bajo --root (excluyendo directorios que empiezan por '.')
y valida la presencia de:
  - Versión SemVer en manifiesto (package.json, pyproject.toml, Cargo.toml, go.mod, setup.py)
  - CHANGELOG.md (formato Keep a Changelog)
  - README.md con al menos una imagen (![...](...))
  - Wiki en wiki/ con páginas mínimas rellenas (RULES.md §5.9)
  - .gitignore
  - Dockerfile
  - CI (.github/workflows/*.yml)
  - .env.example
  - config.yaml (SSoT)
  - Cumplimiento básico de RULES.md §1-4 (retry, fallback, async, progress, error classification, cache, streaming, port control, db robustness)

Genera un reporte Markdown y opcionalmente falla si hay regresiones vs. línea base.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

@dataclass
class ProjectAudit:
    name: str
    path: str
    has_semver: bool
    has_changelog: bool
    readme_has_images: bool
    has_wiki: bool
    has_gitignore: bool
    has_dockerfile: bool
    has_ci: bool
    has_env_example: bool
    has_config_yaml: bool
    has_secret_scan: bool
    # RULES §1-4 checks
    has_retry_backoff: bool
    has_fallback_chain: bool
    has_async: bool
    has_progress: bool
    has_error_classification: bool
    has_cache: bool
    has_streaming: bool
    has_port_control: bool
    has_db_robustness: bool
    score: int  # 0-100
    details: Dict[str, Any]

def detect_language(project_path: Path) -> str:
    """Detecta el lenguaje principal del proyecto."""
    if (project_path / "pyproject.toml").exists() or (project_path / "setup.py").exists() or (project_path / "requirements.txt").exists():
        return "python"
    if (project_path / "package.json").exists():
        return "node"
    if (project_path / "go.mod").exists():
        return "go"
    if (project_path / "Cargo.toml").exists():
        return "rust"
    return "unknown"

def check_semver(project_path: Path, lang: str) -> bool:
    """Verifica si existe versión SemVer en el manifiesto correspondiente."""
    try:
        if lang == "python":
            for f in ["pyproject.toml", "setup.py"]:
                p = project_path / f
                if p.exists():
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    if re.search(r'version\s*=\s*["\']\d+\.\d+\.\d+["\']', txt):
                        return True
        elif lang == "node":
            p = project_path / "package.json"
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("version") and re.match(r"^\d+\.\d+\.\d+", data["version"]):
                    return True
        elif lang == "go":
            p = project_path / "go.mod"
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                if re.search(r"^\s*version\s+\d+\.\d+\.\d+", txt, re.MULTILINE):
                    return True
        elif lang == "rust":
            p = project_path / "Cargo.toml"
            if p.exists():
                txt = p.read_text(encoding="utf-8")
                if re.search(r'version\s*=\s*"\d+\.\d+\.\d+"', txt):
                    return True
    except Exception:
        pass
    return False

def check_changelog(project_path: Path) -> bool:
    p = project_path / "CHANGELOG.md"
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8", errors="ignore")
    # Verifica formato Keep a Changelog básico
    return bool(re.search(r"##\s*\[.*\]\s*-\s*\d{4}-\d{2}-\d{2}", txt))

def check_readme_images(project_path: Path) -> bool:
    p = project_path / "README.md"
    if not p.exists():
        return False
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return bool(re.search(r"!\[.*\]\(.*\)", txt))

REQUIRED_WIKI_PAGES = ("Home.md", "Architecture.md", "Getting-Started.md", "Operations.md")
WIKI_MIN_CHARS = 80

def check_wiki(project_path: Path) -> bool:
    """Verifica wiki/ con las páginas mínimas de RULES.md §5.9, rellenas (no stubs)."""
    wiki = project_path / "wiki"
    if not wiki.is_dir():
        return False
    for name in REQUIRED_WIKI_PAGES:
        p = wiki / name
        if not p.is_file():
            return False
        txt = p.read_text(encoding="utf-8", errors="ignore").strip()
        if len(txt) < WIKI_MIN_CHARS:
            return False
        if not re.search(r"^#\s+\S", txt, re.MULTILINE):
            return False
    return True

def check_file_exists(project_path: Path, name: str) -> bool:
    return (project_path / name).exists()

def check_ci(project_path: Path) -> bool:
    wf = project_path / ".github" / "workflows"
    if not wf.exists():
        return False
    return any(wf.glob("*.yml")) or any(wf.glob("*.yaml"))

def check_secret_scan(project_path: Path) -> bool:
    """Verifica guardarraíl de secretos: script + pre-commit + job en CI (RULES.md §6.2)."""
    if not (project_path / "scripts" / "check-secrets.py").exists():
        return False
    if not (project_path / ".pre-commit-config.yaml").exists():
        return False
    wf = project_path / ".github" / "workflows"
    if not wf.exists():
        return False
    for f in list(wf.glob("*.yml")) + list(wf.glob("*.yaml")):
        try:
            if "check-secrets.py" in f.read_text(encoding="utf-8", errors="ignore"):
                return True
        except Exception:
            continue
    return False

def scan_code_patterns(project_path: Path) -> Dict[str, bool]:
    """Escanea patrones de código para RULES §1-4 (optimizado)."""
    patterns = {
        "has_retry_backoff": [r"backoff", r"exponential.*retry", r"retry.*exponential", r"p-limit", r"Semaphore", r"async.*retry", r"tenacity"],
        "has_fallback_chain": [r"fallback", r"fall-back", r"try.*catch.*continue", r"model.*chain", r"alternative.*model"],
        "has_async": [r"async\s+def", r"async\s+function", r"await\s+", r"Promise\.", r"asyncio\.", r"threading\.Thread", r"ThreadPoolExecutor"],
        "has_progress": [r"progress", r"callback.*progres", r"tqdm", r"rich\.progress", r"ProgressBar", r"status\.json"],
        "has_error_classification": [r"classify.*error", r"error.*classif", r"\bAuth\b", r"\bRateLimit\b", r"\bNotFound\b", r"\bTimeout\b", r"\b401\b", r"\b429\b", r"\b503\b"],
        "has_cache": [r"\bcache\b", r"\bCache\b", r"\bLRU\b", r"\bRedis\b", r"\bIndexedDB\b", r"\bTTL\b", r"memoize", r"lru_cache"],
        "has_streaming": [r"\bstream\b", r"\bStream\b", r"BytesIO", r"io\.BytesIO", r"pipeline", r"generator", r"\byield\b"],
        "has_port_control": [r"EADDRINUSE", r"port.*in.use", r"listen.*port", r"server.*close", r"process\.exit"],
        "has_db_robustness": [r"busy_timeout", r"PRAGMA", r"transaction", r"idempotent", r"migration", r"schema.*check", r"runCatching"],
    }
    results = {k: False for k in patterns}
    code_ext = {".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt"}
    try:
        # Limit to first 30 code files per project for speed
        file_count = 0
        for f in project_path.rglob("*"):
            if file_count >= 30:
                break
            if f.suffix in code_ext and f.is_file():
                file_count += 1
                try:
                    txt = f.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for key, pats in patterns.items():
                    if not results[key]:
                        for pat in pats:
                            if re.search(pat, txt, re.IGNORECASE):
                                results[key] = True
                                break
    except Exception:
        pass
    return results

def audit_project(project_path: Path) -> ProjectAudit:
    name = project_path.name
    lang = detect_language(project_path)
    code_patterns = scan_code_patterns(project_path)

    has_semver = check_semver(project_path, lang)
    has_changelog = check_changelog(project_path)
    readme_has_images = check_readme_images(project_path)
    has_wiki = check_wiki(project_path)
    has_gitignore = check_file_exists(project_path, ".gitignore")
    has_dockerfile = check_file_exists(project_path, "Dockerfile")
    has_ci = check_ci(project_path)
    has_env_example = check_file_exists(project_path, ".env.example")
    has_config_yaml = check_file_exists(project_path, "config.yaml")
    has_secret_scan = check_secret_scan(project_path)

    # Score ponderado
    weights = {
        "has_semver": 10,
        "has_changelog": 10,
        "readme_has_images": 5,
        "has_wiki": 5,
        "has_gitignore": 5,
        "has_dockerfile": 5,
        "has_ci": 10,
        "has_env_example": 5,
        "has_config_yaml": 10,
        "has_secret_scan": 10,
        "has_retry_backoff": 5,
        "has_fallback_chain": 5,
        "has_async": 5,
        "has_progress": 5,
        "has_error_classification": 5,
        "has_cache": 5,
        "has_streaming": 5,
        "has_port_control": 5,
        "has_db_robustness": 5,
    }
    checks = {
        "has_semver": has_semver,
        "has_changelog": has_changelog,
        "readme_has_images": readme_has_images,
        "has_wiki": has_wiki,
        "has_gitignore": has_gitignore,
        "has_dockerfile": has_dockerfile,
        "has_ci": has_ci,
        "has_env_example": has_env_example,
        "has_config_yaml": has_config_yaml,
        "has_secret_scan": has_secret_scan,
        **code_patterns,
    }
    score = sum(w for k, w in weights.items() if checks.get(k, False))

    return ProjectAudit(
        name=name,
        path=str(project_path),
        has_semver=has_semver,
        has_changelog=has_changelog,
        readme_has_images=readme_has_images,
        has_wiki=has_wiki,
        has_gitignore=has_gitignore,
        has_dockerfile=has_dockerfile,
        has_ci=has_ci,
        has_env_example=has_env_example,
        has_config_yaml=has_config_yaml,
        has_secret_scan=has_secret_scan,
        has_retry_backoff=code_patterns["has_retry_backoff"],
        has_fallback_chain=code_patterns["has_fallback_chain"],
        has_async=code_patterns["has_async"],
        has_progress=code_patterns["has_progress"],
        has_error_classification=code_patterns["has_error_classification"],
        has_cache=code_patterns["has_cache"],
        has_streaming=code_patterns["has_streaming"],
        has_port_control=code_patterns["has_port_control"],
        has_db_robustness=code_patterns["has_db_robustness"],
        score=score,
        details={"language": lang},
    )

def generate_report(audits: List[ProjectAudit], output_path: Path) -> None:
    """Genera reporte Markdown estilo AUDIT_REPORT.md."""
    lines = [
        f"# REPORTE DE AUDITORÍA AUTOMATIZADA - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Total proyectos auditados: {len(audits)}",
        f"Promedio score: {sum(a.score for a in audits) / len(audits):.1f}/100" if audits else "N/A",
        "",
        "---",
        ""
    ]
    for a in sorted(audits, key=lambda x: -x.score):
        status = "✅" if a.score >= 80 else ("⚠️" if a.score >= 50 else "❌")
        lines.append(f"## {status} {a.name} — Score: {a.score}/100")
        lines.append(f"- **Ruta**: `{a.path}`")
        lines.append(f"- **Lenguaje**: {a.details.get('language', 'unknown')}")
        lines.append("")
        # Tabla de checks
        checks = [
            ("SemVer", a.has_semver),
            ("CHANGELOG", a.has_changelog),
            ("README c/ imágenes", a.readme_has_images),
            ("Wiki (wiki/ §5.9)", a.has_wiki),
            (".gitignore", a.has_gitignore),
            ("Dockerfile", a.has_dockerfile),
            ("CI/CD", a.has_ci),
            (".env.example", a.has_env_example),
            ("config.yaml (SSoT)", a.has_config_yaml),
            ("Escaneo de secretos (RULES.md §6)", a.has_secret_scan),
            ("Retry/Backoff", a.has_retry_backoff),
            ("Fallback chain", a.has_fallback_chain),
            ("Async/No-bloqueante", a.has_async),
            ("Progreso/status.json", a.has_progress),
            ("Clasificación errores", a.has_error_classification),
            ("Caché", a.has_cache),
            ("Streaming/Zero-disk", a.has_streaming),
            ("Control puertos", a.has_port_control),
            ("Robustez BD", a.has_db_robustness),
        ]
        lines.append("| Check | Estado |")
        lines.append("|-------|--------|")
        for label, ok in checks:
            lines.append(f"| {label} | {'✅' if ok else '❌'} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reporte generado: {output_path}")

def load_baseline(baseline_path: Path) -> Dict[str, int]:
    """Carga línea base de scores previos (JSON)."""
    if baseline_path.exists():
        return json.loads(baseline_path.read_text(encoding="utf-8"))
    return {}

def save_baseline(baseline_path: Path, audits: List[ProjectAudit]) -> None:
    data = {a.name: a.score for a in audits}
    baseline_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Auditoría dev-standards")
    parser.add_argument("--root", default="D:\\Projects", help="Directorio raíz de proyectos")
    parser.add_argument("--output", default="AUDIT_REPORT.md", help="Archivo de salida Markdown")
    parser.add_argument("--baseline", default="audit_baseline.json", help="Archivo JSON línea base")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit 1 si algún proyecto baja score")
    args = parser.parse_args()

    root = Path(args.root)
    projects = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")]
    print(f"Auditando {len(projects)} proyectos en {root}...")

    audits = []
    for p in projects:
        try:
            audit = audit_project(p)
            audits.append(audit)
            print(f"  {audit.name}: {audit.score}/100")
        except Exception as e:
            print(f"  {p.name}: ERROR - {e}")

    generate_report(audits, Path(args.output))

    baseline = load_baseline(Path(args.baseline))
    regressions = []
    for a in audits:
        prev = baseline.get(a.name)
        if prev is not None and a.score < prev:
            regressions.append(f"{a.name}: {prev} → {a.score} (-{prev - a.score})")

    if regressions:
        print("\n[ALERT]  REGRESIONES DETECTADAS:")
        for r in regressions:
            print(f"  - {r}")
        if args.fail_on_regression:
            sys.exit(1)
    else:
        print("\n[OK]  Sin regresiones vs. línea base.")

    save_baseline(Path(args.baseline), audits)
    print(f"Línea base actualizada: {args.baseline}")

if __name__ == "__main__":
    main()