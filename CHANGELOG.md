# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- RULES.md §5.9: every repository must keep a filled, up-to-date Wiki in `wiki/`
- Wiki check in `scripts/audit-standards.py` and `wiki/` scaffold in `scripts/bootstrap-project.sh`
- This repository's Wiki: `wiki/Home.md`, `Architecture.md`, `Getting-Started.md`, `Operations.md`
- RULES.md §6 (Seguridad y Gestión de Secretos): `scripts/check-secrets.py`, pre-commit hook, and
  CI `secret-scan` job, generated automatically by `bootstrap-project.sh` for every new repo

### Changed
- RULES.md §5.6 and §5.7 now include the Wiki as a bootstrap and audit requirement

### Removed
- Leftover `DeepSeek-V2` bootstrap demo (`src/deepseek-v2/`, README/`pyproject.toml` identity):
  this repo's own manifest and README now correctly describe `dev-standards` itself. CI's
  lint job and `Dockerfile` no longer reference the deleted `src/` package.

## [0.1.0] - 2026-09-20

### Added
- Initial release scaffold
