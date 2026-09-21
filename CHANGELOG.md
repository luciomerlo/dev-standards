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
- RULES.md §7 (Cómputo Local vs. Cómputo Web): standard for GPU/CUDA runtime detection with
  four selectable backends (`local`, `colab`, `cloud-api`, `cloud-serverless`) that never remove
  `local` as an option. Reference implementation:
  - `scripts/gpu_compute.py` — `detect_cuda()`, `resolve_backend()`, `cuda_status_tag()`
    (green "Local GPU CUDA available" tag for dashboards), `HEAVY_BACKENDS`/`MODERATE_BACKENDS`
    per-project backend subsets
  - `scripts/make_colab_notebook.py` — generates the `colab` companion notebook (assisted
    flow: Colab has no public API for transparent remote invocation)
  - `scripts/run_on_runpod.py` — `cloud-serverless` client (RunPod Serverless REST API)
  - `scripts/transcribe_via_groq.py` — `cloud-api` client for Whisper-based projects (Groq)
  - `scripts/run_on_hf_inference.py` — `cloud-api` client for other hosted models (HF Inference API)

### Changed
- RULES.md §5.6 and §5.7 now include the Wiki as a bootstrap and audit requirement

### Removed
- Leftover `DeepSeek-V2` bootstrap demo (`src/deepseek-v2/`, README/`pyproject.toml` identity):
  this repo's own manifest and README now correctly describe `dev-standards` itself. CI's
  lint job and `Dockerfile` no longer reference the deleted `src/` package.

## [0.1.0] - 2026-09-20

### Added
- Initial release scaffold
