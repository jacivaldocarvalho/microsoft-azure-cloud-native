#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PLAN_FILE="$(mktemp /tmp/lab1-ecommerce.XXXXXX.tfplan)"

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

echo "Checking Terraform formatting and configuration..."
terraform fmt -check -recursive
terraform validate

echo "Creating a saved execution plan..."
terraform plan -input=false -out="$PLAN_FILE" "$@"

read -r -p "Apply this plan? [y/N]: " confirmation
case "$confirmation" in
  y | Y | yes | YES)
    echo "Applying the saved plan..."
    terraform apply -input=false "$PLAN_FILE"
    ;;
  *)
    echo "Plan not applied."
    ;;
esac
