# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- RULES.md §5.11: `README.md` and every `wiki/` page carry `_Last updated: YYYY-MM-DD_` below the H1,
  updated in the same change as any significant edit. `bootstrap-project.sh` stamps it,
  `audit-standards.py` checks it (`has_last_updated`, 5 points), and this repo's README and Wiki carry it.
- RULES.md §5.5(c): README screenshots are captured with [iris](https://github.com/brijr/iris) into
  `docs/screenshots/`, relevant screens only. Bootstrap creates the folder and a commented iris recipe.
- RULES.md §6.5: new projects are offered the central API key catalog of the private
  `luciomerlo/LocalProjectsTracker` repo. Bootstrap writes `APIKEYS_MATCH=` plus every catalog key name
  as a commented option in `.env.example` (`--apikeys-catalog`, auto-detects `../LocalProjectsTracker/APIKEYS.env`);
  values never leave `APIKEYS.env`.

### Changed
- `generate-contexto.py`: the "Last updated" line is not taken as the project purpose.
- RULES.md §5.10: every repository must keep an up-to-date `contexto_proyecto.md` at the
  root (architecture summary plus the full text of relevant source, config, and normative
  docs) so a later LLM can read the codebase without walking the tree. Reference generator:
  `scripts/generate-contexto.py`, copied and run by `bootstrap-project.sh`. Audit check in
  `scripts/audit-standards.py`. This repository's own `contexto_proyecto.md` is generated.
- RULES.md §5.9: every repository must keep a filled, up-to-date Wiki in `wiki/`
- Wiki check in `scripts/audit-standards.py` and `wiki/` scaffold in `scripts/bootstrap-project.sh`
- This repository's Wiki: `wiki/Home.md`, `Architecture.md`, `Getting-Started.md`, `Operations.md`
- RULES.md §6 (Seguridad y Gestión de Secretos): `scripts/check-secrets.py`, pre-commit hook, and
  CI `secret-scan` job, generated automatically by `bootstrap-project.sh` for every new repo
- RULES.md §7 (Cómputo Local vs. Cómputo Web): standard for GPU/CUDA runtime detection with
  five selectable backends (`local`, `colab`, `cloud-api`, `cloud-serverless`, `modal`) that never
  remove `local` as an option. Reference implementation:
  - `scripts/gpu_compute.py` — `detect_cuda()`, `resolve_backend()`, `cuda_status_tag()`
    (green "Local GPU CUDA available" tag for dashboards), `HEAVY_BACKENDS`/`MODERATE_BACKENDS`
    per-project backend subsets
  - `scripts/make_colab_notebook.py` — generates the `colab` companion notebook (assisted
    flow: Colab has no public API for transparent remote invocation)
  - `scripts/run_on_runpod.py` — `cloud-serverless` client (RunPod Serverless REST API)
  - `scripts/run_on_modal.py` — `modal` client (`call_modal_function()`, Modal's Python-native
    remote-function lookup/call; ~$30 USD/month free credit, must be mentioned in any README
    that offers this backend)
  - `scripts/transcribe_via_groq.py` — `cloud-api` client for Whisper-based projects (Groq)
  - `scripts/run_on_hf_inference.py` — `cloud-api` client for other hosted models (HF Inference API)
- New Wiki page `wiki/Compute.md` documenting RULES.md §7 in full (the 5 backends, which
  subset each weight tier — red/yellow — is allowed, the diffusion-model exclusion, and the
  adoption checklist); `Home.md`, `Architecture.md`, `Getting-Started.md`, `Operations.md` and
  `_Sidebar.md` updated to reference §6/§7 and the new page

### Changed
- RULES.md §5.6 and §5.7 now include the Wiki as a bootstrap and audit requirement

### Removed
- Leftover `DeepSeek-V2` bootstrap demo (`src/deepseek-v2/`, README/`pyproject.toml` identity):
  this repo's own manifest and README now correctly describe `dev-standards` itself. CI's
  lint job and `Dockerfile` no longer reference the deleted `src/` package.

## [0.1.0] - 2026-09-20

### Added
- Initial release scaffold
