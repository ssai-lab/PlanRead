# Docker Image

The application ships as a single image: the FastAPI backend, the built React
frontend (`app/dist/`), PaddleOCR on the GPU, and the local `packages/`
libraries. `docker-compose.yml` mounts `./data` and a `chroma_db` volume on top.

```bash
docker compose build          # ~10-15 min cold, seconds when cached
docker compose up             # http://localhost:8001
docker compose logs -f
docker compose down
```

## What the image contains

| Layer | Contents |
| --- | --- |
| `frontend-builder` stage | `node:20-slim`, `npm ci`, `vite build` → `app/dist/` |
| Runtime base | `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04` (CUDA 11.8, cuDNN 8.9.6) |
| System packages | `python3.10`, `libgl1`, `libglib2.0-0`, `libsm6`, `libxext6`, `libxrender1`, `libgomp1`, `curl` |
| Python packages | `backend/requirements.txt` + the five `packages/*` libraries |
| Baked models | `all-MiniLM-L6-v2` (sentence-transformers) and PP-OCRv4 det/rec (PaddleOCR) |

## Design decisions

Each of these is deliberate; please read the "why" before changing one.

### `uv` instead of `pip`

Dependency installation is the slowest build step for this stack (paddle,
torch, paddlex, chromadb, langchain). `uv` resolves the whole graph once and
installs from a BuildKit cache mount (`/root/.cache/uv`), which took the install
phase to roughly **~50 s** on a warm cache. pip is not installed in the image.

### CPU-only torch

`torch` is only a transitive dependency of `sentence-transformers`, and nothing
in this repo imports it directly. `HuggingFaceEmbeddings` uses the CPU by
default, so the Dockerfile installs `torch==2.12.0` from
`https://download.pytorch.org/whl/cpu` before `requirements.txt` (PEP 440 makes
`2.12.0+cpu` satisfy the pinned `torch==2.12.0`).

The PyPI wheel for Linux would instead pull ~2.5-2.9 GB of `nvidia-*` CUDA 13
libraries. Besides the size, those would sit next to the CUDA 11.8 stack and
compete with PaddleOCR for the GPU's VRAM (4 GB on the reference RTX 3050 Ti).
If embeddings ever need the GPU, pin the CUDA build explicitly and re-check
VRAM headroom.

### PaddlePaddle wheel installed with `--no-deps`

`paddlepaddle-gpu==3.0.0` is not on PyPI, so it is installed by direct URL from
Paddle's Beijing CDN bucket (the default host returns HTTP 403 behind some
corporate DNS filters). That wheel declares `nvidia-*-cu11==11.8.*`
dependencies, but the `nvidia/cuda:11.8.0-cudnn8-runtime` base **already
provides every one of those libraries** (`libcudnn.so.8.9.6`, `libcublas.so.11`,
`libcufft`, `libcurand`, `libcusolver`, `libcusparse`, `libnccl`, `libnvrtc`).
Installing the wheels duplicated ~3.1 GB.

The wheel's non-CUDA dependencies are therefore listed in
`backend/requirements.txt` explicitly: `astor`, `decorator`, `opt-einsum`
(everything else was already covered). Do **not** drop `--no-deps` without
re-running the GPU check below: the only unresolved library at build time is
`libcuda.so.1`, which comes from the driver / `/usr/local/cuda/compat`, not
from pip.

### `opencv-contrib-python` instead of `opencv-python`

`paddlex[ocr-core]` (pulled in by `paddleocr`) already installs
`opencv-contrib-python`, which is a superset of `opencv-python`. Listing both
ships two copies of `cv2` (~90 MB). `requirements.txt` pins the contrib
distribution only.

### Local packages installed with `--no-deps`

All runtime dependencies of `packages/*` are pinned in
`backend/requirements.txt`. Installing them with `--no-deps` avoids resolving
the langchain/chromadb graph once per package.

### Layer ordering and caches

* apt lists/archives and the uv/npm caches are BuildKit cache mounts, so they
  never enter an image layer.
* The requirements install and the baked model downloads happen **before**
  `COPY packages/` and `COPY backend/`, so changing application code does not
  re-download models or rebuild the dependency layer.
* The frontend `dist/` is copied from the builder stage last.
* `.dockerignore` excludes `data/`, `.env`, caches, docs, tests and notebooks
  so the build context stays small.

### Kept on purpose

* The CUDA base image and `paddlepaddle-gpu`: OCR on the GPU is the point of
  the compose deployment (`construction_ocr/engine.py` auto-detects the GPU).
* The GL/SM/X11 libraries: `opencv-contrib-python` links against them.
* `curl` and the `HEALTHCHECK` hitting `/healthz`.

## Measured results

Measured on an RTX 3050 Ti laptop (WSL2, Docker 29, driver 616.92):

| Metric | Value |
| --- | --- |
| Image size (on disk) | 14.5 GB |
| Image size (compressed / registry) | 4.04 GB |
| No-op rebuild | 6.2 s |
| Rebuild after a backend code change | 2.3 s |
| Dependency install, warm uv cache | ~50 s |
| Container start → `/healthz` 200 | ~4 s |
| PaddleOCR GPU, first inference (CUDA init) | ~23 s |
| PaddleOCR GPU, warm inference | ~0.07 s |

Before the CUDA de-duplication and CPU torch changes the same pipeline produced
a 19.6 GB image; the original Dockerfile (pip, CUDA torch, duplicate OpenCV) is
estimated at ~22.5 GB.

Remaining bulk is inherent to GPU Paddle: `paddle/libs` alone is 3.9 GB
(`libphi_core.so` 1.7 GB, `libphi_gpu.so` 1.4 GB, `libflashattn.so` 679 MB).

## Verifying a build

```bash
# Build
docker build -t stem-ai:opt .

# Size
docker images stem-ai:opt

# Python sanity check (no GPU needed)
docker run --rm --entrypoint python stem-ai:opt -c \
  "import torch, cv2, paddle, sentence_transformers; print(torch.__version__)"

# GPU check: paddle must see the device
docker run --rm --gpus all --entrypoint python stem-ai:opt -c \
  "import paddle; print(paddle.device.is_compiled_with_cuda(), paddle.device.cuda.device_count())"

# GPU inference through the app's own package
docker run --rm --gpus all --entrypoint python stem-ai:opt -c \
  "import numpy as np; from construction_ocr.pipeline import detect_text; \
   print(detect_text(np.full((120,400,3),255,np.uint8)))"

# Serve and probe
docker compose up -d && curl -f http://localhost:8001/healthz
```

If `import paddle` reports a missing `lib*.so`, the base image stopped
providing a CUDA library the wheel expects. Check with:

```bash
docker run --rm --entrypoint sh stem-ai:opt -c \
  'ldd /usr/local/lib/python3.10/dist-packages/paddle/base/libpaddle.so | grep "not found"'
```

`libcuda.so.1` is expected there (it is supplied by the NVIDIA container
runtime at run time, and by `/usr/local/cuda/compat` during the build).

## Maintenance notes

* **Changing the `nvidia/cuda` base tag** (e.g. moving to CUDA 12.x) requires
  re-validating the `--no-deps` Paddle install: repeat the `ldd` and GPU
  inference checks above, and check whether the newer Paddle wheel still
  expects cuDNN 8.
* **Changing `paddlepaddle-gpu`** means re-checking its `requires_dist`; any new
  non-CUDA dependencies must be added to `backend/requirements.txt` because
  `--no-deps` skips them all.
* **Changing `backend/requirements.txt`** invalidates the dependency layer and
  the baked-model layer (by design — models must match the installed versions).
* **`uv` version**: the Dockerfile currently copies
  `ghcr.io/astral-sh/uv:latest`. Pin a version tag for reproducible builds.
* **CPU-only deployments**: a separate `Dockerfile.cpu` based on
  `python:3.10-slim` with CPU `paddlepaddle` would drop the CUDA base and
  `paddle/libs` GPU kernels (~1.8 GB), at the cost of GPU OCR.
