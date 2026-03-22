# ============================================================
# Stage 1: Builder — Install dependencies (cần C++ cho Prophet)
# ============================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Cài build tools cần thiết cho Prophet (pystan), LightGBM, psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary từ official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy lock files trước → tận dụng Docker layer cache
COPY pyproject.toml uv.lock ./

# Sync deps vào .venv (không cài dev deps, không cài project package)
# --frozen: dùng lock file chính xác, không update
RUN uv sync --frozen --no-dev --no-install-project

# ============================================================
# Stage 2: Runtime — Image gọn nhẹ, không có build tools
# ============================================================
FROM python:3.10-slim AS runtime

WORKDIR /app

# Non-root user để tăng bảo mật
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Copy virtual environment từ builder stage
COPY --from=builder --chown=appuser:appgroup /app/.venv ./.venv

# Copy source code của backend
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup run.py ./

# Tạo thư mục shared (models & data sẽ được mount qua volume)
RUN mkdir -p /app/shared/models /app/shared/data/processed \
    && chown -R appuser:appgroup /app/shared

# Thư mục logs
RUN mkdir -p /app/shared/logs && chown appuser:appgroup /app/shared/logs

# Cấu hình PATH dùng venv
ENV PATH="/app/.venv/bin:$PATH"
# PYTHONPATH để import từ src/
ENV PYTHONPATH="/app/src"
# Không buffer stdout/stderr (quan trọng cho logging trong container)
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Production: không dùng reload=True
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
