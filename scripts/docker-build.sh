#!/usr/bin/env bash
# Build the Docker image and smoke-test it.
#   scripts/docker-build.sh [tag]        tag defaults to the git sha or "local"
#   PUSH=1 IMAGE_NAME=ghcr.io/me/flask-todo scripts/docker-build.sh v1
source "$(dirname "$0")/_common.sh"
require docker

TAG="${1:-$(git rev-parse --short HEAD 2>/dev/null || echo local)}"
IMAGE="$IMAGE_NAME:$TAG"

info "Building $IMAGE"
docker build -t "$IMAGE" .

info "Smoke test: starting container and calling /api/health"
cid="$(docker run -d -e SECRET_KEY=smoke-test -p 127.0.0.1::8000 "$IMAGE")"
trap 'docker rm -f "$cid" >/dev/null' EXIT
port="$(docker port "$cid" 8000 | head -n1 | sed 's/.*://')"

for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:$port/api/health" >/dev/null 2>&1; then
    info "Healthy"
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:$port/api/health" >/dev/null || {
  docker logs "$cid"
  die "container did not become healthy"
}

if [[ "${PUSH:-0}" == "1" ]]; then
  info "Pushing $IMAGE"
  docker push "$IMAGE"
fi
