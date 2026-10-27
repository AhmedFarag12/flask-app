# syntax=docker/dockerfile:1

# ---- build stage: install dependencies into a virtualenv ----
FROM python:3.13-slim AS build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- runtime stage: small image with only what the app needs ----
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Run as an unprivileged user instead of root.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=appuser:appuser config.py gunicorn.conf.py run.py ./
COPY --chown=appuser:appuser app ./app

# The SQLite database lives in instance/; mount a volume here to keep data.
RUN mkdir instance && chown appuser:appuser instance
VOLUME ["/app/instance"]

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/health', timeout=2)"

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:create_app()"]
