#!/usr/bin/env bash
set -Eeuo pipefail

LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN is not available in PATH." >&2
  exit 1
fi

if ! command -v terraform >/dev/null 2>&1; then
  echo "Error: terraform is not available in PATH." >&2
  exit 1
fi

cd -- "$LAB_DIR"

echo "Checking Python dependencies..."
"$PYTHON_BIN" -m pip check

echo "Running Python tests..."
"$PYTHON_BIN" -m unittest discover -s tests -v

echo "Initializing Terraform without a remote backend..."
terraform -chdir=terraform init -backend=false -input=false

echo "Checking and testing Terraform..."
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
terraform -chdir=terraform test

echo "Offline validation completed successfully."
