#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PLAN_FILE="$(mktemp /tmp/lab1-ecommerce-destroy.XXXXXX.tfplan)"

cleanup() {
  rm -f -- "$PLAN_FILE"
}
trap cleanup EXIT

if ! command -v terraform >/dev/null 2>&1; then
  echo "Error: terraform is not installed or is not available in PATH." >&2
  exit 1
fi

cd -- "$SCRIPT_DIR"

echo "Initializing Terraform..."
terraform init -input=false

echo "Creating a saved destruction plan..."
terraform plan -destroy -input=false -out="$PLAN_FILE" "$@"

echo "This removes every resource managed by this lab state."
read -r -p "Type DESTROY to apply the destruction plan: " confirmation
if [[ "$confirmation" != "DESTROY" ]]; then
  echo "Destruction cancelled."
  exit 0
fi

terraform apply -input=false "$PLAN_FILE"
echo "Destruction completed."
