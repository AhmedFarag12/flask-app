#!/usr/bin/env bash
# Lint and test, the same checks CI runs. Extra args go to pytest.
source "$(dirname "$0")/_common.sh"

PY="$(venv_python)"

info "flake8"
"$PY" -m flake8

info "pytest"
"$PY" -m pytest --cov=app --cov-report=term-missing "$@"
