#!/usr/bin/env bash
# Create the virtualenv, install dependencies and create .env if missing.
source "$(dirname "$0")/_common.sh"

SYSTEM_PYTHON="$(command -v python3 || command -v python || true)"
[[ -n "$SYSTEM_PYTHON" ]] || die "Python is not installed"

if [[ ! -d venv ]]; then
  info "Creating virtualenv"
  "$SYSTEM_PYTHON" -m venv venv
fi

PY="$(venv_python)"
info "Installing dependencies"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r requirements-dev.txt

if [[ ! -f .env ]]; then
  info "Creating .env from .env.example with a fresh SECRET_KEY"
  secret="$("$PY" -c 'import secrets; print(secrets.token_hex(32))')"
  sed "s/^SECRET_KEY=.*/SECRET_KEY=$secret/" .env.example > .env
fi

info "Done. Start the app with: scripts/dev.sh"
