#!/usr/bin/env python3
"""check-secrets.py — Bloquea commits con credenciales hardcodeadas (RULES.md §6.1).

Uso:
  python scripts/check-secrets.py            # escanea el staged diff (pre-commit)
  python scripts/check-secrets.py --tree      # escanea todos los archivos versionados (CI)
  python scripts/check-secrets.py --history   # escanea todo el historial (auditoría puntual)

Salida no vacía y exit code 1 si encuentra un patrón de secreto. Falso positivo:
agregar `# allowlist-secret` al final de la línea.
"""

import argparse
import re
import subprocess
import sys

PATTERNS = {
    "Groq API key": r"gsk_[A-Za-z0-9]{20,}",
    "OpenAI/Anthropic key": r"sk-(ant-)?[A-Za-z0-9_-]{20,}",
    "AWS access key": r"AKIA[0-9A-Z]{16}",
    "Google API key": r"AIza[0-9A-Za-z_-]{30,}",
    "GitHub token": r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}",
    "Slack token": r"xox[baprs]-[A-Za-z0-9-]{10,}",
    "Private key block": r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "Hardcoded secret assignment": r'(api[_-]?key|secret|token|password)["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
}
# Valores que parecen nombres de variable de entorno (ANTHROPIC_API_KEY), no secretos reales.
_ENV_VAR_LOOKALIKE = re.compile(r"^[A-Z][A-Z0-9_]{15,}$")
ALLOWLIST_MARKER = "allowlist-secret"
SKIP_FILES = (".env.example", "check-secrets.py")


def iter_lines(mode: str):
    if mode == "staged":
        diff = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--no-color"],
            capture_output=True, text=True, check=False,
        ).stdout
        path = None
        for line in diff.splitlines():
            if line.startswith("+++ b/"):
                path = line[6:]
            elif line.startswith("+") and not line.startswith("+++") and path:
                yield path, line[1:]
    elif mode == "tree":
        files = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=False,
        ).stdout.splitlines()
        for path in files:
            if any(skip in path for skip in SKIP_FILES):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        yield path, line
            except (OSError, IsADirectoryError):
                continue
    elif mode == "history":
        log = subprocess.run(
            ["git", "log", "--all", "-p", "--no-color"],
            capture_output=True, text=True, check=False,
        ).stdout
        path = None
        for line in log.splitlines():
            if line.startswith("+++ b/"):
                path = line[6:]
            elif line.startswith("+") and not line.startswith("+++") and path:
                yield path, line[1:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", action="store_true")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()

    mode = "tree" if args.tree else "history" if args.history else "staged"
    findings = []
    for path, line in iter_lines(mode):
        if any(skip in path for skip in SKIP_FILES) or ALLOWLIST_MARKER in line:
            continue
        for label, pattern in PATTERNS.items():
            m = re.search(pattern, line, re.IGNORECASE)
            if not m:
                continue
            # Para "Hardcoded secret assignment", descartar valores que son en
            # realidad un nombre de variable de entorno (ANTHROPIC_API_KEY), no un secreto.
            if label == "Hardcoded secret assignment" and _ENV_VAR_LOOKALIKE.match(m.group(2)):
                continue
            findings.append(f"{path}: posible {label}")
            break

    if findings:
        print("❌ Posibles secretos detectados (RULES.md §6.1):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nSi es un falso positivo, agregá '# allowlist-secret' al final de la línea.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
