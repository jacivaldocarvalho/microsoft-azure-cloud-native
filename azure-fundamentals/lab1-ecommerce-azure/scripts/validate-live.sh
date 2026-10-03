#!/usr/bin/env bash
set -Eeuo pipefail

LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VAR_FILE="${1:-terraform.tfvars}"
PLAN_FILE="$(mktemp /tmp/lab1-live-validation.XXXXXX.tfplan)"

cleanup() {
  rm -f -- "$PLAN_FILE"
}
trap cleanup EXIT

required_commands=(az terraform "$PYTHON_BIN")
for command_name in "${required_commands[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Error: $command_name is not available in PATH." >&2
    exit 1
  fi
done

required_variables=(TF_VAR_sql_password)
for variable_name in "${required_variables[@]}"; do
  if [[ -z "${!variable_name:-}" ]]; then
    echo "Error: $variable_name is required." >&2
    exit 1
  fi
done

cd -- "$LAB_DIR"

echo "Checking Terraform state for drift..."
set +e
terraform -chdir=terraform plan \
  -detailed-exitcode \
  -input=false \
  -var-file="$VAR_FILE" \
  -out="$PLAN_FILE"
plan_status=$?
set -e

case "$plan_status" in
  0) ;;
  2)
    echo "Error: Terraform detected infrastructure drift or pending changes." >&2
    exit 1
    ;;
  *)
    echo "Error: Terraform plan failed." >&2
    exit "$plan_status"
    ;;
esac

terraform -chdir=terraform state list

resource_group="$(terraform -chdir=terraform output -raw resource_group_name)"
storage_account="$(terraform -chdir=terraform output -raw storage_account_name)"
storage_container="$(terraform -chdir=terraform output -raw storage_container_name)"
storage_connection_string="$(az storage account show-connection-string \
  --resource-group "$resource_group" \
  --name "$storage_account" \
  --query connectionString \
  --output tsv)"

echo "Checking repeatable database initialization and queries..."
"$PYTHON_BIN" app/database/init-db.py
"$PYTHON_BIN" app/database/init-db.py
"$PYTHON_BIN" app/database/inspect-db.py schema
"$PYTHON_BIN" app/database/inspect-db.py products

echo "Checking private Blob container configuration and stored objects..."
public_access="$(az storage container show \
  --name "$storage_container" \
  --connection-string "$storage_connection_string" \
  --query 'properties.publicAccess' \
  --output tsv)"
if [[ -n "$public_access" && "$public_access" != "None" && "$public_access" != "null" ]]; then
  echo "Error: Blob container public access is enabled: $public_access" >&2
  exit 1
fi
az storage container show \
  --name "$storage_container" \
  --connection-string "$storage_connection_string" \
  --query '{Name:name,PublicAccess:properties.publicAccess}' \
  --output table
az storage blob list \
  --container-name "$storage_container" \
  --connection-string "$storage_connection_string" \
  --query '[].{Name:name,ContentType:properties.contentSettings.contentType,SizeBytes:properties.contentLength}' \
  --output table

echo "Live validation completed successfully."
