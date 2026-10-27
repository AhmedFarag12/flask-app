#!/usr/bin/env bash
# Deploy to the Kubernetes cluster of the current kubectl context.
#   scripts/deploy.sh <image>     e.g. ghcr.io/me/flask-todo:abc1234
# Secrets are read from .env (or ENV_FILE) and stored as a Kubernetes Secret.
source "$(dirname "$0")/_common.sh"
require kubectl

IMAGE="${1:-}"
[[ -n "$IMAGE" ]] || die "usage: scripts/deploy.sh <image>"
ENV_FILE="${ENV_FILE:-.env}"
[[ -f "$ENV_FILE" ]] || die "$ENV_FILE not found"
NAMESPACE=flask-todo

info "Deploying $IMAGE to context $(kubectl config current-context)"
kubectl apply -f k8s/namespace.yaml

info "Updating secret from $ENV_FILE"
kubectl -n "$NAMESPACE" create secret generic flask-todo-secret \
  --from-env-file="$ENV_FILE" --dry-run=client -o yaml | kubectl apply -f -

info "Applying manifests"
kubectl apply -k k8s
kubectl -n "$NAMESPACE" set image deployment/flask-todo web="$IMAGE"

info "Waiting for rollout"
kubectl -n "$NAMESPACE" rollout status deployment/flask-todo --timeout=120s
