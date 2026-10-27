# Shared helpers, sourced by the other scripts (not run directly).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

IMAGE_NAME="${IMAGE_NAME:-flask-todo}"

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# The venv keeps its python in bin/ on Linux/macOS and Scripts/ on Windows.
venv_python() {
  if [[ -x venv/bin/python ]]; then
    echo venv/bin/python
  elif [[ -x venv/Scripts/python.exe ]]; then
    echo venv/Scripts/python.exe
  else
    die "virtualenv not found, run scripts/setup.sh first"
  fi
}

require() {
  command -v "$1" >/dev/null 2>&1 || die "'$1' is not installed"
}
