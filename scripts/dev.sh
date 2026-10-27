#!/usr/bin/env bash
# Run the Flask development server with auto-reload.
source "$(dirname "$0")/_common.sh"

"$(venv_python)" run.py
