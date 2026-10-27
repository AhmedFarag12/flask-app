"""Gunicorn settings for running the app in production (e.g. inside Docker)."""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# SQLite allows only one writer at a time, so a single worker process with a
# few threads is the safe default. Raise WEB_WORKERS only with a server DB.
workers = int(os.environ.get("WEB_WORKERS", "1"))
threads = int(os.environ.get("WEB_THREADS", "4"))
worker_class = "gthread"
timeout = 30

# Log to stdout/stderr so `docker logs` and `kubectl logs` pick them up.
accesslog = "-"
errorlog = "-"
