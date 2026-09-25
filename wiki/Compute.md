# Compute — dev-standards

_Last updated: 2026-09-25_

Cómputo local (GPU/CUDA) vs. cómputo web, para todo proyecto cuya ejecución
dependa opcionalmente de una GPU (`torch`, `tensorflow`, `demucs`, `whisper`,
modelos de `transformers`, etc.). Fuente de verdad: [RULES.md §7](../RULES.md).

## Por qué existe

Varios proyectos del ecosistema (separadores de stems con Demucs, generación
musical, transcripción Whisper, tagging con AST) asumían `device="cuda"` sin
verificar disponibilidad, y no tenían forma de correr la parte pesada si la
máquina no tenía GPU. §7 estandariza la detección y ofrece alternativas web
sin sacar nunca la opción local.

## Detección obligatoria (§7.1)

Antes de asumir GPU: `torch.cuda.is_available()` o equivalente. Nunca
hardcodear `device="cuda"` sin ruta de fallback a CPU o a un backend remoto.

## Los 5 backends (§7.2)

Ninguno reemplaza permanentemente a los demás; se seleccionan en runtime.

| Backend | Cómo funciona | Automático | Requiere |
|---|---|---|---|
| `local` | GPU (o CPU) de la máquina donde corre el proceso. **Nunca se elimina como opción.** | Sí | Nada — es el default cuando hay CUDA |
| `colab` | Genera/actualiza un notebook companion (`notebook/<tarea>.ipynb`) con badge "Open in Colab" | **No** — flujo asistido: el usuario abre el notebook, sube el input, corre las celdas y descarga el resultado | Nada de antemano; Colab no expone API pública para invocación remota transparente |
| `cloud-api` | Llama a un servicio gestionado con el modelo ya hospedado (Groq, HF Inference API) vía API key | Sí | API key en `.env` |
| `cloud-serverless` | Despliega/invoca un contenedor propio en una plataforma serverless GPU (RunPod) para checkpoints/fine-tunes propios | Sí | Endpoint desplegado de antemano + `RUNPOD_API_KEY`/`RUNPOD_ENDPOINT_ID` |
| `modal` | Invoca una función Python ya deployada en [Modal](https://modal.com) vía `modal.Function.lookup(...).remote(...)` | Sí | `modal deploy modal_app.py` hecho una vez (auth: `modal token new`). **~$30 USD de crédito gratis por mes — todo README que ofrezca este backend debe decirlo explícitamente.** |

`modal` no requiere armar ni mantener una imagen Docker propia como
`cloud-serverless`: la función pesada se decora con `@app.function(gpu=...)`
en un `modal_app.py` del proyecto y se despliega con un solo comando.

## Qué backend le toca a cada proyecto (por tier de peso)

El ecosistema clasificó cada proyecto con carga GPU en dos tiers según qué
tan pesada es la carga, y cada tier tiene su propio subconjunto de backends
remotos — **no todos los proyectos ofrecen los 5 backends**:

| Tier | Backends remotos permitidos | Backends explícitamente excluidos |
|---|---|---|
| **Rojo** (muy pesado: separación de stems con Demucs, generación musical) | `colab` (última prioridad, pero debe existir), `cloud-serverless`, `modal` | `cloud-api` — no hay servicio gestionado para checkpoints custom |
| **Amarillo** (moderado: transcripción Whisper, tagging AST, subtitulado) | `cloud-api`, `cloud-serverless`, `modal` | `colab` — la carga no lo justifica |

`local` está en ambos tiers siempre. Ejemplos ya migrados: rojos —
CompleteStemSeparator, tango-stem-separator, BandoneonSeparator,
LoFiMusicGeneration; amarillos — LocalCoursesIndexer, OfflineLucio,
YTTranscript, PiazzollaMidiGenerator, ars-nova-mpt.

## Selección de backend en la UI/CLI (§7.3)

- **Dashboard/UI:** selector visible en un panel de Settings con las
  opciones que el proyecto soporte. Debe mostrarse un tag de estado: verde
  con el texto **"Local GPU CUDA available"** cuando `detect_cuda()` da
  `True`; gris o rojo indicando ausencia de GPU local cuando no.
- **CLI:** flag `--compute {local,colab,cloud-api,cloud-serverless,modal}`
  (limitado al subconjunto del tier). Default `local` si hay CUDA
  disponible; si no hay CUDA y no se especificó `--compute`, informar la
  ausencia y listar alternativas — nunca caer en CPU silenciosamente sobre
  una carga pesada.

## Modelos tipo Stable Diffusion (§7.4)

Los modelos de difusión de imágenes (y componentes de difusión dentro de
proyectos no-Stable-Diffusion, ej. Riffusion dentro de un pipeline de
audio) quedan **fuera de `colab`/`cloud-api`/`cloud-serverless`/`modal`**
por decisión de producto. Deben quedar detrás de un flag explícito de
opt-in (`--allow-diffusion-models`), nunca habilitados por default,
independientemente del backend de cómputo elegido.

## Implementación de referencia (§7.5)

`scripts/gpu_compute.py` en este repositorio provee:

- `detect_cuda()` — nunca lanza excepción, intenta importar `torch` y cae a `False`.
- `resolve_backend(requested, *, available=BACKENDS, allow_diffusion_models=False)`.
- `cuda_status_tag()` — el tag verde/gris/rojo para dashboards.
- `colab_badge(notebook_path, repo, branch="main")` / `require_colab_notebook(...)`.
- `HEAVY_BACKENDS = ("local", "cloud-serverless", "modal", "colab")` (tier rojo).
- `MODERATE_BACKENDS = ("local", "cloud-api", "cloud-serverless", "modal")` (tier amarillo).

Clientes por backend, cada uno con su propio manejo de error tipado (nunca
cae a local en silencio si el remoto falla):

- `scripts/make_colab_notebook.py` — genera el `.ipynb` companion.
- `scripts/run_on_runpod.py` — `RunPodError`, `run_job(payload, *, endpoint_id=None, api_key=None, ...)`.
- `scripts/run_on_hf_inference.py` — `HFInferenceError`, `infer(*, model_id, data, ...)`.
- `scripts/transcribe_via_groq.py` — `GroqTranscriptionError`, `transcribe()`/`transcribe_verbose()`.
- `scripts/run_on_modal.py` — `ModalError`, `call_modal_function(app_name, function_name, **kwargs)`.

Cada proyecto copia estos scripts a su propio `scripts/` y adapta el
dispatch a su carga de trabajo (un `modal_app.py`, un `_separate_modal()`,
etc.) en vez de reimplementar la detección desde cero.

## Adoptar esto en un proyecto existente

1. Copiar `scripts/gpu_compute.py` (y los clientes de los backends que el
   tier del proyecto permita) desde dev-standards.
2. Definir el tier (rojo/amarillo) y elegir el subconjunto de
   `HEAVY_BACKENDS`/`MODERATE_BACKENDS` correspondiente.
3. Agregar el selector de backend a la UI (Settings) o el flag `--compute`
   a la CLI, con el tag de estado CUDA si es dashboard.
4. Si se ofrece `modal`: escribir `modal_app.py` con la función pesada
   decorada, documentar `modal deploy modal_app.py` y **mencionar el
   crédito gratis mensual en el README** (obligatorio, no opcional).
5. Si se ofrece `colab`: generar el notebook companion con
   `make_colab_notebook.py` y dejar claro en el README que es un flujo
   asistido, no automático.
6. Actualizar el README y esta clase de página (`wiki/Compute.md` si el
   proyecto la adoptó) en el mismo cambio (RULES.md §5.9).
