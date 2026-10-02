#!/usr/bin/env bash
set -euo pipefail

# Use the same configuration and database client as the Python initializer.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/init-db.py"
