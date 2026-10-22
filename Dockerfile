# syntax=docker/dockerfile:1
# ============================================================
# Stage 1: Build the React frontend
# ============================================================
FROM node:20-slim AS frontend-builder

WORKDIR /build/app
COPY app/package.json app/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --no-fund
COPY app/ ./
RUN npm run build
# Output: /build/app/dist/

# ============================================================
# Stage 2: Python backend + CUDA runtime
# ============================================================
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    HF_HUB_DISABLE_TELEMETRY=1 \
    ANONYMIZED_TELEMETRY=False

# uv replaces pip: same indexes, far faster resolution for this stack.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ── System dependencies ──────────────────────────────────────
# No python3-pip / python3.10-venv: uv installs into the system interpreter.
# apt caches live in BuildKit mounts, so their contents never enter a layer.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        python3.10 \
        libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
        libgomp1 curl && \
    ln -sf /usr/bin/python3.10 /usr/bin/python

WORKDIR /app

# ── Python dependencies ──────────────────────────────────────
# PaddleOCR 3.x + PaddlePaddle 3.x are pinned in backend/requirements.txt.
# paddlepaddle-gpu==3.0.0 is not published on PyPI. Paddle's default CDN host
# (paddle-whl.cdn.bcebos.com) is blocked by some corporate networks
# (OpenDNS/Cisco Umbrella -> HTTP 403), but the identical wheel is served from
# the unblocked Beijing bucket. Install it by direct URL alongside
# requirements.txt (one resolution instead of two).
ARG PADDLE_GPU_WHEEL=https://paddle-whl.bj.bcebos.com/stable/cu118/paddlepaddle-gpu/paddlepaddle_gpu-3.0.0-cp310-cp310-manylinux1_x86_64.whl
COPY backend/requirements.txt /app/backend/requirements.txt

# torch is only a transitive dependency of sentence-transformers, and the app
# never uses CUDA through torch (HuggingFaceEmbeddings defaults to CPU). The
# PyPI wheel would drag in ~2.5 GB of unused nvidia-cu13 libraries on top of
# the cu118 stack this image already carries, so install the CPU build first.
# requirements.txt's `torch==2.12.0` is satisfied by 2.12.0+cpu (PEP 440).
# The paddlepaddle-gpu wheel declares nvidia-*-cu11==11.8.* dependencies, but
# this base image already ships the matching CUDA 11.8 runtime and cuDNN 8.9
# libraries (verified: only libcuda.so.1 is "not found" at build time, and that
# comes from the driver/compat dir). Installing those wheels would add ~3.1 GB
# of duplicate CUDA libraries, so install the wheel with --no-deps and list its
# two non-CUDA-only deps (astor, opt-einsum) in requirements.txt.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --python /usr/bin/python3.10 --break-system-packages \
        --index-url https://download.pytorch.org/whl/cpu \
        torch==2.12.0 && \
    uv pip install --system --python /usr/bin/python3.10 --break-system-packages \
        --no-deps "${PADDLE_GPU_WHEEL}" && \
    uv pip install --system --python /usr/bin/python3.10 --break-system-packages \
        -r /app/backend/requirements.txt

# ── Pre-download heavy ML models ─────────────────────────────
# Baked into the image so containers start instantly. These depend only on
# requirements.txt (paddleocr + sentence-transformers), so they run before the
# local packages and stay cached across local-package code changes.
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2'); \
print('[Docker] sentence-transformers model cached')" && \
    LD_LIBRARY_PATH=/usr/local/cuda/compat:${LD_LIBRARY_PATH} \
    CUDA_VISIBLE_DEVICES="" \
    python -c "\
import os; os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK']='True'; \
from paddleocr import PaddleOCR; \
PaddleOCR(device='cpu', use_textline_orientation=True, lang='en', \
          ocr_version='PP-OCRv4', \
          use_doc_orientation_classify=False, \
          use_doc_unwarping=False); \
print('[Docker] PaddleOCR PP-OCRv4 models cached')"

# ── Local packages ───────────────────────────────────────────
# --no-deps: every runtime dependency is already pinned in requirements.txt, so
# this skips re-resolving the langchain/chromadb tree once per package.
COPY packages/ /app/packages/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --python /usr/bin/python3.10 \
        --break-system-packages --no-deps \
        /app/packages/construction_ocr \
        /app/packages/construction_circle_detector \
        /app/packages/construction_llm_explainer \
        /app/packages/construction_plan_rag \
        /app/packages/construction_vlm_analyzer

# ── Copy backend code ────────────────────────────────────────
COPY backend/ /app/backend/

# ── Copy built frontend from Stage 1 ─────────────────────────
COPY --from=frontend-builder /build/app/dist/ /app/app/dist/

# ── Expose port ───────────────────────────────────────────────
EXPOSE 8001

# ── Health check ──────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/healthz || exit 1

# ── Startup ───────────────────────────────────────────────────
# Run uvicorn directly (bypass launcher.py which uses Tkinter GUI)
WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
